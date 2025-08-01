"""
📋 Modelos Simplificados del Agente Inteligente

Versión simplificada de los modelos para evitar conflictos con SQLAlchemy.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass


class PriorityLevel(str, Enum):
    """Niveles de prioridad"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Estados de tareas"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Tipos de agentes"""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYZER = "analyzer"
    SYNTHESIZER = "synthesizer"
    VALIDATOR = "validator"


@dataclass
class AgentRequest:
    """Solicitud del agente"""
    query: str
    priority: PriorityLevel = PriorityLevel.MEDIUM
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AgentResponse:
    """Respuesta del agente"""
    success: bool
    content: str
    summary: Optional[str] = None
    confidence_score: float = 0.0
    processing_time: float = 0.0
    error: Optional[str] = None
    sources: List[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if self.meta_data is None:
            self.meta_data = {}


@dataclass
class Task:
    """Tarea del agente"""
    id: str
    title: str
    agent_type: AgentType
    status: TaskStatus = TaskStatus.PENDING
    priority: PriorityLevel = PriorityLevel.MEDIUM
    description: Optional[str] = None
    conversation_id: Optional[str] = None
    dependencies: List[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.meta_data is None:
            self.meta_data = {}


@dataclass
class SystemStatus:
    """Estado del sistema"""
    status: str = "running"
    uptime: float = 0.0
    active_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    memory_usage: Optional[str] = None
    cpu_usage: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.meta_data is None:
            self.meta_data = {}


@dataclass
class AgentStatus:
    """Estado de un agente específico"""
    agent_id: str
    agent_type: AgentType
    status: str = "idle"
    is_available: bool = True
    current_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    uptime: float = 0.0
    last_activity: Optional[datetime] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.meta_data is None:
            self.meta_data = {} 