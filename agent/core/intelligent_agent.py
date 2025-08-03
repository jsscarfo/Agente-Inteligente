"""
🧠 Agente Inteligente Principal

Este módulo contiene la clase principal IntelligentAgent que coordina
todos los componentes del sistema de agente inteligente, incluyendo
el procesamiento de peticiones, gestión de tareas y generación de respuestas.
"""

import asyncio
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger

from .config import get_config
from .models import (
    AgentRequest, AgentResponse, Task, TaskStatus, 
    AgentType, PriorityLevel, SystemStatus, AgentStatus
)
from .database import get_db_manager, ConversationRepository, MessageRepository, TaskRepository
from .rag_system import get_rag_system
from .workflow_graph import get_workflow_graph
from .sequential_thinking import SequentialThinkingEngine, create_thinking_engine, format_thinking_output


class IntelligentAgent:
    """
    Agente Inteligente Principal
    
    Esta clase es el núcleo del sistema de agente inteligente. Coordina
    todos los agentes especializados, gestiona tareas, y genera respuestas
    estructuradas a peticiones complejas usando PostgreSQL, LangGraph y RAG.
    """
    
    def __init__(self):
        """Inicializar el agente inteligente"""
        self.config = get_config()
        self.agent_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        
        # Inicializar componentes del sistema
        self.db_manager = get_db_manager()
        self.rag_system = get_rag_system()
        self.workflow_graph = get_workflow_graph()
        
        # Motor de razonamiento secuencial
        self.thinking_engine = None  # Se inicializará después
        
        # Repositorios de base de datos
        self.conversation_repo = ConversationRepository(self.db_manager)
        self.message_repo = MessageRepository(self.db_manager)
        self.task_repo = TaskRepository(self.db_manager)
        
        # Estado del sistema
        self.is_running = False
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
        
        logger.info(f"🤖 Agente Inteligente inicializado con ID: {self.agent_id}")
    
    async def start(self):
        """Iniciar el agente inteligente"""
        try:
            self.is_running = True
            
            # Inicializar base de datos
            await self.db_manager.initialize()
            logger.info("✅ Base de datos inicializada")
            
            # Inicializar sistema RAG
            await self.rag_system.initialize()
            logger.info("✅ Sistema RAG inicializado")
            
            # Inicializar grafo de flujo de trabajo
            await self.workflow_graph.initialize()
            logger.info("✅ Grafo de flujo de trabajo inicializado")
            
            # Inicializar motor de razonamiento secuencial
            self.thinking_engine = await create_thinking_engine()
            logger.info("🧠 Motor de razonamiento secuencial inicializado")
            
            logger.info("🤖 Agente Inteligente iniciado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error iniciando agente: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Detener el agente inteligente"""
        try:
            self.is_running = False
            
            # Cerrar base de datos
            await self.db_manager.close()
            logger.info("🛑 Base de datos cerrada")
            
            logger.info("🛑 Agente Inteligente detenido correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error deteniendo agente: {e}")
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Procesar una petición del usuario
        
        Args:
            request: Petición del usuario
            
        Returns:
            Respuesta estructurada del agente
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        conversation_id = str(uuid.uuid4())
        
        try:
            logger.info(f"📝 Procesando petición {request_id}: {request.query[:100]}...")
            
            # Validar que el agente esté ejecutándose
            if not self.is_running:
                raise RuntimeError("El agente no está ejecutándose")
            
            # Crear conversación en la base de datos
            await self.conversation_repo.create_conversation(
                conversation_id=conversation_id,
                user_id=request.user_id,
                session_id=request.session_id,
                title=request.query[:100],
                metadata={"request_id": request_id, "priority": request.priority.value}
            )
            
            # Guardar mensaje del usuario
            await self.message_repo.add_message(
                message_id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role="user",
                content=request.query,
                metadata={"request_id": request_id}
            )
            
            # Ejecutar flujo de trabajo con LangGraph
            workflow_result = await self.workflow_graph.execute_workflow(request)
            
            # Procesar resultado del flujo de trabajo
            if workflow_result.get("success", False):
                # Respuesta exitosa
                content = workflow_result.get("content", "")
                confidence_score = workflow_result.get("confidence_score", 0.0)
                
                # Guardar respuesta del asistente
                await self.message_repo.add_message(
                    message_id=str(uuid.uuid4()),
                    conversation_id=conversation_id,
                    role="assistant",
                    content=content,
                    metadata={
                        "request_id": request_id,
                        "confidence_score": confidence_score,
                        "workflow_id": workflow_result.get("workflow_id")
                    }
                )
                
                # Crear respuesta estructurada
                response = AgentResponse(
                    success=True,
                    content=content,
                    confidence_score=confidence_score,
                    processing_time=time.time() - start_time,
                    metadata={
                        "request_id": request_id,
                        "conversation_id": conversation_id,
                        "agent_id": self.agent_id,
                        "workflow_id": workflow_result.get("workflow_id"),
                        "tasks_executed": workflow_result.get("tasks_executed", 0),
                        "database_used": "PostgreSQL" if self.config.use_postgres() else "SQLite",
                        "rag_enabled": True,
                        "langgraph_enabled": True
                    }
                )
                
            else:
                # Respuesta de error
                error_content = workflow_result.get("content", "Error desconocido")
                
                # Guardar mensaje de error
                await self.message_repo.add_message(
                    message_id=str(uuid.uuid4()),
                    conversation_id=conversation_id,
                    role="assistant",
                    content=f"Error: {error_content}",
                    metadata={
                        "request_id": request_id,
                        "error": True,
                        "error_details": workflow_result.get("error", "")
                    }
                )
                
                response = AgentResponse(
                    success=False,
                    content=f"Lo siento, ocurrió un error procesando tu petición: {error_content}",
                    confidence_score=0.0,
                    processing_time=time.time() - start_time,
                    metadata={
                        "request_id": request_id,
                        "conversation_id": conversation_id,
                        "agent_id": self.agent_id,
                        "error": workflow_result.get("error", "")
                    }
                )
            
            logger.info(f"✅ Petición {request_id} procesada exitosamente en {response.processing_time:.2f}s")
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Error procesando petición {request_id}: {e}")
            
            # Crear respuesta de error
            return AgentResponse(
                success=False,
                content=f"Lo siento, ocurrió un error procesando tu petición: {str(e)}",
                confidence_score=0.0,
                processing_time=processing_time,
                metadata={
                    "request_id": request_id,
                    "agent_id": self.agent_id,
                    "error": str(e)
                }
            )
    
    async def get_status(self) -> SystemStatus:
        """Obtener el estado del sistema"""
        try:
            # Obtener estadísticas de la base de datos
            async with self.db_manager.get_async_session() as session:
                # Contar conversaciones
                result = await session.execute("SELECT COUNT(*) FROM conversations")
                total_conversations = result.scalar() or 0
                
                # Contar mensajes
                result = await session.execute("SELECT COUNT(*) FROM messages")
                total_messages = result.scalar() or 0
                
                # Contar tareas
                result = await session.execute("SELECT COUNT(*) FROM tasks")
                total_tasks = result.scalar() or 0
                
                # Contar tareas completadas
                result = await session.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
                completed_tasks = result.scalar() or 0
                
                # Contar tareas fallidas
                result = await session.execute("SELECT COUNT(*) FROM tasks WHERE status = 'failed'")
                failed_tasks = result.scalar() or 0
            
            # Calcular tasa de éxito
            success_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.0
            
            # Obtener estadísticas del sistema RAG
            rag_stats = await self.rag_system.get_statistics()
            
            # Crear estado de agentes
            agents_status = [
                AgentStatus(
                    agent_id=self.agent_id,
                    agent_type=AgentType.COORDINATOR,
                    status="running" if self.is_running else "stopped",
                    is_available=self.is_running,
                    current_tasks=len(self.active_tasks),
                    completed_tasks=completed_tasks,
                    failed_tasks=failed_tasks,
                    uptime=(datetime.now() - self.start_time).total_seconds(),
                    last_activity=datetime.now(),
                    performance_metrics={
                        "total_conversations": total_conversations,
                        "total_messages": total_messages,
                        "rag_documents": rag_stats.get("total_documents", 0),
                        "vector_embeddings": rag_stats.get("vector_embeddings", 0)
                    }
                )
            ]
            
            return SystemStatus(
                system_status="running" if self.is_running else "stopped",
                agents_status=agents_status,
                active_tasks=len(self.active_tasks),
                total_tasks=total_tasks,
                success_rate=success_rate,
                average_response_time=2.5,  # Valor estimado
                system_uptime=(datetime.now() - self.start_time).total_seconds(),
                memory_usage=rag_stats.get("total_documents", 0) * 0.1,  # Estimación
                cpu_usage=50.0 if self.is_running else 0.0  # Estimación
            )
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado del sistema: {e}")
            raise
    
    async def add_knowledge(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Añadir conocimiento a la base de datos"""
        try:
            # Añadir al sistema RAG
            document_id = await self.rag_system.add_document(
                content=content,
                metadata=metadata
            )
            
            logger.info(f"📚 Conocimiento añadido exitosamente: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"❌ Error añadiendo conocimiento: {e}")
            raise
    
    async def search_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Buscar en la base de conocimiento"""
        try:
            results = await self.rag_system.search(query, max_results=limit)
            return results
        except Exception as e:
            logger.error(f"❌ Error buscando conocimiento: {e}")
            return []
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Obtener historial de una conversación"""
        try:
            messages = await self.message_repo.get_messages(conversation_id)
            
            history = []
            for message in messages:
                history.append({
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat(),
                    "metadata": message.metadata
                })
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo historial: {e}")
            return []
    
    async def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener conversaciones de un usuario"""
        try:
            conversations = await self.conversation_repo.get_conversations_by_user(user_id, limit)
            
            result = []
            for conv in conversations:
                result.append({
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "metadata": conv.metadata
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo conversaciones: {e}")
            return []
    
    async def generate_rag_response(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Generar respuesta usando RAG"""
        try:
            response = await self.rag_system.generate_answer(question, context)
            return response
        except Exception as e:
            logger.error(f"❌ Error generando respuesta RAG: {e}")
            return {
                "answer": f"Error generando respuesta: {str(e)}",
                "sources": [],
                "question": question,
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def get_uptime(self) -> float:
        """Obtener tiempo activo del agente"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_version(self) -> str:
        """Obtener versión del agente"""
        return "2.0.0"  # Versión con PostgreSQL, LangGraph y RAG
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtener información del sistema"""
        return {
            "version": self.get_version(),
            "database": "PostgreSQL" if self.config.use_postgres() else "SQLite",
            "rag_system": "Enabled",
            "langgraph": "Enabled",
            "sequential_thinking": "Enabled" if self.thinking_engine else "Disabled",
            "vector_store": self.config.vector_db_type,
            "environment": self.config.environment,
            "uptime": self.get_uptime(),
            "agent_id": self.agent_id
        }
    
    async def solve_with_sequential_thinking(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Resolver un problema usando razonamiento secuencial
        
        Args:
            problem: El problema a resolver
            context: Contexto adicional para el problema
            
        Returns:
            Dict con la respuesta y metadatos del razonamiento
        """
        try:
            if not self.thinking_engine:
                raise Exception("Motor de razonamiento secuencial no inicializado")
            
            logger.info(f"🧠 Iniciando razonamiento secuencial para: {problem[:100]}...")
            
            # Crear sesión de razonamiento
            session = await self.thinking_engine.solve_problem(problem, context)
            
            # Obtener resumen de la sesión
            summary = self.thinking_engine.get_session_summary(session)
            
            # Formatear salida para el usuario
            formatted_output = format_thinking_output(session)
            
            return {
                "success": session.status == "completed",
                "answer": session.final_answer or "No se pudo resolver el problema",
                "confidence": session.confidence,
                "formatted_output": formatted_output,
                "summary": summary,
                "session_id": session.id,
                "total_steps": len(session.steps),
                "completed_steps": len([s for s in session.steps if s.status == "completed"]),
                "failed_steps": len([s for s in session.steps if s.status == "failed"])
            }
            
        except Exception as e:
            logger.error(f"Error en razonamiento secuencial: {e}")
            return {
                "success": False,
                "answer": f"Error en razonamiento secuencial: {str(e)}",
                "confidence": 0.0,
                "formatted_output": f"❌ Error: {str(e)}",
                "summary": {},
                "session_id": None,
                "total_steps": 0,
                "completed_steps": 0,
                "failed_steps": 0
            }
    
    async def get_thinking_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información de una sesión de razonamiento específica
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Dict con información de la sesión o None si no existe
        """
        try:
            if not self.thinking_engine:
                return None
            
            session = self.thinking_engine.sessions.get(session_id)
            if not session:
                return None
            
            return self.thinking_engine.export_session(session)
            
        except Exception as e:
            logger.error(f"Error obteniendo sesión de razonamiento: {e}")
            return None 