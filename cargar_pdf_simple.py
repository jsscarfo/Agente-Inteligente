#!/usr/bin/env python3
"""
📄 Cargador Simple de PDFs

Script simple para cargar documentos PDF a la base de datos del asistente.
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Instalar dependencias si no están disponibles
try:
    import PyPDF2
    from PyPDF2 import PdfReader
except ImportError:
    print("📦 Instalando PyPDF2...")
    os.system("pip install PyPDF2")
    from PyPDF2 import PdfReader

try:
    import fitz  # PyMuPDF
except ImportError:
    print("📦 Instalando PyMuPDF...")
    os.system("pip install PyMuPDF")
    import fitz


class SimplePDFLoader:
    """Cargador simple de PDFs"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.uploads_dir = self.data_dir / "uploads"
        self.documents_file = self.data_dir / "documents.json"
        self.chunks_file = self.data_dir / "chunks.json"
        
        # Crear directorios si no existen
        self.data_dir.mkdir(exist_ok=True)
        self.uploads_dir.mkdir(exist_ok=True)
        
        # Cargar datos existentes
        self.documents = self._load_json(self.documents_file, {})
        self.chunks = self._load_json(self.chunks_file, {})
        
        print(f"📄 Cargador de PDFs inicializado")
        print(f"📁 Directorio de uploads: {self.uploads_dir}")
    
    def _load_json(self, file_path: Path, default: Any) -> Any:
        """Cargar archivo JSON"""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error cargando {file_path}: {e}")
        return default
    
    def _save_json(self, file_path: Path, data: Any):
        """Guardar archivo JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error guardando {file_path}: {e}")
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[str]:
        """Extraer texto del PDF página por página"""
        try:
            # Intentar con PyMuPDF primero (mejor calidad)
            doc = fitz.open(pdf_path)
            pages_text = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                pages_text.append(text.strip())
            
            doc.close()
            print(f"✅ Texto extraído con PyMuPDF: {len(pages_text)} páginas")
            return pages_text
            
        except Exception as e:
            print(f"⚠️ PyMuPDF falló, usando PyPDF2: {e}")
            try:
                # Fallback a PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PdfReader(file)
                    pages_text = []
                    
                    for page in reader.pages:
                        text = page.extract_text()
                        pages_text.append(text.strip())
                    
                    print(f"✅ Texto extraído con PyPDF2: {len(pages_text)} páginas")
                    return pages_text
                    
            except Exception as e2:
                print(f"❌ Error extrayendo texto: {e2}")
                return []
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Dividir texto en fragmentos"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Buscar un buen punto de corte
            if end < len(text):
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
    
    def load_pdf(self, pdf_path: Path, tags: List[str] = None) -> bool:
        """Cargar un PDF a la base de datos"""
        try:
            print(f"📄 Procesando: {pdf_path.name}")
            
            if not pdf_path.exists():
                print(f"❌ Archivo no encontrado: {pdf_path}")
                return False
            
            # Información del archivo
            file_size = pdf_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"📊 Tamaño: {file_size_mb:.2f} MB")
            
            # Extraer texto
            pages_text = self.extract_text_from_pdf(pdf_path)
            if not pages_text:
                print("❌ No se pudo extraer texto")
                return False
            
            # Crear documento
            doc_id = str(uuid.uuid4())
            document = {
                'id': doc_id,
                'filename': pdf_path.name,
                'title': pdf_path.stem,
                'pages': len(pages_text),
                'size_bytes': file_size,
                'upload_date': datetime.now().isoformat(),
                'tags': tags or [],
                'total_chunks': 0
            }
            
            # Procesar páginas
            total_chunks = 0
            for page_num, page_text in enumerate(pages_text):
                if not page_text.strip():
                    continue
                
                # Dividir en fragmentos
                chunks = self.chunk_text(page_text)
                
                for chunk_index, chunk_text in enumerate(chunks):
                    chunk_id = str(uuid.uuid4())
                    chunk = {
                        'id': chunk_id,
                        'document_id': doc_id,
                        'content': chunk_text,
                        'page_number': page_num + 1,
                        'chunk_index': chunk_index,
                        'metadata': {
                            'document_title': document['title'],
                            'page_number': page_num + 1,
                            'chunk_size': len(chunk_text)
                        }
                    }
                    
                    self.chunks[chunk_id] = chunk
                    total_chunks += 1
            
            document['total_chunks'] = total_chunks
            self.documents[doc_id] = document
            
            # Guardar datos
            self._save_json(self.documents_file, self.documents)
            self._save_json(self.chunks_file, self.chunks)
            
            print(f"✅ Documento cargado exitosamente:")
            print(f"   📄 Título: {document['title']}")
            print(f"   📊 Páginas: {document['pages']}")
            print(f"   🧩 Fragmentos: {total_chunks}")
            print(f"   🏷️  Tags: {', '.join(document['tags']) if document['tags'] else 'Ninguno'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error cargando documento: {e}")
            return False
    
    def load_all_pdfs_in_directory(self, directory_path: Path, tags: List[str] = None) -> int:
        """Cargar todos los PDFs de un directorio"""
        if not directory_path.exists():
            print(f"❌ Directorio no encontrado: {directory_path}")
            return 0
        
        pdf_files = list(directory_path.glob("*.pdf"))
        if not pdf_files:
            print(f"📁 No se encontraron PDFs en: {directory_path}")
            return 0
        
        print(f"📁 Encontrados {len(pdf_files)} archivos PDF")
        
        loaded_count = 0
        for pdf_file in pdf_files:
            if self.load_pdf(pdf_file, tags):
                loaded_count += 1
        
        return loaded_count
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Buscar en los documentos"""
        query_lower = query.lower()
        results = []
        
        for chunk_id, chunk in self.chunks.items():
            if query_lower in chunk['content'].lower():
                doc = self.documents.get(chunk['document_id'])
                if doc:
                    results.append({
                        'chunk_id': chunk_id,
                        'document_title': doc['title'],
                        'page_number': chunk['page_number'],
                        'content': chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content'],
                        'relevance': chunk['content'].lower().count(query_lower)
                    })
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas"""
        total_docs = len(self.documents)
        total_chunks = len(self.chunks)
        total_pages = sum(doc['pages'] for doc in self.documents.values())
        total_size_mb = sum(doc['size_bytes'] for doc in self.documents.values()) / (1024 * 1024)
        
        return {
            'total_documents': total_docs,
            'total_chunks': total_chunks,
            'total_pages': total_pages,
            'total_size_mb': total_size_mb,
            'documents': [
                {
                    'title': doc['title'],
                    'pages': doc['pages'],
                    'chunks': doc['total_chunks'],
                    'size_mb': doc['size_bytes'] / (1024 * 1024),
                    'upload_date': doc['upload_date']
                }
                for doc in self.documents.values()
            ]
        }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """Listar documentos"""
        return [
            {
                'title': doc['title'],
                'pages': doc['pages'],
                'chunks': doc['total_chunks'],
                'size_mb': doc['size_bytes'] / (1024 * 1024),
                'tags': doc['tags']
            }
            for doc in self.documents.values()
        ]


def main():
    """Función principal"""
    print("📄 CARGADOR SIMPLE DE PDFs")
    print("=" * 40)
    
    loader = SimplePDFLoader()
    
    # Mostrar estadísticas iniciales
    stats = loader.get_statistics()
    print(f"📊 Estado inicial: {stats['total_documents']} documentos, {stats['total_chunks']} fragmentos")
    
    # Buscar PDFs en el directorio de uploads
    pdf_files = list(loader.uploads_dir.glob("*.pdf"))
    
    if pdf_files:
        print(f"\n📁 Encontrados {len(pdf_files)} archivos PDF:")
        for pdf_file in pdf_files:
            print(f"   📄 {pdf_file.name}")
        
        # Preguntar si cargar
        print(f"\n¿Deseas cargar estos archivos? (s/n): ", end="")
        response = input().strip().lower()
        
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            print(f"\n📄 Cargando archivos...")
            loaded_count = loader.load_all_pdfs_in_directory(loader.uploads_dir, tags=['cargado_automaticamente'])
            print(f"✅ {loaded_count} documentos cargados exitosamente")
        else:
            print("❌ Carga cancelada")
    else:
        print(f"\n📁 No se encontraron archivos PDF en {loader.uploads_dir}")
        print(f"💡 Coloca archivos PDF en el directorio para cargarlos")
    
    # Mostrar estadísticas finales
    stats = loader.get_statistics()
    print(f"\n📊 Estado final:")
    print(f"   📄 Documentos: {stats['total_documents']}")
    print(f"   🧩 Fragmentos: {stats['total_chunks']}")
    print(f"   📊 Páginas: {stats['total_pages']}")
    print(f"   💾 Tamaño total: {stats['total_size_mb']:.2f} MB")
    
    if stats['documents']:
        print(f"\n📚 Documentos cargados:")
        for i, doc in enumerate(stats['documents'], 1):
            print(f"   {i}. {doc['title']}")
            print(f"      📊 Páginas: {doc['pages']}, Fragmentos: {doc['chunks']}")
            print(f"      💾 Tamaño: {doc['size_mb']:.2f} MB")
    
    # Demostrar búsqueda
    if stats['total_chunks'] > 0:
        print(f"\n🔍 Probando búsqueda...")
        results = loader.search_documents("documento", limit=3)
        if results:
            print(f"📄 Encontrados {len(results)} resultados:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['document_title']} (página {result['page_number']})")
                print(f"      {result['content']}")
                print()
        else:
            print("❌ No se encontraron resultados")
    
    print(f"\n✅ Proceso completado. Los documentos están listos para ser usados por el asistente de IA.")


if __name__ == "__main__":
    main() 