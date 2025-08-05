#!/usr/bin/env python3
"""
🤖 MLB Assistant Chat - Aplicación para Railway con PostgreSQL y RAG Contextual Avanzado

Esta aplicación está optimizada para despliegue en Railway y usa PostgreSQL
como base de datos principal con sistema RAG contextual para respuestas expertas.
"""

import os
import json
import time
import uuid
import re
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

app = FastAPI(title="MLB Assistant Chat", version="2.0.0")

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

class AdvancedRAGSystem:
    """Sistema RAG avanzado para respuestas contextuales y expertas"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def extract_keywords(self, query: str) -> List[str]:
        """Extraer palabras clave relevantes de la consulta"""
        # Palabras clave específicas de MLB
        mlb_keywords = [
            'regla', 'reglas', 'pitch', 'bateo', 'corredor', 'base', 'out', 'inning',
            'apuesta', 'apuestas', 'drogas', 'tabaco', 'violencia', 'doméstica',
            'redes', 'sociales', 'novatadas', 'fantasma', 'clock', 'reloj',
            'suspensión', 'multa', 'penalización', 'prohibido', 'permitido'
        ]
        
        query_lower = query.lower()
        keywords = []
        
        # Buscar palabras clave específicas
        for keyword in mlb_keywords:
            if keyword in query_lower:
                keywords.append(keyword)
        
        # Agregar palabras generales importantes
        words = re.findall(r'\b\w+\b', query_lower)
        for word in words:
            if len(word) > 3 and word not in ['para', 'con', 'los', 'las', 'del', 'una', 'este', 'esta']:
                keywords.append(word)
        
        return list(set(keywords))
    
    def search_contextual(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Búsqueda contextual avanzada"""
        try:
            keywords = self.extract_keywords(query)
            
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Búsqueda principal con relevancia
                    cursor.execute("""
                        SELECT c.id, c.content, c.title, c.document_id,
                               ts_rank(to_tsvector('spanish', c.content), plainto_tsquery('spanish', %s)) as relevance
                        FROM chunks c
                        WHERE to_tsvector('spanish', c.content) @@ plainto_tsquery('spanish', %s)
                        ORDER BY relevance DESC
                        LIMIT %s
                    """, (query, query, limit))
                    
                    primary_results = cursor.fetchall()
                    
                    # Si no hay resultados suficientes, buscar por palabras clave
                    if len(primary_results) < 3 and keywords:
                        keyword_query = ' | '.join(keywords)
                        cursor.execute("""
                            SELECT c.id, c.content, c.title, c.document_id,
                                   ts_rank(to_tsvector('spanish', c.content), plainto_tsquery('spanish', %s)) as relevance
                            FROM chunks c
                            WHERE to_tsvector('spanish', c.content) @@ plainto_tsquery('spanish', %s)
                            ORDER BY relevance DESC
                            LIMIT %s
                        """, (keyword_query, keyword_query, limit - len(primary_results)))
                        
                        keyword_results = cursor.fetchall()
                        primary_results.extend(keyword_results)
                    
                    return [dict(row) for row in primary_results]
                    
        except Exception as e:
            print(f"❌ Error en búsqueda contextual: {e}")
            return []
    
    def format_expert_response(self, query: str, search_results: List[Dict], confidence: float) -> str:
        """Formatear respuesta con tono experto y profesional"""
        
        if not search_results:
            return self.format_no_results_response(query)
        
        # Extraer información relevante
        relevant_content = []
        sources_info = []
        
        for result in search_results:
            content = result['content'].strip()
            title = result.get('title', 'Documento MLB')
            
            # Limpiar y formatear contenido
            clean_content = re.sub(r'\s+', ' ', content)
            clean_content = clean_content.replace('...', '').strip()
            
            if len(clean_content) > 50:  # Solo contenido sustancial
                relevant_content.append(clean_content)
                sources_info.append(title)
        
        if not relevant_content:
            return self.format_no_results_response(query)
        
        # Construir respuesta experta
        response_parts = []
        
        # Encabezado profesional
        response_parts.append(f"🎯 **Consulta:** {query}")
        response_parts.append("")
        
        # Respuesta principal
        response_parts.append("📋 **Información Relevante:**")
        response_parts.append("")
        
        # Combinar y formatear contenido
        combined_content = ' '.join(relevant_content[:3])  # Máximo 3 fragmentos
        
        # Dividir en párrafos lógicos
        sentences = re.split(r'[.!?]+', combined_content)
        formatted_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Solo oraciones sustanciales
                # Capitalizar primera letra
                if sentence and sentence[0].islower():
                    sentence = sentence[0].upper() + sentence[1:]
                formatted_sentences.append(sentence)
        
        # Agrupar en párrafos con mejor formato
        if formatted_sentences:
            paragraphs = []
            current_paragraph = []
            
            for sentence in formatted_sentences:
                current_paragraph.append(sentence)
                if len(current_paragraph) >= 3:  # Máximo 3 oraciones por párrafo
                    paragraphs.append('. '.join(current_paragraph) + '.')
                    current_paragraph = []
            
            # Agregar párrafo restante
            if current_paragraph:
                paragraphs.append('. '.join(current_paragraph) + '.')
            
            # Agregar cada párrafo con saltos de línea
            for i, paragraph in enumerate(paragraphs):
                response_parts.append(paragraph)
                if i < len(paragraphs) - 1:  # No agregar línea extra después del último párrafo
                    response_parts.append("")
        
        # Información adicional si hay confianza alta
        if confidence > 0.7:
            response_parts.append("")
            response_parts.append("💡 **Nota:** Esta información está basada en las reglas oficiales de MLB y puede estar sujeta a actualizaciones.")
        
        # Fuentes
        if sources_info:
            response_parts.append("")
            response_parts.append("📚 **Fuentes:**")
            unique_sources = list(set(sources_info))
            for source in unique_sources[:3]:  # Máximo 3 fuentes
                response_parts.append(f"• {source}")
        
        return "\n".join(response_parts)
    
    def format_no_results_response(self, query: str) -> str:
        """Formatear respuesta cuando no hay resultados"""
        
        response_parts = []
        response_parts.append(f"🔍 **Consulta:** {query}")
        response_parts.append("")
        response_parts.append("❌ **No encontré información específica** sobre tu consulta en la base de datos actual.")
        response_parts.append("")
        response_parts.append("💡 **Sugerencias para mejorar tu búsqueda:**")
        response_parts.append("")
        response_parts.append("🎯 **Términos específicos que funcionan:**")
        response_parts.append("")
        response_parts.append("• 'corredor fantasma' - Reglas sobre corredores en base")
        response_parts.append("")
        response_parts.append("• 'pitch clock' - Regulaciones de tiempo")
        response_parts.append("")
        response_parts.append("• 'reglas de apuestas' - Políticas sobre apuestas")
        response_parts.append("")
        response_parts.append("• 'política de drogas' - Sustancias prohibidas")
        response_parts.append("")
        response_parts.append("• 'violencia doméstica' - Sanciones por violencia")
        response_parts.append("")
        response_parts.append("• 'redes sociales' - Uso de medios sociales")
        response_parts.append("")
        response_parts.append("• 'tabaco' - Políticas sobre tabaco")
        response_parts.append("")
        response_parts.append("• 'novatadas' - Prohibiciones de novatadas")
        response_parts.append("")
        response_parts.append("🔧 **Consejos:**")
        response_parts.append("")
        response_parts.append("• Usa términos más específicos")
        response_parts.append("")
        response_parts.append("• Busca por número de regla (ej: 'Regla 21')")
        response_parts.append("")
        response_parts.append("• Reformula tu pregunta con palabras clave")
        response_parts.append("")
        response_parts.append("📚 **¿Necesitas cargar más documentos?** Usa la sección de carga de documentos para agregar más información.")
        
        return "\n".join(response_parts)

