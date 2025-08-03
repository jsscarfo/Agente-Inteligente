<<<<<<< HEAD
#!/usr/bin/env python3
"""
📚 Ejemplo de Uso del Agente Inteligente

Este archivo contiene ejemplos prácticos de cómo usar el sistema
de agente inteligente para diferentes tipos de tareas.
"""

import asyncio
import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent import IntelligentAgent
from agent.core.models import AgentRequest, PriorityLevel


async def example_basic_query():
    """Ejemplo básico de consulta"""
    print("🔍 Ejemplo 1: Consulta Básica")
    print("=" * 50)
    
    agent = IntelligentAgent()
    await agent.start()
    
    try:
        # Crear petición simple
        request = AgentRequest(
            query="¿Qué es la inteligencia artificial?",
            priority=PriorityLevel.MEDIUM
        )
        
        print(f"📝 Petición: {request.query}")
        print("🔄 Procesando...")
        
        # Procesar petición
        response = await agent.process_request(request)
        
        # Mostrar resultado
        if response.success:
            print(f"✅ Respuesta exitosa")
            print(f"📊 Confianza: {response.confidence_score:.1%}")
            print(f"⏱️  Tiempo: {response.processing_time:.2f}s")
            print(f"🔧 Tareas: {response.metadata.get('tasks_executed', 0)}")
            print()
            print("📄 Contenido:")
            print("-" * 40)
            print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
        else:
            print(f"❌ Error: {response.content}")
    
    finally:
        await agent.stop()


async def example_research_task():
    """Ejemplo de tarea de investigación"""
    print("\n🔬 Ejemplo 2: Tarea de Investigación")
    print("=" * 50)
    
    agent = IntelligentAgent()
    await agent.start()
    
    try:
        # Petición de investigación compleja
        request = AgentRequest(
            query="Investiga sobre las últimas tendencias en inteligencia artificial y machine learning, incluyendo los avances más recientes y sus aplicaciones prácticas",
            priority=PriorityLevel.HIGH,
            context={
                "focus_areas": ["deep learning", "natural language processing", "computer vision"],
                "time_period": "últimos 2 años",
                "include_applications": True
            }
        )
        
        print(f"📝 Petición: {request.query[:100]}...")
        print("🔄 Procesando investigación...")
        
        response = await agent.process_request(request)
        
        if response.success:
            print(f"✅ Investigación completada")
            print(f"📊 Confianza: {response.confidence_score:.1%}")
            print(f"⏱️  Tiempo: {response.processing_time:.2f}s")
            print(f"🔧 Tareas ejecutadas: {response.metadata.get('tasks_executed', 0)}")
            print()
            
            if response.summary:
                print("📋 Resumen:")
                print("-" * 20)
                print(response.summary)
                print()
            
            if response.sources:
                print(f"📚 Fuentes consultadas ({len(response.sources)}):")
                for i, source in enumerate(response.sources, 1):
                    print(f"  {i}. {source.get('title', 'Sin título')}")
                    if source.get('url'):
                        print(f"     URL: {source['url']}")
                print()
            
            print("📄 Contenido completo:")
            print("-" * 40)
            print(response.content)
        else:
            print(f"❌ Error en la investigación: {response.content}")
    
    finally:
        await agent.stop()


async def example_analysis_task():
    """Ejemplo de tarea de análisis"""
    print("\n📊 Ejemplo 3: Tarea de Análisis")
    print("=" * 50)
    
    agent = IntelligentAgent()
    await agent.start()
    
    try:
        # Petición de análisis
        request = AgentRequest(
            query="Analiza las ventajas y desventajas de diferentes frameworks de machine learning como TensorFlow, PyTorch y Scikit-learn. Proporciona recomendaciones para diferentes casos de uso",
            priority=PriorityLevel.HIGH
        )
        
        print(f"📝 Petición: {request.query[:100]}...")
        print("🔄 Realizando análisis...")
        
        response = await agent.process_request(request)
        
        if response.success:
            print(f"✅ Análisis completado")
            print(f"📊 Confianza: {response.confidence_score:.1%}")
            print(f"⏱️  Tiempo: {response.processing_time:.2f}s")
            print()
            print("📄 Análisis:")
            print("-" * 40)
            print(response.content)
        else:
            print(f"❌ Error en el análisis: {response.content}")
    
    finally:
        await agent.stop()


