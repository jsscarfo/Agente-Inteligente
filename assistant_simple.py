#!/usr/bin/env python3
"""
🤖 Asistente de IA Simplificado

Una versión simplificada del asistente de IA que funciona sin problemas
de base de datos y demuestra las capacidades básicas.
"""

import asyncio
import sys
import time
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent.core.models_simple import AgentRequest, AgentResponse, PriorityLevel, TaskStatus, AgentType
from agent.core.config import get_config


class SimpleAssistant:
    """Asistente de IA simplificado"""
    
    def __init__(self):
        self.config = get_config()
        self.agent_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        self.is_running = False
        self.conversation_history = []
        
        print(f"🤖 Asistente Simple inicializado con ID: {self.agent_id}")
    
    async def start(self):
        """Iniciar el asistente"""
        self.is_running = True
        print("✅ Asistente iniciado correctamente")
    
    async def stop(self):
        """Detener el asistente"""
        self.is_running = False
        print("🛑 Asistente detenido correctamente")
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """Procesar una petición"""
        start_time = time.time()
        
        try:
            print(f"📝 Procesando: {request.query}")
            
            # Simular procesamiento
            await asyncio.sleep(1)
            
            # Generar respuesta basada en el tipo de consulta
            response_content = await self._generate_response(request.query)
            
            processing_time = time.time() - start_time
            
            # Guardar en historial
            self.conversation_history.append({
                "timestamp": datetime.now(),
                "query": request.query,
                "response": response_content
            })
            
            return AgentResponse(
                success=True,
                content=response_content,
                summary=f"Respuesta generada para: {request.query[:50]}...",
                confidence_score=0.85,
                processing_time=processing_time,
                sources=[],
                meta_data={
                    "agent_id": self.agent_id,
                    "tasks_executed": 1,
                    "model_used": "simple_assistant"
                }
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                content="",
                error=f"Error procesando petición: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    async def _generate_response(self, query: str) -> str:
        """Generar respuesta basada en la consulta"""
        query_lower = query.lower()
        
        # Respuestas predefinidas para diferentes tipos de consultas
        if "hola" in query_lower or "cómo estás" in query_lower:
            return "¡Hola! Soy tu asistente de IA. Estoy funcionando perfectamente y listo para ayudarte con cualquier tarea. ¿En qué puedo asistirte hoy?"
        
        elif "clima" in query_lower or "tiempo" in query_lower:
            return "Para obtener información del clima, necesitaría conectarme a una API de clima. En una versión completa, podría darte datos actuales del clima de cualquier ciudad."
        
        elif "noticias" in query_lower:
            return "Para obtener las últimas noticias, necesitaría conectarme a APIs de noticias. En una versión completa, podría buscar y resumir noticias sobre cualquier tema."
        
        elif "calcula" in query_lower or "matemática" in query_lower:
            return "Tengo capacidades de cálculo integradas. En una versión completa, podría resolver ecuaciones complejas, estadísticas y más."
        
        elif "análisis" in query_lower or "investiga" in query_lower:
            return "Puedo realizar análisis complejos y investigaciones. En una versión completa, podría analizar datos, buscar información y generar reportes detallados."
        
        elif "ayuda" in query_lower or "qué puedes hacer" in query_lower:
            return """¡Con gusto te explico mis capacidades!

🤖 **Como Asistente de IA puedo:**

📝 **Procesar peticiones en texto libre** - Entiendo consultas complejas y las descompongo en tareas

🔄 **Estructurar tareas automáticamente** - Uso LangGraph para coordinar múltiples pasos

🔍 **Conectarme a fuentes de datos** - APIs de clima, noticias, finanzas, búsqueda web

📊 **Generar respuestas inteligentes** - Combinando información de múltiples fuentes

🛠️ **Usar herramientas especializadas** - Calculadora, analizador de texto, procesador de datos

🗄️ **Almacenar información** - Base de datos PostgreSQL y sistema RAG

💡 **Ejemplos de uso:**
- "¿Cuál es el clima en Madrid?"
- "Analiza el mercado de criptomonedas"
- "Crea un plan de marketing digital"
- "Calcula la rentabilidad de una inversión"

¿Qué te gustaría que haga por ti?"""
        
        else:
            return f"""He recibido tu consulta: "{query}"

En esta versión simplificada, puedo procesar tu petición y generar respuestas básicas. Para funcionalidades completas como:

• Conexión a APIs externas (clima, noticias, finanzas)
• Análisis complejos con múltiples fuentes
• Herramientas especializadas (cálculos, análisis de texto)
• Sistema RAG para conocimiento personalizado

Necesitarías configurar las APIs correspondientes en el archivo .env.

¿Te gustaría que te ayude con algo específico o que te explique más sobre mis capacidades?"""
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del asistente"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "agent_id": self.agent_id,
            "status": "running" if self.is_running else "stopped",
            "uptime": uptime,
            "conversations": len(self.conversation_history),
            "version": self.config.agent_version,
            "model": "simple_assistant"
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Obtener historial de conversaciones"""
        return self.conversation_history


async def interactive_mode():
    """Modo interactivo"""
    print("🤖 ASISTENTE DE IA - MODO INTERACTIVO")
    print("=" * 50)
    print("💡 Escribe 'salir' para terminar")
    print("💡 Escribe 'ayuda' para ver mis capacidades")
    print("=" * 50)
    
    assistant = SimpleAssistant()
    await assistant.start()
    
    try:
        while True:
            print(f"\n👤 Tú: ", end="")
            user_input = input().strip()
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                break
            
            if not user_input:
                continue
            
            # Crear petición
            request = AgentRequest(
                query=user_input,
                priority=PriorityLevel.MEDIUM
            )
            
            # Procesar petición
            print("🤖 Asistente: Procesando...")
            response = await assistant.process_request(request)
            
            if response.success:
                print(f"🤖 Asistente: {response.content}")
                print(f"⏱️  Tiempo: {response.processing_time:.2f}s")
                print(f"📊 Confianza: {response.confidence_score:.1%}")
            else:
                print(f"❌ Error: {response.error}")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Interrumpido por el usuario")
    
    finally:
        await assistant.stop()
        
        # Mostrar estadísticas
        status = assistant.get_status()
        print(f"\n📊 Estadísticas de la sesión:")
        print(f"   Conversaciones: {status['conversations']}")
        print(f"   Tiempo activo: {status['uptime']:.2f}s")
        print(f"   Estado: {status['status']}")


async def demo_mode():
    """Modo demostración"""
    print("🎯 ASISTENTE DE IA - MODO DEMOSTRACIÓN")
    print("=" * 50)
    
    assistant = SimpleAssistant()
    await assistant.start()
    
    # Consultas de demostración
    demo_queries = [
        "Hola, ¿cómo estás?",
        "¿Qué puedes hacer?",
        "¿Puedes ayudarme con el clima?",
        "Necesito un análisis de mercado",
        "Calcula 25 + 37"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n🔍 Demostración {i}: {query}")
        print("-" * 40)
        
        request = AgentRequest(
            query=query,
            priority=PriorityLevel.MEDIUM
        )
        
        response = await assistant.process_request(request)
        
        if response.success:
            print(f"✅ Respuesta: {response.content}")
            print(f"⏱️  Tiempo: {response.processing_time:.2f}s")
            print(f"📊 Confianza: {response.confidence_score:.1%}")
        else:
            print(f"❌ Error: {response.error}")
        
        print("-" * 40)
    
    await assistant.stop()
    
    # Mostrar estadísticas finales
    status = assistant.get_status()
    print(f"\n📊 Estadísticas de la demostración:")
    print(f"   Consultas procesadas: {status['conversations']}")
    print(f"   Tiempo total: {status['uptime']:.2f}s")
    print(f"   Estado: {status['status']}")


async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Asistente de IA Simplificado")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interactivo")
    parser.add_argument("--demo", "-d", action="store_true", help="Modo demostración")
    parser.add_argument("--query", "-q", type=str, help="Consulta única")
    
    args = parser.parse_args()
    
    if args.interactive:
        await interactive_mode()
    elif args.demo:
        await demo_mode()
    elif args.query:
        assistant = SimpleAssistant()
        await assistant.start()
        
        request = AgentRequest(query=args.query, priority=PriorityLevel.MEDIUM)
        response = await assistant.process_request(request)
        
        if response.success:
            print(f"🤖 Respuesta: {response.content}")
        else:
            print(f"❌ Error: {response.error}")
        
        await assistant.stop()
    else:
        # Modo por defecto: demostración
        await demo_mode()


if __name__ == "__main__":
    asyncio.run(main()) 