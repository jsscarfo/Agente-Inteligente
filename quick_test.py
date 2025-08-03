<<<<<<< HEAD
#!/usr/bin/env python3
"""
🧪 Prueba Rápida del Asistente de IA

Este script realiza una prueba rápida del asistente de IA para verificar
que todos los componentes funcionan correctamente.
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Colores para la terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header():
    """Imprimir encabezado"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("🧪 PRUEBA RÁPIDA DEL ASISTENTE DE IA")
    print("=" * 50)
    print(f"{Colors.ENDC}")


def print_step(step: str, message: str):
    """Imprimir paso"""
    print(f"\n{Colors.OKBLUE}[{step}]{Colors.ENDC} {message}")


def print_success(message: str):
    """Imprimir éxito"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Imprimir advertencia"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def print_error(message: str):
    """Imprimir error"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_info(message: str):
    """Imprimir información"""
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")


async def test_configuration():
    """Probar configuración"""
    print_step("1", "Verificando configuración...")
    
    try:
        from agent.core.config import get_config
        
        config = get_config()
        validation = config.validate_configuration()
        
        if validation["valid"]:
            print_success("Configuración válida")
        else:
            print_warning("Configuración con advertencias:")
            for error in validation["errors"]:
                print_error(f"  - {error}")
            for warning in validation["warnings"]:
                print_warning(f"  - {warning}")
        
        # Mostrar características disponibles
        if validation["available_features"]:
            print_info("Características disponibles:")
            for feature in validation["available_features"]:
                print_success(f"  - {feature}")
        
        return validation["valid"]
        
    except Exception as e:
        print_error(f"Error verificando configuración: {e}")
        return False


async def test_database():
    """Probar base de datos"""
    print_step("2", "Probando base de datos...")
    
    try:
        from agent.core.database import get_db_manager
        
        db_manager = get_db_manager()
        await db_manager.initialize()
        
        print_success("Base de datos inicializada correctamente")
        
        # Probar operaciones básicas
        async with db_manager.get_async_session() as session:
            # Verificar que la sesión funciona
            result = await session.execute("SELECT 1")
            await session.commit()
        
        print_success("Operaciones de base de datos funcionando")
        
        await db_manager.close()
        return True
        
    except Exception as e:
        print_error(f"Error probando base de datos: {e}")
        return False


async def test_rag_system():
    """Probar sistema RAG"""
    print_step("3", "Probando sistema RAG...")
    
    try:
        from agent.core.rag_system import get_rag_system
        
        rag_system = get_rag_system()
        await rag_system.initialize()
        
        print_success("Sistema RAG inicializado correctamente")
        
        # Probar operaciones básicas
        test_content = "La inteligencia artificial está transformando el mundo."
        doc_id = await rag_system.add_document(
            content=test_content,
            source="Test Document",
            content_type="text"
        )
        
        print_success(f"Documento añadido con ID: {doc_id}")
        
        # Probar búsqueda
        search_results = await rag_system.search("inteligencia artificial", max_results=5)
        print_success(f"Búsqueda exitosa: {len(search_results)} resultados")
        
        # Probar generación de respuesta
        rag_response = await rag_system.generate_answer("¿Qué está transformando la IA?")
        if rag_response.get('success'):
            print_success("Generación de respuesta RAG funcionando")
        else:
            print_warning("Generación de respuesta RAG con advertencias")
        
        return True
        
    except Exception as e:
        print_error(f"Error probando sistema RAG: {e}")
        return False


async def test_workflow_graph():
    """Probar grafo de flujo de trabajo"""
    print_step("4", "Probando grafo de flujo de trabajo...")
    
    try:
        from agent.core.workflow_graph import get_workflow_graph
        
        workflow_graph = get_workflow_graph()
        await workflow_graph.initialize()
        
        print_success("Grafo de flujo de trabajo inicializado correctamente")
        
        # Verificar que el grafo está configurado
        if workflow_graph.graph is not None:
            print_success("Grafo de flujo de trabajo configurado")
        else:
            print_warning("Grafo de flujo de trabajo no configurado")
        
        return True
        
    except Exception as e:
        print_error(f"Error probando grafo de flujo: {e}")
        return False


