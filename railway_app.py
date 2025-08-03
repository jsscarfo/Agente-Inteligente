#!/usr/bin/env python3
"""
🚂 Railway App - Aplicación Web Unificada para Railway

Esta aplicación está específicamente diseñada para despliegue en Railway,
combinando todas las capacidades del sistema en una interfaz web unificada.
"""

import os
import json
import uuid
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configurar logging para Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
import sys
sys.path.insert(0, str(project_root))

# Importar componentes del sistema
try:
    from agent.core.models_simple import AgentRequest, AgentResponse
    from agent.core.config import get_config
    from assistant_standalone import StandaloneAssistant
    # Removed problematic imports that cause errors
    # from assistant_multimodal import MultimodalAssistant
    # from cargar_pdf_simple import SimplePDFLoader
except ImportError as e:
    logger.warning(f"⚠️ Algunos componentes no disponibles: {e}")

# Configuración de Railway
PORT = int(os.environ.get("PORT", 8080))  # Railway usa 8080 por defecto
RAILWAY_ENVIRONMENT = os.environ.get("RAILWAY_ENVIRONMENT", "development")

# Crear aplicación FastAPI
app = FastAPI(
    title="AI Assistant - Railway",
    description="Asistente de IA Multifuncional desplegado en Railway",
    version="2.0.0"
)

# Configurar CORS para Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar archivos estáticos y templates
STATIC_DIR = project_root / "static"
TEMPLATES_DIR = project_root / "templates"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if TEMPLATES_DIR.exists():
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
else:
    templates = None

# Modelos Pydantic
class ChatMessage(BaseModel):
    message: str
    mode: str = "text"  # text, multimodal, sequential
    file_path: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    success: bool
    mode: str
    processing_time: float
    metadata: Dict[str, Any] = {}

class SystemStatus(BaseModel):
    status: str
    uptime: float
    version: str
    environment: str
    components: Dict[str, str]

# Variables globales para el sistema
assistant = None
multimodal_assistant = None
pdf_loader = None
system_start_time = datetime.now()

