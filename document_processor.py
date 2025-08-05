#!/usr/bin/env python3
"""
📄 Document Processor - Procesador de documentos para MLB Assistant

Este script procesa documentos PDF y texto para extraer contenido
y prepararlo para el sistema de búsqueda.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️  PyPDF2 no está disponible. Los PDFs se procesarán como texto simple.")

class DocumentProcessor:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.documents_file = self.data_dir / "documents.json"
        self.chunks_file = self.data_dir / "chunks.json"
        
        # Cargar datos existentes
        self.documents = self.load_json(self.documents_file, {})
        self.chunks = self.load_json(self.chunks_file, {})
    
    def load_json(self, file_path: Path, default: Any) -> Any:
        """Cargar archivo JSON de forma segura"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error cargando {file_path}: {e}")
        return default
    
    def save_json(self, file_path: Path, data: Any):
        """Guardar datos en archivo JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando {file_path}: {e}")
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extraer texto de un archivo PDF"""
        if not PDF_AVAILABLE:
            return f"PDF no procesado: {pdf_path.name}"
        
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Página {page_num + 1} ---\n"
                        text += page_text + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error procesando PDF {pdf_path}: {e}")
            return f"Error procesando PDF: {str(e)}"
    
    def extract_text_from_txt(self, txt_path: Path) -> str:
        """Extraer texto de un archivo de texto"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error leyendo archivo de texto {txt_path}: {e}")
            return f"Error leyendo archivo: {str(e)}"
    
    def clean_text(self, text: str) -> str:
        """Limpiar y normalizar texto"""
        # Eliminar caracteres extraños
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', ' ', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        
        # Eliminar líneas vacías múltiples
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def split_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Dividir texto en fragmentos con superposición"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Si no es el final del texto, buscar un buen punto de corte
            if end < len(text):
                # Buscar el final de una oración
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Buscar el final de una palabra
                    word_end = text.rfind(' ', start, end)
                    if word_end > start + chunk_size // 2:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Mover al siguiente chunk con superposición
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_document(self, file_path: str, title: str = None) -> Dict[str, Any]:
        """Procesar un documento completo"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        # Usar el nombre del archivo como título si no se proporciona
        if not title:
            title = file_path.stem
        
        # Extraer texto según el tipo de archivo
        if file_path.suffix.lower() == '.pdf':
            raw_text = self.extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.txt', '.md']:
            raw_text = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Tipo de archivo no soportado: {file_path.suffix}")
        
        # Limpiar texto
        clean_text = self.clean_text(raw_text)
        
        # Dividir en fragmentos
        chunks = self.split_into_chunks(clean_text)
        
        # Generar ID único para el documento
        doc_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_path.stem}"
        
        # Guardar documento
        self.documents[doc_id] = {
            'title': title,
            'filename': file_path.name,
            'file_path': str(file_path),
            'upload_date': datetime.now().isoformat(),
            'total_chunks': len(chunks),
            'total_words': len(clean_text.split()),
            'file_size': file_path.stat().st_size
        }
        
        # Guardar fragmentos
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i:03d}"
            self.chunks[chunk_id] = {
                'content': chunk,
                'title': title,
                'document': doc_id,
                'page': 1,  # Simplificado por ahora
                'chunk_index': i,
                'word_count': len(chunk.split())
            }
        
        # Guardar datos
        self.save_json(self.documents_file, self.documents)
        self.save_json(self.chunks_file, self.chunks)
        
        return {
            'doc_id': doc_id,
            'title': title,
            'filename': file_path.name,
            'chunks_created': len(chunks),
            'total_words': len(clean_text.split()),
            'file_size': file_path.stat().st_size
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de documentos"""
        total_words = sum(doc.get('total_words', 0) for doc in self.documents.values())
        
        return {
            'total_documents': len(self.documents),
            'total_chunks': len(self.chunks),
            'total_words': total_words,
            'documents': [
                {
                    'id': doc_id,
                    'title': doc.get('title', 'Sin título'),
                    'filename': doc.get('filename', ''),
                    'upload_date': doc.get('upload_date', ''),
                    'chunks': doc.get('total_chunks', 0),
                    'words': doc.get('total_words', 0)
                }
                for doc_id, doc in self.documents.items()
            ]
        }
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Buscar en los documentos"""
        query_lower = query.lower()
        results = []
        seen_content = set()
        
        for chunk_id, chunk_data in self.chunks.items():
            content = chunk_data.get('content', '').lower()
            title = chunk_data.get('title', '').lower()
            
            # Buscar coincidencias
            if query_lower in content or query_lower in title:
                if content not in seen_content:
                    seen_content.add(content)
                    results.append({
                        'id': chunk_id,
                        'title': chunk_data.get('title', 'Sin título'),
                        'content': chunk_data.get('content', ''),
                        'document': chunk_data.get('document', ''),
                        'relevance': 0.9
                    })
        
        # Ordenar por relevancia y limitar resultados
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:limit]

def main():
    """Función principal para procesar documentos desde línea de comandos"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python document_processor.py <archivo> [título]")
        print("Ejemplo: python document_processor.py reglas_mlb.pdf 'Reglas de MLB 2024'")
        return
    
    file_path = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    
    processor = DocumentProcessor()
    
    try:
        result = processor.process_document(file_path, title)
        print(f"✅ Documento procesado exitosamente:")
        print(f"   Título: {result['title']}")
        print(f"   Archivo: {result['filename']}")
        print(f"   Fragmentos creados: {result['chunks_created']}")
        print(f"   Palabras totales: {result['total_words']}")
        
        # Mostrar estadísticas
        stats = processor.get_stats()
        print(f"\n📊 Estadísticas generales:")
        print(f"   Documentos totales: {stats['total_documents']}")
        print(f"   Fragmentos totales: {stats['total_chunks']}")
        print(f"   Palabras totales: {stats['total_words']}")
        
    except Exception as e:
        print(f"❌ Error procesando documento: {e}")

if __name__ == "__main__":
    main() 