async def example_knowledge_management():
    """Ejemplo de gestión de conocimiento"""
    print("\n📚 Ejemplo 4: Gestión de Conocimiento")
    print("=" * 50)
    
    agent = IntelligentAgent()
    await agent.start()
    
    try:
        # Añadir conocimiento al agente
        knowledge_content = """
        La inteligencia artificial (IA) es un campo de la informática que busca crear sistemas 
        capaces de realizar tareas que normalmente requieren inteligencia humana. 
        
        Tipos principales de IA:
        1. IA débil (narrow AI): Diseñada para tareas específicas
        2. IA fuerte (general AI): Capaz de realizar cualquier tarea intelectual humana
        3. IA superinteligente: Más inteligente que los humanos en todos los aspectos
        
        Aplicaciones comunes:
        - Procesamiento de lenguaje natural
        - Visión por computadora
        - Sistemas de recomendación
        - Automatización de procesos
        """
        
        print("📝 Añadiendo conocimiento al agente...")
        await agent.add_knowledge(
            content=knowledge_content,
            metadata={
                "topic": "inteligencia artificial",
                "type": "educational",
                "source": "manual"
            }
        )
        print("✅ Conocimiento añadido exitosamente")
        
        # Buscar en el conocimiento
        print("\n🔍 Buscando información sobre IA...")
        results = await agent.search_knowledge("inteligencia artificial", limit=5)
        
        print(f"📚 Encontrados {len(results)} resultados:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.get('content', 'Sin contenido')[:100]}...")
            print(f"     Relevancia: {result.get('score', 0):.2f}")
    
    finally:
        await agent.stop()


async def example_system_status():
    """Ejemplo de monitoreo del sistema"""
    print("\n📊 Ejemplo 5: Estado del Sistema")
    print("=" * 50)
    
    agent = IntelligentAgent()
    await agent.start()
    
    try:
        # Procesar algunas peticiones para generar métricas
        requests = [
            "¿Qué es Python?",
            "Explica el concepto de programación orientada a objetos",
            "¿Cuáles son las mejores prácticas de desarrollo de software?"
        ]
        
        for i, query in enumerate(requests, 1):
            print(f"📝 Petición {i}: {query}")
            request = AgentRequest(query=query)
            response = await agent.process_request(request)
            print(f"✅ Completada en {response.processing_time:.2f}s")
        
        # Obtener estado del sistema
        print("\n📊 Estado del Sistema:")
        status = await agent.get_status()
        
        print(f"🔄 Estado: {status.system_status}")
        print(f"⏰ Uptime: {status.system_uptime:.2f}s")
        print(f"📈 Tareas Activas: {status.active_tasks}")
        print(f"📊 Total Tareas: {status.total_tasks}")
        print(f"✅ Tasa de Éxito: {status.success_rate:.1%}")
        print(f"⚡ Tiempo Promedio: {status.average_response_time:.2f}s")
        print(f"💾 Memoria: {status.memory_usage:.1f}MB")
        print(f"🖥️  CPU: {status.cpu_usage:.1f}%")
        
        print("\n🤖 Estado de Agentes:")
        for agent_status in status.agents_status:
            print(f"  • {agent_status.agent_type.value}: {agent_status.status}")
            print(f"    - Disponible: {'✅' if agent_status.is_available else '❌'}")
            print(f"    - Tareas Completadas: {agent_status.completed_tasks}")
            print(f"    - Tareas Fallidas: {agent_status.failed_tasks}")
    
    finally:
        await agent.stop()


async def main():
    """Función principal con todos los ejemplos"""
    print("🤖 EJEMPLOS DE USO - AGENTE INTELIGENTE")
    print("=" * 60)
    
    examples = [
        ("Consulta Básica", example_basic_query),
        ("Tarea de Investigación", example_research_task),
        ("Tarea de Análisis", example_analysis_task),
        ("Gestión de Conocimiento", example_knowledge_management),
        ("Estado del Sistema", example_system_status)
    ]
    
    for i, (name, example_func) in enumerate(examples, 1):
        try:
            print(f"\n🎯 Ejemplo {i}: {name}")
            print("-" * 40)
            await example_func()
            print(f"✅ Ejemplo {i} completado exitosamente")
        except Exception as e:
            print(f"❌ Error en ejemplo {i}: {e}")
        
        # Pausa entre ejemplos
        if i < len(examples):
            print("\n⏳ Esperando 2 segundos...")
            await asyncio.sleep(2)
    
    print("\n🎉 Todos los ejemplos completados")
    print("💡 Para más información, consulta la documentación en docs/")


if __name__ == "__main__":
    # Verificar configuración
    try:
        from agent.core.config import get_config
        config = get_config()
        print("✅ Configuración cargada correctamente")
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        print("💡 Asegúrate de tener un archivo .env configurado")
        print("💡 Ejecuta: python scripts/init_system.py")
        sys.exit(1)
    
    # Ejecutar ejemplos
