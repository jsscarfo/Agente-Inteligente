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
            return "Actualmente no tengo acceso a datos meteorológicos en tiempo real, pero puedo ayudarte con información general sobre el clima o recomendaciones para diferentes tipos de clima."
        
        elif "noticias" in query_lower or "actualidad" in query_lower:
            return "No tengo acceso directo a noticias en tiempo real, pero puedo ayudarte con análisis de tendencias, explicaciones de eventos históricos o información general sobre temas de actualidad."
        
        elif "matemáticas" in query_lower or "calcular" in query_lower or "suma" in query_lower:
            return "Puedo ayudarte con cálculos matemáticos básicos. Por favor, proporciona los números y la operación que necesitas realizar."
        
        elif "ayuda" in query_lower or "qué puedes hacer" in query_lower:
            return """¡Con gusto te ayudo! Puedo asistirte con:

🔍 **Búsqueda de información**: Explicar conceptos, definir términos, analizar temas
📊 **Análisis de datos**: Interpretar información, crear resúmenes, identificar patrones
✍️ **Generación de contenido**: Escribir textos, crear planes, desarrollar ideas
🧮 **Cálculos**: Operaciones matemáticas básicas y análisis numérico
📋 **Organización**: Crear listas, estructurar información, planificar tareas
💡 **Recomendaciones**: Sugerir soluciones, proponer alternativas, dar consejos

¿En qué área específica te gustaría que te ayude?"""
        
        elif "gracias" in query_lower or "thanks" in query_lower:
            return "¡De nada! Es un placer poder ayudarte. Si necesitas algo más, no dudes en preguntar."
        
        elif "adiós" in query_lower or "bye" in query_lower or "chao" in query_lower:
            return "¡Hasta luego! Ha sido un placer ayudarte. Que tengas un excelente día."
        
        else:
            return f"""He recibido tu consulta: "{query}"

Como asistente simplificado, puedo ayudarte con:
- Explicaciones de conceptos
- Análisis de información
- Generación de contenido
- Cálculos básicos
- Recomendaciones generales

Para obtener respuestas más específicas y detalladas, te recomiendo usar el asistente completo con acceso a bases de datos y APIs externas.

¿Te gustaría que te ayude con algo específico dentro de mis capacidades?"""
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del asistente"""
        return {
            "agent_id": self.agent_id,
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat(),
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "conversations": len(self.conversation_history),
            "version": "1.0.0",
            "type": "simple_assistant"
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Obtener historial de conversaciones"""
        return [
            {
                "timestamp": conv["timestamp"].isoformat(),
                "query": conv["query"],
                "response": conv["response"]
            }
            for conv in self.conversation_history
        ]


async def interactive_mode():
    """Modo interactivo"""
    assistant = SimpleAssistant()
    await assistant.start()
    
    print("\n🎮 Modo Interactivo - Asistente Simple")
    print("Escribe 'quit' para salir")
    print("Escribe 'status' para ver el estado")
    print("Escribe 'history' para ver el historial")
    print("-" * 50)
    
    while True:
        try:
            query = input("\n🤖 Tú: ").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'status':
                status = assistant.get_status()
                print(f"\n📊 Estado del Asistente:")
                print(f"  ID: {status['agent_id']}")
                print(f"  Ejecutándose: {'Sí' if status['is_running'] else 'No'}")
                print(f"  Conversaciones: {status['conversations']}")
                print(f"  Versión: {status['version']}")
                continue
            elif query.lower() == 'history':
                history = assistant.get_conversation_history()
                print(f"\n📚 Historial de Conversaciones ({len(history)}):")
                for i, conv in enumerate(history[-5:], 1):  # Mostrar solo las últimas 5
                    print(f"  {i}. {conv['query'][:50]}...")
                continue
            elif not query:
                continue
            
            # Procesar consulta
            request = AgentRequest(query=query)
            response = await assistant.process_request(request)
            
            if response.success:
                print(f"\n🤖 Asistente: {response.content}")
            else:
                print(f"\n❌ Error: {response.error}")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    await assistant.stop()


async def demo_mode():
    """Modo demostración"""
    assistant = SimpleAssistant()
    await assistant.start()
    
    print("\n🎬 Modo Demostración - Asistente Simple")
    print("=" * 60)
    
    # Consultas de ejemplo
    demo_queries = [
        "Hola, ¿cómo estás?",
        "¿Qué puedes hacer?",
        "Necesito información sobre el clima",
        "¿Puedes ayudarme con matemáticas?",
        "Gracias por tu ayuda"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n🔍 Consulta {i}: {query}")
        print("-" * 40)
        
        request = AgentRequest(query=query)
        response = await assistant.process_request(request)
        
        if response.success:
            print(f"✅ Respuesta generada en {response.processing_time:.2f}s")
            print(f"📊 Confianza: {response.confidence_score:.1%}")
            print(f"📄 Respuesta: {response.content}")
        else:
            print(f"❌ Error: {response.error}")
        
        print("\n" + "=" * 60)
        await asyncio.sleep(1)
    
    # Mostrar estadísticas finales
    status = assistant.get_status()
    print(f"\n📊 Estadísticas Finales:")
    print(f"  Conversaciones: {status['conversations']}")
    print(f"  Tiempo activo: {status['uptime']:.2f}s")
    
    await assistant.stop()


async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🤖 Asistente de IA Simplificado")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interactivo")
    parser.add_argument("--demo", "-d", action="store_true", help="Modo demostración")
    parser.add_argument("--query", "-q", help="Consulta única")
    
    args = parser.parse_args()
    
    if args.interactive:
        await interactive_mode()
    elif args.demo:
        await demo_mode()
    elif args.query:
        assistant = SimpleAssistant()
        await assistant.start()
        
        request = AgentRequest(query=args.query)
        response = await assistant.process_request(request)
        
        if response.success:
            print(f"✅ Respuesta: {response.content}")
        else:
            print(f"❌ Error: {response.error}")
        
        await assistant.stop()
    else:
        print("🤖 Asistente de IA Simplificado")
        print("Uso:")
        print("  python assistant_simple.py --interactive")
        print("  python assistant_simple.py --demo")
        print("  python assistant_simple.py --query 'tu consulta'")


if __name__ == "__main__":
    asyncio.run(main()) 