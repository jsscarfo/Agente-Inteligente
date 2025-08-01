"""
🤖 Agente Inteligente - Módulo Principal

Este módulo contiene el núcleo del sistema de agente inteligente,
incluyendo la clase principal IntelligentAgent y todos los componentes
necesarios para el procesamiento de peticiones complejas.
"""

from .core.intelligent_agent import IntelligentAgent
from .core.config import AgentConfig
from .core.models_simple import AgentRequest, AgentResponse, TaskStatus, PriorityLevel, AgentType

__version__ = "1.0.0"
__author__ = "Agente Inteligente Team"
__email__ = "soporte@agente-inteligente.com"

__all__ = [
    "IntelligentAgent",
    "AgentConfig", 
    "AgentRequest",
    "AgentResponse",
    "TaskStatus",
    "PriorityLevel",
    "AgentType"
] 