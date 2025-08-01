"""
🔄 Sistema de Flujo de Trabajo con LangGraph del Agente Inteligente

Este módulo implementa un sistema de flujo de trabajo usando LangGraph
que coordina múltiples agentes y tareas para procesar peticiones complejas.
"""

import asyncio
import uuid
from typing import List, Dict, Any, Optional, TypedDict, Annotated
from datetime import datetime
from enum import Enum

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from loguru import logger

from .config import get_config
from .models import AgentRequest, AgentResponse, Task, TaskStatus, AgentType
from .rag_system import get_rag_system


class WorkflowState(TypedDict):
    """Estado del flujo de trabajo"""
    messages: Annotated[List, add_messages]
    request: AgentRequest
    tasks: List[Task]
    current_task: Optional[Task]
    results: Dict[str, Any]
    context: Dict[str, Any]
    metadata: Dict[str, Any]


class WorkflowStep(str, Enum):
    """Pasos del flujo de trabajo"""
    ANALYZE_REQUEST = "analyze_request"
    PLAN_TASKS = "plan_tasks"
    EXECUTE_RESEARCH = "execute_research"
    EXECUTE_ANALYSIS = "execute_analysis"
    EXECUTE_SYNTHESIS = "execute_synthesis"
    VALIDATE_RESPONSE = "validate_response"
    GENERATE_FINAL_RESPONSE = "generate_final_response"


