"""
🗄️ Sistema de Base de Datos del Agente Inteligente

Este módulo maneja todas las operaciones de base de datos del sistema,
incluyendo conexiones a PostgreSQL, modelos de datos, y operaciones CRUD.
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime, Text, Boolean, JSON, Float
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from .config import get_config

# Base para modelos SQLAlchemy
Base = declarative_base()

# Metadata para migraciones
metadata = MetaData()


class DatabaseManager:
    """
    Gestor de base de datos del Agente Inteligente
    
    Maneja conexiones a PostgreSQL y SQLite, migraciones,
    y operaciones de base de datos.
    """
    
    def __init__(self):
        self.config = get_config()
        self.async_engine = None
        self.sync_engine = None
        self.async_session_factory = None
        self.sync_session_factory = None
        self.is_initialized = False
    
    async def initialize(self):
        """Inicializar conexiones de base de datos"""
        try:
            # Crear motores de base de datos
            database_url = self.config.get_database_url()
            sync_database_url = self.config.get_sync_database_url()
            
            logger.info(f"🔗 Conectando a base de datos: {database_url}")
            
            # Motor asíncrono
            self.async_engine = create_async_engine(
                database_url,
                echo=self.config.debug,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Motor síncrono
            self.sync_engine = create_engine(
                sync_database_url,
                echo=self.config.debug,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Crear sesiones
            self.async_session_factory = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self.sync_session_factory = sessionmaker(
                self.sync_engine,
                expire_on_commit=False
            )
            
            # Crear tablas
            await self.create_tables()
            
            self.is_initialized = True
            logger.info("✅ Base de datos inicializada correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")
            raise
    
    async def create_tables(self):
        """Crear tablas en la base de datos"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Tablas creadas correctamente")
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            raise
    
    async def close(self):
        """Cerrar conexiones de base de datos"""
        try:
            if self.async_engine:
                await self.async_engine.dispose()
            if self.sync_engine:
                self.sync_engine.dispose()
            logger.info("✅ Conexiones de base de datos cerradas")
        except Exception as e:
            logger.error(f"❌ Error cerrando conexiones: {e}")
    
    def get_async_session(self) -> AsyncSession:
        """Obtener sesión asíncrona"""
        if not self.is_initialized:
            raise RuntimeError("Base de datos no inicializada")
        return self.async_session_factory()
    
    def get_sync_session(self):
        """Obtener sesión síncrona"""
        if not self.is_initialized:
            raise RuntimeError("Base de datos no inicializada")
        return self.sync_session_factory()


# Modelos de base de datos
class Conversation(Base):
    """Modelo para conversaciones"""
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(100), nullable=True)
    session_id = Column(String(100), nullable=True)
    title = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    conversation_metadata = Column(JSON, default={})


class Message(Base):
    """Modelo para mensajes"""
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True)
    conversation_id = Column(String(36), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_metadata = Column(JSON, default={})


class Task(Base):
    """Modelo para tareas"""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True)
    conversation_id = Column(String(36), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    priority = Column(String(20), default="medium")
    dependencies = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    task_metadata = Column(JSON, default={})


class Knowledge(Base):
    """Modelo para base de conocimiento"""
    __tablename__ = "knowledge"
    
    id = Column(String(36), primary_key=True)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, document, image, etc.
    source = Column(String(500), nullable=True)
    embedding_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    knowledge_metadata = Column(JSON, default={})


class AgentStatus(Base):
    """Modelo para estado de agentes"""
    __tablename__ = "agent_status"
    
    id = Column(String(36), primary_key=True)
    agent_id = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=False)
    status = Column(String(20), default="idle")  # idle, busy, error, offline
    is_available = Column(Boolean, default=True)
    current_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    uptime = Column(Float, default=0.0)
    last_activity = Column(DateTime, nullable=True)
    performance_metrics = Column(JSON, default={})
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SystemMetrics(Base):
    """Modelo para métricas del sistema"""
    __tablename__ = "system_metrics"
    
    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metric_type = Column(String(50), nullable=False)  # cpu, memory, response_time, etc.
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)
    metrics_metadata = Column(JSON, default={})


# Operaciones CRUD para conversaciones
class ConversationRepository:
    """Repositorio para operaciones de conversaciones"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_conversation(self, conversation_id: str, user_id: Optional[str] = None, 
                                session_id: Optional[str] = None, title: Optional[str] = None,
                                metadata: Optional[Dict[str, Any]] = None) -> Conversation:
        """Crear una nueva conversación"""
        async with self.db_manager.get_async_session() as session:
            conversation = Conversation(
                id=conversation_id,
                user_id=user_id,
                session_id=session_id,
                title=title,
                conversation_metadata=metadata or {}
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            return conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Obtener una conversación por ID"""
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                f"SELECT * FROM conversations WHERE id = '{conversation_id}'"
            )
            return result.fetchone()
    
    async def get_conversations_by_user(self, user_id: str, limit: int = 50) -> List[Conversation]:
        """Obtener conversaciones de un usuario"""
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                f"SELECT * FROM conversations WHERE user_id = '{user_id}' ORDER BY updated_at DESC LIMIT {limit}"
            )
            return result.fetchall()
    
    async def update_conversation(self, conversation_id: str, **kwargs) -> bool:
        """Actualizar una conversación"""
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                f"UPDATE conversations SET updated_at = NOW() WHERE id = '{conversation_id}'"
            )
            await session.commit()
            return result.rowcount > 0


# Operaciones CRUD para mensajes
class MessageRepository:
    """Repositorio para operaciones de mensajes"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def add_message(self, message_id: str, conversation_id: str, role: str, 
                         content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Añadir un mensaje a una conversación"""
        async with self.db_manager.get_async_session() as session:
            message = Message(
                id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                message_metadata=metadata or {}
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message
    
    async def get_messages(self, conversation_id: str, limit: int = 100) -> List[Message]:
        """Obtener mensajes de una conversación"""
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                f"SELECT * FROM messages WHERE conversation_id = '{conversation_id}' ORDER BY timestamp ASC LIMIT {limit}"
            )
            return result.fetchall()


# Operaciones CRUD para tareas
class TaskRepository:
    """Repositorio para operaciones de tareas"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_task(self, task_id: str, title: str, agent_type: str, 
                         description: Optional[str] = None, conversation_id: Optional[str] = None,
                         priority: str = "medium", dependencies: Optional[List[str]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Task:
        """Crear una nueva tarea"""
        async with self.db_manager.get_async_session() as session:
            task = Task(
                id=task_id,
                conversation_id=conversation_id,
                title=title,
                description=description,
                agent_type=agent_type,
                priority=priority,
                dependencies=dependencies or [],
                task_metadata=metadata or {}
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task
    
    async def update_task_status(self, task_id: str, status: str, 
                                result: Optional[Dict[str, Any]] = None,
                                error: Optional[str] = None) -> bool:
        """Actualizar el estado de una tarea"""
        async with self.db_manager.get_async_session() as session:
            update_data = {"status": status}
            if status == "running":
                update_data["started_at"] = datetime.utcnow()
            elif status in ["completed", "failed"]:
                update_data["completed_at"] = datetime.utcnow()
                if result:
                    update_data["result"] = result
                if error:
                    update_data["error"] = error
            
            result = await session.execute(
                f"UPDATE tasks SET status = '{status}' WHERE id = '{task_id}'"
            )
            await session.commit()
            return result.rowcount > 0


# Instancia global del gestor de base de datos
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """Obtener el gestor de base de datos"""
    return db_manager 