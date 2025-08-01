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
            # Fallback sin IA - contexto básico
            return f"Document: {chunk.document_title} (Page {chunk.page_number}). "
        
        try:
            # Obtener contexto del documento completo
            doc_content = self.get_document_context(chunk.document_id)
            
            prompt = f"""<document> 
{doc_content}
</document> 
Here is the chunk we want to situate within the whole document 
<chunk> 
{chunk.original_content}
</chunk> 
Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else."""

            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.1
            )
            
            context = response.choices[0].message.content.strip()
            return context
            
        except Exception as e:
            print(f"⚠️ Error generando contexto para chunk {chunk.chunk_id}: {e}")
            # Fallback
            return f"Document: {chunk.document_title} (Page {chunk.page_number}). "
    
    def get_document_context(self, doc_id: str) -> str:
        """Obtener contexto del documento completo"""
        doc_info = self.documents.get(doc_id, {})
        
        # Buscar todos los chunks del documento
        doc_chunks = [chunk for chunk in self.contextual_chunks if chunk.document_id == doc_id]
        
        # Crear resumen del documento
        all_content = ' '.join([chunk.original_content for chunk in doc_chunks])
        
        # Limitar a 4000 tokens para el contexto
        if len(all_content) > 16000:  # ~4000 tokens
            all_content = all_content[:16000] + "..."
        
        return f"Title: {doc_info.get('title', 'Unknown')}. Content: {all_content}"
    
    def contextualize_all_chunks(self):
        """Contextualizar todos los chunks"""
        print("🔄 Iniciando contextualización de chunks...")
        
        for i, chunk in enumerate(self.contextual_chunks):
            if i % 10 == 0:
                print(f"📝 Procesando chunk {i+1}/{len(self.contextual_chunks)}")
            
            # Generar contexto
            context = self.generate_context_for_chunk(chunk)
            chunk.context_summary = context
            
            # Crear contenido contextualizado
            chunk.contextualized_content = f"{context} {chunk.original_content}"
        
        print("✅ Contextualización completada")
    
    def create_contextual_embeddings(self):
        """Crear embeddings contextualizados"""
        print("🧠 Creando embeddings contextualizados...")
        
        if not self.openai_api_key:
            print("⚠️ No hay API key de OpenAI. Usando embeddings simulados.")
            # Embeddings simulados para demo
            self.chunk_embeddings = [
                np.random.rand(1536).tolist() for _ in self.contextual_chunks
            ]
            return
        
        try:
            self.chunk_embeddings = []
            
            for i, chunk in enumerate(self.contextual_chunks):
                if i % 10 == 0:
                    print(f"🔢 Embedding chunk {i+1}/{len(self.contextual_chunks)}")
                
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                
                response = client.embeddings.create(
                    input=chunk.contextualized_content,
                    model="text-embedding-ada-002"
                )
                
                embedding = response.data[0].embedding
                chunk.embedding = embedding
                self.chunk_embeddings.append(embedding)
            
            print("✅ Embeddings contextualizados creados")
            
        except Exception as e:
            print(f"❌ Error creando embeddings: {e}")
    
    def create_contextual_bm25(self):
        """Crear índice BM25 contextualizado"""
        print("🔍 Creando índice BM25 contextualizado...")
        
        # Usar contenido contextualizado para BM25
        contextualized_texts = [chunk.contextualized_content for chunk in self.contextual_chunks]
        
        self.tfidf_vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            max_features=10000
        )
        
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(contextualized_texts)
        print("✅ Índice BM25 contextualizado creado")
    
    def search_contextual(self, query: str, limit: int = 20, use_reranking: bool = True) -> List[Dict[str, Any]]:
        """Búsqueda contextual combinando embeddings y BM25"""
        print(f"🔍 Búsqueda contextual para: '{query}'")
        
        # 1. Búsqueda inicial con embeddings contextualizados
        embedding_results = self.search_embeddings(query, limit=150)
        
        # 2. Búsqueda con BM25 contextualizado
        bm25_results = self.search_bm25(query, limit=150)
        
        # 3. Combinar resultados
        combined_results = self.combine_results(embedding_results, bm25_results)
        
        # 4. Reranking (opcional)
        if use_reranking and self.openai_api_key:
            combined_results = self.rerank_results(query, combined_results, limit)
        else:
            combined_results = combined_results[:limit]
        
        return combined_results
    
    def search_embeddings(self, query: str, limit: int = 150) -> List[Dict[str, Any]]:
        """Búsqueda por similitud de embeddings contextualizados"""
        if not self.chunk_embeddings:
            return []
        
        # Crear embedding de la query
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            query_embedding = client.embeddings.create(
                input=query,
                model="text-embedding-ada-002"
            ).data[0].embedding
        except:
            # Fallback: embedding simulado
            query_embedding = np.random.rand(1536).tolist()
        
        # Calcular similitudes
        similarities = []
        for i, chunk_embedding in enumerate(self.chunk_embeddings):
            similarity = cosine_similarity(
                [query_embedding], [chunk_embedding]
            )[0][0]
            similarities.append((i, similarity))
        
        # Ordenar por similitud
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in similarities[:limit]:
            chunk = self.contextual_chunks[idx]
            results.append({
                'chunk': chunk,
                'score': score,
                'method': 'embedding'
            })
        
        return results
    
    def search_bm25(self, query: str, limit: int = 150) -> List[Dict[str, Any]]:
        """Búsqueda BM25 contextualizada"""
        if self.tfidf_matrix is None:
            return []
        
        # Vectorizar query
        query_vector = self.tfidf_vectorizer.transform([query])
        
        # Calcular similitudes
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Obtener top resultados
        top_indices = similarities.argsort()[-limit:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                chunk = self.contextual_chunks[idx]
                results.append({
                    'chunk': chunk,
                    'score': float(similarities[idx]),
                    'method': 'bm25'
                })
        
        return results
    
    def combine_results(self, embedding_results: List[Dict], bm25_results: List[Dict]) -> List[Dict[str, Any]]:
        """Combinar resultados de embeddings y BM25 usando rank fusion"""
        # Crear diccionario de scores combinados
        combined_scores = defaultdict(lambda: {'embedding': 0, 'bm25': 0, 'chunk': None})
        
        # Procesar resultados de embeddings
        for i, result in enumerate(embedding_results):
            chunk_id = result['chunk'].chunk_id
            combined_scores[chunk_id]['embedding'] = result['score']
            combined_scores[chunk_id]['chunk'] = result['chunk']
        
        # Procesar resultados de BM25
        for i, result in enumerate(bm25_results):
            chunk_id = result['chunk'].chunk_id
            combined_scores[chunk_id]['bm25'] = result['score']
            if combined_scores[chunk_id]['chunk'] is None:
                combined_scores[chunk_id]['chunk'] = result['chunk']
        
        # Calcular score combinado (promedio ponderado)
        combined_results = []
        for chunk_id, scores in combined_scores.items():
            if scores['chunk']:
                # Normalizar scores y combinar
                combined_score = (scores['embedding'] * 0.6 + scores['bm25'] * 0.4)
                combined_results.append({
                    'chunk': scores['chunk'],
                    'combined_score': combined_score,
                    'embedding_score': scores['embedding'],
                    'bm25_score': scores['bm25']
                })
        
        # Ordenar por score combinado
        combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return combined_results
    
    def rerank_results(self, query: str, results: List[Dict], limit: int = 20) -> List[Dict[str, Any]]:
        """Reranking de resultados usando modelo especializado"""
        if not self.openai_api_key:
            return results[:limit]
        
        print(f"🏆 Reranking {len(results)} resultados...")
        
        try:
            reranked_results = []
            
            for result in results:
                chunk = result['chunk']
                
                # Prompt para reranking
                rerank_prompt = f"""Query: {query}

Document chunk: {chunk.contextualized_content}

Rate the relevance of this document chunk to the query on a scale of 0-10, where:
0 = Completely irrelevant
5 = Somewhat relevant
10 = Highly relevant

Consider:
- Does the chunk directly answer the query?
- Is the information specific and accurate?
- Is the context helpful for understanding?

Respond with only the number (0-10):"""

                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": rerank_prompt}],
                    max_tokens=5,
                    temperature=0.1
                )
                
                try:
                    rerank_score = float(response.choices[0].message.content.strip())
                except:
                    rerank_score = result['combined_score'] * 10  # Fallback
                
                result['rerank_score'] = rerank_score
                reranked_results.append(result)
            
            # Ordenar por rerank score
            reranked_results.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            print("✅ Reranking completado")
            return reranked_results[:limit]
            
        except Exception as e:
            print(f"⚠️ Error en reranking: {e}")
            return results[:limit]
    
    def save_contextualized_data(self, output_file: str = "data/contextual_chunks.json"):
        """Guardar chunks contextualizados"""
        try:
            contextual_data = []
            for chunk in self.contextual_chunks:
                contextual_data.append({
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
                })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(contextual_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Datos contextualizados guardados en {output_file}")
            
        except Exception as e:
            print(f"❌ Error guardando datos: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema contextual"""
        return {
            'total_documents': len(self.documents),
            'total_contextual_chunks': len(self.contextual_chunks),
            'has_embeddings': len(self.chunk_embeddings) > 0,
            'has_bm25': self.tfidf_matrix is not None,
            'has_openai': bool(self.openai_api_key),
            'documents': [
                {
                    'title': doc.get('title', 'Sin título'),
                    'pages': doc.get('pages', 0),
                    'chunks': len([c for c in self.contextual_chunks if c.document_id == doc_id])
                }
                for doc_id, doc in self.documents.items()
            ]
        }

def main():
    """Función principal para probar Contextual Retrieval"""
    print("🚀 Iniciando Contextual Retrieval...")
    
    # Inicializar sistema
    cr = ContextualRetrieval()
    
    # Cargar datos
    if not cr.load_data():
        print("❌ Error cargando datos")
        return
    
    # Contextualizar chunks
    cr.contextualize_all_chunks()
    
    # Crear embeddings contextualizados
    cr.create_contextual_embeddings()
    
    # Crear BM25 contextualizado
    cr.create_contextual_bm25()
    
    # Guardar datos
    cr.save_contextualized_data()
    
    # Mostrar estadísticas
    stats = cr.get_stats()
    print(f"\n📊 Estadísticas del sistema:")
    print(f"   Documentos: {stats['total_documents']}")
    print(f"   Chunks contextualizados: {stats['total_contextual_chunks']}")
    print(f"   Embeddings: {'✅' if stats['has_embeddings'] else '❌'}")
    print(f"   BM25: {'✅' if stats['has_bm25'] else '❌'}")
    print(f"   OpenAI: {'✅' if stats['has_openai'] else '❌'}")
    
    # Prueba de búsqueda
    test_query = "corredor fantasma"
    print(f"\n🔍 Probando búsqueda: '{test_query}'")
    
    results = cr.search_contextual(test_query, limit=5, use_reranking=True)
    
    print(f"\n📋 Resultados encontrados: {len(results)}")
    for i, result in enumerate(results[:3]):
        chunk = result['chunk']
        print(f"\n{i+1}. {chunk.document_title} (Página {chunk.page_number})")
        print(f"   Score combinado: {result.get('combined_score', 0):.3f}")
        print(f"   Score rerank: {result.get('rerank_score', 0):.1f}")
        print(f"   Contexto: {chunk.context_summary[:100]}...")
        print(f"   Contenido: {chunk.original_content[:200]}...")

if __name__ == "__main__":
    main() 