=======
#!/usr/bin/env python3
"""
📚 Ejemplo de Uso del Agente Inteligente

Este archivo contiene ejemplos prácticos de cómo usar el sistema
de agente inteligente para diferentes tipos de tareas.
"""

import asyncio
import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent import IntelligentAgent
from agent.core.models import AgentRequest, PriorityLevel


async def example_basic_query():
    """Ejemplo básico de consulta"""
    print("🔍 Ejemplo 1: Consulta Básica")
    print("=" * 50)
    
    agent = IntelligentAgent()
    await agent.start()
    
    try:
        # Crear petición simple
        request = AgentRequest(
            query="¿Qué es la inteligencia artificial?",
            priority=PriorityLevel.MEDIUM
        )
        
        print(f"📝 Petición: {request.query}")
        print("🔄 Procesando...")
        
        # Procesar petición
        response = await agent.process_request(request)
        
        # Mostrar resultado
        if response.success:
            print(f"✅ Respuesta exitosa")
            print(f"📊 Confianza: {response.confidence_score:.1%}")
            print(f"⏱️  Tiempo: {response.processing_time:.2f}s")
            print(f"🔧 Tareas: {response.metadata.get('tasks_executed', 0)}")
            print()
            print("📄 Contenido:")
            print("-" * 40)
            print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
        else:
            print(f"❌ Error: {response.content}")
    
    finally:
        await agent.stop()


async def example_research_task():
    """Ejemplo de tarea de investigación"""
    print("\n🔬 Ejemplo 2: Tarea de Investigación")
    print("=" * 50)
    
    agent = IntelligentAgent()
    await agent.start()
    
    try:
        # Petición de investigación compleja
        request = AgentRequest(
            query="Investiga sobre las últimas tendencias en inteligencia artificial y machine learning, incluyendo los avances más recientes y sus aplicaciones prácticas",
            priority=PriorityLevel.HIGH,
            context={
                "focus_areas": ["deep learning", "natural language processing", "computer vision"],
                "time_period": "últimos 2 años",
                "include_applications": True
            }
        )
        
        print(f"📝 Petición: {request.query[:100]}...")
        print("🔄 Procesando investigación...")
        
        response = await agent.process_request(request)
        
        if response.success:
            print(f"✅ Investigación completada")
            print(f"📊 Confianza: {response.confidence_score:.1%}")
            print(f"⏱️  Tiempo: {response.processing_time:.2f}s")
            print(f"🔧 Tareas ejecutadas: {response.metadata.get('tasks_executed', 0)}")
            print()
            
            if response.summary:
                print("📋 Resumen:")
                print("-" * 20)
                print(response.summary)
                print()
            
            if response.sources:
                print(f"📚 Fuentes consultadas ({len(response.sources)}):")
                for i, source in enumerate(response.sources, 1):
                    print(f"  {i}. {source.get('title', 'Sin título')}")
                    if source.get('url'):
                        print(f"     URL: {source['url']}")
                print()
            
            print("📄 Contenido completo:")
            print("-" * 40)
            print(response.content)
        else:
            print(f"❌ Error en la investigación: {response.content}")
    
    finally:
        await agent.stop()


async def example_analysis_task():
    """Ejemplo de tarea de análisis"""
    print("\n📊 Ejemplo 3: Tarea de Análisis")
    print("=" * 50)
    
    agent = IntelligentAgent()
    await agent.start()
    
    try:
        # Petición de análisis
        request = AgentRequest(
            query="Analiza las ventajas y desventajas de diferentes frameworks de machine learning como TensorFlow, PyTorch y Scikit-learn. Proporciona recomendaciones para diferentes casos de uso",
            priority=PriorityLevel.HIGH
        )
        
        print(f"📝 Petición: {request.query[:100]}...")
        print("🔄 Realizando análisis...")
        
        response = await agent.process_request(request)
        
        if response.success:
            print(f"✅ Análisis completado")
            print(f"📊 Confianza: {response.confidence_score:.1%}")
            print(f"⏱️  Tiempo: {response.processing_time:.2f}s")
            print()
            print("📄 Análisis:")
            print("-" * 40)
            print(response.content)
        else:
            print(f"❌ Error en el análisis: {response.content}")
    
    finally:
        await agent.stop()


