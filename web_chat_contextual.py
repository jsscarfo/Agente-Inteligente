"""
Web Chat Interface con Contextual Retrieval
Implementación mejorada basada en Anthropic's Contextual Retrieval
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import json
import os
from pathlib import Path

# Importar Contextual Retrieval
from contextual_retrieval import ContextualRetrieval

# Configuración de la aplicación
app = FastAPI(title="MLB Assistant Chat - Contextual Retrieval", version="2.0")
templates = Jinja2Templates(directory="templates")

# Modelos de datos
class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []
    confidence: float = 0.0
    processing_time: float = 0.0
    search_method: str = "contextual"

# Inicializar sistema de Contextual Retrieval
print("🤖 MLB Assistant Chat - Contextual Retrieval - Iniciando...")

# Verificar si existen datos contextualizados
contextual_data_file = "data/contextual_chunks.json"
if os.path.exists(contextual_data_file):
    print("📚 Cargando sistema Contextual Retrieval...")
    contextual_retrieval = ContextualRetrieval()
    
    if contextual_retrieval.load_data():
        # Cargar datos contextualizados si existen
        try:
            with open(contextual_data_file, 'r', encoding='utf-8') as f:
                contextual_data = json.load(f)
            
            # Reconstruir chunks contextualizados
            contextual_retrieval.contextual_chunks = []
            for chunk_data in contextual_data:
                from contextual_retrieval import ContextualChunk
                chunk = ContextualChunk(
                    original_content=chunk_data.get('original_content', ''),
                    contextualized_content=chunk_data.get('contextualized_content', ''),
                    document_id=chunk_data.get('document_id', ''),
                    document_title=chunk_data.get('document_title', ''),
                    page_number=chunk_data.get('page_number', 1),
                    chunk_id=chunk_data.get('chunk_id', ''),
                    context_summary=chunk_data.get('context_summary', ''),
                    embedding=chunk_data.get('embedding'),
                    bm25_score=chunk_data.get('bm25_score', 0.0),
                    rerank_score=chunk_data.get('rerank_score', 0.0)
                )
                contextual_retrieval.contextual_chunks.append(chunk)
            
            # Recrear índices
            if contextual_data and contextual_data[0].get('embedding'):
                contextual_retrieval.chunk_embeddings = [
                    chunk_data.get('embedding') for chunk_data in contextual_data
                ]
            
            # Recrear BM25
            contextual_retrieval.create_contextual_bm25()
            
            print("✅ Sistema Contextual Retrieval cargado")
            USE_CONTEXTUAL = True
            
        except Exception as e:
            print(f"⚠️ Error cargando datos contextualizados: {e}")
            USE_CONTEXTUAL = False
    else:
        USE_CONTEXTUAL = False
else:
    print("⚠️ No se encontraron datos contextualizados")
    USE_CONTEXTUAL = False

# Fallback al sistema básico si no hay contextual
if not USE_CONTEXTUAL:
    print("🔄 Usando sistema de búsqueda básico como fallback...")
    from web_chat_interface import DocumentSearch
    document_search = DocumentSearch()
    document_search.load_data()

# Estadísticas del sistema
def get_system_stats():
    if USE_CONTEXTUAL:
        stats = contextual_retrieval.get_stats()
        return {
            'total_documents': stats['total_documents'],
            'total_chunks': stats['total_contextual_chunks'],
            'has_embeddings': stats['has_embeddings'],
            'has_bm25': stats['has_bm25'],
            'has_openai': stats['has_openai'],
            'system_type': 'Contextual Retrieval',
            'features': [
                'Contextual Embeddings',
                'Contextual BM25',
                'Reranking',
                'Rank Fusion'
            ]
        }
    else:
        stats = document_search.get_document_stats()
        return {
            'total_documents': stats['total_documents'],
            'total_chunks': stats['total_chunks'],
            'has_embeddings': False,
            'has_bm25': True,
            'has_openai': False,
            'system_type': 'Basic Search',
            'features': [
                'Keyword Search',
                'Semantic Matching',
                'Content Scoring'
            ]
        }

@app.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
    """Interfaz principal del chat"""
    stats = get_system_stats()
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "stats": stats,
        "system_type": stats['system_type']
    })

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Endpoint para procesar mensajes del chat con Contextual Retrieval"""
    import time
    start_time = time.time()
    
    try:
        if USE_CONTEXTUAL:
            # Usar Contextual Retrieval
            print(f"🔍 Búsqueda contextual para: '{chat_message.message}'")
            
            # Búsqueda con Contextual Retrieval
            search_results = contextual_retrieval.search_contextual(
                chat_message.message, 
                limit=3, 
                use_reranking=True
            )
            
            # Generar respuesta basada en los resultados
            if search_results:
                # Generar respuesta personalizada y natural
                response_parts = []
                
                # Respuesta principal en primera persona
                response_parts.append("¡Hola! Te explico sobre lo que preguntas:")
                response_parts.append("")
                
                # Usar el contenido contextualizado
                all_content = []
                for result in search_results:
                    chunk = result['chunk']
                    # Usar contenido original pero con contexto mejorado
                    content = chunk.original_content
                    clean_content = content.replace("...", "").strip()
                    all_content.append(clean_content)
                
                # Combinar contenido
                combined_content = ' '.join(all_content)
                
                # Dividir en oraciones para mejor legibilidad
                sentences = combined_content.split('. ')
                formatted_sentences = []
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence and len(sentence) > 10:  # Solo oraciones con sentido
                        # Capitalizar la primera letra
                        if sentence and sentence[0].islower():
                            sentence = sentence[0].upper() + sentence[1:]
                        formatted_sentences.append(sentence)
                
                # Unir las oraciones formateadas
                if formatted_sentences:
                    response_parts.append('. '.join(formatted_sentences) + '.')
                else:
                    response_parts.append(combined_content)
                
                response_text = "\n".join(response_parts)
                confidence = 0.9 if len(search_results) > 0 else 0.3
                
                # Preparar fuentes para la respuesta
                sources = []
                for result in search_results:
                    chunk = result['chunk']
                    sources.append({
                        'document_title': chunk.document_title,
                        'page_number': chunk.page_number,
                        'content': chunk.original_content[:200] + "...",
                        'relevance_score': result.get('combined_score', 0),
                        'rerank_score': result.get('rerank_score', 0),
                        'context_summary': chunk.context_summary[:100] + "..."
                    })
                
            else:
                response_text = f"""❌ **No encontré información específica sobre:** '{chat_message.message}'

💡 **Consejos para mejorar tu búsqueda:**
• Intenta con términos más específicos
• Usa palabras clave relacionadas con el tema
• Pregunta sobre reglas específicas como 'Regla 21' o 'Regla 510'
• Consulta sobre temas como: apuestas, drogas, tabaco, violencia doméstica, redes sociales

🔍 **Ejemplos de búsquedas que funcionan:**
• "corredor fantasma"
• "reglas de apuestas"
• "política de drogas"
• "violencia doméstica"
• "redes sociales"
• "tabaco"
• "novatadas"

🎯 **Intenta reformular tu pregunta o usar términos más específicos.**"""
                confidence = 0.3
                sources = []
        
        else:
            # Fallback al sistema básico
            print(f"🔍 Búsqueda básica para: '{chat_message.message}'")
            
            search_results = document_search.search_documents(chat_message.message, limit=2)
            
            if search_results:
                response_parts = []
                response_parts.append("¡Hola! Te explico sobre lo que preguntas:")
                response_parts.append("")
                
                all_content = []
                for result in search_results:
                    content = result['content']
                    clean_content = content.replace("...", "").strip()
                    all_content.append(clean_content)
                
                combined_content = ' '.join(all_content)
                
                sentences = combined_content.split('. ')
                formatted_sentences = []
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence and len(sentence) > 10:
                        if sentence and sentence[0].islower():
                            sentence = sentence[0].upper() + sentence[1:]
                        formatted_sentences.append(sentence)
                
                if formatted_sentences:
                    response_parts.append('. '.join(formatted_sentences) + '.')
                else:
                    response_parts.append(combined_content)
                
                response_text = "\n".join(response_parts)
                confidence = 0.7
                sources = search_results
            else:
                response_text = f"""❌ **No encontré información específica sobre:** '{chat_message.message}'

💡 **Consejos para mejorar tu búsqueda:**
• Intenta con términos más específicos
• Usa palabras clave relacionadas con el tema
• Pregunta sobre reglas específicas como 'Regla 21' o 'Regla 510'
• Consulta sobre temas como: apuestas, drogas, tabaco, violencia doméstica, redes sociales

🔍 **Ejemplos de búsquedas que funcionan:**
• "corredor fantasma"
• "reglas de apuestas"
• "política de drogas"
• "violencia doméstica"
• "redes sociales"
• "tabaco"
• "novatadas"

🎯 **Intenta reformular tu pregunta o usar términos más específicos.**"""
                confidence = 0.3
                sources = []
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            response=response_text,
            sources=sources,
            confidence=confidence,
            processing_time=processing_time,
            search_method="contextual" if USE_CONTEXTUAL else "basic"
        )
        
    except Exception as e:
        return ChatResponse(
            response=f"❌ **Error:** {str(e)}",
            confidence=0.0,
            processing_time=time.time() - start_time,
            search_method="error"
        )

