#!/usr/bin/env python3
"""
🤖 Agente Inteligente - Punto de Entrada Principal

Este es el archivo principal del sistema de agente inteligente.
Proporciona una interfaz de línea de comandos y funcionalidades
básicas para interactuar con el agente.
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent import IntelligentAgent
from agent.core.models import AgentRequest, PriorityLevel
from agent.core.config import get_config


class AgentCLI:
    """Interfaz de línea de comandos para el Agente Inteligente"""
    
    def __init__(self):
        self.agent = None
        self.config = get_config()
    
    async def start(self):
        """Iniciar el agente"""
        try:
            print("🤖 Iniciando Agente Inteligente...")
            
            # Crear e iniciar el agente
            self.agent = IntelligentAgent()
            await self.agent.start()
            
            print("✅ Agente Inteligente iniciado correctamente")
            print(f"🆔 ID del Agente: {self.agent.agent_id}")
            print(f"⏰ Uptime: {self.agent.get_uptime():.2f} segundos")
            print(f"📊 Versión: {self.agent.get_version()}")
            print()
            
        except Exception as e:
            print(f"❌ Error iniciando el agente: {e}")
            sys.exit(1)
    
    async def stop(self):
        """Detener el agente"""
        if self.agent:
            try:
                print("🛑 Deteniendo Agente Inteligente...")
                await self.agent.stop()
                print("✅ Agente detenido correctamente")
            except Exception as e:
                print(f"❌ Error deteniendo el agente: {e}")
    
    async def process_query(self, query: str, priority: str = "medium"):
        """Procesar una consulta"""
        if not self.agent:
            print("❌ El agente no está iniciado")
            return
        
        try:
            # Crear petición
            request = AgentRequest(
                query=query,
                priority=PriorityLevel(priority.lower())
            )
            
            print(f"📝 Procesando: {query}")
            print("🔄 Ejecutando...")
            
            # Procesar petición
            response = await self.agent.process_request(request)
            
            # Mostrar resultado
            print("\n" + "="*60)
            print("🎯 RESPUESTA DEL AGENTE")
            print("="*60)
            
            if response.success:
                print(f"✅ Estado: Exitoso")
                print(f"📊 Confianza: {response.confidence_score:.1%}")
                print(f"⏱️  Tiempo: {response.processing_time:.2f}s")
                print(f"🔧 Tareas: {response.metadata.get('tasks_executed', 0)} ejecutadas")
                print()
                print("📄 Contenido:")
                print("-" * 40)
                print(response.content)
                
                if response.summary:
                    print("\n📋 Resumen:")
                    print("-" * 20)
                    print(response.summary)
                
                if response.sources:
                    print(f"\n📚 Fuentes ({len(response.sources)}):")
                    for i, source in enumerate(response.sources, 1):
                        print(f"  {i}. {source.get('title', 'Sin título')}")
                
            else:
                print(f"❌ Estado: Fallido")
                print(f"⏱️  Tiempo: {response.processing_time:.2f}s")
                print(f"💬 Error: {response.content}")
            
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error procesando la consulta: {e}")
    
    async def show_status(self):
        """Mostrar estado del sistema"""
        if not self.agent:
            print("❌ El agente no está iniciado")
            return
        
        try:
            status = await self.agent.get_status()
            
            print("\n" + "="*60)
            print("📊 ESTADO DEL SISTEMA")
            print("="*60)
            print(f"🔄 Estado: {status.system_status}")
            print(f"⏰ Uptime: {status.system_uptime:.2f}s")
            print(f"📈 Tareas Activas: {status.active_tasks}")
            print(f"📊 Total Tareas: {status.total_tasks}")
            print(f"✅ Tasa de Éxito: {status.success_rate:.1%}")
            print(f"⚡ Tiempo Promedio: {status.average_response_time:.2f}s")
            print(f"💾 Memoria: {status.memory_usage:.1f}MB")
            print(f"🖥️  CPU: {status.cpu_usage:.1f}%")
            print()
            
            print("🤖 AGENTES:")
            for agent_status in status.agents_status:
                print(f"  • {agent_status.agent_type.value}: {agent_status.status}")
                print(f"    - Disponible: {'✅' if agent_status.is_available else '❌'}")
                print(f"    - Tareas Actuales: {agent_status.current_tasks}")
                print(f"    - Tareas Completadas: {agent_status.completed_tasks}")
                print(f"    - Tareas Fallidas: {agent_status.failed_tasks}")
                print()
            
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error obteniendo estado: {e}")
    
    async def interactive_mode(self):
        """Modo interactivo"""
        print("\n🎮 Modo Interactivo")
        print("Comandos disponibles:")
        print("  /query <texto> - Procesar una consulta")
        print("  /status - Mostrar estado del sistema")
        print("  /help - Mostrar esta ayuda")
        print("  /quit - Salir")
        print()
        
        while True:
            try:
                command = input("🤖 Agente> ").strip()
                
                if not command:
                    continue
                
                if command.lower() == "/quit":
                    break
                elif command.lower() == "/help":
                    print("Comandos disponibles:")
                    print("  /query <texto> - Procesar una consulta")
                    print("  /status - Mostrar estado del sistema")
                    print("  /help - Mostrar esta ayuda")
                    print("  /quit - Salir")
                elif command.lower() == "/status":
                    await self.show_status()
                elif command.startswith("/query "):
                    query = command[7:].strip()
                    if query:
                        await self.process_query(query)
                    else:
                        print("❌ Debes proporcionar una consulta")
                else:
                    # Tratar como consulta directa
                    await self.process_query(command)
                    
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


async def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="🤖 Agente Inteligente - Sistema de IA Avanzado",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py --query "¿Qué es la inteligencia artificial?"
  python main.py --interactive
  python main.py --status
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        help="Procesar una consulta específica"
    )
    
    parser.add_argument(
        "--priority", "-p",
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="Prioridad de la consulta (default: medium)"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Iniciar modo interactivo"
    )
    
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Mostrar estado del sistema"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Agente Inteligente v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Crear CLI
    cli = AgentCLI()
    
    try:
        # Iniciar agente
        await cli.start()
        
        # Ejecutar comando solicitado
        if args.query:
            await cli.process_query(args.query, args.priority)
        elif args.status:
            await cli.show_status()
        elif args.interactive:
            await cli.interactive_mode()
        else:
            # Modo interactivo por defecto
            await cli.interactive_mode()
    
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        # Detener agente
        await cli.stop()


if __name__ == "__main__":
    # Verificar configuración
    try:
        config = get_config()
        print("✅ Configuración cargada correctamente")
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        print("💡 Asegúrate de tener un archivo .env configurado")
        sys.exit(1)
    
    # Ejecutar aplicación
    asyncio.run(main()) 