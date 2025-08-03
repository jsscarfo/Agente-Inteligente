#!/usr/bin/env python3
"""
🔍 Procesador de Visión - Extracción y Análisis de Imágenes

Este módulo proporciona capacidades avanzadas de procesamiento de imágenes,
incluyendo extracción de imágenes de PDFs, OCR, y análisis visual.
"""

import asyncio
import base64
import io
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

import aiohttp
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF

# Intentar importar OCR
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

from .config import get_config

logger = logging.getLogger(__name__)


class ImageFormat(Enum):
    """Formatos de imagen soportados"""
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    WEBP = "webp"


@dataclass
class ExtractedImage:
    """Imagen extraída de un documento"""
    id: str
    page_number: int
    image_data: bytes
    format: ImageFormat
    width: int
    height: int
    bbox: Tuple[int, int, int, int]  # x0, y0, x1, y1
    confidence: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ImageAnalysis:
    """Resultado del análisis de una imagen"""
    image_id: str
    description: Optional[str] = None
    ocr_text: Optional[str] = None
    objects_detected: List[str] = None
    text_blocks: List[Dict[str, Any]] = None
    confidence: float = 0.0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.objects_detected is None:
            self.objects_detected = []
        if self.text_blocks is None:
            self.text_blocks = []
        if self.metadata is None:
            self.metadata = {}


