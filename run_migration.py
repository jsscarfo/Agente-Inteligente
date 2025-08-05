#!/usr/bin/env python3
"""
🚀 Run Database Migration - Ejecutar migración completa a PostgreSQL

Este script configura el entorno y ejecuta la migración de datos JSON a PostgreSQL.
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Configurar variables de entorno"""
    # URL de la base de datos PostgreSQL en Railway
    database_url = "postgresql://postgres:DF*fc11Ec5FAB1BD5A2dGB5fBcfa2DA6@mainline.proxy.rlwy.net:23682/railway"
    
    # Configurar variable de entorno
    os.environ['DATABASE_URL'] = database_url
    
    print("✅ Variables de entorno configuradas")
    return database_url

def run_migration():
    """Ejecutar la migración"""
    try:
        from migrate_to_postgres import DatabaseMigrator
        
        print("🚀 Iniciando migración...")
        migrator = DatabaseMigrator()
        success = migrator.run_migration()
        
        if success:
            print("\n🎉 ¡Migración completada exitosamente!")
            return True
        else:
            print("\n❌ La migración falló")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

def main():
    """Función principal"""
    print("🗄️  Migración de Base de Datos - JSON a PostgreSQL")
    print("=" * 55)
    
    # Configurar entorno
    setup_environment()
    
    # Ejecutar migración
    success = run_migration()
    
    if success:
        print("\n🎯 Tu base de datos está lista en Railway!")
        print("📊 Puedes verificar los datos en el panel de Railway")
        print("🔗 URL de la aplicación: https://agente-inteligente-production.up.railway.app")
    else:
        print("\n⚠️  La migración no se completó")
        sys.exit(1)

if __name__ == "__main__":
    main() 