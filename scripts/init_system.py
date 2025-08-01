#!/usr/bin/env python3
"""
🔧 Script de Inicialización del Sistema Agente Inteligente

Este script inicializa todos los componentes necesarios para el
funcionamiento del sistema de agente inteligente, incluyendo
directorios, bases de datos y configuraciones.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Any

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_directories() -> List[str]:
    """
    Crear directorios necesarios para el sistema
    
    Returns:
        Lista de directorios creados
    """
    directories = [
        "data/database",
        "data/knowledge",
        "data/logs",
        "data/cache",
        "data/temp",
        "web/static",
        "web/templates",
        "docs/api",
        "docs/user",
        "tests/unit",
        "tests/integration",
        "tests/fixtures"
    ]
    
    created_dirs = []
    
    for directory in directories:
        dir_path = project_root / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(directory)
            print(f"✅ Creado directorio: {directory}")
        else:
            print(f"ℹ️  Directorio ya existe: {directory}")
    
    return created_dirs


def create_env_file() -> bool:
    """
    Crear archivo .env desde el template
    
    Returns:
        True si se creó exitosamente
    """
    env_template = project_root / "env.example"
    env_file = project_root / ".env"
    
    if env_file.exists():
        print("ℹ️  Archivo .env ya existe")
        return True
    
    if not env_template.exists():
        print("❌ Archivo env.example no encontrado")
        return False
    
    try:
        shutil.copy(env_template, env_file)
        print("✅ Archivo .env creado desde env.example")
        print("💡 Recuerda configurar tus claves de API en el archivo .env")
        return True
    except Exception as e:
        print(f"❌ Error creando archivo .env: {e}")
        return False


def create_init_files() -> List[str]:
    """
    Crear archivos __init__.py necesarios
    
    Returns:
        Lista de archivos creados
    """
    init_paths = [
        "agent/__init__.py",
        "agent/core/__init__.py",
        "agent/agents/__init__.py",
        "agent/connectors/__init__.py",
        "agent/tools/__init__.py",
        "web/__init__.py",
        "web/api/__init__.py",
        "web/frontend/__init__.py",
        "web/dashboard/__init__.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py"
    ]
    
    created_files = []
    
    for init_path in init_paths:
        file_path = project_root / init_path
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
            created_files.append(init_path)
            print(f"✅ Creado archivo: {init_path}")
    
    return created_files


def create_gitignore() -> bool:
    """
    Crear archivo .gitignore si no existe
    
    Returns:
        True si se creó exitosamente
    """
    gitignore_path = project_root / ".gitignore"
    
    if gitignore_path.exists():
        print("ℹ️  Archivo .gitignore ya existe")
        return True
    
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Project specific
data/database/*.db
data/logs/*.log
data/cache/*
data/temp/*
*.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
    
    try:
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("✅ Archivo .gitignore creado")
        return True
    except Exception as e:
        print(f"❌ Error creando .gitignore: {e}")
        return False


def create_requirements_dev() -> bool:
    """
    Crear archivo requirements-dev.txt para desarrollo
    
    Returns:
        True si se creó exitosamente
    """
    dev_requirements_path = project_root / "requirements-dev.txt"
    
    if dev_requirements_path.exists():
        print("ℹ️  Archivo requirements-dev.txt ya existe")
        return True
    
    dev_requirements_content = """# Development dependencies
-r requirements.txt

# Testing
pytest>=7.4.3
pytest-asyncio>=0.21.1
pytest-cov>=4.1.0
pytest-mock>=3.12.0
pytest-xdist>=3.3.1

# Code quality
black>=23.11.0
isort>=5.12.0
flake8>=6.1.0
mypy>=1.7.1
bandit>=1.7.5

# Documentation
mkdocs>=1.5.3
mkdocs-material>=9.4.8
mkdocstrings[python]>=0.24.0

# Development tools
pre-commit>=3.5.0
jupyter>=1.0.0
ipython>=8.17.0

# Monitoring and debugging
memory-profiler>=0.61.0
line-profiler>=4.1.0
"""
    
    try:
        with open(dev_requirements_path, 'w', encoding='utf-8') as f:
            f.write(dev_requirements_content)
        print("✅ Archivo requirements-dev.txt creado")
        return True
    except Exception as e:
        print(f"❌ Error creando requirements-dev.txt: {e}")
        return False


def create_docker_files() -> List[str]:
    """
    Crear archivos Docker si no existen
    
    Returns:
        Lista de archivos creados
    """
    docker_files = []
    
    # Dockerfile
    dockerfile_path = project_root / "Dockerfile"
    if not dockerfile_path.exists():
        dockerfile_content = """# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data/database data/knowledge data/logs data/cache data/temp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "main.py"]
