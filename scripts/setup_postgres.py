#!/usr/bin/env python3
"""
🗄️ Script de Configuración de PostgreSQL para el Agente Inteligente

Este script ayuda a configurar PostgreSQL para el sistema de agente inteligente,
incluyendo la creación de la base de datos, usuario y tablas necesarias.
"""

import asyncio
import sys
import subprocess
from pathlib import Path
from typing import Optional

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.core.config import get_config
from agent.core.database import get_db_manager


class PostgreSQLSetup:
    """Configurador de PostgreSQL"""
    
    def __init__(self):
        self.config = get_config()
        self.db_manager = get_db_manager()
    
    async def check_postgres_installation(self) -> bool:
        """Verificar si PostgreSQL está instalado"""
        try:
            result = subprocess.run(
                ["psql", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ PostgreSQL encontrado: {result.stdout.strip()}")
                return True
            else:
                print("❌ PostgreSQL no encontrado")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ PostgreSQL no está instalado o no está en el PATH")
            return False
    
    async def create_database_and_user(self) -> bool:
        """Crear base de datos y usuario"""
        try:
            print("🔧 Configurando base de datos PostgreSQL...")
            
            # Crear usuario
            create_user_cmd = [
                "psql", "-U", "postgres", "-c",
                f"CREATE USER {self.config.postgres_user} WITH PASSWORD '{self.config.postgres_password}';"
            ]
            
            result = subprocess.run(
                create_user_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 or "already exists" in result.stderr:
                print(f"✅ Usuario {self.config.postgres_user} configurado")
            else:
                print(f"⚠️  Usuario ya existe o error: {result.stderr}")
            
            # Crear base de datos
            create_db_cmd = [
                "psql", "-U", "postgres", "-c",
                f"CREATE DATABASE {self.config.postgres_database} OWNER {self.config.postgres_user};"
            ]
            
            result = subprocess.run(
                create_db_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 or "already exists" in result.stderr:
                print(f"✅ Base de datos {self.config.postgres_database} creada")
                return True
            else:
                print(f"⚠️  Base de datos ya existe o error: {result.stderr}")
                return True
                
        except Exception as e:
            print(f"❌ Error configurando PostgreSQL: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Probar conexión a PostgreSQL"""
        try:
            print("🔗 Probando conexión a PostgreSQL...")
            
            # Inicializar base de datos
            await self.db_manager.initialize()
            
            # Probar consulta simple
            async with self.db_manager.get_async_session() as session:
                result = await session.execute("SELECT version();")
                version = result.scalar()
                print(f"✅ Conexión exitosa: {version}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error conectando a PostgreSQL: {e}")
            return False
    
    async def create_tables(self) -> bool:
        """Crear tablas en la base de datos"""
        try:
            print("📋 Creando tablas...")
            
            # Las tablas se crean automáticamente al inicializar
            await self.db_manager.create_tables()
            
            print("✅ Tablas creadas correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
            return False
    
    async def setup_extensions(self) -> bool:
        """Configurar extensiones de PostgreSQL"""
        try:
            print("🔧 Configurando extensiones...")
            
            # Conectar como superusuario para crear extensiones
            extensions = [
                "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
                "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";",
                "CREATE EXTENSION IF NOT EXISTS \"btree_gin\";"
            ]
            
            for extension in extensions:
                result = subprocess.run(
                    ["psql", "-U", "postgres", "-d", self.config.postgres_database, "-c", extension],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"✅ Extensión configurada: {extension}")
                else:
                    print(f"⚠️  Extensión ya existe o error: {result.stderr}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error configurando extensiones: {e}")
            return False
    
    async def setup_permissions(self) -> bool:
        """Configurar permisos de usuario"""
        try:
            print("🔐 Configurando permisos...")
            
            permissions = [
                f"GRANT ALL PRIVILEGES ON DATABASE {self.config.postgres_database} TO {self.config.postgres_user};",
                f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {self.config.postgres_user};",
                f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {self.config.postgres_user};",
                f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {self.config.postgres_user};",
                f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {self.config.postgres_user};"
            ]
            
            for permission in permissions:
                result = subprocess.run(
                    ["psql", "-U", "postgres", "-d", self.config.postgres_database, "-c", permission],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"✅ Permiso configurado: {permission[:50]}...")
                else:
                    print(f"⚠️  Error configurando permiso: {result.stderr}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error configurando permisos: {e}")
            return False
    
    async def run_full_setup(self) -> bool:
        """Ejecutar configuración completa"""
        print("🚀 Iniciando configuración completa de PostgreSQL")
        print("=" * 60)
        
        try:
            # Verificar instalación
            if not await self.check_postgres_installation():
                print("\n💡 Para instalar PostgreSQL:")
                print("   Windows: https://www.postgresql.org/download/windows/")
                print("   macOS: brew install postgresql")
                print("   Ubuntu: sudo apt-get install postgresql postgresql-contrib")
                return False
            
            # Crear base de datos y usuario
            if not await self.create_database_and_user():
                return False
            
            # Configurar extensiones
            if not await self.setup_extensions():
                return False
            
            # Configurar permisos
            if not await self.setup_permissions():
                return False
            
            # Probar conexión
            if not await self.test_connection():
                return False
            
            # Crear tablas
            if not await self.create_tables():
                return False
            
            print("\n" + "=" * 60)
            print("✅ Configuración de PostgreSQL completada exitosamente")
            print("=" * 60)
            
            print("\n📋 Resumen de configuración:")
            print(f"   Host: {self.config.postgres_host}")
            print(f"   Puerto: {self.config.postgres_port}")
            print(f"   Base de datos: {self.config.postgres_database}")
            print(f"   Usuario: {self.config.postgres_user}")
            print(f"   SSL Mode: {self.config.postgres_ssl_mode}")
            
            print("\n🎯 Próximos pasos:")
            print("   1. Configura las variables de entorno en .env")
            print("   2. Ejecuta: python main.py")
            print("   3. El sistema usará PostgreSQL automáticamente")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error en configuración: {e}")
            return False
        finally:
            # Cerrar conexiones
            await self.db_manager.close()


async def main():
    """Función principal"""
    print("🗄️ Configurador de PostgreSQL - Agente Inteligente")
    print("=" * 60)
    
    try:
        # Verificar configuración
        config = get_config()
        print("✅ Configuración cargada correctamente")
        
        # Crear configurador
        setup = PostgreSQLSetup()
        
        # Ejecutar configuración
        success = await setup.run_full_setup()
        
        if success:
            print("\n🎉 ¡PostgreSQL está listo para usar!")
        else:
            print("\n❌ La configuración no se completó correctamente")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Asegúrate de tener PostgreSQL instalado y configurado")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 