@app.get("/api/stats")
async def get_stats():
    """Obtener estadísticas del sistema"""
    return get_system_stats()

@app.get("/api/documents")
async def get_documents():
    """Obtener lista de documentos disponibles"""
    if USE_CONTEXTUAL:
        documents = []
        for doc_id, doc in contextual_retrieval.documents.items():
            chunks_count = len([c for c in contextual_retrieval.contextual_chunks if c.document_id == doc_id])
            documents.append({
                "id": doc_id,
                "title": doc.get('title', 'Sin título'),
                "pages": doc.get('pages', 0),
                "chunks": chunks_count,
                "contextualized": True
            })
        return {"documents": documents}
    else:
        return document_search.get_document_stats()

@app.get("/api/system-info")
async def get_system_info():
    """Obtener información detallada del sistema"""
    stats = get_system_stats()
    
    info = {
        "system_type": stats['system_type'],
        "features": stats['features'],
        "capabilities": {
            "contextual_embeddings": stats['has_embeddings'],
            "contextual_bm25": stats['has_bm25'],
            "reranking": stats['has_openai'],
            "rank_fusion": True
        },
        "performance": {
            "total_documents": stats['total_documents'],
            "total_chunks": stats['total_chunks'],
            "search_accuracy": "High" if USE_CONTEXTUAL else "Medium"
        }
    }
    
    return info

if __name__ == "__main__":
    import uvicorn
    
    stats = get_system_stats()
    print(f"📊 Sistema: {stats['system_type']}")
    print(f"📚 Documentos: {stats['total_documents']}")
    print(f"🧩 Fragmentos: {stats['total_chunks']}")
    print(f"🔧 Características: {', '.join(stats['features'])}")
    print(f"🌐 Servidor web iniciando en http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False) 