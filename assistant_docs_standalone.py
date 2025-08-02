#!/usr/bin/env python3
"""
🤖 Asistente Independiente con Documentos PDF

Asistente que puede acceder a documentos PDF cargados en la base de datos
sin depender de módulos problemáticos.
"""

import asyncio
import sys
import time
import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Colores para la terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class PriorityLevel(str, Enum):
    """Niveles de prioridad"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class AgentRequest:
    """Solicitud del agente"""
    query: str
    priority: PriorityLevel = PriorityLevel.MEDIUM
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AgentResponse:
    """Respuesta del agente"""
    success: bool
    content: str
    summary: Optional[str] = None
    confidence_score: float = 0.0
    processing_time: float = 0.0
    error: Optional[str] = None
    sources: List[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if self.meta_data is None:
            self.meta_data = {}


@dataclass
class DocumentSearchResult:
    """Resultado de búsqueda en documentos"""
    document_title: str
    page_number: int
    content: str
    relevance_score: float
    source: str = "pdf_database"


class DocumentAwareAssistant:
    """Asistente que puede acceder a documentos PDF"""
    
    def __init__(self):
        self.agent_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        self.is_running = False
        self.conversation_history = []
        
        # Cargar base de datos de documentos
        self.documents_file = Path("data/documents.json")
        self.chunks_file = Path("data/chunks.json")
        self.documents = self._load_json(self.documents_file, {})
        self.chunks = self._load_json(self.chunks_file, {})
        
        print(f"{Colors.OKGREEN}🤖 Asistente con Documentos inicializado{Colors.ENDC}")
        print(f"{Colors.OKCYAN}🆔 ID: {self.agent_id}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}📚 Documentos disponibles: {len(self.documents)}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}🧩 Fragmentos de texto: {len(self.chunks)}{Colors.ENDC}")
    
    def _load_json(self, file_path: Path, default: Any) -> Any:
        """Cargar archivo JSON"""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"{Colors.WARNING}⚠️ Error cargando {file_path}: {e}{Colors.ENDC}")
        return default
    
    async def start(self):
        """Iniciar el asistente"""
        self.is_running = True
        print(f"{Colors.OKGREEN}✅ Asistente iniciado correctamente{Colors.ENDC}")
    
    async def stop(self):
        """Detener el asistente"""
        self.is_running = False
        print(f"{Colors.WARNING}🛑 Asistente detenido correctamente{Colors.ENDC}")
    
    def search_documents(self, query: str, limit: int = 5) -> List[DocumentSearchResult]:
        """Buscar en los documentos cargados"""
        query_lower = query.lower()
        results = []
        
        for chunk_id, chunk in self.chunks.items():
            if query_lower in chunk['content'].lower():
                doc = self.documents.get(chunk['document_id'])
                if doc:
                    relevance = chunk['content'].lower().count(query_lower)
                    results.append(DocumentSearchResult(
                        document_title=doc['title'],
                        page_number=chunk['page_number'],
                        content=chunk['content'],
                        relevance_score=relevance
                    ))
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """Procesar una petición usando documentos disponibles"""
        start_time = time.time()
        
        try:
            print(f"{Colors.OKBLUE}📝 Procesando: {request.query}{Colors.ENDC}")
            
            # Buscar en documentos
            search_results = self.search_documents(request.query)
            
            # Generar respuesta basada en documentos y conocimiento general
            response_content = await self._generate_response(request.query, search_results)
            
            processing_time = time.time() - start_time
            
            # Guardar en historial
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "query": request.query,
                "response": response_content,
                "documents_used": len(search_results),
                "processing_time": processing_time
            })
            
            return AgentResponse(
                success=True,
                content=response_content,
                summary=f"Respuesta generada usando {len(search_results)} documentos",
                confidence_score=0.85 if search_results else 0.70,
                processing_time=processing_time,
                sources=[{
                    "type": "pdf_document",
                    "title": result.document_title,
                    "page": result.page_number,
                    "relevance": result.relevance_score
                } for result in search_results],
                meta_data={
                    "agent_id": self.agent_id,
                    "documents_consulted": len(search_results),
                    "total_documents_available": len(self.documents),
                    "total_chunks_available": len(self.chunks)
                }
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                content="",
                error=f"Error procesando petición: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    async def _generate_response(self, query: str, search_results: List[DocumentSearchResult]) -> str:
        """Generar respuesta basada en documentos y consulta"""
        query_lower = query.lower()
        
        # Si hay resultados de documentos, usarlos
        if search_results:
            response_parts = []
            
            # Información de documentos encontrados
            response_parts.append(f"📚 **Encontré información relevante en {len(search_results)} documentos:**\n")
            
            for i, result in enumerate(search_results, 1):
                response_parts.append(f"**{i}. {result.document_title}** (página {result.page_number})")
                response_parts.append(f"   Relevancia: {result.relevance_score}")
                response_parts.append(f"   Contenido: {result.content[:300]}...")
                response_parts.append("")
            
            # Respuesta basada en el contenido
            if "langgraph" in query_lower:
                response_parts.append("""
