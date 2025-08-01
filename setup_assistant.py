#!/usr/bin/env python3
"""
🚀 Configuración Automática del Asistente de IA Multifuncional

Este script configura automáticamente el entorno del asistente de IA,
incluyendo la creación de directorios, configuración de variables de entorno,
inicialización de la base de datos y pruebas de funcionalidad.
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

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
    UNDERLINE = '\033[4m'


class AssistantSetup:
    """Configurador automático del asistente de IA"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / ".env"
        self.data_dir = self.project_root / "data"
        self.requirements_file = self.project_root / "requirements.txt"
        
        # Configuración por defecto
        self.default_config = {
            "OPENAI_API_KEY": "",
            "OPENAI_MODEL": "gpt-4",
            "OPENAI_MAX_TOKENS": "4000",
            "OPENAI_TEMPERATURE": "0.7",
            "ENVIRONMENT": "development",
            "DEBUG": "true",
            "LOG_LEVEL": "INFO",
            "MAX_CONCURRENT_TASKS": "10",
            "REQUEST_TIMEOUT": "30",
            "MAX_RETRIES": "3",
            "CACHE_TTL": "3600",
            "AGENT_NAME": "Asistente IA",
            "AGENT_VERSION": "1.0.0",
            "AGENT_DESCRIPTION": "Asistente de IA multifuncional",
            "RAG_CHUNK_SIZE": "1000",
            "RAG_CHUNK_OVERLAP": "200",
            "RAG_MAX_RESULTS": "10",
            "RAG_EMBEDDING_MODEL": "text-embedding-ada-002",
            "LANGGRAPH_MAX_ITERATIONS": "10",
            "LANGGRAPH_CHECKPOINT_DIR": "./data/checkpoints",
            "VECTOR_DB_PATH": "./data/knowledge/vector_db",
            "VECTOR_DB_TYPE": "chroma",
            "SQLITE_DATABASE": "sqlite:///./data/database/agent.db",
            "DATA_DIR": "./data",
            "LOGS_DIR": "./data/logs",
            "TEMP_DIR": "./data/temp",
            "UPLOADS_DIR": "./data/uploads",
            "ENABLE_CALCULATOR": "true",
            "ENABLE_TEXT_ANALYZER": "true",
            "ENABLE_DATA_PROCESSOR": "true",
            "ENABLE_FILE_HANDLER": "true",
            "ENABLE_WEB_SCRAPER": "false",
            "ENABLE_TRANSLATOR": "false",
            "ENABLE_SCHEDULER": "false",
            "ENABLE_EMAIL_SENDER": "false",
            "ENABLE_WEATHER_CONNECTOR": "true",
            "ENABLE_NEWS_CONNECTOR": "true",
            "ENABLE_FINANCE_CONNECTOR": "true",
            "ENABLE_SEARCH_CONNECTOR": "true",
            "ENABLE_METRICS": "true",
            "METRICS_PORT": "9090",
            "ENABLE_HEALTH_CHECK": "true",
            "HEALTH_CHECK_INTERVAL": "30",
            "SECRET_KEY": "tu_clave_secreta_muy_larga_y_segura_aqui",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
            "REFRESH_TOKEN_EXPIRE_DAYS": "7",
            "ALGORITHM": "HS256",
            "CORS_ORIGINS": '["http://localhost:3000", "http://localhost:8000"]'
        }
    
    def print_header(self):
        """Imprimir encabezado del setup"""
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("🤖 ASISTENTE DE IA MULTIFUNCIONAL")
        print("=" * 50)
        print("🚀 Configuración Automática del Sistema")
        print("=" * 50)
        print(f"{Colors.ENDC}")
    
    def print_step(self, step: str, message: str):
        """Imprimir paso del setup"""
        print(f"\n{Colors.OKBLUE}[{step}]{Colors.ENDC} {message}")
    
    def print_success(self, message: str):
        """Imprimir mensaje de éxito"""
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
    
    def print_warning(self, message: str):
        """Imprimir mensaje de advertencia"""
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
    
    def print_error(self, message: str):
        """Imprimir mensaje de error"""
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
    
    def print_info(self, message: str):
        """Imprimir mensaje informativo"""
        print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")
    
    def check_python_version(self) -> bool:
        """Verificar versión de Python"""
        self.print_step("1", "Verificando versión de Python...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.print_error(f"Se requiere Python 3.8 o superior. Versión actual: {version.major}.{version.minor}")
            return False
        
        self.print_success(f"Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    
    def create_directories(self) -> bool:
        """Crear directorios necesarios"""
        self.print_step("2", "Creando estructura de directorios...")
        
        directories = [
            self.data_dir,
            self.data_dir / "database",
            self.data_dir / "knowledge",
            self.data_dir / "logs",
            self.data_dir / "temp",
            self.data_dir / "uploads",
            self.data_dir / "checkpoints",
            self.data_dir / "vector_db"
        ]
        
        try:
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.print_success(f"Directorio creado: {directory}")
            
            return True
        except Exception as e:
            self.print_error(f"Error creando directorios: {e}")
            return False
    
    def create_env_file(self) -> bool:
        """Crear archivo .env si no existe"""
        self.print_step("3", "Configurando archivo .env...")
        
        if self.env_file.exists():
            self.print_warning("Archivo .env ya existe")
            return True
        
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write("# =============================================================================\n")
                f.write("# 🤖 ASISTENTE DE IA - CONFIGURACIÓN\n")
                f.write("# =============================================================================\n\n")
                
                for key, value in self.default_config.items():
                    f.write(f"{key}={value}\n")
                
                f.write("\n# =============================================================================\n")
                f.write("# 🌐 EXTERNAL APIs (Configurar según necesidad)\n")
                f.write("# =============================================================================\n")
                f.write("# Weather APIs\n")
                f.write("WEATHER_API_KEY=tu_clave_weather_api\n")
                f.write("OPENWEATHER_API_KEY=tu_clave_openweather\n\n")
                f.write("# News APIs\n")
                f.write("NEWS_API_KEY=tu_clave_news_api\n")
                f.write("GNEWS_API_KEY=tu_clave_gnews\n\n")
                f.write("# Finance APIs\n")
                f.write("ALPHA_VANTAGE_API_KEY=tu_clave_alpha_vantage\n")
                f.write("YAHOO_FINANCE_API_KEY=tu_clave_yahoo_finance\n\n")
                f.write("# Search APIs\n")
                f.write("GOOGLE_SEARCH_API_KEY=tu_clave_google_search\n")
                f.write("SERPER_API_KEY=tu_clave_serper\n\n")
                f.write("# Translation APIs\n")
                f.write("GOOGLE_TRANSLATE_API_KEY=tu_clave_google_translate\n")
                f.write("DEEPL_API_KEY=tu_clave_deepl\n\n")
                f.write("# Email APIs\n")
                f.write("SMTP_HOST=smtp.gmail.com\n")
                f.write("SMTP_PORT=587\n")
                f.write("SMTP_USER=tu_email@gmail.com\n")
                f.write("SMTP_PASSWORD=tu_password_de_aplicacion\n\n")
                f.write("# =============================================================================\n")
                f.write("# 🔗 INTEGRATIONS (Opcional)\n")
                f.write("# =============================================================================\n")
                f.write("SLACK_WEBHOOK_URL=tu_webhook_de_slack\n")
                f.write("DISCORD_WEBHOOK_URL=tu_webhook_de_discord\n")
                f.write("TELEGRAM_BOT_TOKEN=tu_token_de_telegram\n")
            
            self.print_success("Archivo .env creado correctamente")
            self.print_warning("IMPORTANTE: Configura tu OPENAI_API_KEY en el archivo .env")
            return True
            
        except Exception as e:
            self.print_error(f"Error creando archivo .env: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Instalar dependencias"""
        self.print_step("4", "Instalando dependencias...")
        
        if not self.requirements_file.exists():
            self.print_error("Archivo requirements.txt no encontrado")
            return False
        
        try:
            # Verificar si pip está disponible
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                self.print_error("pip no está disponible")
                return False
            
            # Instalar dependencias
            self.print_info("Instalando dependencias (esto puede tomar varios minutos)...")
            
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_success("Dependencias instaladas correctamente")
                return True
            else:
                self.print_error(f"Error instalando dependencias: {result.stderr}")
                return False
                
        except Exception as e:
            self.print_error(f"Error durante la instalación: {e}")
            return False
    
    async def test_system(self) -> bool:
        """Probar el sistema"""
        self.print_step("5", "Probando el sistema...")
        
        try:
            # Importar módulos del agente
            sys.path.insert(0, str(self.project_root))
            
            from agent.core.config import get_config
            from agent.core.database import get_db_manager
            from agent.core.rag_system import get_rag_system
            from agent.core.workflow_graph import get_workflow_graph
            from agent.core.connectors import get_connector_manager
            from agent.core.tools import get_tool_manager
            
            # Probar configuración
            self.print_info("Probando configuración...")
            config = get_config()
            validation = config.validate_configuration()
            
            if validation["valid"]:
                self.print_success("Configuración válida")
            else:
                self.print_warning("Configuración con advertencias:")
                for error in validation["errors"]:
                    self.print_error(f"  - {error}")
                for warning in validation["warnings"]:
                    self.print_warning(f"  - {warning}")
            
            # Mostrar características disponibles
            if validation["available_features"]:
                self.print_info("Características disponibles:")
                for feature in validation["available_features"]:
                    self.print_success(f"  - {feature}")
            
            # Probar base de datos
            self.print_info("Probando base de datos...")
            db_manager = get_db_manager()
            await db_manager.initialize()
            self.print_success("Base de datos inicializada")
            
            # Probar sistema RAG
            self.print_info("Probando sistema RAG...")
            rag_system = get_rag_system()
            await rag_system.initialize()
            self.print_success("Sistema RAG inicializado")
            
            # Probar grafo de flujo de trabajo
            self.print_info("Probando grafo de flujo de trabajo...")
            workflow_graph = get_workflow_graph()
            await workflow_graph.initialize()
            self.print_success("Grafo de flujo de trabajo inicializado")
            
            # Probar gestor de conectores
            self.print_info("Probando gestor de conectores...")
            connector_manager = get_connector_manager()
            await connector_manager.initialize()
            available_connectors = connector_manager.get_available_sources()
            if available_connectors:
                self.print_success(f"Conectores disponibles: {', '.join(available_connectors)}")
            else:
                self.print_warning("No hay conectores disponibles (configura las APIs)")
            
            # Probar gestor de herramientas
            self.print_info("Probando gestor de herramientas...")
            tool_manager = get_tool_manager()
            await tool_manager.initialize()
            available_tools = tool_manager.get_available_tools()
            if available_tools:
                self.print_success(f"Herramientas disponibles: {', '.join(available_tools)}")
            
            # Cerrar conexiones
            await db_manager.close()
            await connector_manager.close()
            
            return True
            
        except Exception as e:
            self.print_error(f"Error probando el sistema: {e}")
            return False
    
    def create_example_scripts(self) -> bool:
        """Crear scripts de ejemplo"""
        self.print_step("6", "Creando scripts de ejemplo...")
        
        try:
            # Script de prueba básica
            test_script = self.project_root / "test_basic.py"
            if not test_script.exists():
                with open(test_script, 'w', encoding='utf-8') as f:
                    f.write('''#!/usr/bin/env python3
"""
🧪 Prueba Básica del Asistente de IA

Este script realiza una prueba básica del asistente de IA
para verificar que todo funciona correctamente.
"""

import asyncio
import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent import IntelligentAgent
from agent.core.models import AgentRequest, PriorityLevel


async def test_basic_functionality():
    """Probar funcionalidad básica"""
    print("🧪 Probando funcionalidad básica del asistente...")
    
    try:
        # Crear e inicializar el agente
        agent = IntelligentAgent()
        await agent.start()
        
        print(f"✅ Agente inicializado con ID: {agent.agent_id}")
        
        # Probar consulta simple
        request = AgentRequest(
            query="Hola, ¿cómo estás?",
            priority=PriorityLevel.MEDIUM
        )
        
        print("📝 Procesando consulta de prueba...")
        response = await agent.process_request(request)
        
        if response.success:
            print("✅ Consulta procesada exitosamente")
            print(f"📄 Respuesta: {response.content[:200]}...")
            print(f"📊 Confianza: {response.confidence_score:.1%}")
            print(f"⏱️  Tiempo: {response.processing_time:.2f}s")
        else:
            print(f"❌ Error: {response.error}")
        
        # Detener el agente
        await agent.stop()
        print("✅ Prueba completada")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
''')
                self.print_success("Script de prueba básica creado: test_basic.py")
            
            # Script de demostración
            demo_script = self.project_root / "run_demo.py"
            if not demo_script.exists():
                with open(demo_script, 'w', encoding='utf-8') as f:
                    f.write('''#!/usr/bin/env python3
"""
🎯 Demostración del Asistente de IA

Este script ejecuta una demostración completa del asistente de IA
mostrando todas sus capacidades.
"""

import asyncio
import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from assistant_demo import AssistantDemo


async def main():
    """Ejecutar demostración"""
    print("🎯 Iniciando demostración del asistente...")
    
    demo = AssistantDemo()
    await demo.start_demo()


if __name__ == "__main__":
    asyncio.run(main())
''')
                self.print_success("Script de demostración creado: run_demo.py")
            
            return True
            
        except Exception as e:
            self.print_error(f"Error creando scripts: {e}")
            return False
    
    def show_next_steps(self):
        """Mostrar próximos pasos"""
        self.print_step("7", "Próximos pasos")
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ¡Configuración completada!{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}📋 Para comenzar a usar el asistente:{Colors.ENDC}")
        print(f"  1. {Colors.BOLD}Configura tu API key de OpenAI:{Colors.ENDC}")
        print(f"     Edita el archivo .env y añade: OPENAI_API_KEY=tu_clave_aqui")
        print(f"  2. {Colors.BOLD}Ejecuta una prueba básica:{Colors.ENDC}")
        print(f"     python test_basic.py")
        print(f"  3. {Colors.BOLD}Ejecuta la demostración completa:{Colors.ENDC}")
        print(f"     python run_demo.py")
        print(f"  4. {Colors.BOLD}Usa el asistente interactivamente:{Colors.ENDC}")
        print(f"     python main.py")
        
        print(f"\n{Colors.OKCYAN}🔧 Comandos útiles:{Colors.ENDC}")
        print(f"  • python main.py --help")
        print(f"  • python assistant_demo.py")
        print(f"  • python test_basic.py")
        
        print(f"\n{Colors.WARNING}⚠️  Notas importantes:{Colors.ENDC}")
        print(f"  • El asistente funciona mejor con una API key de OpenAI")
        print(f"  • Para funcionalidades completas, configura las APIs externas")
        print(f"  • En desarrollo, usa SQLite; en producción, PostgreSQL")
        
        print(f"\n{Colors.OKGREEN}🚀 ¡Listo para usar el asistente de IA!{Colors.ENDC}")
    
    async def run_setup(self) -> bool:
        """Ejecutar configuración completa"""
        self.print_header()
        
        steps = [
            ("Verificación de Python", self.check_python_version),
            ("Creación de directorios", self.create_directories),
            ("Configuración de .env", self.create_env_file),
            ("Instalación de dependencias", self.install_dependencies),
            ("Prueba del sistema", self.test_system),
            ("Creación de scripts", self.create_example_scripts)
        ]
        
        for step_name, step_func in steps:
            if step_name == "Prueba del sistema":
                success = await step_func()
            else:
                success = step_func()
            
            if not success:
                self.print_error(f"Error en paso: {step_name}")
                return False
        
        self.show_next_steps()
        return True


async def main():
    """Función principal"""
    setup = AssistantSetup()
    success = await setup.run_setup()
    
    if success:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ Configuración completada exitosamente{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Configuración falló{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 