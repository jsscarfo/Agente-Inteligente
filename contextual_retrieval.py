"""
Contextual Retrieval Implementation
Based on Anthropic's Contextual Retrieval approach
"""

import json
import hashlib
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ContextualChunk:
    """Chunk con contexto añadido"""
    original_content: str
    contextualized_content: str
    document_id: str
    document_title: str
    page_number: int
    chunk_id: str
    context_summary: str
    embedding: Optional[List[float]] = None
    bm25_score: float = 0.0
    rerank_score: float = 0.0

class ContextualRetrieval:
    """Sistema de Contextual Retrieval basado en Anthropic"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        self.documents = {}
        self.contextual_chunks = []
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.chunk_embeddings = []
        
        # Configuración
        self.chunk_size = 800  # tokens
        self.chunk_overlap = 100  # tokens
        self.context_length = 100  # tokens para contexto
        
    def load_data(self, documents_file: str = "data/documents.json", 
                  chunks_file: str = "data/chunks.json"):
        """Cargar documentos y chunks existentes"""
        try:
            with open(documents_file, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks_data = json.load(f)
            
            print(f"📚 Documentos cargados: {len(self.documents)}")
            print(f"🧩 Chunks originales: {len(chunks_data)}")
            
            # Convertir a ContextualChunks
            self.contextual_chunks = []
            for chunk_id, chunk_data in chunks_data.items():
                # El formato es {chunk_id: chunk_data}
                doc_id = chunk_data.get('document_id', 'unknown')
                doc_info = self.documents.get(doc_id, {})
                
                # Verificar que doc_info sea un diccionario
                if not isinstance(doc_info, dict):
                    doc_info = {}
                
                chunk = ContextualChunk(
                    original_content=chunk_data.get('content', ''),
                    contextualized_content='',  # Se llenará después
                    document_id=doc_id,
                    document_title=doc_info.get('title', 'Documento desconocido'),
                    page_number=chunk_data.get('page_number', 1),
                    chunk_id=chunk_id,
                    context_summary=''
                )
                self.contextual_chunks.append(chunk)
            
            print(f"✅ Chunks convertidos a formato contextual")
            
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return False
        
        return True
    
    def generate_context_for_chunk(self, chunk: ContextualChunk) -> str:
        """Generar contexto específico para un chunk usando Claude"""
        if not self.openai_api_key:
            # Fallback sin API
            return f"Contexto del documento '{chunk.document_title}', página {chunk.page_number}"
        
        try:
            # Obtener contexto del documento
            doc_context = self.get_document_context(chunk.document_id)
            
            prompt = f"""
            Documento: {chunk.document_title}
            Contexto del documento: {doc_context}
            Página: {chunk.page_number}
            
            Contenido del chunk:
            {chunk.original_content}
            
            Genera un contexto breve (máximo 100 palabras) que ayude a entender este fragmento específico del documento.
            El contexto debe incluir información sobre el tema general, el propósito del documento y el contexto específico de esta sección.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️ Error generando contexto: {e}")
            return f"Contexto del documento '{chunk.document_title}', página {chunk.page_number}"
    
    def get_document_context(self, doc_id: str) -> str:
        """Obtener contexto general del documento"""
        doc_info = self.documents.get(doc_id, {})
        if not doc_info:
            return "Documento desconocido"
        
        # Construir contexto básico
        context_parts = []
        if doc_info.get('title'):
            context_parts.append(f"Título: {doc_info['title']}")
        if doc_info.get('author'):
            context_parts.append(f"Autor: {doc_info['author']}")
        if doc_info.get('subject'):
            context_parts.append(f"Tema: {doc_info['subject']}")
        if doc_info.get('tags'):
            context_parts.append(f"Etiquetas: {', '.join(doc_info['tags'])}")
        
        return " | ".join(context_parts) if context_parts else "Sin contexto disponible"
    
    def contextualize_all_chunks(self):
        """Contextualizar todos los chunks"""
        print("🔄 Contextualizando chunks...")
        
        for i, chunk in enumerate(self.contextual_chunks):
            if i % 10 == 0:
                print(f"  Procesando chunk {i+1}/{len(self.contextual_chunks)}")
            
            # Generar contexto
            context = self.generate_context_for_chunk(chunk)
            chunk.context_summary = context
            
            # Crear contenido contextualizado
            chunk.contextualized_content = f"""
            Contexto: {context}
            
            Contenido:
            {chunk.original_content}
            """
        
        print(f"✅ {len(self.contextual_chunks)} chunks contextualizados")
    
    def create_contextual_embeddings(self):
        """Crear embeddings para el contenido contextualizado"""
        if not self.openai_api_key:
            print("⚠️ No hay API key de OpenAI, saltando embeddings")
            return
        
        print("🔍 Creando embeddings contextuales...")
        
        try:
            # Preparar textos para embedding
            texts = [chunk.contextualized_content for chunk in self.contextual_chunks]
            
            # Crear embeddings en lotes
            batch_size = 10
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                
                response = openai.Embedding.create(
                    input=batch_texts,
                    model="text-embedding-ada-002"
                )
                
                batch_embeddings = [item['embedding'] for item in response['data']]
                all_embeddings.extend(batch_embeddings)
                
                print(f"  Embeddings creados: {len(all_embeddings)}/{len(texts)}")
            
            # Asignar embeddings a chunks
            for chunk, embedding in zip(self.contextual_chunks, all_embeddings):
                chunk.embedding = embedding
            
            self.chunk_embeddings = all_embeddings
            print(f"✅ {len(all_embeddings)} embeddings creados")
            
        except Exception as e:
            print(f"❌ Error creando embeddings: {e}")
    
    def create_contextual_bm25(self):
        """Crear índice BM25 para búsqueda contextual"""
        print("📊 Creando índice BM25 contextual...")
        
        try:
            # Preparar textos para BM25
            texts = [chunk.contextualized_content for chunk in self.contextual_chunks]
            
            # Crear vectorizador TF-IDF
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=10000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.9
            )
            
            # Crear matriz TF-IDF
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            print(f"✅ Índice BM25 creado con {self.tfidf_matrix.shape[1]} características")
            
        except Exception as e:
            print(f"❌ Error creando BM25: {e}")
    
    def search_contextual(self, query: str, limit: int = 20, use_reranking: bool = True) -> List[Dict[str, Any]]:
        """Búsqueda contextual combinando embeddings y BM25"""
        print(f"🔍 Búsqueda contextual: '{query}'")
        
        # Búsqueda por embeddings
        embedding_results = self.search_embeddings(query, limit=150)
        
        # Búsqueda por BM25
        bm25_results = self.search_bm25(query, limit=150)
        
        # Combinar resultados
        combined_results = self.combine_results(embedding_results, bm25_results)
        
        # Re-ranking si está habilitado
        if use_reranking and self.openai_api_key:
            combined_results = self.rerank_results(query, combined_results, limit)
        
        return combined_results[:limit]
    
    def search_embeddings(self, query: str, limit: int = 150) -> List[Dict[str, Any]]:
        """Búsqueda por similitud de embeddings"""
        if not self.chunk_embeddings:
            return []
        
        try:
            # Crear embedding de la consulta
            query_embedding = openai.Embedding.create(
                input=[query],
                model="text-embedding-ada-002"
            )['data'][0]['embedding']
            
            # Calcular similitudes
            similarities = []
            for i, chunk_embedding in enumerate(self.chunk_embeddings):
                similarity = cosine_similarity(
                    [query_embedding], 
                    [chunk_embedding]
                )[0][0]
                similarities.append((i, similarity))
            
            # Ordenar por similitud
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Crear resultados
            results = []
            for i, similarity in similarities[:limit]:
                chunk = self.contextual_chunks[i]
                results.append({
                    'chunk_id': chunk.chunk_id,
                    'document_title': chunk.document_title,
                    'page_number': chunk.page_number,
                    'content': chunk.original_content,
                    'contextualized_content': chunk.contextualized_content,
                    'context_summary': chunk.context_summary,
                    'score': similarity,
                    'method': 'embeddings'
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error en búsqueda por embeddings: {e}")
            return []
    
    def search_bm25(self, query: str, limit: int = 150) -> List[Dict[str, Any]]:
        """Búsqueda por BM25"""
        if self.tfidf_matrix is None:
            return []
        
        try:
            # Vectorizar consulta
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calcular similitudes
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Obtener índices ordenados
            indices = similarities.argsort()[::-1]
            
            # Crear resultados
            results = []
            for i in indices[:limit]:
                if similarities[i] > 0:
                    chunk = self.contextual_chunks[i]
                    results.append({
                        'chunk_id': chunk.chunk_id,
                        'document_title': chunk.document_title,
                        'page_number': chunk.page_number,
                        'content': chunk.original_content,
                        'contextualized_content': chunk.contextualized_content,
                        'context_summary': chunk.context_summary,
                        'score': float(similarities[i]),
                        'method': 'bm25'
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Error en búsqueda BM25: {e}")
            return []
    
    def combine_results(self, embedding_results: List[Dict], bm25_results: List[Dict]) -> List[Dict[str, Any]]:
        """Combinar resultados de embeddings y BM25"""
        # Crear diccionario de resultados combinados
        combined = {}
        
        # Procesar resultados de embeddings
        for result in embedding_results:
            chunk_id = result['chunk_id']
            if chunk_id not in combined:
                combined[chunk_id] = result.copy()
                combined[chunk_id]['embedding_score'] = result['score']
                combined[chunk_id]['bm25_score'] = 0.0
            else:
                combined[chunk_id]['embedding_score'] = result['score']
        
        # Procesar resultados de BM25
        for result in bm25_results:
            chunk_id = result['chunk_id']
            if chunk_id not in combined:
                combined[chunk_id] = result.copy()
                combined[chunk_id]['embedding_score'] = 0.0
                combined[chunk_id]['bm25_score'] = result['score']
            else:
                combined[chunk_id]['bm25_score'] = result['score']
        
        # Calcular score combinado
        for result in combined.values():
            # Normalizar scores (0-1)
            embedding_norm = min(result['embedding_score'], 1.0)
            bm25_norm = min(result['bm25_score'], 1.0)
            
            # Score combinado (promedio ponderado)
            result['combined_score'] = 0.6 * embedding_norm + 0.4 * bm25_norm
            result['score'] = result['combined_score']
        
        # Ordenar por score combinado
        combined_list = list(combined.values())
        combined_list.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return combined_list
    
    def rerank_results(self, query: str, results: List[Dict], limit: int = 20) -> List[Dict[str, Any]]:
        """Re-ranking usando LLM"""
        if not self.openai_api_key or not results:
            return results[:limit]
        
        try:
            print(f"🔄 Re-ranking {len(results)} resultados...")
            
            # Preparar prompt para re-ranking
            prompt = f"""
            Consulta: {query}
            
            Evalúa la relevancia de cada resultado (0-10) basándote en:
            1. Relevancia directa a la consulta
            2. Calidad del contexto
            3. Completitud de la información
            
            Resultados:
            """
            
            for i, result in enumerate(results[:50]):  # Limitar a 50 para el prompt
                prompt += f"""
            {i+1}. Documento: {result['document_title']}
                Página: {result['page_number']}
                Contexto: {result['context_summary']}
                Contenido: {result['content'][:200]}...
                Score actual: {result['score']:.3f}
                """
            
            prompt += """
            Proporciona solo una lista de números (1-50) ordenados por relevancia, separados por comas.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )
            
            # Parsear respuesta
            try:
                ranked_indices = [
                    int(x.strip()) - 1 
                    for x in response.choices[0].message.content.split(',')
                    if x.strip().isdigit()
                ]
                
                # Reordenar resultados
                reranked_results = []
                for idx in ranked_indices:
                    if 0 <= idx < len(results):
                        reranked_results.append(results[idx])
                
                # Añadir resultados no incluidos en el re-ranking
                reranked_ids = {r['chunk_id'] for r in reranked_results}
                for result in results:
                    if result['chunk_id'] not in reranked_ids:
                        reranked_results.append(result)
                
                print(f"✅ Re-ranking completado")
                return reranked_results[:limit]
                
            except Exception as e:
                print(f"⚠️ Error parseando re-ranking: {e}")
                return results[:limit]
                
        except Exception as e:
            print(f"❌ Error en re-ranking: {e}")
            return results[:limit]
    
    def save_contextualized_data(self, output_file: str = "data/contextual_chunks.json"):
        """Guardar datos contextualizados"""
        try:
            data = []
            for chunk in self.contextual_chunks:
                chunk_data = {
                    'chunk_id': chunk.chunk_id,
                    'document_id': chunk.document_id,
                    'document_title': chunk.document_title,
                    'page_number': chunk.page_number,
                    'original_content': chunk.original_content,
                    'contextualized_content': chunk.contextualized_content,
                    'context_summary': chunk.context_summary,
                    'embedding': chunk.embedding,
                    'bm25_score': chunk.bm25_score,
                    'rerank_score': chunk.rerank_score
                }
                data.append(chunk_data)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Datos contextualizados guardados en {output_file}")
            
        except Exception as e:
            print(f"❌ Error guardando datos: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        return {
            'total_chunks': len(self.contextual_chunks),
            'total_documents': len(self.documents),
            'chunks_with_embeddings': sum(1 for c in self.contextual_chunks if c.embedding is not None),
            'chunks_with_context': sum(1 for c in self.contextual_chunks if c.context_summary),
            'has_bm25_index': self.tfidf_matrix is not None,
            'bm25_features': self.tfidf_matrix.shape[1] if self.tfidf_matrix is not None else 0
        }


def main():
    """Función principal de demostración"""
    print("🔍 Contextual Retrieval System")
    print("=" * 50)
    
    # Inicializar sistema
    retrieval = ContextualRetrieval()
    
    # Cargar datos
    if not retrieval.load_data():
        print("❌ No se pudieron cargar los datos")
        return
    
    # Contextualizar chunks
    retrieval.contextualize_all_chunks()
    
    # Crear embeddings
    retrieval.create_contextual_embeddings()
    
    # Crear BM25
    retrieval.create_contextual_bm25()
    
    # Guardar datos
    retrieval.save_contextualized_data()
    
    # Mostrar estadísticas
    stats = retrieval.get_stats()
    print(f"\n📊 Estadísticas:")
    print(f"  Chunks totales: {stats['total_chunks']}")
    print(f"  Documentos: {stats['total_documents']}")
    print(f"  Chunks con embeddings: {stats['chunks_with_embeddings']}")
    print(f"  Chunks con contexto: {stats['chunks_with_context']}")
    print(f"  Índice BM25: {'Sí' if stats['has_bm25_index'] else 'No'}")
    print(f"  Características BM25: {stats['bm25_features']}")
    
    # Demostrar búsqueda
    test_queries = [
        "¿Qué es la inteligencia artificial?",
        "Explica el machine learning",
        "¿Cómo funciona el deep learning?"
    ]
    
    print(f"\n🔍 Pruebas de búsqueda:")
    for query in test_queries:
        print(f"\nConsulta: {query}")
        results = retrieval.search_contextual(query, limit=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['document_title']} (página {result['page_number']})")
            print(f"     Score: {result['score']:.3f}")
            print(f"     Contexto: {result['context_summary'][:100]}...")


if __name__ == "__main__":
    main() 