**Basándome en los documentos sobre LangGraph:**

LangGraph es una biblioteca de Python que permite construir agentes de IA complejos y sistemas de flujo de trabajo utilizando grafos de estado. Es especialmente útil para:

• **Grafos de Estado:** Modelar flujos de trabajo complejos como grafos dirigidos
• **Coordinación de Agentes:** Facilitar la comunicación entre múltiples agentes de IA
• **Persistencia de Estado:** Mantener el estado del flujo de trabajo entre ejecuciones
• **Integración con LangChain:** Se integra perfectamente con el ecosistema de LangChain
• **Escalabilidad:** Permite construir sistemas distribuidos y escalables

**Casos de uso comunes:**
- Asistentes conversacionales que mantienen contexto
- Sistemas de investigación automatizada
- Flujos de trabajo empresariales complejos
- Pipelines de análisis de datos
- Sistemas de generación de contenido en múltiples pasos
""")
            
            elif "inteligencia artificial" in query_lower or "ia" in query_lower:
                response_parts.append("""
**Basándome en los documentos sobre Inteligencia Artificial:**

La Inteligencia Artificial (IA) es una rama de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana.

**Tipos de IA:**
1. **IA Débil (Narrow AI):** Diseñada para tareas específicas como reconocimiento de voz o diagnóstico médico
2. **IA General (AGI):** Puede realizar cualquier tarea intelectual humana
3. **IA Superinteligente:** Supera la inteligencia humana en todos los aspectos

**Aplicaciones principales:**
• Medicina: Diagnóstico, análisis de imágenes, desarrollo de fármacos
• Finanzas: Detección de fraudes, trading algorítmico
• Transporte: Vehículos autónomos, optimización de rutas
• Educación: Tutores personalizados, evaluación automática
• Entretenimiento: Recomendaciones, generación de contenido

**Tecnologías clave:**
- Machine Learning: Algoritmos que aprenden sin programación explícita
- Deep Learning: Redes neuronales artificiales
- Procesamiento de Lenguaje Natural: Comprensión del lenguaje humano
- Computer Vision: Interpretación de información visual
""")
            
            else:
                # Respuesta general basada en documentos
                response_parts.append("""
**Información relevante de los documentos:**

Los documentos disponibles contienen información sobre:
• **Inteligencia Artificial:** Fundamentos, tipos, aplicaciones y tecnologías
• **LangGraph:** Biblioteca para construir agentes de IA complejos

¿Te gustaría que profundice en algún aspecto específico de estos temas?
""")
            
            return "\n".join(response_parts)
        
        else:
            # Sin documentos relevantes, respuesta general
            if "documento" in query_lower or "pdf" in query_lower:
                return f"""
📚 **Información sobre Documentos Disponibles:**

Actualmente tengo acceso a {len(self.documents)} documentos con {len(self.chunks)} fragmentos de texto:

**Documentos cargados:**
{chr(10).join([f"• {doc['title']} ({doc['pages']} páginas, {doc['total_chunks']} fragmentos)" for doc in self.documents.values()])}

**Para buscar información específica:**
• Pregunta sobre "Inteligencia Artificial" para obtener información sobre IA
• Pregunta sobre "LangGraph" para obtener información sobre la biblioteca
• O haz cualquier pregunta y buscaré en los documentos disponibles

