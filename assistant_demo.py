#!/usr/bin/env python3
"""
🤖 Asistente de IA Multifuncional - Demostración Completa

Este archivo demuestra todas las capacidades del asistente de IA:
- Procesamiento de peticiones en texto libre
- Estructuración automática de tareas
- Conexión a fuentes de datos (APIs y vector DB)
- Generación de respuestas usando RAG
- Coordinación con LangGraph
- Almacenamiento en PostgreSQL
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent import IntelligentAgent
from agent.core.models import AgentRequest, PriorityLevel, AgentType
from agent.core.config import get_config


class AssistantDemo:
    """Demostración del Asistente de IA Multifuncional"""
    
    def __init__(self):
        self.agent = None
        self.config = get_config()
        self.demo_queries = [
            "¿Cuál es el clima actual en Madrid y qué actividades recomiendas para hacer hoy?",
            "Necesito un resumen de las últimas noticias sobre inteligencia artificial",
            "Analiza el rendimiento de las acciones de Apple y Tesla en los últimos 30 días",
            "Crea un plan de estudio para aprender Python en 3 meses",
            "Investiga sobre las mejores prácticas de seguridad en aplicaciones web",
            "¿Puedes ayudarme a planificar un viaje a Japón para el próximo año?",
            "Analiza las tendencias de mercado en el sector de la tecnología",
            "Crea un resumen ejecutivo sobre el impacto de la IA en el empleo"
        ]
    
    async def start_demo(self):
        """Iniciar la demostración completa"""
        print("🤖 ASISTENTE DE IA MULTIFUNCIONAL")
        print("=" * 60)
        print("🚀 Iniciando demostración completa...")
        print()
        
        try:
            # Inicializar el agente
            await self._initialize_agent()
            
            # Ejecutar demostraciones
            await self._demo_basic_queries()
            await self._demo_complex_workflows()
            await self._demo_rag_capabilities()
            await self._demo_data_integration()
            await self._demo_task_coordination()
            
            # Mostrar estadísticas finales
            await self._show_final_stats()
            
        except Exception as e:
            print(f"❌ Error en la demostración: {e}")
        finally:
            await self._cleanup()
    
    async def _initialize_agent(self):
        """Inicializar el agente inteligente"""
        print("🔧 Inicializando Agente Inteligente...")
        
        self.agent = IntelligentAgent()
        await self.agent.start()
        
        print(f"✅ Agente inicializado con ID: {self.agent.agent_id}")
        print(f"📊 Versión: {self.agent.get_version()}")
        print()
    
    async def _demo_basic_queries(self):
        """Demostrar consultas básicas"""
        print("📝 DEMOSTRACIÓN: Consultas Básicas")
        print("-" * 40)
        
        for i, query in enumerate(self.demo_queries[:3], 1):
            print(f"\n🔍 Consulta {i}: {query}")
            print("⏳ Procesando...")
            
            request = AgentRequest(
                query=query,
                priority=PriorityLevel.MEDIUM
            )
            
            response = await self.agent.process_request(request)
            
            if response.success:
                print(f"✅ Respuesta exitosa ({response.processing_time:.2f}s)")
                print(f"📊 Confianza: {response.confidence_score:.1%}")
                print(f"🔧 Tareas ejecutadas: {response.metadata.get('tasks_executed', 0)}")
                print(f"📄 Resumen: {response.summary[:100]}...")
            else:
                print(f"❌ Error: {response.error}")
            
            print("-" * 40)
    
    async def _demo_complex_workflows(self):
        """Demostrar flujos de trabajo complejos"""
        print("\n🔄 DEMOSTRACIÓN: Flujos de Trabajo Complejos")
        print("-" * 50)
        
        complex_queries = [
            "Analiza el impacto de la inteligencia artificial en el mercado laboral, incluyendo estadísticas recientes, tendencias futuras y recomendaciones para profesionales",
            "Crea un plan de marketing digital completo para una startup de tecnología, incluyendo análisis de competencia, estrategias de contenido y métricas de seguimiento",
            "Investiga y compara las diferentes tecnologías de blockchain, sus aplicaciones prácticas, y el estado actual del mercado de criptomonedas"
        ]
        
        for i, query in enumerate(complex_queries, 1):
            print(f"\n🎯 Flujo Complejo {i}: {query[:80]}...")
            print("🔄 Ejecutando flujo de trabajo con LangGraph...")
            
            request = AgentRequest(
                query=query,
                priority=PriorityLevel.HIGH
            )
            
            start_time = datetime.now()
            response = await self.agent.process_request(request)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if response.success:
                print(f"✅ Flujo completado en {processing_time:.2f}s")
                print(f"📊 Confianza: {response.confidence_score:.1%}")
                print(f"🔧 Tareas ejecutadas: {response.metadata.get('tasks_executed', 0)}")
                print(f"📚 Fuentes consultadas: {len(response.sources)}")
                print(f"📄 Contenido generado: {len(response.content)} caracteres")
                
                # Mostrar estructura de tareas
                if 'task_breakdown' in response.metadata:
                    print("📋 Desglose de tareas:")
                    for task in response.metadata['task_breakdown']:
                        print(f"  • {task['type']}: {task['status']}")
            else:
                print(f"❌ Error en flujo: {response.error}")
            
            print("-" * 50)
    
    async def _demo_rag_capabilities(self):
        """Demostrar capacidades RAG"""
        print("\n🔍 DEMOSTRACIÓN: Sistema RAG")
        print("-" * 35)
        
        # Añadir conocimiento al sistema
        knowledge_items = [
            {
                "content": "La inteligencia artificial está transformando la industria de la salud con aplicaciones en diagnóstico, descubrimiento de fármacos y atención personalizada.",
                "source": "Informe de McKinsey 2024",
                "content_type": "text"
            },
            {
                "content": "El machine learning es una rama de la IA que permite a las computadoras aprender y mejorar automáticamente sin ser programadas explícitamente.",
                "source": "Guía de Machine Learning",
                "content_type": "text"
            },
            {
                "content": "Las redes neuronales profundas han revolucionado el procesamiento de lenguaje natural, permitiendo sistemas como GPT y BERT.",
                "source": "Investigación en NLP",
                "content_type": "text"
            }
        ]
        
        print("📚 Añadiendo conocimiento al sistema RAG...")
        document_ids = await self.agent.rag_system.add_knowledge_base(knowledge_items)
        print(f"✅ {len(document_ids)} documentos añadidos")
        
        # Consultar conocimiento
        rag_queries = [
            "¿Cómo está impactando la IA en la salud?",
            "¿Qué es el machine learning y cómo funciona?",
            "¿Cuáles son los avances recientes en procesamiento de lenguaje natural?"
        ]
        
        for i, query in enumerate(rag_queries, 1):
            print(f"\n🔍 Consulta RAG {i}: {query}")
            
            # Buscar en la base de conocimiento
            search_results = await self.agent.rag_system.search(query, max_results=3)
            print(f"📚 Encontrados {len(search_results)} documentos relevantes")
            
            # Generar respuesta aumentada
            rag_response = await self.agent.rag_system.generate_answer(query)
            
            if rag_response.get('success'):
                print(f"✅ Respuesta RAG generada")
                print(f"📊 Confianza: {rag_response.get('confidence', 0):.1%}")
                print(f"📄 Respuesta: {rag_response.get('answer', '')[:150]}...")
            else:
                print(f"❌ Error en RAG: {rag_response.get('error', 'Error desconocido')}")
            
            print("-" * 35)
    
    async def _demo_data_integration(self):
        """Demostrar integración de datos"""
        print("\n🔗 DEMOSTRACIÓN: Integración de Datos")
        print("-" * 40)
        
        # Simular consultas que requieren datos externos
        data_queries = [
            "¿Cuál es el precio actual del Bitcoin y su tendencia en las últimas 24 horas?",
            "Necesito información sobre el clima en Barcelona para el fin de semana",
            "¿Cuáles son las últimas noticias sobre el mercado de tecnología?"
        ]
        
        for i, query in enumerate(data_queries, 1):
            print(f"\n📊 Consulta de Datos {i}: {query}")
            print("🔗 Conectando a fuentes de datos externas...")
            
            request = AgentRequest(
                query=query,
                priority=PriorityLevel.MEDIUM
            )
            
            response = await self.agent.process_request(request)
            
            if response.success:
                print(f"✅ Datos obtenidos exitosamente")
                print(f"📊 Fuentes consultadas: {len(response.sources)}")
                print(f"⏱️  Tiempo de respuesta: {response.processing_time:.2f}s")
                
                # Mostrar fuentes de datos
                if response.sources:
                    print("📚 Fuentes de datos:")
                    for source in response.sources[:3]:  # Mostrar solo las primeras 3
                        print(f"  • {source.get('name', 'Fuente desconocida')}: {source.get('url', 'N/A')}")
            else:
                print(f"❌ Error obteniendo datos: {response.error}")
            
            print("-" * 40)
    
    async def _demo_task_coordination(self):
        """Demostrar coordinación de tareas"""
        print("\n🎯 DEMOSTRACIÓN: Coordinación de Tareas")
        print("-" * 45)
        
        # Consulta que requiere múltiples tareas coordinadas
        complex_query = """
        Necesito un análisis completo del mercado de vehículos eléctricos que incluya:
        1. Estadísticas actuales de ventas
        2. Principales competidores y sus estrategias
        3. Tendencias tecnológicas emergentes
        4. Análisis de regulaciones gubernamentales
        5. Predicciones de mercado para los próximos 5 años
        6. Recomendaciones para inversores
        """
        
        print(f"🎯 Consulta Compleja: {complex_query[:100]}...")
        print("🔄 Coordinando múltiples tareas con LangGraph...")
        
        request = AgentRequest(
            query=complex_query,
            priority=PriorityLevel.HIGH
        )
        
        start_time = datetime.now()
        response = await self.agent.process_request(request)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if response.success:
            print(f"✅ Análisis completado en {processing_time:.2f}s")
            print(f"📊 Confianza general: {response.confidence_score:.1%}")
            print(f"🔧 Tareas coordinadas: {response.metadata.get('tasks_executed', 0)}")
            
            # Mostrar estructura del análisis
            if 'analysis_structure' in response.metadata:
                print("📋 Estructura del análisis:")
                for section in response.metadata['analysis_structure']:
                    print(f"  • {section['title']}: {section['status']}")
            
            print(f"📄 Contenido generado: {len(response.content)} caracteres")
            print(f"📚 Fuentes consultadas: {len(response.sources)}")
        else:
            print(f"❌ Error en coordinación: {response.error}")
        
        print("-" * 45)
    
    async def _show_final_stats(self):
        """Mostrar estadísticas finales"""
        print("\n📊 ESTADÍSTICAS FINALES")
        print("=" * 30)
        
        try:
            # Obtener estado del sistema
            status = await self.agent.get_status()
            
            print(f"🤖 ID del Agente: {self.agent.agent_id}")
            print(f"⏰ Tiempo activo: {self.agent.get_uptime():.2f} segundos")
            print(f"📊 Estado: {status.status}")
            print(f"🔧 Tareas activas: {len(self.agent.active_tasks)}")
            print(f"✅ Tareas completadas: {len(self.agent.completed_tasks)}")
            print(f"❌ Tareas fallidas: {len(self.agent.failed_tasks)}")
            
            # Estadísticas RAG
            rag_stats = await self.agent.rag_system.get_statistics()
            print(f"📚 Documentos en RAG: {rag_stats.get('total_documents', 0)}")
            print(f"🔍 Consultas RAG: {rag_stats.get('total_queries', 0)}")
            
            # Información del sistema
            system_info = self.agent.get_system_info()
            print(f"💾 Memoria utilizada: {system_info.get('memory_usage', 'N/A')}")
            print(f"🖥️  CPU: {system_info.get('cpu_usage', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
        
        print("=" * 30)
    
    async def _cleanup(self):
        """Limpiar recursos"""
        if self.agent:
            print("\n🧹 Limpiando recursos...")
            await self.agent.stop()
            print("✅ Limpieza completada")


async def main():
    """Función principal"""
    demo = AssistantDemo()
    await demo.start_demo()


if __name__ == "__main__":
    print("🚀 Iniciando Asistente de IA Multifuncional...")
    asyncio.run(main()) 