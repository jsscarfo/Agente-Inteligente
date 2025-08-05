#!/usr/bin/env python3
"""
🤖 MLB Assistant Chat - Aplicación para Railway con PostgreSQL

Esta aplicación está optimizada para despliegue en Railway y usa PostgreSQL
como base de datos principal.
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuración de directorios
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "data" / "uploads"

# Crear directorios si no existen
DATA_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

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

class PostgreSQLDatabase:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL no encontrada en variables de entorno")
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        return psycopg2.connect(self.database_url)
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Buscar documentos usando búsqueda de texto completo"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT c.id, c.content, c.title, c.document_id,
                               ts_rank(to_tsvector('spanish', c.content), plainto_tsquery('spanish', %s)) as relevance
                        FROM chunks c
                        WHERE to_tsvector('spanish', c.content) @@ plainto_tsquery('spanish', %s)
                        ORDER BY relevance DESC
                        LIMIT %s
                    """, (query, query, limit))
                    
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            return []
    
    def add_document(self, doc_id: str, title: str, filename: str, content: str) -> int:
        """Agregar un nuevo documento"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Dividir contenido en fragmentos
                    chunks = self.split_content_into_chunks(content)
                    
                    # Insertar documento
                    cursor.execute("""
                        INSERT INTO documents (id, title, filename, upload_date, total_chunks, total_words, file_size)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            title = EXCLUDED.title,
                            filename = EXCLUDED.filename,
                            upload_date = EXCLUDED.upload_date,
                            total_chunks = EXCLUDED.total_chunks,
                            total_words = EXCLUDED.total_words,
                            file_size = EXCLUDED.file_size
                    """, (
                        doc_id,
                        title,
                        filename,
                        datetime.now(),
                        len(chunks),
                        len(content.split()),
                        len(content.encode('utf-8'))
                    ))
                    
                    # Eliminar chunks existentes del documento
                    cursor.execute("DELETE FROM chunks WHERE document_id = %s", (doc_id,))
                    
                    # Insertar nuevos chunks
                    for i, chunk in enumerate(chunks):
                        chunk_id = f"{doc_id}_chunk_{i:03d}"
                        cursor.execute("""
                            INSERT INTO chunks (id, content, title, document_id, page, chunk_index, word_count)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            chunk_id,
                            chunk,
                            title,
                            doc_id,
                            1,
                            i,
                            len(chunk.split())
                        ))
                    
                    conn.commit()
                    return len(chunks)
                    
        except Exception as e:
            print(f"❌ Error agregando documento: {e}")
            return 0
    
    def split_content_into_chunks(self, content: str, chunk_size: int = 1000) -> List[str]:
        """Dividir contenido en fragmentos manejables"""
        # Dividir por oraciones primero
        sentences = content.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        # Agregar el último chunk si tiene contenido
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Si no hay chunks, crear uno con el contenido completo
        if not chunks:
            chunks = [content]
        
        return chunks
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de documentos"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM documents")
                    total_documents = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM chunks")
                    total_chunks = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COALESCE(SUM(word_count), 0) FROM chunks")
                    total_words = cursor.fetchone()[0]
                    
                    return {
                        "total_documents": total_documents,
                        "total_chunks": total_chunks,
                        "total_words": total_words
                    }
                    
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {"total_documents": 0, "total_chunks": 0, "total_words": 0}
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """Obtener lista de documentos"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, title, filename, upload_date, total_chunks, total_words
                        FROM documents
                        ORDER BY upload_date DESC
                    """)
                    
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            print(f"❌ Error obteniendo documentos: {e}")
            return []
    
    def log_chat(self, user_message: str, assistant_response: str, confidence: float, processing_time: float, sources: List[Dict] = None):
        """Registrar conversación en la base de datos"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO chat_logs (user_message, assistant_response, confidence, processing_time, sources)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        user_message,
                        assistant_response,
                        confidence,
                        processing_time,
                        json.dumps(sources) if sources else None
                    ))
                    conn.commit()
                    
        except Exception as e:
            print(f"❌ Error registrando chat: {e}")

# Instancia global de la base de datos
try:
    db = PostgreSQLDatabase()
    print("✅ Conexión a PostgreSQL establecida")
except Exception as e:
    print(f"❌ Error conectando a PostgreSQL: {e}")
    db = None

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
            .upload-section { padding: 20px; border-top: 1px solid #eee; }
            .upload-form { display: flex; gap: 10px; align-items: center; }
            .upload-form input[type="file"] { flex: 1; }
            .upload-form input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            .upload-form button { padding: 10px 20px; background: #059669; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .upload-form button:hover { background: #047857; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 MLB Assistant Chat</h1>
                <p>Asistente especializado en reglas de MLB (PostgreSQL)</p>
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
            <div class="upload-section">
                <h3>📚 Cargar Documento</h3>
                <form class="upload-form" id="uploadForm">
                    <input type="file" id="documentFile" accept=".txt,.pdf" required>
                    <input type="text" id="documentTitle" placeholder="Título del documento" required>
                    <button type="submit">Cargar</button>
                </form>
                <div id="uploadStatus"></div>
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
        
        // Manejar carga de documentos
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('documentFile');
            const titleInput = document.getElementById('documentTitle');
            const statusDiv = document.getElementById('uploadStatus');
            
            const file = fileInput.files[0];
            const title = titleInput.value.trim();
            
            if (!file || !title) {
                statusDiv.innerHTML = '<p style="color: red;">Por favor selecciona un archivo y proporciona un título.</p>';
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('title', title);
            
            statusDiv.innerHTML = '<p style="color: blue;">Cargando documento...</p>';
            
            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    statusDiv.innerHTML = `<p style="color: green;">✅ Documento cargado exitosamente: ${result.chunks_created} fragmentos creados.</p>`;
                    fileInput.value = '';
                    titleInput.value = '';
                    loadStats();
                } else {
                    statusDiv.innerHTML = `<p style="color: red;">❌ Error: ${result.detail}</p>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<p style="color: red;">❌ Error: ${error.message}</p>`;
            }
        });
        
        // Cargar estadísticas
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                document.getElementById('stats').innerHTML = 
                    `Documentos: ${data.total_documents} | Fragmentos: ${data.total_chunks} | Palabras: ${data.total_words}`;
            } catch (error) {
                document.getElementById('stats').innerHTML = 'Error cargando estadísticas';
            }
        }
        
        loadStats();
        </script>
    </body>
    </html>
    """)

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...), title: str = Form(...)):
    """Endpoint para cargar documentos"""
    if not db:
        raise HTTPException(status_code=500, detail="Base de datos no disponible")
    
    try:
        # Validar tipo de archivo
        if not file.filename.lower().endswith(('.txt', '.pdf')):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos .txt y .pdf")
        
        # Generar ID único para el documento
        doc_id = str(uuid.uuid4())
        
        # Guardar archivo
        file_path = UPLOADS_DIR / f"{doc_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Procesar contenido
        if file.filename.lower().endswith('.txt'):
            # Para archivos de texto
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        else:
            # Para PDFs, por ahora usar contenido simple
            text_content = f"Documento PDF: {title}\n\nEste es un documento PDF que necesita ser procesado con herramientas específicas."
        
        # Agregar documento a la base de datos
        chunks_created = db.add_document(doc_id, title, file.filename, text_content)
        
        return {
            "message": "Documento cargado exitosamente",
            "doc_id": doc_id,
            "title": title,
            "filename": file.filename,
            "chunks_created": chunks_created
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando documento: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Endpoint para procesar mensajes del chat"""
    if not db:
        return ChatResponse(
            response="❌ **Error:** Base de datos no disponible",
            confidence=0.0,
            processing_time=0.0
        )
    
    start_time = time.time()
    
    try:
        # Buscar en documentos
        search_results = db.search_documents(chat_message.message, limit=3)
        
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
        
        # Registrar en la base de datos
        db.log_chat(chat_message.message, response_text, confidence, processing_time, search_results)
        
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
    stats = db.get_stats() if db else {"total_documents": 0, "total_chunks": 0, "total_words": 0}
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "postgresql" if db else "none",
        "documents_loaded": stats.get("total_documents", 0),
        "chunks_loaded": stats.get("total_chunks", 0),
        "words_loaded": stats.get("total_words", 0)
    }

@app.get("/api/stats")
async def get_stats():
    """Obtener estadísticas de documentos"""
    if not db:
        return {"total_documents": 0, "total_chunks": 0, "total_words": 0}
    
    return db.get_stats()

@app.get("/api/documents")
async def get_documents():
    """Obtener lista de documentos disponibles"""
    if not db:
        return {"documents": []}
    
    documents = db.get_documents()
    return {
        "documents": [
            {
                "id": doc.get('id', ''),
                "title": doc.get('title', 'Sin título'),
                "filename": doc.get('filename', ''),
                "upload_date": doc.get('upload_date', ''),
                "chunks": doc.get('total_chunks', 0),
                "words": doc.get('total_words', 0)
            }
            for doc in documents
        ]
    }

if __name__ == "__main__":
    print("🤖 MLB Assistant Chat - Iniciando con PostgreSQL...")
    
    if db:
        stats = db.get_stats()
        print(f"📚 Documentos en BD: {stats.get('total_documents', 0)}")
        print(f"🧩 Fragmentos en BD: {stats.get('total_chunks', 0)}")
        print(f"📝 Palabras en BD: {stats.get('total_words', 0)}")
    else:
        print("⚠️  Base de datos no disponible")
    
    # Obtener puerto de Railway o usar 8000 por defecto
    port = int(os.environ.get("PORT", 8000))
    print(f"🌐 Servidor web iniciando en puerto {port}")
    
    uvicorn.run(
        "railway_app_postgres:app",
        host="0.0.0.0",
        port=port,
        reload=False
    ) 