async def test_connectors():
    """Probar conectores"""
    print_step("5", "Probando conectores...")
    
    try:
        from agent.core.connectors import get_connector_manager
        
        connector_manager = get_connector_manager()
        await connector_manager.initialize()
        
        print_success("Gestor de conectores inicializado correctamente")
        
        # Verificar conectores disponibles
        available_connectors = connector_manager.get_available_sources()
        if available_connectors:
            print_success(f"Conectores disponibles: {', '.join(available_connectors)}")
        else:
            print_warning("No hay conectores disponibles (configura las APIs)")
        
        await connector_manager.close()
        return True
        
    except Exception as e:
        print_error(f"Error probando conectores: {e}")
        return False


async def test_tools():
    """Probar herramientas"""
    print_step("6", "Probando herramientas...")
    
    try:
        from agent.core.tools import get_tool_manager, ToolRequest, ToolType
        
        tool_manager = get_tool_manager()
        await tool_manager.initialize()
        
        print_success("Gestor de herramientas inicializado correctamente")
        
        # Verificar herramientas disponibles
        available_tools = tool_manager.get_available_tools()
        if available_tools:
            print_success(f"Herramientas disponibles: {', '.join(available_tools)}")
            
            # Probar calculadora
            if ToolType.CALCULATOR in available_tools:
                calc_request = ToolRequest(
                    tool_type=ToolType.CALCULATOR,
                    operation="add",
                    parameters={"values": [10, 20, 30]}
                )
                result = await tool_manager.execute_tool(calc_request)
                
                if result.success:
                    print_success(f"Calculadora funcionando: 10 + 20 + 30 = {result.result}")
                else:
                    print_warning(f"Calculadora con error: {result.error}")
        else:
            print_warning("No hay herramientas disponibles")
        
        return True
        
    except Exception as e:
        print_error(f"Error probando herramientas: {e}")
        return False


async def test_agent():
    """Probar agente completo"""
    print_step("7", "Probando agente completo...")
    
    try:
        from agent import IntelligentAgent
        from agent.core.models import AgentRequest, PriorityLevel
        
        # Crear e inicializar el agente
        agent = IntelligentAgent()
        await agent.start()
        
        print_success(f"Agente inicializado con ID: {agent.agent_id}")
        
        # Probar consulta simple
        request = AgentRequest(
            query="Hola, ¿cómo estás?",
            priority=PriorityLevel.MEDIUM
        )
        
        print_info("Procesando consulta de prueba...")
        start_time = time.time()
        
        response = await agent.process_request(request)
        
        processing_time = time.time() - start_time
        
        if response.success:
            print_success("Consulta procesada exitosamente")
            print_info(f"Respuesta: {response.content[:100]}...")
            print_info(f"Confianza: {response.confidence_score:.1%}")
            print_info(f"Tiempo: {processing_time:.2f}s")
            print_info(f"Tareas ejecutadas: {response.metadata.get('tasks_executed', 0)}")
        else:
            print_error(f"Error procesando consulta: {response.error}")
        
        # Detener el agente
        await agent.stop()
        print_success("Agente detenido correctamente")
        
        return response.success
        
    except Exception as e:
        print_error(f"Error probando agente: {e}")
        return False


