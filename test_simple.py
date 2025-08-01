#!/usr/bin/env python3
"""
🧪 Prueba Simple del Asistente de IA

Este script realiza una prueba simple para verificar que la configuración básica funciona.
"""

import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config():
    """Probar configuración básica"""
    try:
        from agent.core.config import get_config
        
        config = get_config()
        print("✅ Configuración cargada correctamente")
        
        # Mostrar información básica
        print(f"🤖 Nombre del agente: {config.agent_name}")
        print(f"📊 Versión: {config.agent_version}")
        print(f"🌍 Entorno: {config.environment}")
        print(f"🔧 Debug: {config.debug}")
        
        # Validar configuración
        validation = config.validate_configuration()
        print(f"\n📋 Validación de configuración:")
        print(f"   Válida: {validation['valid']}")
        
        if validation['errors']:
            print(f"   ❌ Errores: {validation['errors']}")
        
        if validation['warnings']:
            print(f"   ⚠️  Advertencias: {validation['warnings']}")
        
        if validation['available_features']:
            print(f"   ✅ Características disponibles: {validation['available_features']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_imports():
    """Probar imports básicos"""
    try:
        print("\n🔍 Probando imports...")
        
        # Probar imports básicos
        from agent.core.models_simple import AgentRequest, PriorityLevel
        print("✅ Models importados correctamente")
        
        from agent.core.config import get_config
        print("✅ Config importado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 PRUEBA SIMPLE DEL ASISTENTE DE IA")
    print("=" * 40)
    
    # Probar imports
    imports_ok = test_imports()
    
    # Probar configuración
    config_ok = test_config()
    
    # Resumen
    print(f"\n📊 RESUMEN:")
    print(f"   Imports: {'✅ OK' if imports_ok else '❌ FALLÓ'}")
    print(f"   Configuración: {'✅ OK' if config_ok else '❌ FALLÓ'}")
    
    if imports_ok and config_ok:
        print(f"\n🎉 ¡Prueba básica exitosa! El sistema está configurado correctamente.")
        print(f"💡 Para usar el asistente completo, configura tu OPENAI_API_KEY en el archivo .env")
    else:
        print(f"\n❌ Hay problemas que necesitan ser solucionados.")

if __name__ == "__main__":
    main() 