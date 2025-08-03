#!/usr/bin/env python3
"""
🧠 Demo de Sequential Thinking
Demuestra las capacidades de razonamiento secuencial del Agente Inteligente
"""

import asyncio
import json
from pathlib import Path
import sys

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from agent import IntelligentAgent


async def demo_sequential_thinking():
    """Demo de razonamiento secuencial"""
    print("🧠 Demo de Sequential Thinking - Agente Inteligente")
    print("=" * 60)
    
    # Crear instancia del agente
    agent = IntelligentAgent()
    
    try:
        # Iniciar el agente
        print("🚀 Iniciando agente...")
        await agent.start()
        print("✅ Agente iniciado correctamente")
        
        # Mostrar información del sistema
        system_info = agent.get_system_info()
        print(f"\n📊 Información del Sistema:")
        print(f"   Versión: {system_info['version']}")
        print(f"   Sequential Thinking: {system_info['sequential_thinking']}")
        print(f"   RAG System: {system_info['rag_system']}")
        print(f"   LangGraph: {system_info['langgraph']}")
        
        # Problemas de ejemplo para demostrar Sequential Thinking
        problems = [
            {
                "title": "Problema de Planificación",
                "problem": "Necesito planificar una fiesta de cumpleaños para 20 personas en mi casa. Tengo un presupuesto de $500 y solo 2 semanas para prepararlo. ¿Cómo debería proceder?",
                "context": {
                    "location": "casa",
                    "budget": 500,
                    "timeframe": "2 semanas",
                    "guests": 20
                }
            },
            {
                "title": "Problema de Análisis",
                "problem": "Mi empresa está perdiendo clientes y las ventas han bajado 30% en los últimos 3 meses. ¿Cuáles podrían ser las causas y qué acciones debería tomar?",
                "context": {
                    "industry": "tecnología",
                    "company_size": "pequeña",
                    "decline_percentage": 30,
                    "time_period": "3 meses"
                }
            },
            {
                "title": "Problema de Toma de Decisiones",
                "problem": "Tengo dos ofertas de trabajo: una en una startup con salario menor pero más oportunidades de crecimiento, y otra en una empresa grande con mejor salario pero menos flexibilidad. ¿Cuál debería elegir?",
                "context": {
                    "startup_salary": 60000,
                    "corporate_salary": 80000,
                    "experience_level": "mid-level",
                    "location": "ciudad"
                }
            }
        ]
        
        # Ejecutar cada problema
        for i, problem_data in enumerate(problems, 1):
            print(f"\n{'='*60}")
            print(f"🧠 PROBLEMA {i}: {problem_data['title']}")
            print(f"{'='*60}")
            print(f"📝 Problema: {problem_data['problem']}")
            print(f"📋 Contexto: {json.dumps(problem_data['context'], indent=2)}")
            
            # Resolver usando Sequential Thinking
            print(f"\n🔄 Resolviendo con Sequential Thinking...")
            result = await agent.solve_with_sequential_thinking(
                problem=problem_data['problem'],
                context=problem_data['context']
            )
            
            # Mostrar resultados
            print(f"\n✅ Resultado:")
            print(f"   Éxito: {result['success']}")
            print(f"   Confianza: {result['confidence']:.1%}")
            print(f"   Pasos totales: {result['total_steps']}")
            print(f"   Pasos completados: {result['completed_steps']}")
            print(f"   Pasos fallidos: {result['failed_steps']}")
            
            print(f"\n💡 Respuesta:")
            print(result['formatted_output'])
            
            # Mostrar resumen detallado
            if result['summary']:
                print(f"\n📊 Resumen Detallado:")
                summary = result['summary']
                print(f"   ID Sesión: {summary.get('session_id', 'N/A')}")
                print(f"   Estado: {summary.get('status', 'N/A')}")
                print(f"   Duración: {summary.get('duration', 'N/A')} segundos")
                print(f"   Confianza Final: {summary.get('confidence', 0):.1%}")
        
        # Demo de recuperación de sesión
        if result.get('session_id'):
            print(f"\n{'='*60}")
            print(f"📋 RECUPERANDO SESIÓN DE RAZONAMIENTO")
            print(f"{'='*60}")
            
            session_data = await agent.get_thinking_session(result['session_id'])
            if session_data:
                print(f"✅ Sesión recuperada exitosamente")
                print(f"   ID: {session_data['session']['id']}")
                print(f"   Problema: {session_data['session']['problem'][:100]}...")
                print(f"   Estado: {session_data['session']['status']}")
                print(f"   Pasos: {len(session_data['steps'])}")
                
                # Mostrar algunos pasos de ejemplo
                print(f"\n📝 Pasos de Razonamiento:")
                for i, step in enumerate(session_data['steps'][:3], 1):  # Solo primeros 3
                    print(f"   {i}. {step['description']}")
                    print(f"      Tipo: {step['step_type']}")
                    print(f"      Estado: {step['status']}")
                    print(f"      Confianza: {step['confidence']:.1%}")
                    if step['reasoning']:
                        print(f"      Razonamiento: {step['reasoning'][:100]}...")
                    print()
            else:
                print("❌ No se pudo recuperar la sesión")
        
        print(f"\n{'='*60}")
        print(f"🎉 Demo completado exitosamente!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ Error en el demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Detener el agente
        print("\n🛑 Deteniendo agente...")
        await agent.stop()
        print("✅ Agente detenido correctamente")


async def demo_complex_problem():
    """Demo de un problema complejo usando Sequential Thinking"""
    print("\n🧠 Demo de Problema Complejo")
    print("=" * 60)
    
    agent = IntelligentAgent()
    
    try:
        await agent.start()
        
        # Problema complejo de múltiples capas
        complex_problem = """
        Soy el director de una escuela primaria y necesito resolver varios problemas simultáneos:
        
        1. Los resultados de matemáticas han bajado 25% en el último año
        2. Hay conflictos entre algunos maestros que afectan el ambiente laboral
        3. Los padres están preocupados por la seguridad en el recreo
        4. El presupuesto se redujo 15% pero necesitamos mejorar la infraestructura
        5. Tenemos un nuevo sistema de evaluación que los maestros no están usando correctamente
        
        Necesito un plan integral que aborde todos estos problemas de manera efectiva,
        considerando las limitaciones de presupuesto y tiempo, y que mejore tanto
        el rendimiento académico como el ambiente escolar.
        """
        
        context = {
            "school_type": "primaria",
            "student_count": 300,
            "teacher_count": 15,
            "budget_reduction": "15%",
            "math_decline": "25%",
            "timeframe": "6 meses"
        }
        
        print(f"📝 Problema Complejo:")
        print(complex_problem)
        print(f"📋 Contexto: {json.dumps(context, indent=2)}")
        
        print(f"\n🔄 Resolviendo con Sequential Thinking...")
        result = await agent.solve_with_sequential_thinking(complex_problem, context)
        
        print(f"\n✅ Resultado:")
        print(result['formatted_output'])
        
        # Mostrar estadísticas detalladas
        print(f"\n📊 Estadísticas del Razonamiento:")
        print(f"   Pasos totales: {result['total_steps']}")
        print(f"   Pasos exitosos: {result['completed_steps']}")
        print(f"   Pasos fallidos: {result['failed_steps']}")
        print(f"   Tasa de éxito: {result['completed_steps']/max(result['total_steps'], 1)*100:.1f}%")
        print(f"   Confianza final: {result['confidence']:.1%}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await agent.stop()


if __name__ == "__main__":
    print("🧠 Sequential Thinking Demo")
    print("Este demo muestra las capacidades de razonamiento secuencial del Agente Inteligente")
    print()
    
    # Ejecutar demos
    asyncio.run(demo_sequential_thinking())
    asyncio.run(demo_complex_problem())
    
    print("\n🎯 Beneficios del Sequential Thinking:")
    print("   ✅ Razonamiento paso a paso estructurado")
    print("   ✅ Descomposición de problemas complejos")
    print("   ✅ Validación de cada paso del proceso")
    print("   ✅ Transparencia en el proceso de decisión")
    print("   ✅ Mejor debugging y seguimiento")
    print("   ✅ Mayor confianza en las conclusiones")
    print("   ✅ Capacidad de manejar problemas multi-capa") 