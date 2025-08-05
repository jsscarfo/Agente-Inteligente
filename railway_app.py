#!/usr/bin/env python3
"""
🤖 MLB Assistant Chat - Aplicación para Railway

Esta aplicación está optimizada para despliegue en Railway.
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configuración de directorios
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Crear directorios si no existen
DATA_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(title="MLB Assistant Chat", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        """Buscar en los documentos usando búsqueda inteligente"""
        query_lower = query.lower()
        results = []
        seen_content = set()
        
        # Buscar en los fragmentos
        for chunk_id, chunk_data in self.chunks.items():
            content = chunk_data.get('content', '').lower()
            title = chunk_data.get('title', '').lower()
            
            # Verificar si la consulta aparece en el contenido
            if query_lower in content or query_lower in title:
                if content not in seen_content:
                    seen_content.add(content)
                    results.append({
                        'id': chunk_id,
                        'title': chunk_data.get('title', 'Sin título'),
                        'content': chunk_data.get('content', ''),
                        'page': chunk_data.get('page', 0),
                        'document': chunk_data.get('document', ''),
                        'relevance': 0.9
                    })
        
        # Ordenar por relevancia y limitar resultados
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:limit]
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de documentos"""
        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "documents": [
                {
                    "id": doc_id,
                    "title": doc.get('title', 'Sin título'),
                    "pages": doc.get('pages', 0),
                    "chunks": doc.get('total_chunks', 0)
                }
                for doc_id, doc in self.documents.items()
            ]
        }

# Instancia global del buscador de documentos
document_search = DocumentSearch()

@app.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
    """Interfaz principal del chat"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MLB Assistant Chat</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { background: #1e3a8a; color: white; padding: 20px; border-radius: 10px 10px 0 0; }
            .chat-container { padding: 20px; height: 400px; overflow-y: auto; border-bottom: 1px solid #eee; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user-message { background: #e3f2fd; margin-left: 20%; }
            .bot-message { background: #f3e5f5; margin-right: 20%; }
            .input-container { padding: 20px; display: flex; }
            .input-container input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-right: 10px; }
            .input-container button { padding: 10px 20px; background: #1e3a8a; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .input-container button:hover { background: #1e40af; }
            .stats { padding: 10px; background: #f8f9fa; border-radius: 0 0 10px 10px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 MLB Assistant Chat</h1>
                <p>Asistente especializado en reglas de MLB</p>
            </div>
            <div class="chat-container" id="chatContainer">
                <div class="message bot-message">
                    ¡Hola! Soy tu asistente especializado en reglas de MLB. ¿En qué puedo ayudarte?
                </div>
            </div>
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="Escribe tu pregunta..." onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">Enviar</button>
            </div>
            <div class="stats" id="stats">
                Cargando estadísticas...
            </div>
        </div>
        
        <script>
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;
            
                // Agregar mensaje del usuario
                addMessage(message, 'user');
            input.value = '';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: message})
                });
                
                const data = await response.json();
                    addMessage(data.response, 'bot');
                } catch (error) {
                    addMessage('Error: ' + error.message, 'bot');
                }
            }
            
            function addMessage(text, sender) {
                const container = document.getElementById('chatContainer');
                const div = document.createElement('div');
                div.className = `message ${sender}-message`;
                div.innerHTML = text;
                container.appendChild(div);
                container.scrollTop = container.scrollHeight;
            }
            
            // Cargar estadísticas
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    document.getElementById('stats').innerHTML = 
                        `Documentos: ${data.total_documents} | Fragmentos: ${data.total_chunks}`;
                } catch (error) {
                    document.getElementById('stats').innerHTML = 'Error cargando estadísticas';
                }
            }
            
            loadStats();
        </script>
    </body>
    </html>
    """)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Endpoint para procesar mensajes del chat"""
    start_time = time.time()
    
    try:
        # Buscar en documentos
        search_results = document_search.search_documents(chat_message.message, limit=3)
        
        if search_results:
            # Construir respuesta basada en los resultados
            response_parts = []
            response_parts.append(f"✅ **Encontré información sobre:** '{chat_message.message}'")
            response_parts.append("")
            
            # Procesar contenido encontrado
            all_content = []
            for result in search_results:
                content = result['content']
                clean_content = content.replace("...", "").strip()
                all_content.append(clean_content)
            
            # Usar el contenido real encontrado
            combined_content = ' '.join(all_content)
            
            # Dividir en oraciones para mejor legibilidad
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

@app.get("/api/health")
async def health_check():
    """Health check para Railway"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "documents_loaded": len(document_search.documents),
        "chunks_loaded": len(document_search.chunks)
    }

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
    
    # Obtener puerto de Railway o usar 8080 por defecto
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Servidor web iniciando en puerto {port}")
    
    uvicorn.run(
        "railway_app:app",
        host="0.0.0.0",
        port=port,
        reload=False
    ) 