"""
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        docker_files.append("Dockerfile")
        print("✅ Dockerfile creado")
    
    # docker-compose.yml
    compose_path = project_root / "docker-compose.yml"
    if not compose_path.exists():
        compose_content = """version: '3.8'

services:
  agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: agent_db
      POSTGRES_USER: agent_user
      POSTGRES_PASSWORD: agent_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
"""
        with open(compose_path, 'w', encoding='utf-8') as f:
            f.write(compose_content)
        docker_files.append("docker-compose.yml")
        print("✅ docker-compose.yml creado")
    
    return docker_files


def create_makefile() -> bool:
    """
    Crear Makefile para comandos útiles
    
    Returns:
        True si se creó exitosamente
    """
    makefile_path = project_root / "Makefile"
    
    if makefile_path.exists():
        print("ℹ️  Makefile ya existe")
        return True
    
    makefile_content = """# Makefile para Agente Inteligente

.PHONY: help install install-dev test lint format clean run docker-build docker-run

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias de producción
	pip install -r requirements.txt

install-dev: ## Instalar dependencias de desarrollo
	pip install -r requirements-dev.txt

test: ## Ejecutar tests
	pytest tests/ -v --cov=agent --cov-report=html

lint: ## Ejecutar linting
	flake8 agent/ tests/
	mypy agent/

format: ## Formatear código
	black agent/ tests/
	isort agent/ tests/

clean: ## Limpiar archivos temporales
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

run: ## Ejecutar el agente
	python main.py

run-interactive: ## Ejecutar en modo interactivo
	python main.py --interactive

docker-build: ## Construir imagen Docker
	docker build -t agente-inteligente .

docker-run: ## Ejecutar con Docker Compose
	docker-compose up -d

docker-stop: ## Detener Docker Compose
	docker-compose down

setup: install-dev ## Configurar entorno de desarrollo
	pre-commit install
"""
    
    try:
        with open(makefile_path, 'w', encoding='utf-8') as f:
            f.write(makefile_content)
        print("✅ Makefile creado")
        return True
    except Exception as e:
        print(f"❌ Error creando Makefile: {e}")
        return False


def main():
    """Función principal de inicialización"""
    print("🔧 Inicializando Sistema Agente Inteligente")
    print("=" * 50)
    
    try:
        # Crear directorios
        print("\n📁 Creando directorios...")
        created_dirs = create_directories()
        
        # Crear archivos __init__.py
        print("\n📄 Creando archivos __init__.py...")
        created_init_files = create_init_files()
        
        # Crear archivo .env
        print("\n🔐 Configurando archivo .env...")
        env_created = create_env_file()
        
        # Crear .gitignore
        print("\n🚫 Configurando .gitignore...")
        gitignore_created = create_gitignore()
        
        # Crear requirements-dev.txt
        print("\n📦 Configurando dependencias de desarrollo...")
        dev_req_created = create_requirements_dev()
        
        # Crear archivos Docker
        print("\n🐳 Configurando Docker...")
        docker_files = create_docker_files()
        
        # Crear Makefile
        print("\n🔨 Configurando Makefile...")
        makefile_created = create_makefile()
        
        # Resumen
        print("\n" + "=" * 50)
        print("✅ INICIALIZACIÓN COMPLETADA")
        print("=" * 50)
        print(f"📁 Directorios creados: {len(created_dirs)}")
        print(f"📄 Archivos __init__.py creados: {len(created_init_files)}")
        print(f"🔐 Archivo .env: {'✅' if env_created else '❌'}")
        print(f"🚫 Archivo .gitignore: {'✅' if gitignore_created else '❌'}")
        print(f"📦 requirements-dev.txt: {'✅' if dev_req_created else '❌'}")
        print(f"🐳 Archivos Docker: {len(docker_files)}")
        print(f"🔨 Makefile: {'✅' if makefile_created else '❌'}")
        
        print("\n🎯 PRÓXIMOS PASOS:")
        print("1. Configura tu archivo .env con las claves de API necesarias")
        print("2. Instala las dependencias: pip install -r requirements.txt")
        print("3. Ejecuta el agente: python main.py")
        print("4. Para desarrollo: pip install -r requirements-dev.txt")
        
        print("\n📚 DOCUMENTACIÓN:")
        print("- README.md: Documentación principal")
        print("- docs/: Documentación detallada")
        print("- tests/: Tests del sistema")
        
        print("\n🚀 ¡El sistema está listo para usar!")
        
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 