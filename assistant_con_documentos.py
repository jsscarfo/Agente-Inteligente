#!/usr/bin/env python3
"""
🤖 Asistente de IA con Documentos PDF

Asistente que puede acceder a documentos PDF cargados en la base de datos
y responder preguntas basándose en esa información.
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

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent.core.models_simple import AgentRequest, AgentResponse, PriorityLevel


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
        
        print(f"🤖 Asistente con Documentos inicializado")
        print(f"🆔 ID: {self.agent_id}")
        print(f"📚 Documentos disponibles: {len(self.documents)}")
        print(f"🧩 Fragmentos de texto: {len(self.chunks)}")
    
    def _load_json(self, file_path: Path, default: Any) -> Any:
        """Cargar archivo JSON"""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error cargando {file_path}: {e}")
        return default
    
    async def start(self):
        """Iniciar el asistente"""
        self.is_running = True
        print("✅ Asistente iniciado correctamente")
    
    async def stop(self):
        """Detener el asistente"""
        self.is_running = False
        print("🛑 Asistente detenido correctamente")
    
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
            # Buscar información relevante en documentos
            search_results = self.search_documents(request.query)
            
            # Generar respuesta basada en documentos encontrados
            response_content = await self._generate_response(request.query, search_results)
            
            # Calcular tiempo de procesamiento
            processing_time = time.time() - start_time
            
            # Guardar en historial
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'query': request.query,
                'response': response_content,
                'sources_found': len(search_results),
                'processing_time': processing_time
            })
            
            return AgentResponse(
                success=True,
                content=response_content,
                confidence_score=0.9 if search_results else 0.7,
                processing_time=processing_time,
                sources=[{
                    'title': result.document_title,
                    'page': result.page_number,
                    'content': result.content[:200] + "..." if len(result.content) > 200 else result.content
                } for result in search_results]
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                content=f"Error procesando la petición: {str(e)}",
                processing_time=time.time() - start_time,
                error=str(e)
            )
    
    async def _generate_response(self, query: str, search_results: List[DocumentSearchResult]) -> str:
        """Generar respuesta basada en documentos encontrados"""
        if not search_results:
            return f"No encontré información específica sobre '{query}' en los documentos disponibles. ¿Podrías reformular tu pregunta o preguntar sobre otro tema?"
        
        # Construir respuesta basada en documentos encontrados
        response_parts = []
        response_parts.append(f"Basándome en los documentos disponibles, aquí está la información sobre '{query}':\n")
        
        for i, result in enumerate(search_results, 1):
            response_parts.append(f"\n📄 **Fuente {i}: {result.document_title} (página {result.page_number})**")
            response_parts.append(f"Relevancia: {result.relevance_score}")
            response_parts.append(f"Contenido: {result.content}")
            response_parts.append("-" * 50)
        
        # Añadir resumen
        response_parts.append(f"\n📊 **Resumen:**")
        response_parts.append(f"Encontré {len(search_results)} fragmentos relevantes en los documentos.")
        response_parts.append("La información mostrada proviene directamente de los documentos cargados en la base de datos.")
        
        return "\n".join(response_parts)
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del asistente"""
        return {
            'agent_id': self.agent_id,
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat(),
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'documents_loaded': len(self.documents),
            'chunks_loaded': len(self.chunks),
            'conversations': len(self.conversation_history)
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Obtener historial de conversaciones"""
        return self.conversation_history
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """Listar documentos disponibles"""
        return [
            {
                'id': doc_id,
                'title': doc['title'],
                'author': doc.get('author', 'Desconocido'),
                'pages': doc.get('pages', 0),
                'upload_date': doc.get('upload_date', 'Desconocido')
            }
            for doc_id, doc in self.documents.items()
        ]


async def interactive_mode():
    """Modo interactivo"""
    assistant = DocumentAwareAssistant()
    await assistant.start()
    
    print("\n🎮 Modo Interactivo - Asistente con Documentos")
    print("Escribe 'quit' para salir")
    print("Escribe 'status' para ver el estado")
    print("Escribe 'documents' para listar documentos")
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
                print(f"  Documentos: {status['documents_loaded']}")
                print(f"  Fragmentos: {status['chunks_loaded']}")
                print(f"  Conversaciones: {status['conversations']}")
                continue
            elif query.lower() == 'documents':
                documents = assistant.list_documents()
                print(f"\n📚 Documentos Disponibles ({len(documents)}):")
                for doc in documents:
                    print(f"  • {doc['title']} (páginas: {doc['pages']})")
                continue
            elif not query:
                continue
            
            # Procesar consulta
            request = AgentRequest(query=query)
            response = await assistant.process_request(request)
            
            if response.success:
                print(f"\n🤖 Asistente: {response.content}")
                if response.sources:
                    print(f"\n📚 Fuentes: {len(response.sources)} encontradas")
            else:
                print(f"\n❌ Error: {response.content}")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    await assistant.stop()


async def demo_mode():
    """Modo demostración"""
    assistant = DocumentAwareAssistant()
    await assistant.start()
    
    print("\n🎬 Modo Demostración - Asistente con Documentos")
    print("=" * 60)
    
    # Consultas de ejemplo
    demo_queries = [
        "¿Qué es LangGraph?",
        "Explica la inteligencia artificial",
        "¿Cómo funciona el procesamiento de lenguaje natural?",
        "¿Qué son los agentes de IA?",
        "Explica el aprendizaje automático"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n🔍 Consulta {i}: {query}")
        print("-" * 40)
        
        request = AgentRequest(query=query)
        response = await assistant.process_request(request)
        
        if response.success:
            print(f"✅ Respuesta generada en {response.processing_time:.2f}s")
            print(f"📊 Confianza: {response.confidence_score:.1%}")
            print(f"📚 Fuentes: {len(response.sources)} encontradas")
            print(f"\n📄 Respuesta:")
            print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
        else:
            print(f"❌ Error: {response.content}")
        
        print("\n" + "=" * 60)
        await asyncio.sleep(1)
    
    # Mostrar estadísticas finales
    status = assistant.get_status()
    print(f"\n📊 Estadísticas Finales:")
    print(f"  Conversaciones: {status['conversations']}")
    print(f"  Documentos cargados: {status['documents_loaded']}")
    print(f"  Fragmentos disponibles: {status['chunks_loaded']}")
    
    await assistant.stop()


async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🤖 Asistente de IA con Documentos PDF")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interactivo")
    parser.add_argument("--demo", "-d", action="store_true", help="Modo demostración")
    parser.add_argument("--query", "-q", help="Consulta única")
    
    args = parser.parse_args()
    
    if args.interactive:
        await interactive_mode()
    elif args.demo:
        await demo_mode()
    elif args.query:
        assistant = DocumentAwareAssistant()
        await assistant.start()
        
        request = AgentRequest(query=args.query)
        response = await assistant.process_request(request)
        
        if response.success:
            print(f"✅ Respuesta: {response.content}")
        else:
            print(f"❌ Error: {response.content}")
        
        await assistant.stop()
    else:
        print("🤖 Asistente de IA con Documentos PDF")
        print("Uso:")
        print("  python assistant_con_documentos.py --interactive")
        print("  python assistant_con_documentos.py --demo")
        print("  python assistant_con_documentos.py --query 'tu consulta'")


if __name__ == "__main__":
    asyncio.run(main()) 