#!/usr/bin/env python3
"""
🚂 Railway Setup - Configuración para Despliegue en Railway

Este script configura el proyecto para despliegue en Railway,
verificando dependencias y configurando el entorno.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RailwaySetup:
    """Configurador para Railway"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.requirements_file = self.project_root / "requirements.txt"
        self.railway_app_file = self.project_root / "railway_app.py"
        
    def check_railway_environment(self):
        """Verificar si estamos en Railway"""
        railway_vars = [
            "RAILWAY_ENVIRONMENT",
            "RAILWAY_PROJECT_ID",
            "RAILWAY_SERVICE_ID"
        ]
        
        in_railway = any(os.environ.get(var) for var in railway_vars)
        
        if in_railway:
            logger.info("🚂 Detectado entorno Railway")
            logger.info(f"   Entorno: {os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')}")
            logger.info(f"   Puerto: {os.environ.get('PORT', '8000')}")
        else:
            logger.info("💻 Entorno local detectado")
        
        return in_railway
    
    def verify_dependencies(self):
        """Verificar dependencias críticas"""
        logger.info("🔍 Verificando dependencias...")
        
        critical_deps = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "openai",
            "langchain"
        ]
        
        missing_deps = []
        
        for dep in critical_deps:
            try:
                __import__(dep.replace("-", "_"))
                logger.info(f"✅ {dep}")
            except ImportError:
                missing_deps.append(dep)
                logger.warning(f"❌ {dep} - No encontrado")
        
        if missing_deps:
            logger.error(f"❌ Dependencias faltantes: {missing_deps}")
            return False
        
        logger.info("✅ Todas las dependencias críticas están disponibles")
        return True
    
    def check_files(self):
        """Verificar archivos necesarios"""
        logger.info("📁 Verificando archivos...")
        
        required_files = [
            "railway_app.py",
            "requirements.txt",
            "Procfile",
            "runtime.txt"
        ]
        
        missing_files = []
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                logger.info(f"✅ {file_name}")
            else:
                missing_files.append(file_name)
                logger.warning(f"❌ {file_name} - No encontrado")
        
        if missing_files:
            logger.error(f"❌ Archivos faltantes: {missing_files}")
            return False
        
        logger.info("✅ Todos los archivos necesarios están presentes")
        return True
    
    def create_directories(self):
        """Crear directorios necesarios"""
        logger.info("📂 Creando directorios...")
        
        directories = [
            "data",
            "data/temp",
            "data/uploads",
            "data/database",
            "data/logs",
            "static",
            "templates"
        ]
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ {dir_name}")
    
    def check_environment_variables(self):
        """Verificar variables de entorno"""
        logger.info("🔧 Verificando variables de entorno...")
        
        # Variables críticas
        critical_vars = ["OPENAI_API_KEY"]
        
        missing_vars = []
        
        for var in critical_vars:
            if os.environ.get(var):
                logger.info(f"✅ {var} - Configurada")
            else:
                missing_vars.append(var)
                logger.warning(f"⚠️ {var} - No configurada")
        
        # Variables opcionales
        optional_vars = [
            "DATABASE_URL",
            "GOOGLE_VISION_API_KEY",
            "AZURE_VISION_ENDPOINT",
            "WEATHER_API_KEY",
            "NEWS_API_KEY"
        ]
        
        for var in optional_vars:
            if os.environ.get(var):
                logger.info(f"✅ {var} - Configurada")
            else:
                logger.info(f"ℹ️ {var} - No configurada (opcional)")
        
        if missing_vars:
            logger.warning(f"⚠️ Variables críticas faltantes: {missing_vars}")
            logger.warning("   El sistema funcionará con capacidades limitadas")
        
        return len(missing_vars) == 0
    
    def test_imports(self):
        """Probar imports críticos"""
        logger.info("🧪 Probando imports...")
        
        try:
            # Test básico
            import fastapi
            import uvicorn
            logger.info("✅ FastAPI y Uvicorn")
            
            # Test del sistema
            from agent.core.config import get_config
            logger.info("✅ Configuración del agente")
            
            # Test opcional
            try:
                from assistant_multimodal import MultimodalAssistant
                logger.info("✅ Asistente multimodal")
            except ImportError:
                logger.info("ℹ️ Asistente multimodal - No disponible")
            
            logger.info("✅ Todos los imports críticos funcionan")
            return True
            
        except ImportError as e:
            logger.error(f"❌ Error en imports: {e}")
            return False
    
    def run_setup(self):
        """Ejecutar configuración completa"""
        logger.info("🚀 Iniciando configuración de Railway...")
        
        # Verificar entorno
        in_railway = self.check_railway_environment()
        
        # Verificar archivos
        if not self.check_files():
            logger.error("❌ Configuración fallida: Archivos faltantes")
            return False
        
        # Verificar dependencias
        if not self.verify_dependencies():
            logger.error("❌ Configuración fallida: Dependencias faltantes")
            return False
        
        # Crear directorios
        self.create_directories()
        
        # Verificar variables de entorno
        env_ok = self.check_environment_variables()
        
        # Probar imports
        if not self.test_imports():
            logger.error("❌ Configuración fallida: Errores en imports")
            return False
        
        # Resumen
        logger.info("=" * 50)
        logger.info("📊 RESUMEN DE CONFIGURACIÓN")
        logger.info("=" * 50)
        logger.info(f"🚂 Entorno Railway: {'✅' if in_railway else '❌'}")
        logger.info(f"📁 Archivos: ✅")
        logger.info(f"📦 Dependencias: ✅")
        logger.info(f"🔧 Variables de entorno: {'✅' if env_ok else '⚠️'}")
        logger.info(f"🧪 Imports: ✅")
        
        if in_railway:
            logger.info("🎉 ¡Configuración completada! El proyecto está listo para Railway")
        else:
            logger.info("🎉 ¡Configuración completada! El proyecto está listo para desarrollo local")
        
        return True

def main():
    """Función principal"""
    setup = RailwaySetup()
    
    try:
        success = setup.run_setup()
        if success:
            logger.info("✅ Configuración exitosa")
            sys.exit(0)
        else:
            logger.error("❌ Configuración fallida")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error durante la configuración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 