<<<<<<< HEAD
#!/usr/bin/env python3
"""
📄 Cargador de Documentos PDF para el Sistema RAG

Este script permite cargar documentos PDF a la base de datos vectorial
para que el asistente de IA pueda acceder a esa información.
"""

import asyncio
import sys
import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import PyPDF2
    from PyPDF2 import PdfReader
except ImportError:
    print("❌ PyPDF2 no está instalado. Instalando...")
    os.system("pip install PyPDF2")
    from PyPDF2 import PdfReader

try:
    import fitz  # PyMuPDF
except ImportError:
    print("❌ PyMuPDF no está instalado. Instalando...")
    os.system("pip install PyMuPDF")
    import fitz

from agent.core.config import get_config
from agent.core.models_simple import AgentRequest, AgentResponse


@dataclass
class DocumentInfo:
    """Información del documento"""
    id: str
    filename: str
    title: str
    author: Optional[str] = None
    subject: Optional[str] = None
    pages: int = 0
    size_bytes: int = 0
    upload_date: Optional[datetime] = None
    content_type: str = "pdf"
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.upload_date is None:
            self.upload_date = datetime.now()


@dataclass
class DocumentChunk:
    """Fragmento de documento"""
    id: str
    document_id: str
    content: str
    page_number: int
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PDFDocumentLoader:
    """Cargador de documentos PDF"""
    
    def __init__(self):
        self.config = get_config()
        self.upload_dir = Path("data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.documents_db_file = Path("data/documents_database.json")
        self.chunks_db_file = Path("data/document_chunks.json")
        
        # Cargar bases de datos existentes
        self.documents = self._load_documents_db()
        self.chunks = self._load_chunks_db()
        
        print("📄 Cargador de Documentos PDF inicializado")
        print(f"📁 Directorio de uploads: {self.upload_dir}")
    
    def _load_documents_db(self) -> Dict[str, DocumentInfo]:
        """Cargar base de datos de documentos"""
        if self.documents_db_file.exists():
            try:
                with open(self.documents_db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {doc_id: DocumentInfo(**doc_data) for doc_id, doc_data in data.items()}
            except Exception as e:
                print(f"⚠️ Error cargando base de datos de documentos: {e}")
        return {}
    
    def _save_documents_db(self):
        """Guardar base de datos de documentos"""
        try:
            data = {
                doc_id: {
                    'id': doc.id,
                    'filename': doc.filename,
                    'title': doc.title,
                    'author': doc.author,
                    'subject': doc.subject,
                    'pages': doc.pages,
                    'size_bytes': doc.size_bytes,
                    'upload_date': doc.upload_date.isoformat(),
                    'content_type': doc.content_type,
                    'tags': doc.tags,
                    'metadata': doc.metadata
                }
                for doc_id, doc in self.documents.items()
            }
            
            with open(self.documents_db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error guardando base de datos de documentos: {e}")
    
    def _load_chunks_db(self) -> Dict[str, DocumentChunk]:
        """Cargar base de datos de fragmentos"""
        if self.chunks_db_file.exists():
            try:
                with open(self.chunks_db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {chunk_id: DocumentChunk(**chunk_data) for chunk_id, chunk_data in data.items()}
            except Exception as e:
                print(f"⚠️ Error cargando base de datos de fragmentos: {e}")
        return {}
    
    def _save_chunks_db(self):
        """Guardar base de datos de fragmentos"""
        try:
            data = {
                chunk_id: {
                    'id': chunk.id,
                    'document_id': chunk.document_id,
                    'content': chunk.content,
                    'page_number': chunk.page_number,
                    'chunk_index': chunk.chunk_index,
                    'start_char': chunk.start_char,
                    'end_char': chunk.end_char,
                    'metadata': chunk.metadata
                }
                for chunk_id, chunk in self.chunks.items()
            }
            
            with open(self.chunks_db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error guardando base de datos de fragmentos: {e}")
    
    def extract_pdf_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """Extraer metadatos del PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                info = reader.metadata
                
                metadata = {
                    'title': info.get('/Title', ''),
                    'author': info.get('/Author', ''),
                    'subject': info.get('/Subject', ''),
                    'creator': info.get('/Creator', ''),
                    'producer': info.get('/Producer', ''),
                    'creation_date': info.get('/CreationDate', ''),
                    'modification_date': info.get('/ModDate', ''),
                    'pages': len(reader.pages)
                }
                
                return metadata
                
        except Exception as e:
            print(f"⚠️ Error extrayendo metadatos: {e}")
            return {}
    
    def extract_pdf_text(self, pdf_path: Path) -> List[str]:
        """Extraer texto del PDF página por página"""
        try:
            # Usar PyMuPDF para mejor extracción de texto
            doc = fitz.open(pdf_path)
            pages_text = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                pages_text.append(text.strip())
            
            doc.close()
            return pages_text
            
        except Exception as e:
            print(f"⚠️ Error con PyMuPDF, usando PyPDF2: {e}")
            try:
                # Fallback a PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PdfReader(file)
                    pages_text = []
                    
                    for page in reader.pages:
                        text = page.extract_text()
                        pages_text.append(text.strip())
                    
                    return pages_text
                    
            except Exception as e2:
                print(f"❌ Error extrayendo texto del PDF: {e2}")
                return []
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Dividir texto en fragmentos"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Buscar un buen punto de corte (final de oración)
            if end < len(text):
                # Buscar el último punto, coma o salto de línea en el rango
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def load_pdf_document(self, pdf_path: Path, tags: List[str] = None) -> Optional[DocumentInfo]:
        """Cargar un documento PDF completo"""
        try:
            print(f"📄 Cargando documento: {pdf_path.name}")
            
            # Verificar que el archivo existe
            if not pdf_path.exists():
                print(f"❌ Archivo no encontrado: {pdf_path}")
                return None
            
            # Obtener información del archivo
            file_size = pdf_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"📊 Tamaño del archivo: {file_size_mb:.2f} MB")
            
            # Extraer metadatos
            metadata = self.extract_pdf_metadata(pdf_path)
            print(f"📋 Metadatos extraídos: {len(metadata)} campos")
            
            # Extraer texto
            pages_text = self.extract_pdf_text(pdf_path)
            print(f"📄 Páginas extraídas: {len(pages_text)}")
            
            if not pages_text:
                print("❌ No se pudo extraer texto del PDF")
                return None
            
            # Crear documento
            doc_id = str(uuid.uuid4())
            document = DocumentInfo(
                id=doc_id,
                filename=pdf_path.name,
                title=metadata.get('title', pdf_path.stem),
                author=metadata.get('author'),
                subject=metadata.get('subject'),
                pages=len(pages_text),
                size_bytes=file_size,
                tags=tags or [],
                metadata=metadata
            )
            
            # Guardar documento
            self.documents[doc_id] = document
            
            # Procesar páginas y crear fragmentos
            total_chunks = 0
            for page_num, page_text in enumerate(pages_text):
                if not page_text.strip():
                    continue
                
                # Dividir página en fragmentos
                chunks = self.chunk_text(page_text, 
                                       chunk_size=self.config.rag_chunk_size,
                                       overlap=self.config.rag_chunk_overlap)
                
                for chunk_index, chunk_text in enumerate(chunks):
                    chunk_id = str(uuid.uuid4())
                    chunk = DocumentChunk(
                        id=chunk_id,
                        document_id=doc_id,
                        content=chunk_text,
                        page_number=page_num + 1,
                        chunk_index=chunk_index,
                        start_char=0,  # Simplificado
                        end_char=len(chunk_text),
                        metadata={
                            'document_title': document.title,
                            'document_author': document.author,
                            'page_number': page_num + 1,
                            'chunk_size': len(chunk_text)
                        }
                    )
                    
                    self.chunks[chunk_id] = chunk
                    total_chunks += 1
            
            # Guardar bases de datos
            self._save_documents_db()
            self._save_chunks_db()
            
            print(f"✅ Documento cargado exitosamente:")
            print(f"   📄 Título: {document.title}")
            print(f"   👤 Autor: {document.author or 'No especificado'}")
            print(f"   📊 Páginas: {document.pages}")
            print(f"   🧩 Fragmentos: {total_chunks}")
            print(f"   🏷️  Tags: {', '.join(document.tags) if document.tags else 'Ninguno'}")
            
            return document
            
        except Exception as e:
            print(f"❌ Error cargando documento: {e}")
            return None
    
    async def load_pdf_from_directory(self, directory_path: Path, tags: List[str] = None) -> List[DocumentInfo]:
        """Cargar todos los PDFs de un directorio"""
        if not directory_path.exists():
            print(f"❌ Directorio no encontrado: {directory_path}")
            return []
        
        pdf_files = list(directory_path.glob("*.pdf"))
        if not pdf_files:
            print(f"📁 No se encontraron archivos PDF en: {directory_path}")
            return []
        
        print(f"📁 Encontrados {len(pdf_files)} archivos PDF")
        
        loaded_documents = []
        for pdf_file in pdf_files:
            try:
                document = await self.load_pdf_document(pdf_file, tags)
                if document:
                    loaded_documents.append(document)
            except Exception as e:
                print(f"❌ Error procesando {pdf_file.name}: {e}")
        
        return loaded_documents
    
    def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Buscar documentos por contenido"""
        query_lower = query.lower()
        results = []
        
        for chunk_id, chunk in self.chunks.items():
            if query_lower in chunk.content.lower():
                # Obtener información del documento
                doc = self.documents.get(chunk.document_id)
                if doc:
                    results.append({
                        'chunk_id': chunk_id,
                        'document_id': chunk.document_id,
                        'document_title': doc.title,
                        'document_author': doc.author,
                        'page_number': chunk.page_number,
                        'content': chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                        'relevance_score': chunk.content.lower().count(query_lower)
                    })
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:limit]
    
    def get_document_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de la base de datos de documentos"""
        total_documents = len(self.documents)
        total_chunks = len(self.chunks)
        total_pages = sum(doc.pages for doc in self.documents.values())
        total_size_mb = sum(doc.size_bytes for doc in self.documents.values()) / (1024 * 1024)
        
        # Documentos por autor
        authors = {}
        for doc in self.documents.values():
            author = doc.author or "Desconocido"
            authors[author] = authors.get(author, 0) + 1
        
        # Tags más comunes
        all_tags = []
        for doc in self.documents.values():
            all_tags.extend(doc.tags)
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            'total_documents': total_documents,
            'total_chunks': total_chunks,
            'total_pages': total_pages,
            'total_size_mb': total_size_mb,
            'authors': authors,
            'tag_counts': tag_counts,
            'documents': [
                {
                    'id': doc.id,
                    'title': doc.title,
                    'author': doc.author,
                    'pages': doc.pages,
                    'upload_date': doc.upload_date.isoformat(),
                    'tags': doc.tags
                }
                for doc in self.documents.values()
            ]
        }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """Listar todos los documentos"""
        return [
            {
                'id': doc.id,
                'title': doc.title,
                'author': doc.author,
                'subject': doc.subject,
                'pages': doc.pages,
                'size_mb': doc.size_bytes / (1024 * 1024),
                'upload_date': doc.upload_date.isoformat(),
                'tags': doc.tags,
                'chunks_count': len([c for c in self.chunks.values() if c.document_id == doc.id])
            }
            for doc in self.documents.values()
        ]


async def interactive_mode():
    """Modo interactivo para cargar documentos"""
    print("📄 CARGADOR DE DOCUMENTOS PDF - MODO INTERACTIVO")
    print("=" * 50)
    print("💡 Comandos disponibles:")
    print("   'cargar <archivo.pdf>' - Cargar un archivo específico")
    print("   'cargar_directorio <ruta>' - Cargar todos los PDFs de un directorio")
    print("   'buscar <texto>' - Buscar en los documentos")
    print("   'listar' - Listar todos los documentos")
    print("   'estadisticas' - Ver estadísticas")
    print("   'salir' - Terminar")
    print("=" * 50)
    
    loader = PDFDocumentLoader()
    
    try:
        while True:
            print(f"\n📄 Comando: ", end="")
            user_input = input().strip()
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                break
            
            if not user_input:
                continue
            
            parts = user_input.split(' ', 1)
            command = parts[0].lower()
            
            if command == 'cargar' and len(parts) > 1:
                file_path = Path(parts[1])
                if not file_path.is_absolute():
                    file_path = loader.upload_dir / file_path
                
                print(f"📄 Cargando archivo: {file_path}")
                document = await loader.load_pdf_document(file_path)
                if document:
                    print(f"✅ Documento cargado: {document.title}")
                else:
                    print("❌ Error cargando documento")
            
            elif command == 'cargar_directorio' and len(parts) > 1:
                dir_path = Path(parts[1])
                print(f"📁 Cargando directorio: {dir_path}")
                documents = await loader.load_pdf_from_directory(dir_path)
                print(f"✅ {len(documents)} documentos cargados")
            
            elif command == 'buscar' and len(parts) > 1:
                query = parts[1]
                print(f"🔍 Buscando: {query}")
                results = loader.search_documents(query)
                if results:
                    print(f"📄 Encontrados {len(results)} resultados:")
                    for i, result in enumerate(results, 1):
                        print(f"   {i}. {result['document_title']} (página {result['page_number']})")
                        print(f"      {result['content']}")
                        print()
                else:
                    print("❌ No se encontraron resultados")
            
            elif command == 'listar':
                documents = loader.list_documents()
                if documents:
                    print(f"📚 Documentos en la base de datos ({len(documents)}):")
                    for i, doc in enumerate(documents, 1):
                        print(f"   {i}. {doc['title']}")
                        print(f"      👤 Autor: {doc['author'] or 'Desconocido'}")
                        print(f"      📊 Páginas: {doc['pages']}, Tamaño: {doc['size_mb']:.2f} MB")
                        print(f"      🧩 Fragmentos: {doc['chunks_count']}")
                        print(f"      🏷️  Tags: {', '.join(doc['tags']) if doc['tags'] else 'Ninguno'}")
                        print()
                else:
                    print("📚 No hay documentos en la base de datos")
            
            elif command == 'estadisticas':
                stats = loader.get_document_statistics()
                print(f"📊 Estadísticas de la base de datos:")
                print(f"   📄 Documentos totales: {stats['total_documents']}")
                print(f"   🧩 Fragmentos totales: {stats['total_chunks']}")
                print(f"   📊 Páginas totales: {stats['total_pages']}")
                print(f"   💾 Tamaño total: {stats['total_size_mb']:.2f} MB")
                
                if stats['authors']:
                    print(f"   👤 Autores ({len(stats['authors'])}):")
                    for author, count in sorted(stats['authors'].items(), key=lambda x: x[1], reverse=True):
                        print(f"      {author}: {count} documentos")
                
                if stats['tag_counts']:
                    print(f"   🏷️  Tags más comunes:")
                    for tag, count in sorted(stats['tag_counts'].items(), key=lambda x: x[1], reverse=True)[:10]:
                        print(f"      {tag}: {count} veces")
            
            else:
                print("❌ Comando no reconocido. Usa 'ayuda' para ver los comandos disponibles.")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Interrumpido por el usuario")
    
    print("👋 ¡Hasta luego!")


async def demo_mode():
    """Modo demostración"""
    print("🎯 CARGADOR DE DOCUMENTOS PDF - MODO DEMOSTRACIÓN")
    print("=" * 50)
    
    loader = PDFDocumentLoader()
    
    # Mostrar estadísticas iniciales
    stats = loader.get_document_statistics()
    print(f"📊 Estado inicial:")
    print(f"   Documentos: {stats['total_documents']}")
    print(f"   Fragmentos: {stats['total_chunks']}")
    print(f"   Páginas: {stats['total_pages']}")
    
    # Buscar PDFs en el directorio de uploads
    pdf_files = list(loader.upload_dir.glob("*.pdf"))
    
    if pdf_files:
        print(f"\n📁 Encontrados {len(pdf_files)} archivos PDF para cargar:")
        for pdf_file in pdf_files:
            print(f"   📄 {pdf_file.name}")
        
        # Cargar el primer PDF como demostración
        if pdf_files:
            print(f"\n📄 Cargando demostración: {pdf_files[0].name}")
            document = await loader.load_pdf_document(pdf_files[0], tags=['demo', 'ejemplo'])
            
            if document:
                print(f"✅ Documento cargado exitosamente")
                
                # Buscar en el documento
                print(f"\n🔍 Buscando contenido en el documento...")
                results = loader.search_documents("documento", limit=3)
                if results:
                    print(f"📄 Encontrados {len(results)} fragmentos:")
                    for i, result in enumerate(results, 1):
                        print(f"   {i}. Página {result['page_number']}: {result['content'][:100]}...")
                else:
                    print("❌ No se encontraron resultados")
    else:
        print(f"\n📁 No se encontraron archivos PDF en {loader.upload_dir}")
        print(f"💡 Coloca archivos PDF en el directorio para cargarlos")
    
    # Mostrar estadísticas finales
    stats = loader.get_document_statistics()
    print(f"\n📊 Estado final:")
    print(f"   Documentos: {stats['total_documents']}")
    print(f"   Fragmentos: {stats['total_chunks']}")
    print(f"   Páginas: {stats['total_pages']}")


async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cargador de Documentos PDF")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interactivo")
    parser.add_argument("--demo", "-d", action="store_true", help="Modo demostración")
    parser.add_argument("--file", "-f", type=str, help="Cargar archivo PDF específico")
    parser.add_argument("--directory", "-dir", type=str, help="Cargar todos los PDFs de un directorio")
    parser.add_argument("--search", "-s", type=str, help="Buscar en los documentos")
    parser.add_argument("--list", "-l", action="store_true", help="Listar documentos")
    parser.add_argument("--stats", action="store_true", help="Mostrar estadísticas")
    
    args = parser.parse_args()
    
    loader = PDFDocumentLoader()
    
    if args.interactive:
        await interactive_mode()
    elif args.demo:
        await demo_mode()
    elif args.file:
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = loader.upload_dir / file_path
        
        print(f"📄 Cargando archivo: {file_path}")
        document = await loader.load_pdf_document(file_path)
        if document:
            print(f"✅ Documento cargado: {document.title}")
        else:
            print("❌ Error cargando documento")
    
    elif args.directory:
        dir_path = Path(args.directory)
        print(f"📁 Cargando directorio: {dir_path}")
        documents = await loader.load_pdf_from_directory(dir_path)
        print(f"✅ {len(documents)} documentos cargados")
    
    elif args.search:
        print(f"🔍 Buscando: {args.search}")
        results = loader.search_documents(args.search)
        if results:
            print(f"📄 Encontrados {len(results)} resultados:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['document_title']} (página {result['page_number']})")
                print(f"      {result['content']}")
                print()
        else:
            print("❌ No se encontraron resultados")
    
    elif args.list:
        documents = loader.list_documents()
        if documents:
            print(f"📚 Documentos en la base de datos ({len(documents)}):")
            for i, doc in enumerate(documents, 1):
                print(f"   {i}. {doc['title']}")
                print(f"      👤 Autor: {doc['author'] or 'Desconocido'}")
                print(f"      📊 Páginas: {doc['pages']}, Tamaño: {doc['size_mb']:.2f} MB")
                print(f"      🧩 Fragmentos: {doc['chunks_count']}")
        else:
            print("📚 No hay documentos en la base de datos")
    
    elif args.stats:
        stats = loader.get_document_statistics()
        print(f"📊 Estadísticas de la base de datos:")
        print(f"   📄 Documentos totales: {stats['total_documents']}")
        print(f"   🧩 Fragmentos totales: {stats['total_chunks']}")
        print(f"   📊 Páginas totales: {stats['total_pages']}")
        print(f"   💾 Tamaño total: {stats['total_size_mb']:.2f} MB")
    
    else:
        # Modo por defecto: demostración
        await demo_mode()


if __name__ == "__main__":
=======
#!/usr/bin/env python3
"""
📄 Cargador de Documentos PDF para el Sistema RAG

Este script permite cargar documentos PDF a la base de datos vectorial
para que el asistente de IA pueda acceder a esa información.
"""

import asyncio
import sys
import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import PyPDF2
    from PyPDF2 import PdfReader
except ImportError:
    print("❌ PyPDF2 no está instalado. Instalando...")
    os.system("pip install PyPDF2")
    from PyPDF2 import PdfReader

try:
    import fitz  # PyMuPDF
except ImportError:
    print("❌ PyMuPDF no está instalado. Instalando...")
    os.system("pip install PyMuPDF")
    import fitz

from agent.core.config import get_config
from agent.core.models_simple import AgentRequest, AgentResponse


@dataclass
class DocumentInfo:
    """Información del documento"""
    id: str
    filename: str
    title: str
    author: Optional[str] = None
    subject: Optional[str] = None
    pages: int = 0
    size_bytes: int = 0
    upload_date: Optional[datetime] = None
    content_type: str = "pdf"
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.upload_date is None:
            self.upload_date = datetime.now()


@dataclass
class DocumentChunk:
    """Fragmento de documento"""
    id: str
    document_id: str
    content: str
    page_number: int
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PDFDocumentLoader:
    """Cargador de documentos PDF"""
    
    def __init__(self):
        self.config = get_config()
        self.upload_dir = Path("data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.documents_db_file = Path("data/documents_database.json")
        self.chunks_db_file = Path("data/document_chunks.json")
        
        # Cargar bases de datos existentes
        self.documents = self._load_documents_db()
        self.chunks = self._load_chunks_db()
        
        print("📄 Cargador de Documentos PDF inicializado")
        print(f"📁 Directorio de uploads: {self.upload_dir}")
    
    def _load_documents_db(self) -> Dict[str, DocumentInfo]:
        """Cargar base de datos de documentos"""
        if self.documents_db_file.exists():
            try:
                with open(self.documents_db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {doc_id: DocumentInfo(**doc_data) for doc_id, doc_data in data.items()}
            except Exception as e:
                print(f"⚠️ Error cargando base de datos de documentos: {e}")
        return {}
    
    def _save_documents_db(self):
        """Guardar base de datos de documentos"""
        try:
            data = {
                doc_id: {
                    'id': doc.id,
                    'filename': doc.filename,
                    'title': doc.title,
                    'author': doc.author,
                    'subject': doc.subject,
                    'pages': doc.pages,
                    'size_bytes': doc.size_bytes,
                    'upload_date': doc.upload_date.isoformat(),
                    'content_type': doc.content_type,
                    'tags': doc.tags,
                    'metadata': doc.metadata
                }
                for doc_id, doc in self.documents.items()
            }
            
            with open(self.documents_db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error guardando base de datos de documentos: {e}")
    
    def _load_chunks_db(self) -> Dict[str, DocumentChunk]:
        """Cargar base de datos de fragmentos"""
        if self.chunks_db_file.exists():
            try:
                with open(self.chunks_db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {chunk_id: DocumentChunk(**chunk_data) for chunk_id, chunk_data in data.items()}
            except Exception as e:
                print(f"⚠️ Error cargando base de datos de fragmentos: {e}")
        return {}
    
    def _save_chunks_db(self):
        """Guardar base de datos de fragmentos"""
        try:
            data = {
                chunk_id: {
                    'id': chunk.id,
                    'document_id': chunk.document_id,
                    'content': chunk.content,
                    'page_number': chunk.page_number,
                    'chunk_index': chunk.chunk_index,
                    'start_char': chunk.start_char,
                    'end_char': chunk.end_char,
                    'metadata': chunk.metadata
                }
                for chunk_id, chunk in self.chunks.items()
            }
            
            with open(self.chunks_db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error guardando base de datos de fragmentos: {e}")
    
    def extract_pdf_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """Extraer metadatos del PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                info = reader.metadata
                
                metadata = {
                    'title': info.get('/Title', ''),
                    'author': info.get('/Author', ''),
                    'subject': info.get('/Subject', ''),
                    'creator': info.get('/Creator', ''),
                    'producer': info.get('/Producer', ''),
                    'creation_date': info.get('/CreationDate', ''),
                    'modification_date': info.get('/ModDate', ''),
                    'pages': len(reader.pages)
                }
                
                return metadata
                
        except Exception as e:
            print(f"⚠️ Error extrayendo metadatos: {e}")
            return {}
    
    def extract_pdf_text(self, pdf_path: Path) -> List[str]:
        """Extraer texto del PDF página por página"""
        try:
            # Usar PyMuPDF para mejor extracción de texto
            doc = fitz.open(pdf_path)
            pages_text = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                pages_text.append(text.strip())
            
            doc.close()
            return pages_text
            
        except Exception as e:
            print(f"⚠️ Error con PyMuPDF, usando PyPDF2: {e}")
            try:
                # Fallback a PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PdfReader(file)
                    pages_text = []
                    
                    for page in reader.pages:
                        text = page.extract_text()
                        pages_text.append(text.strip())
                    
                    return pages_text
                    
            except Exception as e2:
                print(f"❌ Error extrayendo texto del PDF: {e2}")
                return []
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Dividir texto en fragmentos"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Buscar un buen punto de corte (final de oración)
            if end < len(text):
                # Buscar el último punto, coma o salto de línea en el rango
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def load_pdf_document(self, pdf_path: Path, tags: List[str] = None) -> Optional[DocumentInfo]:
        """Cargar un documento PDF completo"""
        try:
            print(f"📄 Cargando documento: {pdf_path.name}")
            
            # Verificar que el archivo existe
            if not pdf_path.exists():
                print(f"❌ Archivo no encontrado: {pdf_path}")
                return None
            
            # Obtener información del archivo
            file_size = pdf_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"📊 Tamaño del archivo: {file_size_mb:.2f} MB")
            
            # Extraer metadatos
            metadata = self.extract_pdf_metadata(pdf_path)
            print(f"📋 Metadatos extraídos: {len(metadata)} campos")
            
            # Extraer texto
            pages_text = self.extract_pdf_text(pdf_path)
            print(f"📄 Páginas extraídas: {len(pages_text)}")
            
            if not pages_text:
                print("❌ No se pudo extraer texto del PDF")
                return None
            
            # Crear documento
            doc_id = str(uuid.uuid4())
            document = DocumentInfo(
                id=doc_id,
                filename=pdf_path.name,
                title=metadata.get('title', pdf_path.stem),
                author=metadata.get('author'),
                subject=metadata.get('subject'),
                pages=len(pages_text),
                size_bytes=file_size,
                tags=tags or [],
                metadata=metadata
            )
            
            # Guardar documento
            self.documents[doc_id] = document
            
            # Procesar páginas y crear fragmentos
            total_chunks = 0
            for page_num, page_text in enumerate(pages_text):
                if not page_text.strip():
                    continue
                
                # Dividir página en fragmentos
                chunks = self.chunk_text(page_text, 
                                       chunk_size=self.config.rag_chunk_size,
                                       overlap=self.config.rag_chunk_overlap)
                
                for chunk_index, chunk_text in enumerate(chunks):
                    chunk_id = str(uuid.uuid4())
                    chunk = DocumentChunk(
                        id=chunk_id,
                        document_id=doc_id,
                        content=chunk_text,
                        page_number=page_num + 1,
                        chunk_index=chunk_index,
                        start_char=0,  # Simplificado
                        end_char=len(chunk_text),
                        metadata={
                            'document_title': document.title,
                            'document_author': document.author,
                            'page_number': page_num + 1,
                            'chunk_size': len(chunk_text)
                        }
                    )
                    
                    self.chunks[chunk_id] = chunk
                    total_chunks += 1
            
            # Guardar bases de datos
            self._save_documents_db()
            self._save_chunks_db()
            
            print(f"✅ Documento cargado exitosamente:")
            print(f"   📄 Título: {document.title}")
            print(f"   👤 Autor: {document.author or 'No especificado'}")
            print(f"   📊 Páginas: {document.pages}")
            print(f"   🧩 Fragmentos: {total_chunks}")
            print(f"   🏷️  Tags: {', '.join(document.tags) if document.tags else 'Ninguno'}")
            
            return document
            
        except Exception as e:
            print(f"❌ Error cargando documento: {e}")
            return None
    
    async def load_pdf_from_directory(self, directory_path: Path, tags: List[str] = None) -> List[DocumentInfo]:
        """Cargar todos los PDFs de un directorio"""
        if not directory_path.exists():
            print(f"❌ Directorio no encontrado: {directory_path}")
            return []
        
        pdf_files = list(directory_path.glob("*.pdf"))
        if not pdf_files:
            print(f"📁 No se encontraron archivos PDF en: {directory_path}")
            return []
        
        print(f"📁 Encontrados {len(pdf_files)} archivos PDF")
        
        loaded_documents = []
        for pdf_file in pdf_files:
            try:
                document = await self.load_pdf_document(pdf_file, tags)
                if document:
                    loaded_documents.append(document)
            except Exception as e:
                print(f"❌ Error procesando {pdf_file.name}: {e}")
        
        return loaded_documents
    
    def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Buscar documentos por contenido"""
        query_lower = query.lower()
        results = []
        
        for chunk_id, chunk in self.chunks.items():
            if query_lower in chunk.content.lower():
                # Obtener información del documento
                doc = self.documents.get(chunk.document_id)
                if doc:
                    results.append({
                        'chunk_id': chunk_id,
                        'document_id': chunk.document_id,
                        'document_title': doc.title,
                        'document_author': doc.author,
                        'page_number': chunk.page_number,
                        'content': chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                        'relevance_score': chunk.content.lower().count(query_lower)
                    })
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:limit]
    
    def get_document_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de la base de datos de documentos"""
        total_documents = len(self.documents)
        total_chunks = len(self.chunks)
        total_pages = sum(doc.pages for doc in self.documents.values())
        total_size_mb = sum(doc.size_bytes for doc in self.documents.values()) / (1024 * 1024)
        
        # Documentos por autor
        authors = {}
        for doc in self.documents.values():
            author = doc.author or "Desconocido"
            authors[author] = authors.get(author, 0) + 1
        
        # Tags más comunes
        all_tags = []
        for doc in self.documents.values():
            all_tags.extend(doc.tags)
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            'total_documents': total_documents,
            'total_chunks': total_chunks,
            'total_pages': total_pages,
            'total_size_mb': total_size_mb,
            'authors': authors,
            'tag_counts': tag_counts,
            'documents': [
                {
                    'id': doc.id,
                    'title': doc.title,
                    'author': doc.author,
                    'pages': doc.pages,
                    'upload_date': doc.upload_date.isoformat(),
                    'tags': doc.tags
                }
                for doc in self.documents.values()
            ]
        }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """Listar todos los documentos"""
        return [
            {
                'id': doc.id,
                'title': doc.title,
                'author': doc.author,
                'subject': doc.subject,
                'pages': doc.pages,
                'size_mb': doc.size_bytes / (1024 * 1024),
                'upload_date': doc.upload_date.isoformat(),
                'tags': doc.tags,
                'chunks_count': len([c for c in self.chunks.values() if c.document_id == doc.id])
            }
            for doc in self.documents.values()
        ]


async def interactive_mode():
    """Modo interactivo para cargar documentos"""
    print("📄 CARGADOR DE DOCUMENTOS PDF - MODO INTERACTIVO")
    print("=" * 50)
    print("💡 Comandos disponibles:")
    print("   'cargar <archivo.pdf>' - Cargar un archivo específico")
    print("   'cargar_directorio <ruta>' - Cargar todos los PDFs de un directorio")
    print("   'buscar <texto>' - Buscar en los documentos")
    print("   'listar' - Listar todos los documentos")
    print("   'estadisticas' - Ver estadísticas")
    print("   'salir' - Terminar")
    print("=" * 50)
    
    loader = PDFDocumentLoader()
    
    try:
        while True:
            print(f"\n📄 Comando: ", end="")
            user_input = input().strip()
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                break
            
            if not user_input:
                continue
            
            parts = user_input.split(' ', 1)
            command = parts[0].lower()
            
            if command == 'cargar' and len(parts) > 1:
                file_path = Path(parts[1])
                if not file_path.is_absolute():
                    file_path = loader.upload_dir / file_path
                
                print(f"📄 Cargando archivo: {file_path}")
                document = await loader.load_pdf_document(file_path)
                if document:
                    print(f"✅ Documento cargado: {document.title}")
                else:
                    print("❌ Error cargando documento")
            
            elif command == 'cargar_directorio' and len(parts) > 1:
                dir_path = Path(parts[1])
                print(f"📁 Cargando directorio: {dir_path}")
                documents = await loader.load_pdf_from_directory(dir_path)
                print(f"✅ {len(documents)} documentos cargados")
            
            elif command == 'buscar' and len(parts) > 1:
                query = parts[1]
                print(f"🔍 Buscando: {query}")
                results = loader.search_documents(query)
                if results:
                    print(f"📄 Encontrados {len(results)} resultados:")
                    for i, result in enumerate(results, 1):
                        print(f"   {i}. {result['document_title']} (página {result['page_number']})")
                        print(f"      {result['content']}")
                        print()
                else:
                    print("❌ No se encontraron resultados")
            
            elif command == 'listar':
                documents = loader.list_documents()
                if documents:
                    print(f"📚 Documentos en la base de datos ({len(documents)}):")
                    for i, doc in enumerate(documents, 1):
                        print(f"   {i}. {doc['title']}")
                        print(f"      👤 Autor: {doc['author'] or 'Desconocido'}")
                        print(f"      📊 Páginas: {doc['pages']}, Tamaño: {doc['size_mb']:.2f} MB")
                        print(f"      🧩 Fragmentos: {doc['chunks_count']}")
                        print(f"      🏷️  Tags: {', '.join(doc['tags']) if doc['tags'] else 'Ninguno'}")
                        print()
                else:
                    print("📚 No hay documentos en la base de datos")
            
            elif command == 'estadisticas':
                stats = loader.get_document_statistics()
                print(f"📊 Estadísticas de la base de datos:")
                print(f"   📄 Documentos totales: {stats['total_documents']}")
                print(f"   🧩 Fragmentos totales: {stats['total_chunks']}")
                print(f"   📊 Páginas totales: {stats['total_pages']}")
                print(f"   💾 Tamaño total: {stats['total_size_mb']:.2f} MB")
                
                if stats['authors']:
                    print(f"   👤 Autores ({len(stats['authors'])}):")
                    for author, count in sorted(stats['authors'].items(), key=lambda x: x[1], reverse=True):
                        print(f"      {author}: {count} documentos")
                
                if stats['tag_counts']:
                    print(f"   🏷️  Tags más comunes:")
                    for tag, count in sorted(stats['tag_counts'].items(), key=lambda x: x[1], reverse=True)[:10]:
                        print(f"      {tag}: {count} veces")
            
            else:
                print("❌ Comando no reconocido. Usa 'ayuda' para ver los comandos disponibles.")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Interrumpido por el usuario")
    
    print("👋 ¡Hasta luego!")


async def demo_mode():
    """Modo demostración"""
    print("🎯 CARGADOR DE DOCUMENTOS PDF - MODO DEMOSTRACIÓN")
    print("=" * 50)
    
    loader = PDFDocumentLoader()
    
    # Mostrar estadísticas iniciales
    stats = loader.get_document_statistics()
    print(f"📊 Estado inicial:")
    print(f"   Documentos: {stats['total_documents']}")
    print(f"   Fragmentos: {stats['total_chunks']}")
    print(f"   Páginas: {stats['total_pages']}")
    
    # Buscar PDFs en el directorio de uploads
    pdf_files = list(loader.upload_dir.glob("*.pdf"))
    
    if pdf_files:
        print(f"\n📁 Encontrados {len(pdf_files)} archivos PDF para cargar:")
        for pdf_file in pdf_files:
            print(f"   📄 {pdf_file.name}")
        
        # Cargar el primer PDF como demostración
        if pdf_files:
            print(f"\n📄 Cargando demostración: {pdf_files[0].name}")
            document = await loader.load_pdf_document(pdf_files[0], tags=['demo', 'ejemplo'])
            
            if document:
                print(f"✅ Documento cargado exitosamente")
                
                # Buscar en el documento
                print(f"\n🔍 Buscando contenido en el documento...")
                results = loader.search_documents("documento", limit=3)
                if results:
                    print(f"📄 Encontrados {len(results)} fragmentos:")
                    for i, result in enumerate(results, 1):
                        print(f"   {i}. Página {result['page_number']}: {result['content'][:100]}...")
                else:
                    print("❌ No se encontraron resultados")
    else:
        print(f"\n📁 No se encontraron archivos PDF en {loader.upload_dir}")
        print(f"💡 Coloca archivos PDF en el directorio para cargarlos")
    
    # Mostrar estadísticas finales
    stats = loader.get_document_statistics()
    print(f"\n📊 Estado final:")
    print(f"   Documentos: {stats['total_documents']}")
    print(f"   Fragmentos: {stats['total_chunks']}")
    print(f"   Páginas: {stats['total_pages']}")


async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cargador de Documentos PDF")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interactivo")
    parser.add_argument("--demo", "-d", action="store_true", help="Modo demostración")
    parser.add_argument("--file", "-f", type=str, help="Cargar archivo PDF específico")
    parser.add_argument("--directory", "-dir", type=str, help="Cargar todos los PDFs de un directorio")
    parser.add_argument("--search", "-s", type=str, help="Buscar en los documentos")
    parser.add_argument("--list", "-l", action="store_true", help="Listar documentos")
    parser.add_argument("--stats", action="store_true", help="Mostrar estadísticas")
    
    args = parser.parse_args()
    
    loader = PDFDocumentLoader()
    
    if args.interactive:
        await interactive_mode()
    elif args.demo:
        await demo_mode()
    elif args.file:
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = loader.upload_dir / file_path
        
        print(f"📄 Cargando archivo: {file_path}")
        document = await loader.load_pdf_document(file_path)
        if document:
            print(f"✅ Documento cargado: {document.title}")
        else:
            print("❌ Error cargando documento")
    
    elif args.directory:
        dir_path = Path(args.directory)
        print(f"📁 Cargando directorio: {dir_path}")
        documents = await loader.load_pdf_from_directory(dir_path)
        print(f"✅ {len(documents)} documentos cargados")
    
    elif args.search:
        print(f"🔍 Buscando: {args.search}")
        results = loader.search_documents(args.search)
        if results:
            print(f"📄 Encontrados {len(results)} resultados:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['document_title']} (página {result['page_number']})")
                print(f"      {result['content']}")
                print()
        else:
            print("❌ No se encontraron resultados")
    
    elif args.list:
        documents = loader.list_documents()
        if documents:
            print(f"📚 Documentos en la base de datos ({len(documents)}):")
            for i, doc in enumerate(documents, 1):
                print(f"   {i}. {doc['title']}")
                print(f"      👤 Autor: {doc['author'] or 'Desconocido'}")
                print(f"      📊 Páginas: {doc['pages']}, Tamaño: {doc['size_mb']:.2f} MB")
                print(f"      🧩 Fragmentos: {doc['chunks_count']}")
        else:
            print("📚 No hay documentos en la base de datos")
    
    elif args.stats:
        stats = loader.get_document_statistics()
        print(f"📊 Estadísticas de la base de datos:")
        print(f"   📄 Documentos totales: {stats['total_documents']}")
        print(f"   🧩 Fragmentos totales: {stats['total_chunks']}")
        print(f"   📊 Páginas totales: {stats['total_pages']}")
        print(f"   💾 Tamaño total: {stats['total_size_mb']:.2f} MB")
    
    else:
        # Modo por defecto: demostración
        await demo_mode()


if __name__ == "__main__":
>>>>>>> 4caeba3865603c67c51ab60f71b04353770ceb47
    asyncio.run(main()) 