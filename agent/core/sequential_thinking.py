#!/usr/bin/env python3
"""
🧠 Sequential Thinking Module
Implementa razonamiento secuencial para mejorar la resolución de problemas complejos
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class ThinkingStepType(Enum):
    """Tipos de pasos de razonamiento"""
    ANALYSIS = "analysis"
    DECOMPOSITION = "decomposition"
    REASONING = "reasoning"
    VALIDATION = "validation"
    SYNTHESIS = "synthesis"
    DECISION = "decision"
    EXECUTION = "execution"


@dataclass
class ThinkingStep:
    """Un paso individual en el proceso de razonamiento secuencial"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step_type: ThinkingStepType = ThinkingStepType.REASONING
    description: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    output_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class ThinkingSession:
    """Una sesión completa de razonamiento secuencial"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    steps: List[ThinkingStep] = field(default_factory=list)
    current_step: int = 0
    status: str = "initialized"  # initialized, running, completed, failed
    final_answer: Optional[str] = None
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class SequentialThinkingEngine:
    """Motor de razonamiento secuencial"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.sessions: Dict[str, ThinkingSession] = {}
        
    async def create_thinking_session(self, problem: str, context: Dict[str, Any] = None) -> ThinkingSession:
        """Crear una nueva sesión de razonamiento"""
        session = ThinkingSession(
            problem=problem,
            context=context or {}
        )
        self.sessions[session.id] = session
        logger.info(f"🧠 Nueva sesión de razonamiento creada: {session.id}")
        return session
    
    async def analyze_problem(self, session: ThinkingSession) -> ThinkingStep:
        """Analizar el problema y crear un plan de pasos"""
        step = ThinkingStep(
            step_type=ThinkingStepType.ANALYSIS,
            description="Análisis inicial del problema",
            input_data={"problem": session.problem, "context": session.context}
        )
        
        # Prompt para análisis del problema
        analysis_prompt = f"""
        Analiza el siguiente problema y crea un plan de pasos para resolverlo:
        
        PROBLEMA: {session.problem}
        CONTEXTO: {json.dumps(session.context, indent=2)}
        
        Tu tarea es:
        1. Identificar los componentes clave del problema
        2. Determinar qué información necesitas
        3. Crear un plan de pasos lógicos para la solución
        4. Identificar posibles obstáculos
        
        Responde en formato JSON:
        {{
            "problem_components": ["lista de componentes identificados"],
            "required_information": ["información necesaria"],
            "solution_steps": ["pasos para resolver"],
            "potential_obstacles": ["obstáculos identificados"],
            "confidence": 0.85
        }}
        """
        
        try:
            if self.llm_client:
                response = await self.llm_client.generate(analysis_prompt)
                analysis_result = json.loads(response)
            else:
                # Fallback para testing
                analysis_result = {
                    "problem_components": ["componente1", "componente2"],
                    "required_information": ["info1", "info2"],
                    "solution_steps": ["paso1", "paso2", "paso3"],
                    "potential_obstacles": ["obstáculo1"],
                    "confidence": 0.8
                }
            
            step.output_data = analysis_result
            step.reasoning = f"Análisis completado. Componentes identificados: {len(analysis_result.get('problem_components', []))}"
            step.confidence = analysis_result.get('confidence', 0.8)
            step.status = "completed"
            step.completed_at = datetime.utcnow()
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            logger.error(f"Error en análisis del problema: {e}")
        
        session.steps.append(step)
        return step
    
    async def decompose_problem(self, session: ThinkingSession, analysis_step: ThinkingStep) -> List[ThinkingStep]:
        """Descomponer el problema en sub-problemas más pequeños"""
        steps = []
        solution_steps = analysis_step.output_data.get('solution_steps', [])
        
        for i, step_desc in enumerate(solution_steps):
            step = ThinkingStep(
                step_type=ThinkingStepType.DECOMPOSITION,
                description=f"Paso {i+1}: {step_desc}",
                input_data={"step_description": step_desc, "step_number": i+1},
                dependencies=[analysis_step.id]
            )
            
            # Prompt para descomponer cada paso
            decomposition_prompt = f"""
            Descompón el siguiente paso en acciones más específicas:
            
            PASO: {step_desc}
            CONTEXTO DEL PROBLEMA: {session.problem}
            
            Proporciona:
            1. Acciones específicas a realizar
            2. Recursos necesarios
            3. Criterios de éxito
            4. Posibles alternativas
            
            Responde en formato JSON:
            {{
                "specific_actions": ["acción1", "acción2"],
                "required_resources": ["recurso1", "recurso2"],
                "success_criteria": ["criterio1", "criterio2"],
                "alternatives": ["alternativa1"],
                "estimated_difficulty": "easy|medium|hard",
                "confidence": 0.85
            }}
            """
            
            try:
                if self.llm_client:
                    response = await self.llm_client.generate(decomposition_prompt)
                    decomposition_result = json.loads(response)
                else:
                    decomposition_result = {
                        "specific_actions": [f"Acción específica para {step_desc}"],
                        "required_resources": ["recurso1"],
                        "success_criteria": ["criterio1"],
                        "alternatives": [],
                        "estimated_difficulty": "medium",
                        "confidence": 0.8
                    }
                
                step.output_data = decomposition_result
                step.reasoning = f"Paso descompuesto en {len(decomposition_result.get('specific_actions', []))} acciones"
                step.confidence = decomposition_result.get('confidence', 0.8)
                step.status = "completed"
                step.completed_at = datetime.utcnow()
                
            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                logger.error(f"Error descomponiendo paso {i+1}: {e}")
            
            steps.append(step)
            session.steps.append(step)
        
        return steps
    
    async def execute_reasoning_step(self, session: ThinkingSession, step: ThinkingStep) -> ThinkingStep:
        """Ejecutar un paso de razonamiento específico"""
        step.status = "running"
        
        reasoning_prompt = f"""
        Ejecuta el siguiente paso de razonamiento:
        
        PASO: {step.description}
        ACCIONES ESPECÍFICAS: {step.output_data.get('specific_actions', [])}
        CONTEXTO: {session.problem}
        
        Realiza el razonamiento paso a paso:
        1. Considera la información disponible
        2. Aplica lógica y conocimiento relevante
        3. Genera conclusiones específicas
        4. Evalúa la confianza en tus conclusiones
        
        Responde en formato JSON:
        {{
            "reasoning_process": "proceso de razonamiento detallado",
            "conclusions": ["conclusión1", "conclusión2"],
            "evidence": ["evidencia1", "evidencia2"],
            "confidence": 0.85,
            "next_steps": ["siguiente paso recomendado"]
        }}
        """
        
        try:
            if self.llm_client:
                response = await self.llm_client.generate(reasoning_prompt)
                reasoning_result = json.loads(response)
            else:
                reasoning_result = {
                    "reasoning_process": f"Razonamiento aplicado para {step.description}",
                    "conclusions": [f"Conclusión para {step.description}"],
                    "evidence": ["Evidencia disponible"],
                    "confidence": 0.8,
                    "next_steps": ["Continuar al siguiente paso"]
                }
            
            step.output_data.update(reasoning_result)
            step.reasoning = reasoning_result.get('reasoning_process', '')
            step.confidence = reasoning_result.get('confidence', 0.8)
            step.status = "completed"
            step.completed_at = datetime.utcnow()
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            logger.error(f"Error ejecutando paso de razonamiento: {e}")
        
        return step
    
    async def validate_step(self, session: ThinkingSession, step: ThinkingStep) -> ThinkingStep:
        """Validar un paso completado"""
        validation_step = ThinkingStep(
            step_type=ThinkingStepType.VALIDATION,
            description=f"Validación de: {step.description}",
            input_data={"step_to_validate": step.id, "step_output": step.output_data},
            dependencies=[step.id]
        )
        
        validation_prompt = f"""
        Valida el siguiente paso completado:
        
        PASO VALIDADO: {step.description}
        RESULTADO: {json.dumps(step.output_data, indent=2)}
        CONTEXTO: {session.problem}
        
        Evalúa:
        1. ¿El resultado es lógicamente consistente?
        2. ¿Se cumplieron los criterios de éxito?
        3. ¿Hay inconsistencias o errores?
        4. ¿La confianza es apropiada?
        
        Responde en formato JSON:
        {{
            "is_valid": true,
            "validation_score": 0.9,
            "issues_found": ["problema1"],
            "recommendations": ["recomendación1"],
            "confidence_adjustment": 0.05
        }}
        """
        
        try:
            if self.llm_client:
                response = await self.llm_client.generate(validation_prompt)
                validation_result = json.loads(response)
            else:
                validation_result = {
                    "is_valid": True,
                    "validation_score": 0.9,
                    "issues_found": [],
                    "recommendations": ["Continuar al siguiente paso"],
                    "confidence_adjustment": 0.0
                }
            
            validation_step.output_data = validation_result
            validation_step.reasoning = f"Validación completada. Score: {validation_result.get('validation_score', 0)}"
            validation_step.confidence = validation_result.get('validation_score', 0.9)
            validation_step.status = "completed"
            validation_step.completed_at = datetime.utcnow()
            
            # Ajustar confianza del paso original
            if validation_result.get('is_valid', True):
                step.confidence += validation_result.get('confidence_adjustment', 0.0)
                step.confidence = min(1.0, max(0.0, step.confidence))
            
        except Exception as e:
            validation_step.status = "failed"
            validation_step.error = str(e)
            logger.error(f"Error en validación: {e}")
        
        session.steps.append(validation_step)
        return validation_step
    
    async def synthesize_results(self, session: ThinkingSession) -> ThinkingStep:
        """Sintetizar todos los resultados en una respuesta final"""
        synthesis_step = ThinkingStep(
            step_type=ThinkingStepType.SYNTHESIS,
            description="Síntesis de resultados",
            input_data={"all_steps": [step.id for step in session.steps]}
        )
        
        # Recopilar resultados de todos los pasos
        all_results = []
        total_confidence = 0.0
        completed_steps = 0
        
        for step in session.steps:
            if step.status == "completed" and step.step_type in [ThinkingStepType.REASONING, ThinkingStepType.DECOMPOSITION]:
                all_results.append({
                    "step": step.description,
                    "conclusions": step.output_data.get('conclusions', []),
                    "confidence": step.confidence
                })
                total_confidence += step.confidence
                completed_steps += 1
        
        synthesis_prompt = f"""
        Sintetiza los siguientes resultados en una respuesta final:
        
        PROBLEMA ORIGINAL: {session.problem}
        RESULTADOS DE PASOS:
        {json.dumps(all_results, indent=2)}
        
        Crea una síntesis que:
        1. Resuma los hallazgos principales
        2. Proporcione una respuesta clara al problema
        3. Identifique las conclusiones más importantes
        4. Sugiera próximos pasos si es necesario
        
        Responde en formato JSON:
        {{
            "final_answer": "respuesta final al problema",
            "key_findings": ["hallazgo1", "hallazgo2"],
            "main_conclusions": ["conclusión1", "conclusión2"],
            "next_steps": ["paso siguiente"],
            "overall_confidence": 0.85
        }}
        """
        
        try:
            if self.llm_client:
                response = await self.llm_client.generate(synthesis_prompt)
                synthesis_result = json.loads(response)
            else:
                synthesis_result = {
                    "final_answer": f"Respuesta sintetizada para: {session.problem}",
                    "key_findings": ["Hallazgo principal"],
                    "main_conclusions": ["Conclusión principal"],
                    "next_steps": ["Próximo paso recomendado"],
                    "overall_confidence": total_confidence / max(completed_steps, 1)
                }
            
            synthesis_step.output_data = synthesis_result
            synthesis_step.reasoning = "Síntesis completada de todos los pasos"
            synthesis_step.confidence = synthesis_result.get('overall_confidence', 0.8)
            synthesis_step.status = "completed"
            synthesis_step.completed_at = datetime.utcnow()
            
            # Actualizar sesión
            session.final_answer = synthesis_result.get('final_answer')
            session.confidence = synthesis_result.get('overall_confidence', 0.8)
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            
        except Exception as e:
            synthesis_step.status = "failed"
            synthesis_step.error = str(e)
            logger.error(f"Error en síntesis: {e}")
        
        session.steps.append(synthesis_step)
        return synthesis_step
    
    async def solve_problem(self, problem: str, context: Dict[str, Any] = None) -> ThinkingSession:
        """Resolver un problema completo usando razonamiento secuencial"""
        logger.info(f"🧠 Iniciando resolución secuencial del problema: {problem[:100]}...")
        
        # Crear sesión
        session = await self.create_thinking_session(problem, context)
        session.status = "running"
        
        try:
            # 1. Analizar el problema
            analysis_step = await self.analyze_problem(session)
            if analysis_step.status == "failed":
                raise Exception(f"Error en análisis: {analysis_step.error}")
            
            # 2. Descomponer en pasos
            decomposition_steps = await self.decompose_problem(session, analysis_step)
            
            # 3. Ejecutar cada paso de razonamiento
            for step in decomposition_steps:
                if step.status == "failed":
                    logger.warning(f"Paso fallido: {step.error}")
                    continue
                
                # Ejecutar razonamiento
                reasoning_step = await self.execute_reasoning_step(session, step)
                
                # Validar el paso
                await self.validate_step(session, reasoning_step)
            
            # 4. Sintetizar resultados
            await self.synthesize_results(session)
            
            logger.info(f"✅ Resolución secuencial completada. Confianza: {session.confidence:.2f}")
            
        except Exception as e:
            session.status = "failed"
            session.completed_at = datetime.utcnow()
            logger.error(f"❌ Error en resolución secuencial: {e}")
        
        return session
    
    def get_session_summary(self, session: ThinkingSession) -> Dict[str, Any]:
        """Obtener un resumen de la sesión"""
        completed_steps = [s for s in session.steps if s.status == "completed"]
        failed_steps = [s for s in session.steps if s.status == "failed"]
        
        return {
            "session_id": session.id,
            "problem": session.problem,
            "status": session.status,
            "total_steps": len(session.steps),
            "completed_steps": len(completed_steps),
            "failed_steps": len(failed_steps),
            "confidence": session.confidence,
            "final_answer": session.final_answer,
            "duration": (session.completed_at - session.created_at).total_seconds() if session.completed_at else None
        }
    
    def export_session(self, session: ThinkingSession) -> Dict[str, Any]:
        """Exportar sesión completa para análisis"""
        return {
            "session": {
                "id": session.id,
                "problem": session.problem,
                "context": session.context,
                "status": session.status,
                "confidence": session.confidence,
                "final_answer": session.final_answer,
                "created_at": session.created_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            },
            "steps": [
                {
                    "id": step.id,
                    "step_type": step.step_type.value,
                    "description": step.description,
                    "status": step.status,
                    "confidence": step.confidence,
                    "reasoning": step.reasoning,
                    "output_data": step.output_data,
                    "error": step.error,
                    "created_at": step.created_at.isoformat(),
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None
                }
                for step in session.steps
            ]
        }


# Funciones de utilidad
async def create_thinking_engine(llm_client=None) -> SequentialThinkingEngine:
    """Crear una instancia del motor de razonamiento secuencial"""
    return SequentialThinkingEngine(llm_client)


def format_thinking_output(session: ThinkingSession) -> str:
    """Formatear la salida del razonamiento para mostrar al usuario"""
    if not session.final_answer:
        return "❌ No se pudo completar el razonamiento"
    
    output = f"🧠 **Razonamiento Secuencial Completado**\n\n"
    output += f"**Problema:** {session.problem}\n\n"
    output += f"**Respuesta Final:** {session.final_answer}\n\n"
    output += f"**Confianza:** {session.confidence:.1%}\n\n"
    
    if session.steps:
        output += "**Pasos de Razonamiento:**\n"
        for i, step in enumerate(session.steps, 1):
            if step.status == "completed":
                output += f"{i}. ✅ {step.description}\n"
                if step.reasoning:
                    output += f"   💭 {step.reasoning[:100]}...\n"
            else:
                output += f"{i}. ❌ {step.description} (Error: {step.error})\n"
    
    return output 