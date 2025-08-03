#!/usr/bin/env python3
"""
🧠 Test de Sequential Thinking
Script rápido para verificar que Sequential Thinking funciona correctamente
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from agent import IntelligentAgent


async def test_sequential_thinking():
    """Test básico de Sequential Thinking"""
    print("🧠 Test de Sequential Thinking")
    print("=" * 50)
    
    agent = IntelligentAgent()
    
    try:
        # Iniciar agente
        print("🚀 Iniciando agente...")
        await agent.start()
        print("✅ Agente iniciado")
        
        # Verificar que Sequential Thinking está disponible
        system_info = agent.get_system_info()
        print(f"📊 Sequential Thinking: {system_info['sequential_thinking']}")
        
        if system_info['sequential_thinking'] == 'Disabled':
            print("❌ Sequential Thinking no está habilitado")
            return
        
        # Problema de prueba
        test_problem = "Necesito planificar una cena para 8 personas. Tengo un presupuesto de $200 y solo 3 días para prepararlo. ¿Cómo debería proceder?"
        
        print(f"\n📝 Problema de prueba:")
        print(test_problem)
        
        # Resolver con Sequential Thinking
        print(f"\n🔄 Resolviendo con Sequential Thinking...")
        result = await agent.solve_with_sequential_thinking(test_problem)
        
        # Mostrar resultados
        print(f"\n✅ Resultados:")
        print(f"   Éxito: {result['success']}")
        print(f"   Confianza: {result['confidence']:.1%}")
        print(f"   Pasos totales: {result['total_steps']}")
        print(f"   Pasos completados: {result['completed_steps']}")
        print(f"   Pasos fallidos: {result['failed_steps']}")
        
        if result['success']:
            print(f"\n💡 Respuesta:")
            print(result['answer'])
            
            print(f"\n🧠 Proceso de Razonamiento:")
            print(result['formatted_output'])
        else:
            print(f"\n❌ Error: {result['answer']}")
        
        print(f"\n🎉 Test completado!")
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Detener agente
        print("\n🛑 Deteniendo agente...")
        await agent.stop()
        print("✅ Agente detenido")


if __name__ == "__main__":
    asyncio.run(test_sequential_thinking()) 