async def example_knowledge_management():
    """Ejemplo de gestión de conocimiento"""
    print("\n📚 Ejemplo 4: Gestión de Conocimiento")
    print("=" * 50)
    
    agent = IntelligentAgent()
    await agent.start()
    
    try:
        # Añadir conocimiento al agente
        knowledge_content = """
        La inteligencia artificial (IA) es un campo de la informática que busca crear sistemas 
        capaces de realizar tareas que normalmente requieren inteligencia humana. 
        
        Tipos principales de IA:
        1. IA débil (narrow AI): Diseñada para tareas específicas
        2. IA fuerte (general AI): Capaz de realizar cualquier tarea intelectual humana
        3. IA superinteligente: Más inteligente que los humanos en todos los aspectos
        
        Aplicaciones comunes:
        - Procesamiento de lenguaje natural
        - Visión por computadora
        - Sistemas de recomendación
        - Automatización de procesos
        """
        
        print("📝 Añadiendo conocimiento al agente...")
        await agent.add_knowledge(
            content=knowledge_content,
            metadata={
                "topic": "inteligencia artificial",
                "type": "educational",
                "source": "manual"
            }
        )
        print("✅ Conocimiento añadido exitosamente")
        
        # Buscar en el conocimiento
        print("\n🔍 Buscando información sobre IA...")
        results = await agent.search_knowledge("inteligencia artificial", limit=5)
        
        print(f"📚 Encontrados {len(results)} resultados:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.get('content', 'Sin contenido')[:100]}...")
            print(f"     Relevancia: {result.get('score', 0):.2f}")
    
    finally:
        await agent.stop()


async def example_system_status():
    """Ejemplo de monitoreo del sistema"""
    print("\n📊 Ejemplo 5: Estado del Sistema")
    print("=" * 50)
    
    agent = IntelligentAgent()
    await agent.start()
    
    try:
        # Procesar algunas peticiones para generar métricas
        requests = [
            "¿Qué es Python?",
            "Explica el concepto de programación orientada a objetos",
            "¿Cuáles son las mejores prácticas de desarrollo de software?"
        ]
        
        for i, query in enumerate(requests, 1):
            print(f"📝 Petición {i}: {query}")
            request = AgentRequest(query=query)
            response = await agent.process_request(request)
            print(f"✅ Completada en {response.processing_time:.2f}s")
        
        # Obtener estado del sistema
        print("\n📊 Estado del Sistema:")
        status = await agent.get_status()
        
        print(f"🔄 Estado: {status.system_status}")
        print(f"⏰ Uptime: {status.system_uptime:.2f}s")
        print(f"📈 Tareas Activas: {status.active_tasks}")
        print(f"📊 Total Tareas: {status.total_tasks}")
        print(f"✅ Tasa de Éxito: {status.success_rate:.1%}")
        print(f"⚡ Tiempo Promedio: {status.average_response_time:.2f}s")
        print(f"💾 Memoria: {status.memory_usage:.1f}MB")
        print(f"🖥️  CPU: {status.cpu_usage:.1f}%")
        
        print("\n🤖 Estado de Agentes:")
        for agent_status in status.agents_status:
            print(f"  • {agent_status.agent_type.value}: {agent_status.status}")
            print(f"    - Disponible: {'✅' if agent_status.is_available else '❌'}")
            print(f"    - Tareas Completadas: {agent_status.completed_tasks}")
            print(f"    - Tareas Fallidas: {agent_status.failed_tasks}")
    
    finally:
        await agent.stop()


async def main():
    """Función principal con todos los ejemplos"""
    print("🤖 EJEMPLOS DE USO - AGENTE INTELIGENTE")
    print("=" * 60)
    
    examples = [
        ("Consulta Básica", example_basic_query),
        ("Tarea de Investigación", example_research_task),
        ("Tarea de Análisis", example_analysis_task),
        ("Gestión de Conocimiento", example_knowledge_management),
        ("Estado del Sistema", example_system_status)
    ]
    
    for i, (name, example_func) in enumerate(examples, 1):
        try:
            print(f"\n🎯 Ejemplo {i}: {name}")
            print("-" * 40)
            await example_func()
            print(f"✅ Ejemplo {i} completado exitosamente")
        except Exception as e:
            print(f"❌ Error en ejemplo {i}: {e}")
        
        # Pausa entre ejemplos
        if i < len(examples):
            print("\n⏳ Esperando 2 segundos...")
            await asyncio.sleep(2)
    
    print("\n🎉 Todos los ejemplos completados")
    print("💡 Para más información, consulta la documentación en docs/")


if __name__ == "__main__":
    # Verificar configuración
    try:
        from agent.core.config import get_config
        config = get_config()
        print("✅ Configuración cargada correctamente")
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        print("💡 Asegúrate de tener un archivo .env configurado")
        print("💡 Ejecuta: python scripts/init_system.py")
        sys.exit(1)
    
    # Ejecutar ejemplos
>>>>>>> 4caeba3865603c67c51ab60f71b04353770ceb47
    asyncio.run(main()) 