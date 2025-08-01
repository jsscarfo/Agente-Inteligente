"""
Setup Script para Contextual Retrieval
Inicializa y configura el sistema de Contextual Retrieval
"""

import os
import json
import time
from pathlib import Path
from contextual_retrieval import ContextualRetrieval

def main():
    """Función principal para configurar Contextual Retrieval"""
    print("🚀 Configurando Contextual Retrieval...")
    print("=" * 50)
    
    # Verificar archivos necesarios
    documents_file = "data/documents.json"
    chunks_file = "data/chunks.json"
    
    if not os.path.exists(documents_file):
        print(f"❌ No se encontró {documents_file}")
        print("💡 Ejecuta primero cargar_pdf_simple.py para crear los documentos")
        return False
    
    if not os.path.exists(chunks_file):
        print(f"❌ No se encontró {chunks_file}")
        print("💡 Ejecuta primero cargar_pdf_simple.py para crear los chunks")
        return False
    
    # Verificar API key de OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("⚠️ No se encontró OPENAI_API_KEY")
        print("💡 El sistema funcionará con capacidades limitadas")
        print("   Para funcionalidad completa, configura tu API key:")
        print("   set OPENAI_API_KEY=tu_clave_aqui")
        use_openai = False
    else:
        print("✅ OpenAI API key encontrada")
        use_openai = True
    
    # Inicializar sistema
    print("\n📚 Inicializando Contextual Retrieval...")
    cr = ContextualRetrieval(openai_api_key=openai_key)
    
    # Cargar datos
    print("📖 Cargando documentos y chunks...")
    if not cr.load_data(documents_file, chunks_file):
        print("❌ Error cargando datos")
        return False
    
    print(f"✅ Cargados {len(cr.documents)} documentos y {len(cr.contextual_chunks)} chunks")
    
    # Contextualizar chunks
    print("\n🔄 Iniciando contextualización de chunks...")
    start_time = time.time()
    
    cr.contextualize_all_chunks()
    
    contextual_time = time.time() - start_time
    print(f"✅ Contextualización completada en {contextual_time:.2f} segundos")
    
    # Crear embeddings contextualizados
    print("\n🧠 Creando embeddings contextualizados...")
    start_time = time.time()
    
    cr.create_contextual_embeddings()
    
    embedding_time = time.time() - start_time
    print(f"✅ Embeddings creados en {embedding_time:.2f} segundos")
    
    # Crear BM25 contextualizado
    print("\n🔍 Creando índice BM25 contextualizado...")
    start_time = time.time()
    
    cr.create_contextual_bm25()
    
    bm25_time = time.time() - start_time
    print(f"✅ BM25 contextualizado creado en {bm25_time:.2f} segundos")
    
    # Guardar datos contextualizados
    print("\n💾 Guardando datos contextualizados...")
    cr.save_contextualized_data()
    
    # Mostrar estadísticas finales
    stats = cr.get_stats()
    print("\n📊 Estadísticas del sistema Contextual Retrieval:")
    print(f"   📚 Documentos: {stats['total_documents']}")
    print(f"   🧩 Chunks contextualizados: {stats['total_contextual_chunks']}")
    print(f"   🧠 Embeddings: {'✅' if stats['has_embeddings'] else '❌'}")
    print(f"   🔍 BM25: {'✅' if stats['has_bm25'] else '❌'}")
    print(f"   🤖 OpenAI: {'✅' if stats['has_openai'] else '❌'}")
    
    # Prueba del sistema
    print("\n🧪 Probando el sistema...")
    test_queries = [
        "corredor fantasma",
        "reglas de apuestas",
        "política de drogas"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Probando: '{query}'")
        results = cr.search_contextual(query, limit=2, use_reranking=use_openai)
        
        if results:
            best_result = results[0]
            chunk = best_result['chunk']
            print(f"   ✅ Encontrado en: {chunk.document_title}")
            print(f"   📄 Página: {chunk.page_number}")
            print(f"   🎯 Score: {best_result.get('combined_score', 0):.3f}")
            if use_openai:
                print(f"   🏆 Rerank: {best_result.get('rerank_score', 0):.1f}")
            print(f"   📝 Contexto: {chunk.context_summary[:80]}...")
        else:
            print(f"   ❌ No se encontraron resultados")
    
    # Instrucciones de uso
    print("\n🎉 ¡Contextual Retrieval configurado exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Ejecuta el servidor web mejorado:")
    print("   python web_chat_contextual.py")
    print("2. Abre tu navegador en: http://localhost:8080")
    print("3. ¡Disfruta de búsquedas más precisas y relevantes!")
    
    print("\n🔧 Características habilitadas:")
    if use_openai:
        print("   ✅ Contextualización automática con IA")
        print("   ✅ Embeddings contextualizados")
        print("   ✅ Reranking inteligente")
        print("   ✅ Rank fusion avanzado")
    else:
        print("   ✅ Contextualización básica")
        print("   ✅ BM25 contextualizado")
        print("   ✅ Búsqueda híbrida")
        print("   ⚠️ Reranking deshabilitado (sin OpenAI)")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✨ ¡Configuración completada exitosamente!")
    else:
        print("\n❌ Error en la configuración")
        print("💡 Verifica que tengas los archivos de datos necesarios") 