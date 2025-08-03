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
        """Dividir texto en fragmentos con superposición"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Si no es el último chunk, intentar cortar en un espacio
            if end < len(text):
                # Buscar el último espacio antes del límite
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Mover al siguiente chunk con superposición
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def load_pdf(self, pdf_path: Path, tags: List[str] = None) -> bool:
        """Cargar un PDF a la base de datos"""
        try:
            if not pdf_path.exists():
                print(f"❌ Archivo no encontrado: {pdf_path}")
                return False
            
            # Verificar si ya está cargado
            pdf_name = pdf_path.name
            for doc_id, doc in self.documents.items():
                if doc['filename'] == pdf_name:
                    print(f"⚠️ PDF ya cargado: {pdf_name}")
                    return True
            
            print(f"📄 Cargando PDF: {pdf_name}")
            
            # Extraer texto
            pages_text = self.extract_text_from_pdf(pdf_path)
            if not pages_text:
                print(f"❌ No se pudo extraer texto del PDF: {pdf_name}")
                return False
            
            # Crear documento
            doc_id = str(uuid.uuid4())
            document = {
                'id': doc_id,
                'filename': pdf_name,
                'title': pdf_path.stem,
                'author': 'Desconocido',
                'subject': '',
                'pages': len(pages_text),
                'size_bytes': pdf_path.stat().st_size,
                'upload_date': datetime.now().isoformat(),
                'content_type': 'pdf',
                'tags': tags or [],
                'metadata': {
                    'source_path': str(pdf_path),
                    'extraction_method': 'PyMuPDF/PyPDF2'
                }
            }
            
            # Dividir en chunks y guardar
            total_chunks = 0
            for page_num, page_text in enumerate(pages_text, 1):
                if not page_text.strip():
                    continue
                
                chunks = self.chunk_text(page_text)
                for chunk_num, chunk_text in enumerate(chunks, 1):
                    chunk_id = f"{doc_id}_page_{page_num}_chunk_{chunk_num}"
                    
                    chunk_data = {
                        'id': chunk_id,
                        'document_id': doc_id,
                        'content': chunk_text,
                        'page_number': page_num,
                        'chunk_index': chunk_num,
                        'start_char': 0,  # Simplificado
                        'end_char': len(chunk_text),
                        'metadata': {
                            'chunk_size': len(chunk_text),
                            'extraction_method': 'simple'
                        }
                    }
                    
                    self.chunks[chunk_id] = chunk_data
                    total_chunks += 1
            
            # Guardar documento
            self.documents[doc_id] = document
            
            # Guardar a archivos
            self._save_json(self.documents_file, self.documents)
            self._save_json(self.chunks_file, self.chunks)
            
            print(f"✅ PDF cargado exitosamente: {pdf_name}")
            print(f"   📄 Páginas: {len(pages_text)}")
            print(f"   🧩 Fragmentos: {total_chunks}")
            print(f"   📊 Tamaño: {pdf_path.stat().st_size / 1024:.1f} KB")
            
            return True
            
        except Exception as e:
            print(f"❌ Error cargando PDF {pdf_path}: {e}")
            return False
    
    def load_all_pdfs_in_directory(self, directory_path: Path, tags: List[str] = None) -> int:
        """Cargar todos los PDFs de un directorio"""
        if not directory_path.exists():
            print(f"❌ Directorio no encontrado: {directory_path}")
            return 0
        
        pdf_files = list(directory_path.glob("*.pdf"))
        if not pdf_files:
            print(f"⚠️ No se encontraron PDFs en: {directory_path}")
            return 0
        
        print(f"📁 Encontrados {len(pdf_files)} PDFs en {directory_path}")
        
        loaded_count = 0
        for pdf_file in pdf_files:
            if self.load_pdf(pdf_file, tags):
                loaded_count += 1
        
        print(f"✅ Cargados {loaded_count}/{len(pdf_files)} PDFs")
        return loaded_count
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Buscar en los documentos cargados"""
        query_lower = query.lower()
        results = []
        
        for chunk_id, chunk in self.chunks.items():
            if query_lower in chunk['content'].lower():
                doc = self.documents.get(chunk['document_id'])
                if doc:
                    relevance = chunk['content'].lower().count(query_lower)
                    results.append({
                        'document_title': doc['title'],
                        'page_number': chunk['page_number'],
                        'content': chunk['content'],
                        'relevance_score': relevance,
                        'source': 'pdf_database'
                    })
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de la base de datos"""
        total_docs = len(self.documents)
        total_chunks = len(self.chunks)
        
        # Calcular estadísticas por documento
        doc_stats = []
        for doc_id, doc in self.documents.items():
            doc_chunks = [c for c in self.chunks.values() if c['document_id'] == doc_id]
            doc_stats.append({
                'title': doc['title'],
                'pages': doc['pages'],
                'chunks': len(doc_chunks),
                'size_kb': doc['size_bytes'] / 1024
            })
        
        return {
            'total_documents': total_docs,
            'total_chunks': total_chunks,
            'average_chunks_per_doc': total_chunks / total_docs if total_docs > 0 else 0,
            'documents': doc_stats
        }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """Listar documentos disponibles"""
        return [
            {
                'id': doc_id,
                'title': doc['title'],
                'filename': doc['filename'],
                'pages': doc['pages'],
                'upload_date': doc['upload_date'],
                'tags': doc.get('tags', [])
            }
            for doc_id, doc in self.documents.items()
        ]


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="📄 Cargador Simple de PDFs")
    parser.add_argument("--file", "-f", help="Cargar un PDF específico")
    parser.add_argument("--directory", "-d", help="Cargar todos los PDFs de un directorio")
    parser.add_argument("--search", "-s", help="Buscar en documentos cargados")
    parser.add_argument("--list", "-l", action="store_true", help="Listar documentos")
    parser.add_argument("--stats", action="store_true", help="Mostrar estadísticas")
    parser.add_argument("--tags", nargs="+", help="Etiquetas para los documentos")
    
    args = parser.parse_args()
    
    loader = SimplePDFLoader()
    
    if args.file:
        pdf_path = Path(args.file)
        if loader.load_pdf(pdf_path, args.tags):
            print("✅ PDF cargado exitosamente")
        else:
            print("❌ Error cargando PDF")
    
    elif args.directory:
        dir_path = Path(args.directory)
        count = loader.load_all_pdfs_in_directory(dir_path, args.tags)
        print(f"✅ Cargados {count} PDFs")
    
    elif args.search:
        results = loader.search_documents(args.search)
        print(f"\n🔍 Resultados para '{args.search}':")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['document_title']} (página {result['page_number']})")
            print(f"   Relevancia: {result['relevance_score']}")
            print(f"   Contenido: {result['content'][:200]}...")
    
    elif args.list:
        documents = loader.list_documents()
        print(f"\n📚 Documentos disponibles ({len(documents)}):")
        for doc in documents:
            print(f"  • {doc['title']} ({doc['filename']})")
            print(f"    Páginas: {doc['pages']}, Fecha: {doc['upload_date']}")
            if doc['tags']:
                print(f"    Etiquetas: {', '.join(doc['tags'])}")
    
    elif args.stats:
        stats = loader.get_statistics()
        print(f"\n📊 Estadísticas:")
        print(f"  Documentos totales: {stats['total_documents']}")
        print(f"  Fragmentos totales: {stats['total_chunks']}")
        print(f"  Promedio fragmentos/doc: {stats['average_chunks_per_doc']:.1f}")
        
        if stats['documents']:
            print(f"\n📄 Documentos:")
            for doc in stats['documents']:
                print(f"  • {doc['title']}: {doc['pages']} páginas, {doc['chunks']} fragmentos, {doc['size_kb']:.1f} KB")
    
    else:
        print("📄 Cargador Simple de PDFs")
        print("Uso:")
        print("  python cargar_pdf_simple.py --file documento.pdf")
        print("  python cargar_pdf_simple.py --directory ./pdfs")
        print("  python cargar_pdf_simple.py --search 'término'")
        print("  python cargar_pdf_simple.py --list")
        print("  python cargar_pdf_simple.py --stats")


if __name__ == "__main__":
    main() 