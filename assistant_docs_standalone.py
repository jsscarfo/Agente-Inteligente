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
        print(f"{Colors.OKGREEN}🛑 Asistente detenido correctamente{Colors.ENDC}")
    
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
    
    print(f"\n{Colors.HEADER}🎮 Modo Interactivo - Asistente con Documentos{Colors.ENDC}")
    print("Escribe 'quit' para salir")
    print("Escribe 'status' para ver el estado")
    print("Escribe 'documents' para listar documentos")
    print("-" * 50)
    
    while True:
        try:
            query = input(f"\n{Colors.OKCYAN}🤖 Tú: {Colors.ENDC}").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'status':
                status = assistant.get_status()
                print(f"\n{Colors.OKBLUE}📊 Estado del Asistente:{Colors.ENDC}")
                print(f"  ID: {status['agent_id']}")
                print(f"  Ejecutándose: {'Sí' if status['is_running'] else 'No'}")
                print(f"  Documentos: {status['documents_loaded']}")
                print(f"  Fragmentos: {status['chunks_loaded']}")
                print(f"  Conversaciones: {status['conversations']}")
                continue
            elif query.lower() == 'documents':
                documents = assistant.list_documents()
                print(f"\n{Colors.OKBLUE}📚 Documentos Disponibles ({len(documents)}):{Colors.ENDC}")
                for doc in documents:
                    print(f"  • {doc['title']} (páginas: {doc['pages']})")
                continue
            elif not query:
                continue
            
            # Procesar consulta
            request = AgentRequest(query=query)
            response = await assistant.process_request(request)
            
            if response.success:
                print(f"\n{Colors.OKGREEN}🤖 Asistente: {Colors.ENDC}{response.content}")
                if response.sources:
                    print(f"\n{Colors.OKCYAN}📚 Fuentes: {len(response.sources)} encontradas{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}❌ Error: {Colors.ENDC}{response.content}")
                
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}👋 ¡Hasta luego!{Colors.ENDC}")
            break
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    await assistant.stop()


async def demo_mode():
    """Modo demostración"""
    assistant = DocumentAwareAssistant()
    await assistant.start()
    
    print(f"\n{Colors.HEADER}🎬 Modo Demostración - Asistente con Documentos{Colors.ENDC}")
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
        print(f"\n{Colors.OKCYAN}🔍 Consulta {i}: {query}{Colors.ENDC}")
        print("-" * 40)
        
        request = AgentRequest(query=query)
        response = await assistant.process_request(request)
        
        if response.success:
            print(f"{Colors.OKGREEN}✅ Respuesta generada en {response.processing_time:.2f}s{Colors.ENDC}")
            print(f"{Colors.OKBLUE}📊 Confianza: {response.confidence_score:.1%}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}📚 Fuentes: {len(response.sources)} encontradas{Colors.ENDC}")
            print(f"\n{Colors.OKGREEN}📄 Respuesta:{Colors.ENDC}")
            print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
        else:
            print(f"{Colors.FAIL}❌ Error: {response.content}{Colors.ENDC}")
        
        print("\n" + "=" * 60)
        await asyncio.sleep(1)
    
    # Mostrar estadísticas finales
    status = assistant.get_status()
    print(f"\n{Colors.OKBLUE}📊 Estadísticas Finales:{Colors.ENDC}")
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
            print(f"{Colors.OKGREEN}✅ Respuesta: {Colors.ENDC}{response.content}")
        else:
            print(f"{Colors.FAIL}❌ Error: {Colors.ENDC}{response.content}")
        
        await assistant.stop()
    else:
        print(f"{Colors.HEADER}🤖 Asistente de IA con Documentos PDF{Colors.ENDC}")
        print("Uso:")
        print("  python assistant_docs_standalone.py --interactive")
        print("  python assistant_docs_standalone.py --demo")
        print("  python assistant_docs_standalone.py --query 'tu consulta'")


if __name__ == "__main__":
    asyncio.run(main()) 