¿En qué tema te gustaría que te ayude?
"""
            
            elif "ayuda" in query_lower or "qué puedes hacer" in query_lower:
                return f"""
🤖 **Asistente de IA con Documentos - Capacidades**

¡Hola! Soy un asistente de IA que puede acceder a documentos PDF cargados en mi base de datos.

**Mis capacidades:**
• 📚 **Búsqueda en documentos:** Puedo buscar información en {len(self.documents)} documentos cargados
• 🧠 **Procesamiento inteligente:** Entiendo consultas complejas y las relaciono con el contenido disponible
• 📊 **Análisis de relevancia:** Priorizo la información más relevante para tu consulta
• 💡 **Respuestas contextuales:** Combino información de documentos con conocimiento general

**Documentos disponibles:**
{chr(10).join([f"• {doc['title']} ({doc['pages']} páginas)" for doc in self.documents.values()])}

**Ejemplos de consultas:**
• "¿Qué es LangGraph?"
• "Explícame sobre Inteligencia Artificial"
• "¿Cuáles son los tipos de IA?"
• "¿Qué aplicaciones tiene la IA en medicina?"

¿En qué puedo ayudarte hoy?
"""
            
            else:
                return f"""
He recibido tu consulta: "{query}"

Aunque no encontré información específica en los documentos cargados, puedo ayudarte con:

**Documentos disponibles:**
{chr(10).join([f"• {doc['title']} ({doc['pages']} páginas)" for doc in self.documents.values()])}

**Sugerencias:**
• Pregunta sobre "Inteligencia Artificial" o "IA"
• Pregunta sobre "LangGraph" o "agentes de IA"
• O reformula tu pregunta para que pueda buscar mejor en los documentos

¿Te gustaría que busque información sobre algún tema específico en los documentos disponibles?
"""
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del asistente"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "agent_id": self.agent_id,
            "status": "running" if self.is_running else "stopped",
            "uptime": uptime,
            "conversations": len(self.conversation_history),
            "documents_available": len(self.documents),
            "chunks_available": len(self.chunks),
            "model": "document_aware_assistant"
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Obtener historial de conversaciones"""
        return self.conversation_history
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """Listar documentos disponibles"""
        return [
            {
                'title': doc['title'],
                'pages': doc['pages'],
                'chunks': doc['total_chunks'],
                'size_mb': doc['size_bytes'] / (1024 * 1024),
                'upload_date': doc['upload_date'],
                'tags': doc.get('tags', [])
            }
            for doc in self.documents.values()
        ]


