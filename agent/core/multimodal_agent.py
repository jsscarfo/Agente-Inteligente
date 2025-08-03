#!/usr/bin/env python3
"""
🤖 Agente Multimodal - Procesamiento de Texto e Imágenes

Este módulo implementa un agente inteligente capaz de procesar tanto texto como imágenes,
integrando capacidades de visión por computadora con el sistema RAG existente.
"""

import asyncio
import base64
import io
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

import aiohttp
import numpy as np
from PIL import Image
import fitz  # PyMuPDF

from .config import get_config
from .models_simple import AgentRequest, AgentResponse
from .intelligent_agent import IntelligentAgent

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Tipos de contenido que puede procesar el agente"""
    TEXT = "text"
    IMAGE = "image"
    PDF = "pdf"
    MULTIMODAL = "multimodal"


@dataclass
class ImageAnalysisResult:
    """Resultado del análisis de imagen"""
    content_type: ContentType
    text_content: Optional[str] = None
    image_description: Optional[str] = None
    objects_detected: List[str] = None
    ocr_text: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.objects_detected is None:
            self.objects_detected = []
        if self.metadata is None:
            self.metadata = {}


class MultimodalAgent:
    """
    Agente Multimodal - Procesa texto e imágenes
    
    Integra capacidades de visión por computadora con el sistema RAG existente
    para proporcionar análisis completo de contenido multimodal.
    """
    
    def __init__(self):
        self.config = get_config()
        self.text_agent = IntelligentAgent()
        
        # Servicios de visión
        self.vision_services = {
            'openai_vision': self._analyze_with_openai_vision,
            'google_vision': self._analyze_with_google_vision,
            'azure_vision': self._analyze_with_azure_vision,
            'ocr': self._extract_text_with_ocr
        }
        
        # Configuración
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        self.max_image_size = 20 * 1024 * 1024  # 20MB
        
    async def initialize(self):
        """Inicializar el agente multimodal"""
        try:
            logger.info("🤖 Inicializando agente multimodal...")
            
            # Inicializar agente de texto
            await self.text_agent.initialize()
            
            # Verificar servicios de visión disponibles
            await self._check_vision_services()
            
            logger.info("✅ Agente multimodal inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando agente multimodal: {e}")
            raise
    
    async def _check_vision_services(self):
        """Verificar qué servicios de visión están disponibles"""
        available_services = []
        
        # Verificar OpenAI Vision
        if self.config.openai_api_key:
            available_services.append('openai_vision')
        
        # Verificar Google Vision
        if hasattr(self.config, 'google_vision_api_key') and self.config.google_vision_api_key:
            available_services.append('google_vision')
        
        # Verificar Azure Vision
        if hasattr(self.config, 'azure_vision_endpoint') and self.config.azure_vision_endpoint:
            available_services.append('azure_vision')
        
        # OCR siempre disponible
        available_services.append('ocr')
        
        logger.info(f"🔍 Servicios de visión disponibles: {available_services}")
        return available_services
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """Procesar una petición que puede contener texto e imágenes"""
        try:
            # Determinar tipo de contenido
            content_type = self._analyze_content_type(request)
            
            if content_type == ContentType.TEXT:
                # Usar agente de texto existente
                return await self.text_agent.process_request(request)
            
            elif content_type == ContentType.IMAGE:
                # Procesar imagen
                return await self._process_image_request(request)
            
            elif content_type == ContentType.PDF:
                # Procesar PDF (texto + imágenes)
                return await self._process_pdf_request(request)
            
            elif content_type == ContentType.MULTIMODAL:
                # Procesar contenido multimodal
                return await self._process_multimodal_request(request)
            
            else:
                raise ValueError(f"Tipo de contenido no soportado: {content_type}")
                
        except Exception as e:
            logger.error(f"❌ Error procesando petición multimodal: {e}")
            return AgentResponse(
                success=False,
                content=f"Error procesando la petición: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def _analyze_content_type(self, request: AgentRequest) -> ContentType:
        """Analizar el tipo de contenido de la petición"""
        query = request.query.lower()
        
        # Verificar si hay archivos adjuntos
        if hasattr(request, 'attachments') and request.attachments:
            return ContentType.MULTIMODAL
        
        # Verificar si es un PDF
        if query.endswith('.pdf') or 'pdf' in query:
            return ContentType.PDF
        
        # Verificar si menciona imágenes
        image_keywords = ['imagen', 'foto', 'imagen', 'gráfico', 'diagrama', 'chart', 'image', 'photo']
        if any(keyword in query for keyword in image_keywords):
            return ContentType.IMAGE
        
        # Por defecto, texto
        return ContentType.TEXT
    
    async def _process_image_request(self, request: AgentRequest) -> AgentResponse:
        """Procesar una petición que involucra imágenes"""
        try:
            # Extraer imagen de la petición
            image_data = await self._extract_image_from_request(request)
            
            if not image_data:
                return AgentResponse(
                    success=False,
                    content="No se encontró ninguna imagen en la petición",
                    metadata={"error": "no_image_found"}
                )
            
            # Analizar imagen
            analysis_result = await self._analyze_image(image_data)
            
            # Generar respuesta basada en el análisis
            response_content = self._generate_image_response(analysis_result, request.query)
            
            return AgentResponse(
                success=True,
                content=response_content,
                metadata={
                    "content_type": "image_analysis",
                    "analysis_result": analysis_result.__dict__
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error procesando imagen: {e}")
            return AgentResponse(
                success=False,
                content=f"Error analizando la imagen: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _extract_image_from_request(self, request: AgentRequest) -> Optional[bytes]:
        """Extraer datos de imagen de la petición"""
        # Implementar extracción de imagen desde diferentes fuentes
        # - Archivos adjuntos
        # - URLs
        # - Base64
        # - Rutas de archivo
        pass
    
    async def _analyze_image(self, image_data: bytes) -> ImageAnalysisResult:
        """Analizar una imagen usando múltiples servicios"""
        results = []
        
        # Procesar con todos los servicios disponibles
        for service_name, service_func in self.vision_services.items():
            try:
                result = await service_func(image_data)
                if result:
                    results.append(result)
            except Exception as e:
                logger.warning(f"⚠️ Error con servicio {service_name}: {e}")
        
        # Combinar resultados
        return self._combine_analysis_results(results)
    
    async def _analyze_with_openai_vision(self, image_data: bytes) -> Optional[ImageAnalysisResult]:
        """Analizar imagen usando OpenAI Vision (GPT-4V)"""
        try:
            # Implementar análisis con GPT-4V
            # Convertir imagen a base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Llamar a OpenAI Vision API
            # (Implementación específica aquí)
            
            return ImageAnalysisResult(
                content_type=ContentType.IMAGE,
                image_description="Descripción de la imagen",
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"❌ Error con OpenAI Vision: {e}")
            return None
    
    async def _analyze_with_google_vision(self, image_data: bytes) -> Optional[ImageAnalysisResult]:
        """Analizar imagen usando Google Vision API"""
        # Implementar Google Vision API
        pass
    
    async def _analyze_with_azure_vision(self, image_data: bytes) -> Optional[ImageAnalysisResult]:
        """Analizar imagen usando Azure Computer Vision"""
        # Implementar Azure Computer Vision
        pass
    
    async def _extract_text_with_ocr(self, image_data: bytes) -> Optional[ImageAnalysisResult]:
        """Extraer texto de imagen usando OCR"""
        try:
            # Usar Pillow para procesar imagen
            image = Image.open(io.BytesIO(image_data))
            
            # Implementar OCR (puede usar Tesseract, EasyOCR, etc.)
            # Por ahora, retornar resultado básico
            return ImageAnalysisResult(
                content_type=ContentType.IMAGE,
                ocr_text="Texto extraído de la imagen",
                confidence=0.8
            )
            
        except Exception as e:
            logger.error(f"❌ Error con OCR: {e}")
            return None
    
    def _combine_analysis_results(self, results: List[ImageAnalysisResult]) -> ImageAnalysisResult:
        """Combinar resultados de múltiples servicios de análisis"""
        if not results:
            return ImageAnalysisResult(content_type=ContentType.IMAGE)
        
        # Combinar resultados de manera inteligente
        combined = ImageAnalysisResult(content_type=ContentType.IMAGE)
        
        # Combinar descripciones
        descriptions = [r.image_description for r in results if r.image_description]
        if descriptions:
            combined.image_description = " ".join(descriptions)
        
        # Combinar texto OCR
        ocr_texts = [r.ocr_text for r in results if r.ocr_text]
        if ocr_texts:
            combined.ocr_text = " ".join(ocr_texts)
        
        # Combinar objetos detectados
        all_objects = []
        for result in results:
            if result.objects_detected:
                all_objects.extend(result.objects_detected)
        combined.objects_detected = list(set(all_objects))
        
        # Calcular confianza promedio
        confidences = [r.confidence for r in results if r.confidence > 0]
        if confidences:
            combined.confidence = sum(confidences) / len(confidences)
        
        return combined
    
    def _generate_image_response(self, analysis: ImageAnalysisResult, query: str) -> str:
        """Generar respuesta basada en el análisis de imagen"""
        response_parts = []
        
        # Respuesta principal
        response_parts.append("🔍 **Análisis de Imagen Completado**")
        response_parts.append("")
        
        # Descripción de la imagen
        if analysis.image_description:
            response_parts.append(f"📷 **Descripción:** {analysis.image_description}")
            response_parts.append("")
        
        # Texto extraído
        if analysis.ocr_text:
            response_parts.append(f"📝 **Texto detectado:** {analysis.ocr_text}")
            response_parts.append("")
        
        # Objetos detectados
        if analysis.objects_detected:
            response_parts.append(f"🎯 **Objetos detectados:** {', '.join(analysis.objects_detected)}")
            response_parts.append("")
        
        # Confianza
        response_parts.append(f"🎯 **Confianza del análisis:** {analysis.confidence:.1%}")
        
        return "\n".join(response_parts)
    
    async def _process_pdf_request(self, request: AgentRequest) -> AgentResponse:
        """Procesar una petición que involucra PDFs"""
        # Implementar procesamiento de PDFs con imágenes
        pass
    
    async def _process_multimodal_request(self, request: AgentRequest) -> AgentResponse:
        """Procesar una petición multimodal (texto + imágenes)"""
        # Implementar procesamiento multimodal
        pass


# Función de conveniencia para crear el agente
async def create_multimodal_agent() -> MultimodalAgent:
    """Crear y configurar un agente multimodal"""
    agent = MultimodalAgent()
    await agent.initialize()
    return agent 