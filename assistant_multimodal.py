#!/usr/bin/env python3
"""
🤖 Asistente Multimodal - Procesamiento de Texto e Imágenes

Este script proporciona un asistente de IA que puede procesar tanto texto como imágenes,
integrando capacidades de visión por computadora con el sistema RAG existente.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent.core.multimodal_agent import MultimodalAgent, create_multimodal_agent
from agent.core.vision_processor import VisionProcessor, create_vision_processor
from agent.core.models_simple import AgentRequest, AgentResponse


class MultimodalAssistant:
    """
    Asistente Multimodal - Interfaz principal para el usuario
    
    Proporciona una interfaz fácil de usar para procesar texto e imágenes
    usando el sistema de agentes multimodal.
    """
    
    def __init__(self):
        self.agent: Optional[MultimodalAgent] = None
        self.vision_processor: Optional[VisionProcessor] = None
        self.is_initialized = False
    
    async def initialize(self):
        """Inicializar el asistente multimodal"""
        try:
            logger.info("🚀 Inicializando Asistente Multimodal...")
            
            # Crear agente multimodal
            self.agent = await create_multimodal_agent()
            
            # Crear procesador de visión
            self.vision_processor = await create_vision_processor()
            
            self.is_initialized = True
            logger.info("✅ Asistente Multimodal inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando asistente: {e}")
            raise
    
    async def process_query(self, query: str, file_path: Optional[Path] = None) -> AgentResponse:
        """Procesar una consulta que puede incluir texto e imágenes"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Crear request
            request = AgentRequest(
                query=query,
                priority="normal",
                metadata={}
            )
            
            # Si hay archivo, procesarlo primero
            if file_path and file_path.exists():
                if file_path.suffix.lower() == '.pdf':
                    return await self._process_pdf_query(request, file_path)
                elif file_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}:
                    return await self._process_image_query(request, file_path)
            
            # Procesar con agente multimodal
            return await self.agent.process_request(request)
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")
            return AgentResponse(
                success=False,
                content=f"Error procesando la consulta: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _process_pdf_query(self, request: AgentRequest, pdf_path: Path) -> AgentResponse:
        """Procesar una consulta que involucra un PDF"""
        try:
            logger.info(f"📄 Procesando PDF: {pdf_path.name}")
            
            # Procesar PDF con imágenes
            pdf_result = await self.vision_processor.process_pdf_with_images(pdf_path)
            
            # Generar respuesta
            response_content = self._generate_pdf_response(pdf_result, request.query)
            
            return AgentResponse(
                success=True,
                content=response_content,
                metadata={
                    "content_type": "pdf_analysis",
                    "pdf_result": pdf_result
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error procesando PDF: {e}")
            return AgentResponse(
                success=False,
                content=f"Error procesando el PDF: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _process_image_query(self, request: AgentRequest, image_path: Path) -> AgentResponse:
        """Procesar una consulta que involucra una imagen"""
        try:
            logger.info(f"🖼️ Procesando imagen: {image_path.name}")
            
            # Leer imagen
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Analizar imagen
            analysis = await self.vision_processor.analyze_image(image_data, image_path.name)
            
            # Generar respuesta
            response_content = self._generate_image_response(analysis, request.query)
            
            return AgentResponse(
                success=True,
                content=response_content,
                metadata={
                    "content_type": "image_analysis",
                    "analysis": analysis.__dict__
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error procesando imagen: {e}")
            return AgentResponse(
                success=False,
                content=f"Error procesando la imagen: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def _generate_pdf_response(self, pdf_result: dict, query: str) -> str:
        """Generar respuesta para análisis de PDF"""
        response_parts = []
        
        # Encabezado
        response_parts.append("📄 **Análisis de PDF Completado**")
        response_parts.append("")
        
        # Información básica
        response_parts.append(f"📁 **Archivo:** {Path(pdf_result['pdf_path']).name}")
        response_parts.append(f"🖼️ **Imágenes encontradas:** {pdf_result['total_images']}")
        response_parts.append(f"📝 **Imágenes con texto:** {pdf_result['images_with_text']}")
        response_parts.append(f"⏱️ **Tiempo de procesamiento:** {pdf_result['total_processing_time']:.2f}s")
        response_parts.append("")
        
        # Detalles de imágenes
        if pdf_result['image_analyses']:
            response_parts.append("🔍 **Análisis de Imágenes:**")
            response_parts.append("")
            
            for i, img_analysis in enumerate(pdf_result['image_analyses'], 1):
                image = img_analysis['image']
                analysis = img_analysis['analysis']
                
                response_parts.append(f"**Imagen {i}:**")
                response_parts.append(f"  - Página: {image.page_number}")
                response_parts.append(f"  - Tamaño: {image.width}x{image.height}")
                response_parts.append(f"  - Confianza: {analysis.confidence:.1%}")
                
                if analysis.ocr_text:
                    response_parts.append(f"  - Texto: {analysis.ocr_text[:100]}...")
                
                response_parts.append("")
        
        return "\n".join(response_parts)
    
    def _generate_image_response(self, analysis: dict, query: str) -> str:
        """Generar respuesta para análisis de imagen"""
        response_parts = []
        
        # Encabezado
        response_parts.append("🖼️ **Análisis de Imagen Completado**")
        response_parts.append("")
        
        # Descripción
        if analysis.description:
            response_parts.append(f"📷 **Descripción:** {analysis.description}")
            response_parts.append("")
        
        # Texto OCR
        if analysis.ocr_text:
            response_parts.append(f"📝 **Texto detectado:** {analysis.ocr_text}")
            response_parts.append("")
        
        # Objetos detectados
        if analysis.objects_detected:
            response_parts.append(f"🎯 **Objetos detectados:** {', '.join(analysis.objects_detected)}")
            response_parts.append("")
        
        # Bloques de texto
        if analysis.text_blocks:
            response_parts.append("📋 **Bloques de texto:**")
            for i, block in enumerate(analysis.text_blocks, 1):
                response_parts.append(f"  {i}. {block['text']} (confianza: {block['confidence']:.1%})")
            response_parts.append("")
        
        # Métricas
        response_parts.append(f"🎯 **Confianza general:** {analysis.confidence:.1%}")
        response_parts.append(f"⏱️ **Tiempo de procesamiento:** {analysis.processing_time:.2f}s")
        
        return "\n".join(response_parts)
    
    async def interactive_mode(self):
        """Modo interactivo para conversación en tiempo real"""
        print("🤖 **Asistente Multimodal - Modo Interactivo**")
        print("💡 Puedes hacer preguntas sobre texto e imágenes")
        print("📄 Para analizar un PDF: 'analizar archivo.pdf'")
        print("🖼️ Para analizar una imagen: 'analizar imagen.jpg'")
        print("❌ Para salir: 'salir'")
        print("-" * 50)
        
        while True:
            try:
                # Obtener entrada del usuario
                user_input = input("\n👤 Tú: ").strip()
                
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    print("👋 ¡Hasta luego!")
                    break
                
                if not user_input:
                    continue
                
                # Procesar consulta
                print("\n🤖 Procesando...")
                response = await self.process_query(user_input)
                
                # Mostrar respuesta
                print(f"\n🤖 Asistente: {response.content}")
                
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    async def demo_mode(self):
        """Modo demostración con ejemplos predefinidos"""
        print("🎬 **Asistente Multimodal - Modo Demostración**")
        print("=" * 50)
        
        # Ejemplos de demostración
        demos = [
            {
                "title": "Consulta de Texto Simple",
                "query": "¿Qué es la inteligencia artificial?",
                "description": "Demuestra el procesamiento de texto normal"
            },
            {
                "title": "Consulta sobre Imágenes",
                "query": "Analiza esta imagen y describe lo que ves",
                "description": "Demuestra capacidades de análisis de imágenes"
            },
            {
                "title": "Consulta sobre PDFs",
                "query": "Extrae y analiza las imágenes de este documento",
                "description": "Demuestra procesamiento de PDFs con imágenes"
            }
        ]
        
        for i, demo in enumerate(demos, 1):
            print(f"\n{i}. {demo['title']}")
            print(f"   {demo['description']}")
            print(f"   Consulta: {demo['query']}")
            
            # Simular procesamiento
            print("   🤖 Procesando...")
            await asyncio.sleep(1)
            print("   ✅ Completado")
        
        print("\n🎉 Demostración completada!")
        print("💡 Usa el modo interactivo para probar tus propias consultas")


async def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Asistente Multimodal - Procesamiento de Texto e Imágenes")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interactivo")
    parser.add_argument("--demo", "-d", action="store_true", help="Modo demostración")
    parser.add_argument("--query", "-q", type=str, help="Consulta específica")
    parser.add_argument("--file", "-f", type=str, help="Archivo a procesar (PDF o imagen)")
    parser.add_argument("--help", "-h", action="store_true", help="Mostrar ayuda")
    
    args = parser.parse_args()
    
    # Mostrar ayuda
    if args.help:
        print("🤖 **Asistente Multimodal**")
        print("=" * 30)
        print("Uso:")
        print("  python assistant_multimodal.py --interactive")
        print("  python assistant_multimodal.py --demo")
        print("  python assistant_multimodal.py --query '¿Qué es la IA?'")
        print("  python assistant_multimodal.py --query 'Analiza esta imagen' --file imagen.jpg")
        print("  python assistant_multimodal.py --query 'Extrae imágenes' --file documento.pdf")
        return
    
    try:
        # Crear asistente
        assistant = MultimodalAssistant()
        await assistant.initialize()
        
        # Ejecutar según argumentos
        if args.interactive:
            await assistant.interactive_mode()
        elif args.demo:
            await assistant.demo_mode()
        elif args.query:
            file_path = Path(args.file) if args.file else None
            response = await assistant.process_query(args.query, file_path)
            print(f"\n🤖 Respuesta: {response.content}")
        else:
            # Modo por defecto: interactivo
            await assistant.interactive_mode()
    
    except Exception as e:
        logger.error(f"❌ Error en el asistente: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 