@app.on_event("startup")
async def startup_event():
    """Inicializar el sistema al arrancar"""
    global assistant, multimodal_assistant, pdf_loader
    
    try:
        logger.info("🚀 Inicializando sistema para Railway...")
        
        # Inicializar asistente básico
        try:
            assistant = StandaloneAssistant()
            await assistant.start()
            logger.info("✅ Asistente básico inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Error inicializando asistente básico: {e}")
        
        # Inicializar asistente multimodal (opcional) - Comentado por problemas de import
        # try:
        #     multimodal_assistant = MultimodalAssistant()
        #     await multimodal_assistant.initialize()
        #     logger.info("✅ Asistente multimodal inicializado")
        # except Exception as e:
        #     logger.warning(f"⚠️ Error inicializando asistente multimodal: {e}")
        
        # Inicializar cargador de PDFs (simplificado) - Comentado por problemas de import
        # try:
        #     pdf_loader = SimplePDFLoader()
        #     logger.info("✅ Cargador de PDFs inicializado")
        # except Exception as e:
        #     logger.warning(f"⚠️ Error inicializando cargador de PDFs: {e}")
        
        logger.info(f"✅ Sistema inicializado en entorno: {RAILWAY_ENVIRONMENT}")
        
    except Exception as e:
        logger.error(f"❌ Error en startup: {e}")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal"""
    if templates:
        return templates.TemplateResponse("chat.html", {"request": request})
    
    # HTML básico si no hay templates
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Assistant - Railway</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .chat-box { border: 1px solid #ddd; border-radius: 5px; padding: 20px; margin-bottom: 20px; min-height: 200px; background: #fafafa; }
            .input-group { display: flex; gap: 10px; }
            input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .status { text-align: center; color: #666; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI Assistant</h1>
                <p>Asistente de IA Multifuncional - Railway</p>
            </div>
            
            <div class="chat-box" id="chatBox">
                <p>¡Hola! Soy tu asistente de IA. ¿En qué puedo ayudarte?</p>
            </div>
            
            <div class="input-group">
                <input type="text" id="messageInput" placeholder="Escribe tu mensaje aquí..." onkeypress="if(event.key=='Enter') sendMessage()">
                <button onclick="sendMessage()">Enviar</button>
            </div>
            
            <div class="status">
                <p>🚂 Desplegado en Railway | Modo: """ + RAILWAY_ENVIRONMENT + """</p>
            </div>
        </div>
        
        <script>
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const chatBox = document.getElementById('chatBox');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Mostrar mensaje del usuario
            chatBox.innerHTML += '<p><strong>Tú:</strong> ' + message + '</p>';
            input.value = '';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message, mode: 'text'})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    chatBox.innerHTML += '<p><strong>Asistente:</strong> ' + data.response + '</p>';
                } else {
                    chatBox.innerHTML += '<p><strong>Error:</strong> ' + data.response + '</p>';
                }
            } catch (error) {
                chatBox.innerHTML += '<p><strong>Error:</strong> No se pudo conectar con el servidor</p>';
            }
            
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Endpoint principal para el chat"""
    start_time = datetime.now()
    
    try:
        response_content = ""
        success = False
        mode = chat_message.mode
        
        # Procesar según el modo
        if mode == "multimodal" and multimodal_assistant:
            # Modo multimodal
            response = await multimodal_assistant.process_query(chat_message.message)
            response_content = response.content
            success = response.success
            
        elif assistant:
            # Modo texto normal
            request = AgentRequest(
                query=chat_message.message,
                priority="normal",
                metadata={}
            )
            response = await assistant.process_request(request)
            response_content = response.content
            success = response.success
            
        else:
            response_content = "❌ Sistema no disponible. Por favor, inténtalo más tarde."
            success = False
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ChatResponse(
            response=response_content,
            success=success,
            mode=mode,
            processing_time=processing_time,
            metadata={
                "environment": RAILWAY_ENVIRONMENT,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error en chat endpoint: {e}")
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ChatResponse(
            response=f"❌ Error procesando la consulta: {str(e)}",
            success=False,
            mode=chat_message.mode,
            processing_time=processing_time,
            metadata={"error": str(e)}
        )

@app.get("/api/status", response_model=SystemStatus)
async def get_status():
    """Obtener estado del sistema"""
    uptime = (datetime.now() - system_start_time).total_seconds()
    
    components = {}
    
    if assistant:
        components["assistant"] = "✅ Activo"
    else:
        components["assistant"] = "❌ Inactivo"
    
    if multimodal_assistant:
        components["multimodal"] = "✅ Activo"
    else:
        components["multimodal"] = "❌ Inactivo"
    
    if pdf_loader:
        components["pdf_loader"] = "✅ Activo"
    else:
        components["pdf_loader"] = "❌ Inactivo"
    
    return SystemStatus(
        status="running",
        uptime=uptime,
        version="2.0.0",
        environment=RAILWAY_ENVIRONMENT,
        components=components
    )

@app.get("/api/health")
async def health_check():
    """Health check para Railway"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": RAILWAY_ENVIRONMENT,
        "port": PORT
    }

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Subir y procesar un PDF"""
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
        
        # Guardar archivo temporalmente
        temp_dir = project_root / "data" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Procesar PDF
        if pdf_loader:
            success = pdf_loader.load_pdf(file_path)
            
            # Limpiar archivo temporal
            file_path.unlink()
            
            if success:
                return {
                    "success": True,
                    "message": f"PDF '{file.filename}' procesado correctamente",
                    "filename": file.filename
                }
            else:
                return {
                    "success": False,
                    "message": f"Error procesando PDF '{file.filename}'",
                    "filename": file.filename
                }
        else:
            return {
                "success": False,
                "message": "Cargador de PDFs no disponible",
                "filename": file.filename
            }
            
    except Exception as e:
        logger.error(f"❌ Error subiendo PDF: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "filename": file.filename if file else "unknown"
        }

@app.get("/api/documents")
async def get_documents():
    """Obtener lista de documentos procesados"""
    try:
        if pdf_loader:
            documents = pdf_loader.list_documents()
            stats = pdf_loader.get_statistics()
            
            return {
                "success": True,
                "documents": documents,
                "statistics": stats
            }
        else:
            return {
                "success": False,
                "message": "Cargador de PDFs no disponible",
                "documents": [],
                "statistics": {}
            }
    except Exception as e:
        logger.error(f"❌ Error obteniendo documentos: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "documents": [],
            "statistics": {}
        }

if __name__ == "__main__":
    logger.info(f"🚂 Iniciando aplicación Railway en puerto {PORT}")
    logger.info(f"🌍 Entorno: {RAILWAY_ENVIRONMENT}")
    
    uvicorn.run(
        "railway_app:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="info"
    ) 