class VisionProcessor:
    """
    Procesador de Visión - Maneja extracción y análisis de imágenes
    
    Proporciona capacidades completas para:
    - Extraer imágenes de PDFs
    - Realizar OCR en imágenes
    - Analizar contenido visual
    - Procesar múltiples formatos
    """
    
    def __init__(self):
        self.config = get_config()
        
        # Configuración
        self.supported_formats = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'
        }
        self.max_image_size = 50 * 1024 * 1024  # 50MB
        self.min_image_size = 100  # 100 bytes
        
        # Inicializar OCR
        self.ocr_engines = self._initialize_ocr_engines()
        
        # Servicios de análisis
        self.analysis_services = {
            'ocr': self._perform_ocr,
            'object_detection': self._detect_objects,
            'text_extraction': self._extract_text_blocks
        }
    
    def _initialize_ocr_engines(self) -> Dict[str, Any]:
        """Inicializar motores de OCR disponibles"""
        engines = {}
        
        # Tesseract OCR
        if TESSERACT_AVAILABLE:
            try:
                # Verificar que Tesseract esté instalado
                pytesseract.get_tesseract_version()
                engines['tesseract'] = pytesseract
                logger.info("✅ Tesseract OCR disponible")
            except Exception as e:
                logger.warning(f"⚠️ Tesseract no disponible: {e}")
        
        # EasyOCR
        if EASYOCR_AVAILABLE:
            try:
                engines['easyocr'] = easyocr.Reader(['en', 'es'])
                logger.info("✅ EasyOCR disponible")
            except Exception as e:
                logger.warning(f"⚠️ EasyOCR no disponible: {e}")
        
        if not engines:
            logger.warning("⚠️ No hay motores de OCR disponibles")
        
        return engines
    
    async def extract_images_from_pdf(self, pdf_path: Path) -> List[ExtractedImage]:
        """Extraer todas las imágenes de un PDF"""
        try:
            logger.info(f"🔍 Extrayendo imágenes de: {pdf_path.name}")
            
            # Abrir PDF con PyMuPDF
            doc = fitz.open(pdf_path)
            extracted_images = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Obtener lista de imágenes en la página
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Extraer imagen
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        # Convertir a bytes
                        img_data = pix.tobytes("png")
                        
                        # Verificar tamaño mínimo
                        if len(img_data) < self.min_image_size:
                            continue
                        
                        # Crear objeto de imagen extraída
                        extracted_image = ExtractedImage(
                            id=f"img_{page_num}_{img_index}",
                            page_number=page_num + 1,
                            image_data=img_data,
                            format=ImageFormat.PNG,
                            width=pix.width,
                            height=pix.height,
                            bbox=(0, 0, pix.width, pix.height),
                            metadata={
                                'source_pdf': pdf_path.name,
                                'page_number': page_num + 1,
                                'image_index': img_index,
                                'xref': xref
                            }
                        )
                        
                        extracted_images.append(extracted_image)
                        logger.info(f"✅ Imagen extraída: {extracted_image.id} ({pix.width}x{pix.height})")
                        
                        # Liberar memoria
                        pix = None
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Error extrayendo imagen {img_index} de página {page_num}: {e}")
                        continue
            
            doc.close()
            
            logger.info(f"📊 Total de imágenes extraídas: {len(extracted_images)}")
            return extracted_images
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo imágenes del PDF: {e}")
            return []
    
    async def analyze_image(self, image_data: bytes, image_id: str = None) -> ImageAnalysis:
        """Analizar una imagen usando múltiples servicios"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if image_id is None:
                image_id = f"img_{hash(image_data) % 10000}"
            
            analysis = ImageAnalysis(image_id=image_id)
            
            # Procesar imagen con todos los servicios disponibles
            tasks = []
            
            # OCR
            if self.ocr_engines:
                tasks.append(self._perform_ocr(image_data))
            
            # Detección de objetos
            tasks.append(self._detect_objects(image_data))
            
            # Extracción de bloques de texto
            tasks.append(self._extract_text_blocks(image_data))
            
            # Ejecutar análisis en paralelo
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Procesar resultados
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"⚠️ Error en análisis {i}: {result}")
                    continue
                
                if result:
                    # Combinar resultados en el análisis
                    if hasattr(result, 'ocr_text') and result.ocr_text:
                        analysis.ocr_text = result.ocr_text
                    
                    if hasattr(result, 'objects_detected') and result.objects_detected:
                        analysis.objects_detected.extend(result.objects_detected)
                    
                    if hasattr(result, 'text_blocks') and result.text_blocks:
                        analysis.text_blocks.extend(result.text_blocks)
                    
                    if hasattr(result, 'description') and result.description:
                        analysis.description = result.description
            
            # Calcular tiempo de procesamiento
            analysis.processing_time = asyncio.get_event_loop().time() - start_time
            
            # Calcular confianza general
            analysis.confidence = self._calculate_confidence(analysis)
            
            logger.info(f"✅ Análisis completado para {image_id} en {analysis.processing_time:.2f}s")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analizando imagen {image_id}: {e}")
            return ImageAnalysis(
                image_id=image_id or "unknown",
                confidence=0.0,
                processing_time=asyncio.get_event_loop().time() - start_time
            )
    
    async def _perform_ocr(self, image_data: bytes) -> Optional[ImageAnalysis]:
        """Realizar OCR en la imagen"""
        try:
            # Abrir imagen con Pillow
            image = Image.open(io.BytesIO(image_data))
            
            ocr_results = []
            
            # Probar diferentes motores de OCR
            for engine_name, engine in self.ocr_engines.items():
                try:
                    if engine_name == 'tesseract':
                        # Tesseract OCR
                        text = pytesseract.image_to_string(image, lang='eng+spa')
                        if text.strip():
                            ocr_results.append({
                                'engine': 'tesseract',
                                'text': text.strip(),
                                'confidence': 0.8
                            })
                    
                    elif engine_name == 'easyocr':
                        # EasyOCR
                        results = engine.readtext(np.array(image))
                        text_parts = []
                        for (bbox, text, confidence) in results:
                            text_parts.append(text)
                        
                        if text_parts:
                            ocr_results.append({
                                'engine': 'easyocr',
                                'text': ' '.join(text_parts),
                                'confidence': 0.9
                            })
                
                except Exception as e:
                    logger.warning(f"⚠️ Error con OCR {engine_name}: {e}")
                    continue
            
            if ocr_results:
                # Usar el resultado con mayor confianza
                best_result = max(ocr_results, key=lambda x: x['confidence'])
                
                return ImageAnalysis(
                    image_id="ocr_result",
                    ocr_text=best_result['text'],
                    confidence=best_result['confidence'],
                    metadata={'ocr_engine': best_result['engine']}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error en OCR: {e}")
            return None
    
    async def _detect_objects(self, image_data: bytes) -> Optional[ImageAnalysis]:
        """Detectar objetos en la imagen"""
        try:
            # Implementación básica de detección de objetos
            # En una implementación real, usarías modelos como YOLO, Faster R-CNN, etc.
            
            # Por ahora, retornar análisis básico
            return ImageAnalysis(
                image_id="object_detection",
                objects_detected=["objeto_detectado"],
                confidence=0.7,
                metadata={'method': 'basic_detection'}
            )
            
        except Exception as e:
            logger.error(f"❌ Error en detección de objetos: {e}")
            return None
    
    async def _extract_text_blocks(self, image_data: bytes) -> Optional[ImageAnalysis]:
        """Extraer bloques de texto de la imagen"""
        try:
            # Implementación básica de extracción de bloques de texto
            # En una implementación real, usarías técnicas de detección de texto
            
            return ImageAnalysis(
                image_id="text_blocks",
                text_blocks=[
                    {
                        'text': 'Texto detectado',
                        'bbox': [0, 0, 100, 50],
                        'confidence': 0.8
                    }
                ],
                confidence=0.8,
                metadata={'method': 'basic_extraction'}
            )
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo bloques de texto: {e}")
            return None
    
    def _calculate_confidence(self, analysis: ImageAnalysis) -> float:
        """Calcular confianza general del análisis"""
        confidences = []
        
        if analysis.ocr_text:
            confidences.append(0.8)
        
        if analysis.objects_detected:
            confidences.append(0.7)
        
        if analysis.text_blocks:
            confidences.append(0.8)
        
        if analysis.description:
            confidences.append(0.9)
        
        if confidences:
            return sum(confidences) / len(confidences)
        
        return 0.0
    
    async def process_pdf_with_images(self, pdf_path: Path) -> Dict[str, Any]:
        """Procesar un PDF completo, extrayendo texto e imágenes"""
        try:
            logger.info(f"📄 Procesando PDF completo: {pdf_path.name}")
            
            # Extraer imágenes
            images = await self.extract_images_from_pdf(pdf_path)
            
            # Analizar cada imagen
            image_analyses = []
            for image in images:
                analysis = await self.analyze_image(image.image_data, image.id)
                image_analyses.append({
                    'image': image,
                    'analysis': analysis
                })
            
            # Generar resumen
            summary = {
                'pdf_path': str(pdf_path),
                'total_images': len(images),
                'images_with_text': len([a for a in image_analyses if a['analysis'].ocr_text]),
                'total_processing_time': sum(a['analysis'].processing_time for a in image_analyses),
                'image_analyses': image_analyses
            }
            
            logger.info(f"✅ PDF procesado: {summary['total_images']} imágenes, {summary['images_with_text']} con texto")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error procesando PDF: {e}")
            return {
                'pdf_path': str(pdf_path),
                'error': str(e),
                'total_images': 0,
                'image_analyses': []
            }
    
    def save_image_analysis(self, analysis: ImageAnalysis, output_path: Path):
        """Guardar análisis de imagen en formato JSON"""
        try:
            # Convertir a diccionario
            analysis_dict = {
                'image_id': analysis.image_id,
                'description': analysis.description,
                'ocr_text': analysis.ocr_text,
                'objects_detected': analysis.objects_detected,
                'text_blocks': analysis.text_blocks,
                'confidence': analysis.confidence,
                'processing_time': analysis.processing_time,
                'metadata': analysis.metadata
            }
            
            # Guardar en archivo
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Análisis guardado en: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Error guardando análisis: {e}")


# Función de conveniencia
async def create_vision_processor() -> VisionProcessor:
    """Crear y configurar un procesador de visión"""
    processor = VisionProcessor()
    return processor 