class WorkflowGraph:
    """
    Grafo de flujo de trabajo del Agente Inteligente
    
    Coordina la ejecución de múltiples agentes y tareas
    usando LangGraph para crear flujos de trabajo complejos.
    """
    
    def __init__(self):
        self.config = get_config()
        self.rag_system = get_rag_system()
        
        # Componentes del grafo
        self.llm = None
        self.graph = None
        self.memory = None
        
        # Configuración
        self.max_iterations = 10
        self.is_initialized = False
    
    async def initialize(self):
        """Inicializar el grafo de flujo de trabajo"""
        try:
            logger.info("🔄 Inicializando grafo de flujo de trabajo...")
            
            # Inicializar LLM
            self.llm = ChatOpenAI(
                openai_api_key=self.config.openai_api_key,
                model=self.config.openai_model,
                temperature=0.3
            )
            
            # Crear grafo
            self._create_graph()
            
            # Configurar memoria
            self.memory = MemorySaver()
            
            self.is_initialized = True
            logger.info("✅ Grafo de flujo de trabajo inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando grafo de flujo: {e}")
            raise
    
    def _create_graph(self):
        """Crear el grafo de flujo de trabajo"""
        try:
            # Crear grafo de estado
            workflow = StateGraph(WorkflowState)
            
            # Añadir nodos
            workflow.add_node(WorkflowStep.ANALYZE_REQUEST, self._analyze_request)
            workflow.add_node(WorkflowStep.PLAN_TASKS, self._plan_tasks)
            workflow.add_node(WorkflowStep.EXECUTE_RESEARCH, self._execute_research)
            workflow.add_node(WorkflowStep.EXECUTE_ANALYSIS, self._execute_analysis)
            workflow.add_node(WorkflowStep.EXECUTE_SYNTHESIS, self._execute_synthesis)
            workflow.add_node(WorkflowStep.VALIDATE_RESPONSE, self._validate_response)
            workflow.add_node(WorkflowStep.GENERATE_FINAL_RESPONSE, self._generate_final_response)
            
            # Definir flujo
            workflow.set_entry_point(WorkflowStep.ANALYZE_REQUEST)
            
            # Flujo principal
            workflow.add_edge(WorkflowStep.ANALYZE_REQUEST, WorkflowStep.PLAN_TASKS)
            workflow.add_edge(WorkflowStep.PLAN_TASKS, WorkflowStep.EXECUTE_RESEARCH)
            workflow.add_edge(WorkflowStep.EXECUTE_RESEARCH, WorkflowStep.EXECUTE_ANALYSIS)
            workflow.add_edge(WorkflowStep.EXECUTE_ANALYSIS, WorkflowStep.EXECUTE_SYNTHESIS)
            workflow.add_edge(WorkflowStep.EXECUTE_SYNTHESIS, WorkflowStep.VALIDATE_RESPONSE)
            workflow.add_edge(WorkflowStep.VALIDATE_RESPONSE, WorkflowStep.GENERATE_FINAL_RESPONSE)
            workflow.add_edge(WorkflowStep.GENERATE_FINAL_RESPONSE, END)
            
            # Compilar grafo
            self.graph = workflow.compile(
                checkpointer=self.memory,
                interrupt_before=[WorkflowStep.EXECUTE_RESEARCH, WorkflowStep.EXECUTE_ANALYSIS],
                interrupt_after=[WorkflowStep.EXECUTE_RESEARCH, WorkflowStep.EXECUTE_ANALYSIS]
            )
            
            logger.info("✅ Grafo de flujo de trabajo creado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error creando grafo: {e}")
            raise
    
    async def _analyze_request(self, state: WorkflowState) -> WorkflowState:
        """Analizar la petición del usuario"""
        try:
            request = state["request"]
            
            # Prompt para análisis
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """Eres un analista experto en procesar peticiones complejas.
                
                Tu tarea es analizar la petición del usuario y determinar:
                1. El tipo de petición (investigación, análisis, síntesis, etc.)
                2. Los temas principales involucrados
                3. La complejidad de la petición
                4. Los recursos necesarios
                
                Responde en formato JSON con la siguiente estructura:
                {
                    "request_type": "tipo_de_peticion",
                    "main_topics": ["tema1", "tema2"],
                    "complexity": "baja|media|alta",
                    "required_resources": ["recurso1", "recurso2"],
                    "estimated_tasks": 3,
                    "priority": "baja|media|alta|crítica"
                }"""),
                ("human", "Petición: {request}")
            ])
            
            # Generar análisis
            chain = analysis_prompt | self.llm
            response = await chain.ainvoke({"request": request.query})
            
            # Parsear respuesta
            import json
            analysis = json.loads(response.content)
            
            # Actualizar estado
            state["context"]["analysis"] = analysis
            state["metadata"]["request_type"] = analysis.get("request_type")
            state["metadata"]["complexity"] = analysis.get("complexity")
            
            logger.info(f"📊 Análisis completado: {analysis.get('request_type')}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error analizando petición: {e}")
            state["context"]["analysis"] = {"error": str(e)}
            return state
    
    async def _plan_tasks(self, state: WorkflowState) -> WorkflowState:
        """Planificar las tareas necesarias"""
        try:
            request = state["request"]
            analysis = state["context"].get("analysis", {})
            
            # Prompt para planificación
            planning_prompt = ChatPromptTemplate.from_messages([
                ("system", """Eres un planificador experto en descomponer peticiones complejas en tareas manejables.
                
                Basándote en el análisis de la petición, crea un plan de tareas que incluya:
                1. Tareas de investigación para recopilar información
                2. Tareas de análisis para procesar la información
                3. Tareas de síntesis para generar la respuesta final
                
                Cada tarea debe tener:
                - ID único
                - Título descriptivo
                - Descripción detallada
                - Tipo de agente responsable
                - Prioridad
                - Dependencias (si las hay)
                
                Responde en formato JSON con la siguiente estructura:
                {
                    "tasks": [
                        {
                            "id": "task_1",
                            "title": "Título de la tarea",
                            "description": "Descripción detallada",
                            "agent_type": "research|analysis|synthesis",
                            "priority": "low|medium|high|critical",
                            "dependencies": []
                        }
                    ]
                }"""),
                ("human", """Petición: {request}
                
                Análisis: {analysis}
                
                Genera un plan de tareas detallado.""")
            ])
            
            # Generar plan
            chain = planning_prompt | self.llm
            response = await chain.ainvoke({
                "request": request.query,
                "analysis": json.dumps(analysis)
            })
            
            # Parsear respuesta
            import json
            plan = json.loads(response.content)
            
            # Crear tareas
            tasks = []
            for task_data in plan.get("tasks", []):
                task = Task(
                    id=task_data["id"],
                    title=task_data["title"],
                    description=task_data["description"],
                    agent_type=AgentType(task_data["agent_type"]),
                    priority=task_data["priority"],
                    dependencies=task_data.get("dependencies", [])
                )
                tasks.append(task)
            
            # Actualizar estado
            state["tasks"] = tasks
            state["context"]["plan"] = plan
            
            logger.info(f"📋 Planificación completada: {len(tasks)} tareas creadas")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error planificando tareas: {e}")
            state["tasks"] = []
            return state
    
    async def _execute_research(self, state: WorkflowState) -> WorkflowState:
        """Ejecutar tareas de investigación"""
        try:
            research_tasks = [task for task in state["tasks"] if task.agent_type == AgentType.RESEARCH]
            
            if not research_tasks:
                logger.info("🔍 No hay tareas de investigación")
                return state
            
            research_results = []
            
            for task in research_tasks:
                logger.info(f"🔍 Ejecutando tarea de investigación: {task.title}")
                
                # Buscar información usando RAG
                search_results = await self.rag_system.search(task.description, max_results=5)
                
                # Generar respuesta de investigación
                research_prompt = ChatPromptTemplate.from_messages([
                    ("system", """Eres un investigador experto. Analiza la información encontrada y genera un resumen estructurado.
                    
                    Incluye:
                    - Puntos clave encontrados
                    - Fuentes relevantes
                    - Conclusiones principales
                    - Información faltante (si la hay)"""),
                    ("human", """Tarea: {task_description}
                    
                    Información encontrada:
                    {search_results}
                    
                    Genera un resumen de investigación estructurado.""")
                ])
                
                chain = research_prompt | self.llm
                response = await chain.ainvoke({
                    "task_description": task.description,
                    "search_results": json.dumps(search_results, indent=2)
                })
                
                # Actualizar tarea
                task.status = TaskStatus.COMPLETED
                task.result = {
                    "content": response.content,
                    "sources": search_results,
                    "completed_at": datetime.utcnow().isoformat()
                }
                
                research_results.append({
                    "task_id": task.id,
                    "result": task.result
                })
            
            # Actualizar estado
            state["results"]["research"] = research_results
            state["context"]["research_completed"] = True
            
            logger.info(f"✅ Investigación completada: {len(research_results)} tareas")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando investigación: {e}")
            state["results"]["research"] = []
            return state
    
    async def _execute_analysis(self, state: WorkflowState) -> WorkflowState:
        """Ejecutar tareas de análisis"""
        try:
            analysis_tasks = [task for task in state["tasks"] if task.agent_type == AgentType.ANALYSIS]
            
            if not analysis_tasks:
                logger.info("📊 No hay tareas de análisis")
                return state
            
            analysis_results = []
            research_results = state["results"].get("research", [])
            
            for task in analysis_tasks:
                logger.info(f"📊 Ejecutando tarea de análisis: {task.title}")
                
                # Preparar contexto de investigación
                research_context = ""
                for result in research_results:
                    research_context += f"\n\n{result['result']['content']}"
                
                # Generar análisis
                analysis_prompt = ChatPromptTemplate.from_messages([
                    ("system", """Eres un analista experto. Analiza la información proporcionada y genera insights profundos.
                    
                    Tu análisis debe incluir:
                    - Patrones identificados
                    - Tendencias observadas
                    - Relaciones entre conceptos
                    - Implicaciones y conclusiones
                    - Recomendaciones (si aplica)"""),
                    ("human", """Tarea de análisis: {task_description}
                    
                    Información de investigación:
                    {research_context}
                    
                    Genera un análisis detallado y estructurado.""")
                ])
                
                chain = analysis_prompt | self.llm
                response = await chain.ainvoke({
                    "task_description": task.description,
                    "research_context": research_context
                })
                
                # Actualizar tarea
                task.status = TaskStatus.COMPLETED
                task.result = {
                    "content": response.content,
                    "analysis_type": "pattern_analysis",
                    "completed_at": datetime.utcnow().isoformat()
                }
                
                analysis_results.append({
                    "task_id": task.id,
                    "result": task.result
                })
            
            # Actualizar estado
            state["results"]["analysis"] = analysis_results
            state["context"]["analysis_completed"] = True
            
            logger.info(f"✅ Análisis completado: {len(analysis_results)} tareas")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando análisis: {e}")
            state["results"]["analysis"] = []
            return state
    
    async def _execute_synthesis(self, state: WorkflowState) -> WorkflowState:
        """Ejecutar tareas de síntesis"""
        try:
            synthesis_tasks = [task for task in state["tasks"] if task.agent_type == AgentType.SYNTHESIS]
            
            if not synthesis_tasks:
                logger.info("🎯 No hay tareas de síntesis")
                return state
            
            synthesis_results = []
            research_results = state["results"].get("research", [])
            analysis_results = state["results"].get("analysis", [])
            
            for task in synthesis_tasks:
                logger.info(f"🎯 Ejecutando tarea de síntesis: {task.title}")
                
                # Preparar contexto completo
                context = f"Petición original: {state['request'].query}\n\n"
                
                if research_results:
                    context += "Información de investigación:\n"
                    for result in research_results:
                        context += f"- {result['result']['content'][:200]}...\n"
                
                if analysis_results:
                    context += "\nAnálisis realizados:\n"
                    for result in analysis_results:
                        context += f"- {result['result']['content'][:200]}...\n"
                
                # Generar síntesis
                synthesis_prompt = ChatPromptTemplate.from_messages([
                    ("system", """Eres un experto en síntesis. Combina toda la información disponible para crear una respuesta coherente y completa.
                    
                    Tu síntesis debe:
                    - Responder directamente a la petición original
                    - Integrar información de investigación y análisis
                    - Ser clara, estructurada y útil
                    - Incluir conclusiones y recomendaciones cuando sea apropiado"""),
                    ("human", """Tarea de síntesis: {task_description}
                    
                    Contexto completo:
                    {context}
                    
                    Genera una síntesis final completa.""")
                ])
                
                chain = synthesis_prompt | self.llm
                response = await chain.ainvoke({
                    "task_description": task.description,
                    "context": context
                })
                
                # Actualizar tarea
                task.status = TaskStatus.COMPLETED
                task.result = {
                    "content": response.content,
                    "synthesis_type": "final_response",
                    "completed_at": datetime.utcnow().isoformat()
                }
                
                synthesis_results.append({
                    "task_id": task.id,
                    "result": task.result
                })
            
            # Actualizar estado
            state["results"]["synthesis"] = synthesis_results
            state["context"]["synthesis_completed"] = True
            
            logger.info(f"✅ Síntesis completada: {len(synthesis_results)} tareas")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando síntesis: {e}")
            state["results"]["synthesis"] = []
            return state
    
    async def _validate_response(self, state: WorkflowState) -> WorkflowState:
        """Validar la respuesta generada"""
        try:
            synthesis_results = state["results"].get("synthesis", [])
            
            if not synthesis_results:
                logger.warning("⚠️ No hay resultados de síntesis para validar")
                return state
            
            # Obtener la respuesta principal
            main_response = synthesis_results[0]["result"]["content"]
            
            # Validar respuesta
            validation_prompt = ChatPromptTemplate.from_messages([
                ("system", """Eres un validador experto. Evalúa la calidad y precisión de la respuesta generada.
                
                Evalúa:
                1. Relevancia: ¿Responde directamente a la petición?
                2. Completitud: ¿Cubre todos los aspectos solicitados?
                3. Precisión: ¿La información es correcta?
                4. Claridad: ¿Es fácil de entender?
                5. Estructura: ¿Está bien organizada?
                
                Responde en formato JSON:
                {
                    "is_valid": true/false,
                    "confidence_score": 0.0-1.0,
                    "issues": ["problema1", "problema2"],
                    "suggestions": ["sugerencia1", "sugerencia2"],
                    "overall_quality": "excelente|buena|regular|mala"
                }"""),
                ("human", """Petición original: {request}
                
                Respuesta generada:
                {response}
                
                Evalúa la calidad de la respuesta.""")
            ])
            
            chain = validation_prompt | self.llm
            response = await chain.ainvoke({
                "request": state["request"].query,
                "response": main_response
            })
            
            # Parsear validación
            import json
            validation = json.loads(response.content)
            
            # Actualizar estado
            state["context"]["validation"] = validation
            state["metadata"]["confidence_score"] = validation.get("confidence_score", 0.0)
            state["metadata"]["is_valid"] = validation.get("is_valid", False)
            
            logger.info(f"✅ Validación completada: {validation.get('overall_quality')}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error validando respuesta: {e}")
            state["context"]["validation"] = {"error": str(e)}
            return state
    
    async def _generate_final_response(self, state: WorkflowState) -> WorkflowState:
        """Generar la respuesta final"""
        try:
            synthesis_results = state["results"].get("synthesis", [])
            validation = state["context"].get("validation", {})
            
            if not synthesis_results:
                # Generar respuesta de error
                final_response = "Lo siento, no pude procesar tu petición correctamente."
            else:
                main_response = synthesis_results[0]["result"]["content"]
                
                # Si la validación indica problemas, mejorar la respuesta
                if not validation.get("is_valid", True):
                    improvement_prompt = ChatPromptTemplate.from_messages([
                        ("system", """Mejora la respuesta basándote en los problemas identificados.
                        
                        Mantén la información correcta pero:
                        - Corrige errores identificados
                        - Añade información faltante
                        - Mejora la claridad y estructura
                        - Responde directamente a la petición original"""),
                        ("human", """Petición original: {request}
                        
                        Respuesta actual:
                        {current_response}
                        
                        Problemas identificados:
                        {issues}
                        
                        Sugerencias:
                        {suggestions}
                        
                        Genera una respuesta mejorada.""")
                    ])
                    
                    chain = improvement_prompt | self.llm
                    response = await chain.ainvoke({
                        "request": state["request"].query,
                        "current_response": main_response,
                        "issues": validation.get("issues", []),
                        "suggestions": validation.get("suggestions", [])
                    })
                    
                    final_response = response.content
                else:
                    final_response = main_response
            
            # Crear respuesta final
            state["results"]["final_response"] = {
                "content": final_response,
                "confidence_score": state["metadata"].get("confidence_score", 0.0),
                "validation": validation,
                "tasks_executed": len(state["tasks"]),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info("✅ Respuesta final generada")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error generando respuesta final: {e}")
            state["results"]["final_response"] = {
                "content": f"Lo siento, ocurrió un error: {str(e)}",
                "confidence_score": 0.0,
                "error": str(e)
            }
            return state
    
    async def execute_workflow(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Ejecutar el flujo de trabajo completo
        
        Args:
            request: Petición del usuario
            
        Returns:
            Resultado del flujo de trabajo
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("Grafo de flujo de trabajo no inicializado")
            
            # Estado inicial
            initial_state = WorkflowState(
                messages=[],
                request=request,
                tasks=[],
                current_task=None,
                results={},
                context={},
                metadata={
                    "workflow_id": str(uuid.uuid4()),
                    "started_at": datetime.utcnow().isoformat()
                }
            )
            
            # Ejecutar grafo
            logger.info(f"🔄 Iniciando flujo de trabajo: {initial_state['metadata']['workflow_id']}")
            
            result = await self.graph.ainvoke(initial_state)
            
            # Procesar resultado
            final_response = result["results"].get("final_response", {})
            
            response_data = {
                "success": True,
                "content": final_response.get("content", ""),
                "confidence_score": final_response.get("confidence_score", 0.0),
                "workflow_id": initial_state["metadata"]["workflow_id"],
                "tasks_executed": len(result["tasks"]),
                "execution_time": datetime.utcnow().isoformat(),
                "metadata": {
                    "workflow_steps": list(WorkflowStep),
                    "validation": result["context"].get("validation", {}),
                    "analysis": result["context"].get("analysis", {})
                }
            }
            
            logger.info(f"✅ Flujo de trabajo completado: {response_data['workflow_id']}")
            return response_data
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando flujo de trabajo: {e}")
            return {
                "success": False,
                "content": f"Error en el flujo de trabajo: {str(e)}",
                "confidence_score": 0.0,
                "error": str(e)
            }


# Instancia global del grafo de flujo de trabajo
workflow_graph = WorkflowGraph()


def get_workflow_graph() -> WorkflowGraph:
    """Obtener el grafo de flujo de trabajo"""
    return workflow_graph 