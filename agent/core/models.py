"""
📊 Modelos de Datos del Agente Inteligente

Este módulo define todos los modelos de datos utilizados en el sistema
de agente inteligente, incluyendo peticiones, respuestas, tareas y
estados del sistema.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator


class TaskStatus(str, Enum):
    """Estados posibles de una tarea"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Tipos de agentes disponibles"""
    COORDINATOR = "coordinator"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"


class DataSourceType(str, Enum):
    """Tipos de fuentes de datos"""
    API = "api"
    VECTOR_DB = "vector_db"
    RELATIONAL_DB = "relational_db"
    FILE = "file"
    WEB = "web"


class PriorityLevel(str, Enum):
    """Niveles de prioridad"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentRequest(BaseModel):
    """
    Modelo para peticiones al agente inteligente
    """
    query: str = Field(..., description="Petición del usuario en texto libre")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Contexto adicional")
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, description="Prioridad de la petición")
    timeout: Optional[int] = Field(default=None, description="Timeout personalizado en segundos")
    user_id: Optional[str] = Field(default=None, description="ID del usuario")
    session_id: Optional[str] = Field(default=None, description="ID de la sesión")
    
    @validator("query")
    def validate_query(cls, v):
        """Validar que la petición no esté vacía"""
        if not v.strip():
            raise ValueError("La petición no puede estar vacía")
        return v.strip()
    
    @validator("timeout")
    def validate_timeout(cls, v):
        """Validar timeout"""
        if v is not None and v <= 0:
            raise ValueError("Timeout debe ser mayor que 0")
        return v


class Task(BaseModel):
    """
    Modelo para tareas del agente
    """
    id: str = Field(..., description="ID único de la tarea")
    title: str = Field(..., description="Título de la tarea")
    description: str = Field(..., description="Descripción detallada")
    agent_type: AgentType = Field(..., description="Tipo de agente que ejecutará la tarea")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Estado actual")
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, description="Prioridad")
    dependencies: List[str] = Field(default=[], description="IDs de tareas dependientes")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    started_at: Optional[datetime] = Field(default=None, description="Fecha de inicio")
    completed_at: Optional[datetime] = Field(default=None, description="Fecha de finalización")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Resultado de la tarea")
    error: Optional[str] = Field(default=None, description="Error si la tarea falló")
    metadata: Dict[str, Any] = Field(default={}, description="Metadatos adicionales")


class AgentResponse(BaseModel):
    """
    Modelo para respuestas del agente inteligente
    """
    success: bool = Field(..., description="Indica si la petición fue exitosa")
    content: str = Field(..., description="Contenido principal de la respuesta")
    summary: Optional[str] = Field(default=None, description="Resumen de la respuesta")
    confidence_score: float = Field(default=0.0, description="Puntuación de confianza (0-1)")
    sources: List[Dict[str, Any]] = Field(default=[], description="Fuentes utilizadas")
    tasks: List[Task] = Field(default=[], description="Tareas ejecutadas")
    processing_time: float = Field(default=0.0, description="Tiempo de procesamiento en segundos")
    tokens_used: Optional[int] = Field(default=None, description="Tokens utilizados")
    metadata: Dict[str, Any] = Field(default={}, description="Metadatos adicionales")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    
    @validator("confidence_score")
    def validate_confidence(cls, v):
        """Validar puntuación de confianza"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence score debe estar entre 0.0 y 1.0")
        return v
    
    @validator("processing_time")
    def validate_processing_time(cls, v):
        """Validar tiempo de procesamiento"""
        if v < 0:
            raise ValueError("Processing time no puede ser negativo")
        return v


class DataSource(BaseModel):
    """
    Modelo para fuentes de datos
    """
    id: str = Field(..., description="ID único de la fuente")
    name: str = Field(..., description="Nombre de la fuente")
    type: DataSourceType = Field(..., description="Tipo de fuente")
    url: Optional[str] = Field(default=None, description="URL de la fuente")
    config: Dict[str, Any] = Field(default={}, description="Configuración de la fuente")
    is_active: bool = Field(default=True, description="Indica si la fuente está activa")
    last_accessed: Optional[datetime] = Field(default=None, description="Último acceso")
    metadata: Dict[str, Any] = Field(default={}, description="Metadatos adicionales")


class AgentStatus(BaseModel):
    """
    Modelo para el estado del agente
    """
    agent_id: str = Field(..., description="ID del agente")
    agent_type: AgentType = Field(..., description="Tipo de agente")
    status: str = Field(..., description="Estado del agente")
    is_available: bool = Field(default=True, description="Indica si está disponible")
    current_tasks: int = Field(default=0, description="Número de tareas actuales")
    completed_tasks: int = Field(default=0, description="Número de tareas completadas")
    failed_tasks: int = Field(default=0, description="Número de tareas fallidas")
    uptime: float = Field(default=0.0, description="Tiempo activo en segundos")
    last_activity: Optional[datetime] = Field(default=None, description="Última actividad")
    performance_metrics: Dict[str, Any] = Field(default={}, description="Métricas de rendimiento")


class SystemStatus(BaseModel):
    """
    Modelo para el estado del sistema
    """
    system_status: str = Field(..., description="Estado general del sistema")
    agents_status: List[AgentStatus] = Field(default=[], description="Estado de los agentes")
    active_tasks: int = Field(default=0, description="Tareas activas")
    total_tasks: int = Field(default=0, description="Total de tareas")
    success_rate: float = Field(default=0.0, description="Tasa de éxito")
    average_response_time: float = Field(default=0.0, description="Tiempo promedio de respuesta")
    system_uptime: float = Field(default=0.0, description="Tiempo activo del sistema")
    memory_usage: float = Field(default=0.0, description="Uso de memoria en MB")
    cpu_usage: float = Field(default=0.0, description="Uso de CPU en porcentaje")
    last_updated: datetime = Field(default_factory=datetime.now, description="Última actualización")


class ConversationMessage(BaseModel):
    """
    Modelo para mensajes de conversación
    """
    id: str = Field(..., description="ID único del mensaje")
    role: str = Field(..., description="Rol del mensaje (user/assistant)")
    content: str = Field(..., description="Contenido del mensaje")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del mensaje")
    metadata: Dict[str, Any] = Field(default={}, description="Metadatos adicionales")


class Conversation(BaseModel):
    """
    Modelo para conversaciones
    """
    id: str = Field(..., description="ID único de la conversación")
    user_id: Optional[str] = Field(default=None, description="ID del usuario")
    session_id: Optional[str] = Field(default=None, description="ID de la sesión")
    messages: List[ConversationMessage] = Field(default=[], description="Mensajes de la conversación")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.now, description="Última actualización")
    metadata: Dict[str, Any] = Field(default={}, description="Metadatos adicionales")


class ErrorResponse(BaseModel):
    """
    Modelo para respuestas de error
    """
    error: str = Field(..., description="Descripción del error")
    error_code: Optional[str] = Field(default=None, description="Código de error")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Detalles adicionales")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")
    request_id: Optional[str] = Field(default=None, description="ID de la petición que causó el error")


class HealthCheck(BaseModel):
    """
    Modelo para health check
    """
    status: str = Field(..., description="Estado del sistema")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del check")
    version: str = Field(..., description="Versión del sistema")
    uptime: float = Field(..., description="Tiempo activo en segundos")
    checks: Dict[str, bool] = Field(default={}, description="Checks individuales")
    details: Dict[str, Any] = Field(default={}, description="Detalles adicionales") 