async def interactive_mode():
    """Modo interactivo"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("🤖 ASISTENTE CON DOCUMENTOS - MODO INTERACTIVO")
    print("=" * 50)
    print(f"{Colors.ENDC}")
    print("💡 Escribe 'salir' para terminar")
    print("💡 Escribe 'ayuda' para ver mis capacidades")
    print("💡 Escribe 'documentos' para ver documentos disponibles")
    print("💡 Escribe 'estado' para ver el estado del sistema")
    print("=" * 50)
    
    assistant = DocumentAwareAssistant()
    await assistant.start()
    
    try:
        while True:
            print(f"\n{Colors.OKCYAN}👤 Tú: {Colors.ENDC}", end="")
            user_input = input().strip()
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                break
            
            if user_input.lower() == 'documentos':
                documents = assistant.list_documents()
                if documents:
                    print(f"📚 Documentos disponibles ({len(documents)}):")
                    for i, doc in enumerate(documents, 1):
                        print(f"   {i}. {doc['title']}")
                        print(f"      📊 Páginas: {doc['pages']}, Fragmentos: {doc['chunks']}")
                        print(f"      🏷️  Tags: {', '.join(doc['tags']) if doc['tags'] else 'Ninguno'}")
                else:
                    print("📚 No hay documentos disponibles")
                continue
            
            if user_input.lower() == 'estado':
                status = assistant.get_status()
                print(f"📊 Estado del sistema:")
                print(f"   🤖 ID: {status['agent_id']}")
                print(f"   📊 Estado: {status['status']}")
                print(f"   ⏱️  Tiempo activo: {status['uptime']:.2f}s")
                print(f"   💬 Conversaciones: {status['conversations']}")
                print(f"   📚 Documentos: {status['documents_available']}")
                print(f"   🧩 Fragmentos: {status['chunks_available']}")
                continue
            
            if not user_input:
                continue
            
            # Crear petición
            request = AgentRequest(
                query=user_input,
                priority=PriorityLevel.MEDIUM
            )
            
            # Procesar petición
            print(f"{Colors.OKBLUE}🤖 Asistente: Procesando...{Colors.ENDC}")
            response = await assistant.process_request(request)
            
            if response.success:
                print(f"{Colors.OKGREEN}🤖 Asistente: {response.content}{Colors.ENDC}")
                print(f"{Colors.OKCYAN}⏱️  Tiempo: {response.processing_time:.2f}s{Colors.ENDC}")
                print(f"{Colors.OKCYAN}📊 Confianza: {response.confidence_score:.1%}{Colors.ENDC}")
                if response.sources:
                    print(f"{Colors.OKCYAN}📚 Documentos consultados: {len(response.sources)}{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}❌ Error: {response.error}{Colors.ENDC}")
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}🛑 Interrumpido por el usuario{Colors.ENDC}")
    
    finally:
        await assistant.stop()
        
        # Mostrar estadísticas
        status = assistant.get_status()
        print(f"\n{Colors.HEADER}📊 Estadísticas de la sesión:{Colors.ENDC}")
        print(f"   Conversaciones: {status['conversations']}")
        print(f"   Tiempo activo: {status['uptime']:.2f}s")
        print(f"   Documentos consultados: {status['documents_available']}")


async def demo_mode():
    """Modo demostración"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("🎯 ASISTENTE CON DOCUMENTOS - MODO DEMOSTRACIÓN")
    print("=" * 50)
    print(f"{Colors.ENDC}")
    
    assistant = DocumentAwareAssistant()
    await assistant.start()
    
    # Consultas de demostración
    demo_queries = [
        "¿Qué es LangGraph?",
        "Explícame sobre Inteligencia Artificial",
        "¿Cuáles son los tipos de IA?",
        "¿Qué documentos tienes disponibles?",
        "¿Qué aplicaciones tiene la IA en medicina?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{Colors.OKBLUE}🔍 Demostración {i}: {query}{Colors.ENDC}")
        print("-" * 40)
        
        request = AgentRequest(
            query=query,
            priority=PriorityLevel.MEDIUM
        )
        
        response = await assistant.process_request(request)
        
        if response.success:
            print(f"{Colors.OKGREEN}✅ Respuesta: {response.content}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}⏱️  Tiempo: {response.processing_time:.2f}s{Colors.ENDC}")
            print(f"{Colors.OKCYAN}📊 Confianza: {response.confidence_score:.1%}{Colors.ENDC}")
            if response.sources:
                print(f"{Colors.OKCYAN}📚 Documentos consultados: {len(response.sources)}{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ Error: {response.error}{Colors.ENDC}")
        
        print("-" * 40)
    
    await assistant.stop()
    
    # Mostrar estadísticas finales
    status = assistant.get_status()
    print(f"\n{Colors.HEADER}📊 Estadísticas de la demostración:{Colors.ENDC}")
    print(f"   Consultas procesadas: {status['conversations']}")
    print(f"   Tiempo total: {status['uptime']:.2f}s")
    print(f"   Documentos disponibles: {status['documents_available']}")


async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Asistente de IA con Documentos")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interactivo")
    parser.add_argument("--demo", "-d", action="store_true", help="Modo demostración")
    parser.add_argument("--query", "-q", type=str, help="Consulta única")
    
    args = parser.parse_args()
    
    if args.interactive:
        await interactive_mode()
    elif args.demo:
        await demo_mode()
    elif args.query:
        assistant = DocumentAwareAssistant()
        await assistant.start()
        
        request = AgentRequest(query=args.query, priority=PriorityLevel.MEDIUM)
        response = await assistant.process_request(request)
        
        if response.success:
            print(f"{Colors.OKGREEN}🤖 Respuesta: {response.content}{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ Error: {response.error}{Colors.ENDC}")
        
        await assistant.stop()
    else:
        # Modo por defecto: demostración
        await demo_mode()


if __name__ == "__main__":
    asyncio.run(main()) 