class PostgreSQLDatabase:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL no encontrada en variables de entorno")
        
        # Inicializar sistema RAG
        self.rag_system = AdvancedRAGSystem(self)
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        return psycopg2.connect(self.database_url)
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Buscar documentos usando RAG contextual avanzado"""
        return self.rag_system.search_contextual(query, limit)
    
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
    """Interfaz principal del chat con diseño mejorado"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MLB Assistant Chat - Expert System</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .logo-container {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 20px;
                margin-bottom: 20px;
            }
            
            .mlb-logo {
                filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
            }
            
            .logo-text h1 {
                font-size: 3.5rem;
                font-weight: 800;
                margin: 0;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                color: #4682B4;
            }
            
            .logo-text h2 {
                font-size: 1.2rem;
                font-weight: 600;
                margin: 0;
                text-shadow: 0 1px 2px rgba(0,0,0,0.3);
                color: #FF0000;
                letter-spacing: 2px;
            }
            
            .header p {
                font-size: 1.1rem;
                opacity: 0.9;
                font-weight: 300;
            }
            
            .main-content {
                display: grid;
                grid-template-columns: 1fr 350px;
                gap: 0;
                min-height: 600px;
            }
            
            .chat-section {
                padding: 30px;
                border-right: 1px solid #e5e7eb;
            }
            
            .chat-container {
                height: 400px;
                overflow-y: auto;
                border: 2px solid #e5e7eb;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                background: #fafafa;
            }
            
            .message {
                margin: 15px 0;
                padding: 15px 20px;
                border-radius: 15px;
                max-width: 80%;
                line-height: 1.6;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            
            .user-message {
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: white;
                margin-left: auto;
                text-align: right;
            }
            
            .bot-message {
                background: white;
                border: 2px solid #e5e7eb;
                margin-right: auto;
            }
            
            .bot-message strong {
                color: #1e3a8a;
            }
            
            .input-container {
                display: flex;
                gap: 15px;
                align-items: center;
            }
            
            .input-container input {
                flex: 1;
                padding: 15px 20px;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                font-size: 1rem;
                transition: all 0.3s ease;
                background: white;
            }
            
            .input-container input:focus {
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            .btn {
                padding: 15px 25px;
                border: none;
                border-radius: 12px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: white;
            }
            
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
            }
            
            .btn-success {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
            }
            
            .btn-success:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
            }
            
            .sidebar {
                background: #f8fafc;
                padding: 30px;
            }
            
            .upload-section {
                margin-bottom: 30px;
            }
            
            .upload-section h3 {
                color: #1e3a8a;
                font-size: 1.3rem;
                margin-bottom: 15px;
                font-weight: 600;
            }
            
            .upload-form {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            
            .upload-form input[type="file"] {
                padding: 12px;
                border: 2px dashed #d1d5db;
                border-radius: 10px;
                background: white;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .upload-form input[type="file"]:hover {
                border-color: #3b82f6;
                background: #f0f9ff;
            }
            
            .upload-form input[type="text"] {
                padding: 12px 15px;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                font-size: 0.95rem;
                transition: all 0.3s ease;
            }
            
            .upload-form input[type="text"]:focus {
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            .stats {
                background: white;
                padding: 20px;
                border-radius: 15px;
                border: 2px solid #e5e7eb;
                text-align: center;
            }
            
            .stats h4 {
                color: #1e3a8a;
                margin-bottom: 10px;
                font-weight: 600;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 15px;
            }
            
            .stat-item {
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #bae6fd;
            }
            
            .stat-number {
                font-size: 1.5rem;
                font-weight: 700;
                color: #0369a1;
                display: block;
            }
            
            .stat-label {
                font-size: 0.8rem;
                color: #0c4a6e;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-weight: 500;
            }
            
            .status-message {
                padding: 15px;
                border-radius: 10px;
                margin-top: 15px;
                font-weight: 500;
            }
            
            .status-success {
                background: #dcfce7;
                color: #166534;
                border: 1px solid #bbf7d0;
            }
            
            .status-error {
                background: #fef2f2;
                color: #dc2626;
                border: 1px solid #fecaca;
            }
            
            .status-info {
                background: #dbeafe;
                color: #1e40af;
                border: 1px solid #bfdbfe;
            }
            
            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
                
                .chat-section {
                    border-right: none;
                    border-bottom: 1px solid #e5e7eb;
                }
                
                .logo-container {
                    flex-direction: column;
                    gap: 15px;
                }
                
                .logo-text h1 {
                    font-size: 2.5rem;
                }
                
                .logo-text h2 {
                    font-size: 1rem;
                }
                
                .stats-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-container">
                    <svg class="mlb-logo" width="120" height="120" viewBox="0 0 120 120">
                        <!-- Robot body -->
                        <rect x="30" y="40" width="60" height="70" rx="8" fill="#87CEEB" stroke="#4682B4" stroke-width="2"/>
                        
                        <!-- Robot head -->
                        <rect x="25" y="20" width="70" height="30" rx="8" fill="#87CEEB" stroke="#4682B4" stroke-width="2"/>
                        
                        <!-- Eyes -->
                        <circle cx="40" cy="35" r="4" fill="white"/>
                        <circle cx="40" cy="35" r="2" fill="black"/>
                        <circle cx="80" cy="35" r="4" fill="white"/>
                        <circle cx="80" cy="35" r="2" fill="black"/>
                        
                        <!-- Smile -->
                        <path d="M 35 42 Q 60 50 85 42" stroke="black" stroke-width="2" fill="none"/>
                        
                        <!-- Ears/Communication devices -->
                        <rect x="15" y="25" width="8" height="20" rx="4" fill="#4682B4"/>
                        <rect x="97" y="25" width="8" height="20" rx="4" fill="#4682B4"/>
                        
                        <!-- Antenna -->
                        <line x1="60" y1="20" x2="60" y2="10" stroke="#4682B4" stroke-width="3"/>
                        <circle cx="60" cy="8" r="3" fill="#FF0000"/>
                        
                        <!-- Baseball cap -->
                        <ellipse cx="60" cy="25" rx="40" ry="8" fill="#4682B4"/>
                        <rect x="20" y="20" width="80" height="10" rx="5" fill="#4682B4"/>
                        <ellipse cx="60" cy="30" rx="35" ry="6" fill="#FF0000"/>
                        
                        <!-- Baseball -->
                        <circle cx="60" cy="85" r="15" fill="white" stroke="#FF0000" stroke-width="2"/>
                        <path d="M 45 85 Q 60 75 75 85" stroke="#FF0000" stroke-width="2" fill="none"/>
                        <path d="M 45 85 Q 60 95 75 85" stroke="#FF0000" stroke-width="2" fill="none"/>
                    </svg>
                    <div class="logo-text">
                        <h1>MLB</h1>
                        <h2>CHAT BOT</h2>
                    </div>
                </div>
                <p>Sistema de Inteligencia Artificial Especializado en Reglas de MLB</p>
            </div>
            
            <div class="main-content">
                <div class="chat-section">
                    <div class="chat-container" id="chatContainer">
                        <div class="message bot-message">
                            <strong>¡Hola! Soy tu asistente experto en reglas de MLB.</strong><br><br>
                            Puedo ayudarte con consultas sobre:<br>
                            • Reglas específicas del juego<br>
                            • Políticas de la liga<br>
                            • Sanciones y penalizaciones<br>
                            • Regulaciones sobre apuestas, drogas, etc.<br><br>
                            <em>¿En qué puedo ayudarte hoy?</em>
                        </div>
                    </div>
                    
                    <div class="input-container">
                        <input type="text" id="messageInput" placeholder="Escribe tu pregunta sobre reglas de MLB..." onkeypress="if(event.key==='Enter') sendMessage()">
                        <button class="btn btn-primary" onclick="sendMessage()">Enviar</button>
                    </div>
                </div>
                
                <div class="sidebar">
                    <div class="upload-section">
                        <h3>📚 Cargar Documento</h3>
                        <form class="upload-form" id="uploadForm">
                            <input type="file" id="documentFile" accept=".txt,.pdf" required>
                            <input type="text" id="documentTitle" placeholder="Título del documento" required>
                            <button type="submit" class="btn btn-success">Cargar Documento</button>
                        </form>
                        <div id="uploadStatus"></div>
                    </div>
                    
                    <div class="stats">
                        <h4>📊 Estadísticas del Sistema</h4>
                        <div class="stats-grid" id="statsGrid">
                            <div class="stat-item">
                                <span class="stat-number" id="docCount">-</span>
                                <span class="stat-label">Documentos</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number" id="chunkCount">-</span>
                                <span class="stat-label">Fragmentos</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number" id="wordCount">-</span>
                                <span class="stat-label">Palabras</span>
                            </div>
                        </div>
                    </div>
                </div>
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
                addMessage('❌ Error de conexión: ' + error.message, 'bot');
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
                statusDiv.innerHTML = '<div class="status-message status-error">Por favor selecciona un archivo y proporciona un título.</div>';
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('title', title);
            
            statusDiv.innerHTML = '<div class="status-message status-info">Cargando documento...</div>';
            
            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    statusDiv.innerHTML = `<div class="status-message status-success">✅ Documento cargado exitosamente: ${result.chunks_created} fragmentos creados.</div>`;
                    fileInput.value = '';
                    titleInput.value = '';
                    loadStats();
                } else {
                    statusDiv.innerHTML = `<div class="status-message status-error">❌ Error: ${result.detail}</div>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="status-message status-error">❌ Error: ${error.message}</div>`;
            }
        });
        
        // Cargar estadísticas
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                document.getElementById('docCount').textContent = data.total_documents;
                document.getElementById('chunkCount').textContent = data.total_chunks;
                document.getElementById('wordCount').textContent = data.total_words;
            } catch (error) {
                console.error('Error cargando estadísticas:', error);
            }
        }
        
        // Cargar estadísticas al inicio
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
    """Endpoint para procesar mensajes del chat con RAG contextual"""
    if not db:
        return ChatResponse(
            response="❌ **Error:** Base de datos no disponible",
            confidence=0.0,
            processing_time=0.0
        )
    
    start_time = time.time()
    
    try:
        # Buscar en documentos usando RAG contextual
        search_results = db.search_documents(chat_message.message, limit=5)
        
        # Calcular confianza basada en resultados
        confidence = min(0.9, 0.3 + (len(search_results) * 0.15))
        
        # Formatear respuesta experta
        response_text = db.rag_system.format_expert_response(
            chat_message.message, 
            search_results, 
            confidence
        )
        
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
    print("🤖 MLB Assistant Chat - Iniciando con RAG Contextual Avanzado...")
    
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
        "railway_app:app",
        host="0.0.0.0",
        port=port,
        reload=False
    ) 