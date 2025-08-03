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
                print(f"✅ Respuesta generada en {response.processing_time:.2f}s")
                print(f"📊 Confianza: {response.confidence_score:.1%}")
                print(f"📄 Contenido: {response.content[:200]}...")
            else:
                print(f"❌ Error: {response.content}")
            
            print("-" * 40)
            await asyncio.sleep(1)
    
    async def _demo_complex_workflows(self):
        """Demostrar flujos de trabajo complejos"""
        print("\n🔄 DEMOSTRACIÓN: Flujos de Trabajo Complejos")
        print("-" * 40)
        
        complex_queries = [
            "Investiga sobre el impacto de la IA en el sector financiero y crea un resumen ejecutivo",
            "Analiza las tendencias de mercado en tecnología y genera recomendaciones de inversión",
            "Crea un plan de marketing digital para una startup de e-commerce"
        ]
        
        for i, query in enumerate(complex_queries, 1):
            print(f"\n🔍 Consulta Compleja {i}: {query}")
            print("⏳ Procesando con Sequential Thinking...")
            
            # Usar Sequential Thinking para consultas complejas
            result = await self.agent.solve_with_sequential_thinking(query)
            
            if result['success']:
                print(f"✅ Proceso completado en {result.get('duration', 0):.2f}s")
                print(f"📊 Pasos completados: {result['completed_steps']}/{result['total_steps']}")
                print(f"📄 Respuesta: {result['answer'][:200]}...")
            else:
                print(f"❌ Error: {result['answer']}")
            
            print("-" * 40)
            await asyncio.sleep(2)
    
    async def _demo_rag_capabilities(self):
        """Demostrar capacidades RAG"""
        print("\n🔍 DEMOSTRACIÓN: Sistema RAG")
        print("-" * 40)
        
        # Añadir conocimiento al sistema RAG
        print("📚 Añadiendo conocimiento al sistema RAG...")
        
        knowledge_items = [
            {
                "title": "Inteligencia Artificial",
                "content": "La IA es una rama de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana."
            },
            {
                "title": "Machine Learning",
                "content": "El aprendizaje automático es un subconjunto de la IA que permite a las computadoras aprender sin ser programadas explícitamente."
            },
            {
                "title": "Deep Learning",
                "content": "El aprendizaje profundo utiliza redes neuronales artificiales con múltiples capas para procesar datos complejos."
            }
        ]
        
        for item in knowledge_items:
            await self.agent.rag_system.add_knowledge(
                title=item["title"],
                content=item["content"],
                source="demo_knowledge"
            )
        
        print(f"✅ {len(knowledge_items)} elementos de conocimiento añadidos")
        
        # Consultar el conocimiento RAG
        rag_queries = [
            "¿Qué es la inteligencia artificial?",
            "Explica el machine learning",
            "¿Cómo funciona el deep learning?"
        ]
        
        for i, query in enumerate(rag_queries, 1):
            print(f"\n🔍 Consulta RAG {i}: {query}")
            print("⏳ Buscando en base de conocimiento...")
            
            request = AgentRequest(query=query, priority=PriorityLevel.HIGH)
            response = await self.agent.process_request(request)
            
            if response.success:
                print(f"✅ Respuesta RAG generada en {response.processing_time:.2f}s")
                print(f"📚 Fuentes encontradas: {len(response.sources)}")
                print(f"📄 Contenido: {response.content[:200]}...")
            else:
                print(f"❌ Error: {response.content}")
            
            print("-" * 40)
            await asyncio.sleep(1)
    
    async def _demo_data_integration(self):
        """Demostrar integración de datos"""
        print("\n🔌 DEMOSTRACIÓN: Integración de Datos")
        print("-" * 40)
        
        data_queries = [
            "¿Cuál es el clima actual en Barcelona?",
            "Dame las últimas noticias sobre tecnología",
            "¿Cuál es el precio actual de Bitcoin?"
        ]
        
        for i, query in enumerate(data_queries, 1):
            print(f"\n🔍 Consulta de Datos {i}: {query}")
            print("⏳ Conectando con APIs externas...")
            
            request = AgentRequest(query=query, priority=PriorityLevel.MEDIUM)
            response = await self.agent.process_request(request)
            
            if response.success:
                print(f"✅ Datos obtenidos en {response.processing_time:.2f}s")
                print(f"📊 Confianza: {response.confidence_score:.1%}")
                print(f"📄 Contenido: {response.content[:200]}...")
            else:
                print(f"❌ Error: {response.content}")
            
            print("-" * 40)
            await asyncio.sleep(2)
    
    async def _demo_task_coordination(self):
        """Demostrar coordinación de tareas"""
        print("\n🎯 DEMOSTRACIÓN: Coordinación de Tareas")
        print("-" * 40)
        
        coordination_query = """
        Necesito que hagas lo siguiente:
        1. Investiga sobre las tendencias de IA en 2024
        2. Analiza el impacto en el mercado laboral
        3. Crea un resumen ejecutivo
        4. Sugiere acciones recomendadas
        """
        
        print(f"🔍 Tarea Compleja: {coordination_query.strip()}")
        print("⏳ Coordinando múltiples agentes...")
        
        request = AgentRequest(
            query=coordination_query,
            priority=PriorityLevel.HIGH
        )
        
        response = await self.agent.process_request(request)
        
        if response.success:
            print(f"✅ Coordinación completada en {response.processing_time:.2f}s")
            print(f"📊 Tareas ejecutadas: {response.meta_data.get('tasks_executed', 0)}")
            print(f"📄 Resultado: {response.content[:300]}...")
        else:
            print(f"❌ Error: {response.content}")
        
        print("-" * 40)
    
    async def _show_final_stats(self):
        """Mostrar estadísticas finales"""
        print("\n📊 ESTADÍSTICAS FINALES")
        print("=" * 60)
        
        if self.agent:
            status = await self.agent.get_status()
            
            print(f"🆔 ID del Agente: {status.system_id}")
            print(f"⏰ Tiempo de Ejecución: {status.system_uptime:.2f}s")
            print(f"📈 Total de Tareas: {status.total_tasks}")
            print(f"✅ Tasa de Éxito: {status.success_rate:.1%}")
            print(f"⚡ Tiempo Promedio: {status.average_response_time:.2f}s")
            print(f"💾 Uso de Memoria: {status.memory_usage:.1f}MB")
            print(f"🖥️ Uso de CPU: {status.cpu_usage:.1f}%")
            
            print(f"\n🤖 Agentes Activos:")
            for agent_status in status.agents_status:
                print(f"  • {agent_status.agent_type.value}: {agent_status.status}")
                print(f"    - Tareas Completadas: {agent_status.completed_tasks}")
                print(f"    - Tareas Fallidas: {agent_status.failed_tasks}")
        
        print("\n🎉 ¡Demostración completada exitosamente!")
    
    async def _cleanup(self):
        """Limpiar recursos"""
        if self.agent:
            print("\n🧹 Limpiando recursos...")
            await self.agent.stop()
            print("✅ Recursos liberados")


async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🤖 Demostración del Asistente de IA")
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verbose")
    
    args = parser.parse_args()
    
    demo = AssistantDemo()
    await demo.start_demo()


if __name__ == "__main__":
    asyncio.run(main()) 