async def run_quick_test():
    """Ejecutar prueba rápida completa"""
    print_header()
    
    tests = [
        ("Configuración", test_configuration),
        ("Base de Datos", test_database),
        ("Sistema RAG", test_rag_system),
        ("Grafo de Flujo", test_workflow_graph),
        ("Conectores", test_connectors),
        ("Herramientas", test_tools),
        ("Agente Completo", test_agent)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Error en prueba {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 30)
    print(f"{Colors.ENDC}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASÓ")
            passed += 1
        else:
            print_error(f"{test_name}: FALLÓ")
    
    print(f"\n{Colors.BOLD}Resultado Final: {passed}/{total} pruebas pasaron{Colors.ENDC}")
    
    if passed == total:
        print_success("🎉 ¡Todas las pruebas pasaron! El asistente está listo para usar.")
        return True
    elif passed >= total * 0.7:
        print_warning("⚠️  La mayoría de las pruebas pasaron. El asistente debería funcionar.")
        return True
    else:
        print_error("❌ Muchas pruebas fallaron. Revisa la configuración.")
        return False


async def main():
    """Función principal"""
    try:
        success = await run_quick_test()
        
        if success:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
            print("🚀 ¡Prueba completada! Puedes usar el asistente con:")
            print("   python main.py")
            print("   python assistant_demo.py")
            print(f"{Colors.ENDC}")
            sys.exit(0)
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}")
            print("❌ Prueba falló. Revisa los errores y la configuración.")
            print(f"{Colors.ENDC}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Prueba interrumpida por el usuario{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error inesperado: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
=======
#!/usr/bin/env python3
"""
🧪 Prueba Rápida del Asistente de IA

Este script realiza una prueba rápida del asistente de IA para verificar
que todos los componentes funcionan correctamente.
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Colores para la terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header():
    """Imprimir encabezado"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("🧪 PRUEBA RÁPIDA DEL ASISTENTE DE IA")
    print("=" * 50)
    print(f"{Colors.ENDC}")


def print_step(step: str, message: str):
    """Imprimir paso"""
    print(f"\n{Colors.OKBLUE}[{step}]{Colors.ENDC} {message}")


def print_success(message: str):
    """Imprimir éxito"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Imprimir advertencia"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def print_error(message: str):
    """Imprimir error"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_info(message: str):
    """Imprimir información"""
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")


async def test_configuration():
    """Probar configuración"""
    print_step("1", "Verificando configuración...")
    
    try:
        from agent.core.config import get_config
        
        config = get_config()
        validation = config.validate_configuration()
        
        if validation["valid"]:
            print_success("Configuración válida")
        else:
            print_warning("Configuración con advertencias:")
            for error in validation["errors"]:
                print_error(f"  - {error}")
            for warning in validation["warnings"]:
                print_warning(f"  - {warning}")
        
        # Mostrar características disponibles
        if validation["available_features"]:
            print_info("Características disponibles:")
            for feature in validation["available_features"]:
                print_success(f"  - {feature}")
        
        return validation["valid"]
        
    except Exception as e:
        print_error(f"Error verificando configuración: {e}")
        return False


async def test_database():
    """Probar base de datos"""
    print_step("2", "Probando base de datos...")
    
    try:
        from agent.core.database import get_db_manager
        
        db_manager = get_db_manager()
        await db_manager.initialize()
        
        print_success("Base de datos inicializada correctamente")
        
        # Probar operaciones básicas
        async with db_manager.get_async_session() as session:
            # Verificar que la sesión funciona
            result = await session.execute("SELECT 1")
            await session.commit()
        
        print_success("Operaciones de base de datos funcionando")
        
        await db_manager.close()
        return True
        
    except Exception as e:
        print_error(f"Error probando base de datos: {e}")
        return False


async def test_rag_system():
    """Probar sistema RAG"""
    print_step("3", "Probando sistema RAG...")
    
    try:
        from agent.core.rag_system import get_rag_system
        
        rag_system = get_rag_system()
        await rag_system.initialize()
        
        print_success("Sistema RAG inicializado correctamente")
        
        # Probar operaciones básicas
        test_content = "La inteligencia artificial está transformando el mundo."
        doc_id = await rag_system.add_document(
            content=test_content,
            source="Test Document",
            content_type="text"
        )
        
        print_success(f"Documento añadido con ID: {doc_id}")
        
        # Probar búsqueda
        search_results = await rag_system.search("inteligencia artificial", max_results=5)
        print_success(f"Búsqueda exitosa: {len(search_results)} resultados")
        
        # Probar generación de respuesta
        rag_response = await rag_system.generate_answer("¿Qué está transformando la IA?")
        if rag_response.get('success'):
            print_success("Generación de respuesta RAG funcionando")
        else:
            print_warning("Generación de respuesta RAG con advertencias")
        
        return True
        
    except Exception as e:
        print_error(f"Error probando sistema RAG: {e}")
        return False


async def test_workflow_graph():
    """Probar grafo de flujo de trabajo"""
    print_step("4", "Probando grafo de flujo de trabajo...")
    
    try:
        from agent.core.workflow_graph import get_workflow_graph
        
        workflow_graph = get_workflow_graph()
        await workflow_graph.initialize()
        
        print_success("Grafo de flujo de trabajo inicializado correctamente")
        
        # Verificar que el grafo está configurado
        if workflow_graph.graph is not None:
            print_success("Grafo de flujo de trabajo configurado")
        else:
            print_warning("Grafo de flujo de trabajo no configurado")
        
        return True
        
    except Exception as e:
        print_error(f"Error probando grafo de flujo: {e}")
        return False


async def test_connectors():
    """Probar conectores"""
    print_step("5", "Probando conectores...")
    
    try:
        from agent.core.connectors import get_connector_manager
        
        connector_manager = get_connector_manager()
        await connector_manager.initialize()
        
        print_success("Gestor de conectores inicializado correctamente")
        
        # Verificar conectores disponibles
        available_connectors = connector_manager.get_available_sources()
        if available_connectors:
            print_success(f"Conectores disponibles: {', '.join(available_connectors)}")
        else:
            print_warning("No hay conectores disponibles (configura las APIs)")
        
        await connector_manager.close()
        return True
        
    except Exception as e:
        print_error(f"Error probando conectores: {e}")
        return False


async def test_tools():
    """Probar herramientas"""
    print_step("6", "Probando herramientas...")
    
    try:
        from agent.core.tools import get_tool_manager, ToolRequest, ToolType
        
        tool_manager = get_tool_manager()
        await tool_manager.initialize()
        
        print_success("Gestor de herramientas inicializado correctamente")
        
        # Verificar herramientas disponibles
        available_tools = tool_manager.get_available_tools()
        if available_tools:
            print_success(f"Herramientas disponibles: {', '.join(available_tools)}")
            
            # Probar calculadora
            if ToolType.CALCULATOR in available_tools:
                calc_request = ToolRequest(
                    tool_type=ToolType.CALCULATOR,
                    operation="add",
                    parameters={"values": [10, 20, 30]}
                )
                result = await tool_manager.execute_tool(calc_request)
                
                if result.success:
                    print_success(f"Calculadora funcionando: 10 + 20 + 30 = {result.result}")
                else:
                    print_warning(f"Calculadora con error: {result.error}")
        else:
            print_warning("No hay herramientas disponibles")
        
        return True
        
    except Exception as e:
        print_error(f"Error probando herramientas: {e}")
        return False


async def test_agent():
    """Probar agente completo"""
    print_step("7", "Probando agente completo...")
    
    try:
        from agent import IntelligentAgent
        from agent.core.models import AgentRequest, PriorityLevel
        
        # Crear e inicializar el agente
        agent = IntelligentAgent()
        await agent.start()
        
        print_success(f"Agente inicializado con ID: {agent.agent_id}")
        
        # Probar consulta simple
        request = AgentRequest(
            query="Hola, ¿cómo estás?",
            priority=PriorityLevel.MEDIUM
        )
        
        print_info("Procesando consulta de prueba...")
        start_time = time.time()
        
        response = await agent.process_request(request)
        
        processing_time = time.time() - start_time
        
        if response.success:
            print_success("Consulta procesada exitosamente")
            print_info(f"Respuesta: {response.content[:100]}...")
            print_info(f"Confianza: {response.confidence_score:.1%}")
            print_info(f"Tiempo: {processing_time:.2f}s")
            print_info(f"Tareas ejecutadas: {response.metadata.get('tasks_executed', 0)}")
        else:
            print_error(f"Error procesando consulta: {response.error}")
        
        # Detener el agente
        await agent.stop()
        print_success("Agente detenido correctamente")
        
        return response.success
        
    except Exception as e:
        print_error(f"Error probando agente: {e}")
        return False


async def run_quick_test():
    """Ejecutar prueba rápida completa"""
    print_header()
    
    tests = [
        ("Configuración", test_configuration),
        ("Base de Datos", test_database),
        ("Sistema RAG", test_rag_system),
        ("Grafo de Flujo", test_workflow_graph),
        ("Conectores", test_connectors),
        ("Herramientas", test_tools),
        ("Agente Completo", test_agent)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Error en prueba {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 30)
    print(f"{Colors.ENDC}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASÓ")
            passed += 1
        else:
            print_error(f"{test_name}: FALLÓ")
    
    print(f"\n{Colors.BOLD}Resultado Final: {passed}/{total} pruebas pasaron{Colors.ENDC}")
    
    if passed == total:
        print_success("🎉 ¡Todas las pruebas pasaron! El asistente está listo para usar.")
        return True
    elif passed >= total * 0.7:
        print_warning("⚠️  La mayoría de las pruebas pasaron. El asistente debería funcionar.")
        return True
    else:
        print_error("❌ Muchas pruebas fallaron. Revisa la configuración.")
        return False


async def main():
    """Función principal"""
    try:
        success = await run_quick_test()
        
        if success:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
            print("🚀 ¡Prueba completada! Puedes usar el asistente con:")
            print("   python main.py")
            print("   python assistant_demo.py")
            print(f"{Colors.ENDC}")
            sys.exit(0)
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}")
            print("❌ Prueba falló. Revisa los errores y la configuración.")
            print(f"{Colors.ENDC}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Prueba interrumpida por el usuario{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error inesperado: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
>>>>>>> 4caeba3865603c67c51ab60f71b04353770ceb47
    asyncio.run(main()) 