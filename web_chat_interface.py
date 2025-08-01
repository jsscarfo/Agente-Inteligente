import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

# Configuración de directorios
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Crear directorios si no existen
TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(title="MLB Assistant Chat", version="1.0.0")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Configurar templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []
    confidence: float = 0.0
    processing_time: float = 0.0

class DocumentSearch:
    def __init__(self):
        self.documents_file = DATA_DIR / "documents.json"
        self.chunks_file = DATA_DIR / "chunks.json"
        self.documents = {}
        self.chunks = {}
        self.load_data()
    
    def load_data(self):
        """Cargar documentos y fragmentos desde archivos JSON"""
        try:
            if self.documents_file.exists():
                with open(self.documents_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
            
            if self.chunks_file.exists():
                with open(self.chunks_file, 'r', encoding='utf-8') as f:
                    self.chunks = json.load(f)
        except Exception as e:
            print(f"Error cargando datos: {e}")
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Buscar en los documentos usando búsqueda inteligente y flexible"""
        query_lower = query.lower()
        results = []
        seen_content = set()  # Para evitar contenido duplicado
        
        # Extraer palabras clave importantes de la consulta
        def extract_keywords(text):
            # Palabras comunes a ignorar
            stop_words = {
                'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'o', 'pero', 'si', 'no',
                'que', 'cual', 'quien', 'donde', 'cuando', 'como', 'por', 'para', 'con', 'sin',
                'sobre', 'entre', 'detras', 'delante', 'encima', 'debajo', 'dentro', 'fuera',
                'hacia', 'desde', 'hasta', 'despues', 'antes', 'durante', 'mientras', 'hableme',
                'hablame', 'cuentame', 'dime', 'explicame', 'informacion', 'sobre', 'acerca'
            }
            
            # Dividir en palabras y filtrar
            words = text.split()
            keywords = []
            for word in words:
                # Limpiar la palabra
                clean_word = ''.join(c for c in word if c.isalnum() or c in 'áéíóúñü')
                if clean_word and clean_word.lower() not in stop_words and len(clean_word) > 2:
                    keywords.append(clean_word.lower())
            return keywords
        
        # Palabras clave relacionadas para búsquedas más inteligentes
        related_keywords = {
            'jugador': ['corredor', 'player', 'runner', 'base'],
            'fantasma': ['ghost', 'phantom', 'invisible'],
            'corredor': ['runner', 'jugador', 'base', 'player'],
            'apuestas': ['betting', 'gambling', 'wagers', 'apostar', 'apuesta'],
            'drogas': ['drugs', 'substances', 'drug testing', 'doping', 'droga'],
            'tabaco': ['tobacco', 'smoking', 'cigarettes', 'nicotine', 'fumar'],
            'violencia': ['violence', 'abuse', 'aggression', 'domestic'],
            'domestica': ['domestic', 'violence', 'abuse', 'aggression'],
            'redes': ['social', 'media', 'twitter', 'facebook', 'instagram'],
            'sociales': ['social', 'media', 'networks', 'redes'],
            'novatadas': ['hazing', 'initiation', 'bullying', 'novato'],
            'robo': ['stealing', 'theft', 'sign', 'señales'],
            'señales': ['signs', 'stealing', 'robo', 'signals'],
            'regla': ['rule', 'reglas', 'rules'],
            '21': ['twenty one', 'twenty-one', 'rule 21'],
            '510': ['five ten', 'five-ten', 'rule 510'],
            'mlb': ['major league', 'baseball', 'liga mayor'],
            'beisbol': ['baseball', 'mlb', 'liga'],
            'liga': ['league', 'mlb', 'beisbol', 'baseball']
        }
        
        # Extraer palabras clave de la consulta
        query_keywords = extract_keywords(query_lower)
        
        # Construir términos de búsqueda
        search_terms = [query_lower]  # Búsqueda exacta original
        
        # Agregar palabras clave individuales
        for keyword in query_keywords:
            search_terms.append(keyword)
            
            # Agregar términos relacionados
            if keyword in related_keywords:
                search_terms.extend(related_keywords[keyword])
        
        # Agregar combinaciones de palabras clave
        if len(query_keywords) >= 2:
            for i in range(len(query_keywords)):
                for j in range(i + 1, min(i + 3, len(query_keywords))):
                    combined = ' '.join(query_keywords[i:j+1])
                    search_terms.append(combined)
        
        # Eliminar duplicados y términos muy cortos
        search_terms = list(set([term for term in search_terms if len(term) > 2]))
        
        for chunk_id, chunk_data in self.chunks.items():
            content = chunk_data.get('content', '').lower()
            content_text = chunk_data.get('content', '')
            
            # Buscar coincidencias con todos los términos
            best_match = None
            best_score = 0
            best_term = ""
            
            for term in search_terms:
                if term in content:
                    score = content.count(term) * 10  # Puntuación base
                    
                    # Bonus por coincidencia exacta de la consulta original
                    if term == query_lower:
                        score += 200
                    
                    # Bonus por términos más largos
                    score += len(term) * 5
                    
                    # Bonus por palabras clave importantes
                    if term in ['corredor fantasma', 'jugador fantasma', 'ghost runner']:
                        score += 100
                    
                    # Bonus por coincidencias múltiples de palabras clave
                    keyword_matches = sum(1 for keyword in query_keywords if keyword in content)
                    score += keyword_matches * 50
                    
                    # Penalización por contenido muy largo (preferir fragmentos más concisos)
                    if len(content_text) > 1000:
                        score -= 30
                    
                    if score > best_score:
                        best_score = score
                        best_match = term
                        best_term = term
            
            if best_match:
                # Obtener información del documento
                doc_id = chunk_data.get('document_id')
                doc_info = self.documents.get(doc_id, {})
                
                # Extraer contexto relevante más amplio
                query_pos = content_text.lower().find(best_match)
                start_idx = max(0, query_pos - 500)
                end_idx = min(len(content_text), query_pos + 800)
                context = content_text[start_idx:end_idx]
                
                # Limpiar y formatear el contexto
                context = context.strip()
                
                # Buscar el inicio de una oración completa
                if start_idx > 0:
                    # Buscar hacia atrás para encontrar el inicio de una oración
                    for i in range(start_idx, max(0, start_idx - 100), -1):
                        if content_text[i] in '.!?':
                            start_idx = i + 1
                            break
                
                # Buscar el final de una oración completa
                if end_idx < len(content_text):
                    # Buscar hacia adelante para encontrar el final de una oración
                    for i in range(end_idx, min(len(content_text), end_idx + 100)):
                        if content_text[i] in '.!?':
                            end_idx = i + 1
                            break
                
                context = content_text[start_idx:end_idx].strip()
                
                # Crear hash del contenido para evitar duplicados exactos
                content_hash = hash(context.lower())
                if content_hash in seen_content:
                    continue
                seen_content.add(content_hash)
                
                # Solo incluir resultados con puntuación mínima de relevancia
                if best_score >= 50:  # Umbral mínimo de relevancia
                    results.append({
                        'document_title': doc_info.get('title', 'Documento desconocido'),
                        'page_number': chunk_data.get('page_number', 1),
                        'content': context,
                        'relevance_score': best_score,
                        'doc_id': doc_id,
                        'matched_term': best_term
                    })
        
        # Ordenar por relevancia y limitar resultados
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:limit]
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de los documentos"""
        return {
            'total_documents': len(self.documents),
            'total_chunks': len(self.chunks),
            'documents': [
                {
                    'title': doc.get('title', 'Sin título'),
                    'pages': doc.get('pages', 0),
                    'chunks': doc.get('total_chunks', 0)
                }
                for doc in self.documents.values()
            ]
        }

# Instanciar el buscador de documentos
document_search = DocumentSearch()

@app.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
    """Interfaz principal del chat"""
    stats = document_search.get_document_stats()
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "stats": stats
    })

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Endpoint para procesar mensajes del chat"""
    import time
    start_time = time.time()
    
    try:
        # Buscar en documentos
        search_results = document_search.search_documents(chat_message.message, limit=2)
        
        # Generar respuesta basada en los resultados
        if search_results:
            # Generar respuesta personalizada y natural
            response_parts = []
            
            # Respuesta principal en primera persona
            response_parts.append("¡Hola! Te explico sobre lo que preguntas:")
            response_parts.append("")
            
            # Combinar información de múltiples resultados si es necesario
            all_content = []
            for result in search_results:
                content = result['content']
                clean_content = content.replace("...", "").strip()
                all_content.append(clean_content)
            
            # Usar el contenido real encontrado en los documentos
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
            confidence = 0.8 if len(search_results) > 0 else 0.3
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
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            response=response_text,
            sources=search_results,
            confidence=confidence,
            processing_time=processing_time
        )
        
    except Exception as e:
        return ChatResponse(
            response=f"❌ **Error:** {str(e)}",
            confidence=0.0,
            processing_time=time.time() - start_time
        )

@app.get("/api/stats")
async def get_stats():
    """Obtener estadísticas de documentos"""
    return document_search.get_document_stats()

@app.get("/api/documents")
async def get_documents():
    """Obtener lista de documentos disponibles"""
    return {
        "documents": [
            {
                "id": doc_id,
                "title": doc.get('title', 'Sin título'),
                "pages": doc.get('pages', 0),
                "chunks": doc.get('total_chunks', 0),
                "upload_date": doc.get('upload_date', '')
            }
            for doc_id, doc in document_search.documents.items()
        ]
    }

if __name__ == "__main__":
    print("🤖 MLB Assistant Chat - Iniciando...")
    print(f"📚 Documentos cargados: {len(document_search.documents)}")
    print(f"🧩 Fragmentos disponibles: {len(document_search.chunks)}")
    print("🌐 Servidor web iniciando en http://localhost:8080")
    
    uvicorn.run(
        "web_chat_interface:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    ) 