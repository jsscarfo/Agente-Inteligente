#!/usr/bin/env python3
"""
🔧 Setup Database Environment - Configurar variables de entorno para migración

Este script configura la variable DATABASE_URL para conectar con PostgreSQL en Railway.
"""

import os
import sys
from pathlib import Path

def setup_database_url():
    """Configurar DATABASE_URL para Railway PostgreSQL"""
    
    # URL de la base de datos PostgreSQL en Railway
    database_url = "postgresql://postgres:DF*fc11Ec5FAB1BD5A2dGB5fBcfa2DA6@mainline.proxy.rlwy.net:23682/railway"
    
    print("🗄️  Configurando DATABASE_URL para Railway PostgreSQL")
    print("=" * 50)
    print(f"📡 URL: {database_url}")
    print()
    
    # Configurar variable de entorno
    os.environ['DATABASE_URL'] = database_url
    
    print("✅ DATABASE_URL configurada exitosamente")
    print("🚀 Ahora puedes ejecutar la migración con: python migrate_to_postgres.py")
    
    return database_url

def test_connection():
    """Probar conexión a la base de datos"""
    try:
        import psycopg2
        from migrate_to_postgres import DatabaseMigrator
        
        print("\n🔍 Probando conexión a PostgreSQL...")
        
        migrator = DatabaseMigrator()
        if migrator.connect():
            print("✅ Conexión exitosa!")
            migrator.disconnect()
            return True
        else:
            print("❌ Error de conexión")
            return False
            
    except ImportError:
        print("❌ psycopg2 no está instalado")
        print("💡 Instala las dependencias: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 Setup Database Environment")
    print("=" * 30)
    
    # Configurar DATABASE_URL
    setup_database_url()
    
    # Probar conexión
    if test_connection():
        print("\n🎉 ¡Todo listo para la migración!")
        print("📝 Ejecuta: python migrate_to_postgres.py")
    else:
        print("\n⚠️  Hay problemas con la conexión")
        print("🔧 Verifica la configuración e intenta de nuevo")

if __name__ == "__main__":
    main() 