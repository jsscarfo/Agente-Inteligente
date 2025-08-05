#!/usr/bin/env python3
"""
🗄️ Database Migration Script - Migrar datos JSON a PostgreSQL en Railway

Este script migra los datos JSON locales a la base de datos PostgreSQL
en Railway para el MLB Assistant.
"""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from datetime import datetime
import sys

class DatabaseMigrator:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL no encontrada. Configura la variable de entorno o pásala como parámetro.")
        
        self.data_dir = Path("data")
        self.conn = None
    
    def connect(self):
        """Conectar a la base de datos PostgreSQL"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            print("✅ Conexión a PostgreSQL establecida")
            return True
        except Exception as e:
            print(f"❌ Error conectando a PostgreSQL: {e}")
            return False
    
    def disconnect(self):
        """Desconectar de la base de datos"""
        if self.conn:
            self.conn.close()
            print("🔌 Conexión cerrada")
    
    def create_tables(self):
        """Crear las tablas necesarias"""
        try:
            with self.conn.cursor() as cursor:
                # Tabla de documentos
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id VARCHAR(255) PRIMARY KEY,
                        title VARCHAR(500) NOT NULL,
                        filename VARCHAR(255),
                        upload_date TIMESTAMP,
                        total_chunks INTEGER DEFAULT 0,
                        total_words INTEGER DEFAULT 0,
                        file_size BIGINT DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabla de fragmentos
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chunks (
                        id VARCHAR(255) PRIMARY KEY,
                        content TEXT NOT NULL,
                        title VARCHAR(500),
                        document_id VARCHAR(255) REFERENCES documents(id) ON DELETE CASCADE NULL,
                        page INTEGER DEFAULT 1,
                        chunk_index INTEGER DEFAULT 0,
                        word_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabla de logs de chat
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_logs (
                        id SERIAL PRIMARY KEY,
                        user_message TEXT NOT NULL,
                        assistant_response TEXT NOT NULL,
                        confidence FLOAT DEFAULT 0.0,
                        processing_time FLOAT DEFAULT 0.0,
                        sources JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabla de estadísticas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS statistics (
                        id SERIAL PRIMARY KEY,
                        total_documents INTEGER DEFAULT 0,
                        total_chunks INTEGER DEFAULT 0,
                        total_words INTEGER DEFAULT 0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Índices para mejorar el rendimiento
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_content ON chunks USING gin(to_tsvector('spanish', content))")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_logs_created_at ON chat_logs(created_at)")
                
                self.conn.commit()
                print("✅ Tablas creadas exitosamente")
                return True
                
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
            self.conn.rollback()
            return False
    
    def load_json_data(self, file_path: Path) -> dict:
        """Cargar datos desde archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error cargando {file_path}: {e}")
            return {}
    
    def migrate_documents(self):
        """Migrar documentos desde JSON a PostgreSQL"""
        documents_file = self.data_dir / "documents.json"
        if not documents_file.exists():
            print("⚠️  No se encontró documents.json")
            return 0
        
        documents = self.load_json_data(documents_file)
        if not documents:
            return 0
        
        migrated_count = 0
        try:
            with self.conn.cursor() as cursor:
                for doc_id, doc_data in documents.items():
                    # Verificar si el documento ya existe
                    cursor.execute("SELECT id FROM documents WHERE id = %s", (doc_id,))
                    if cursor.fetchone():
                        print(f"⚠️  Documento {doc_id} ya existe, saltando...")
                        continue
                    
                    # Insertar documento
                    cursor.execute("""
                        INSERT INTO documents (id, title, filename, upload_date, total_chunks, total_words, file_size)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        doc_id,
                        doc_data.get('title', 'Sin título'),
                        doc_data.get('filename', ''),
                        doc_data.get('upload_date'),
                        doc_data.get('total_chunks', 0),
                        doc_data.get('total_words', 0),
                        doc_data.get('file_size', 0)
                    ))
                    migrated_count += 1
                
                self.conn.commit()
                print(f"✅ {migrated_count} documentos migrados")
                return migrated_count
                
        except Exception as e:
            print(f"❌ Error migrando documentos: {e}")
            self.conn.rollback()
            return 0
    
    def migrate_chunks(self):
        """Migrar fragmentos desde JSON a PostgreSQL"""
        chunks_file = self.data_dir / "chunks.json"
        if not chunks_file.exists():
            print("⚠️  No se encontró chunks.json")
            return 0
        
        chunks = self.load_json_data(chunks_file)
        if not chunks:
            return 0
        
        migrated_count = 0
        try:
            with self.conn.cursor() as cursor:
                for chunk_id, chunk_data in chunks.items():
                    # Verificar si el chunk ya existe
                    cursor.execute("SELECT id FROM chunks WHERE id = %s", (chunk_id,))
                    if cursor.fetchone():
                        print(f"⚠️  Chunk {chunk_id} ya existe, saltando...")
                        continue
                    
                    # Verificar que el documento existe antes de insertar el chunk
                    document_id = chunk_data.get('document', '')
                    if document_id:
                        cursor.execute("SELECT id FROM documents WHERE id = %s", (document_id,))
                        if not cursor.fetchone():
                            print(f"⚠️  Documento {document_id} no existe para chunk {chunk_id}, saltando...")
                            continue
                    
                    # Insertar chunk
                    cursor.execute("""
                        INSERT INTO chunks (id, content, title, document_id, page, chunk_index, word_count)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        chunk_id,
                        chunk_data.get('content', ''),
                        chunk_data.get('title', 'Sin título'),
                        document_id or None,  # Usar None si document_id está vacío
                        chunk_data.get('page', 1),
                        chunk_data.get('chunk_index', 0),
                        chunk_data.get('word_count', 0)
                    ))
                    migrated_count += 1
                    
                    # Mostrar progreso cada 100 chunks
                    if migrated_count % 100 == 0:
                        print(f"📊 Progreso: {migrated_count} chunks migrados...")
                
                self.conn.commit()
                print(f"✅ {migrated_count} fragmentos migrados")
                return migrated_count
                
        except Exception as e:
            print(f"❌ Error migrando fragmentos: {e}")
            self.conn.rollback()
            return 0
    
    def update_statistics(self):
        """Actualizar estadísticas en la base de datos"""
        try:
            with self.conn.cursor() as cursor:
                # Obtener estadísticas actuales
                cursor.execute("SELECT COUNT(*) FROM documents")
                total_documents = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM chunks")
                total_chunks = cursor.fetchone()[0]
                
                cursor.execute("SELECT COALESCE(SUM(word_count), 0) FROM chunks")
                total_words = cursor.fetchone()[0]
                
                # Insertar o actualizar estadísticas
                cursor.execute("""
                    INSERT INTO statistics (total_documents, total_chunks, total_words, last_updated)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        total_documents = EXCLUDED.total_documents,
                        total_chunks = EXCLUDED.total_chunks,
                        total_words = EXCLUDED.total_words,
                        last_updated = EXCLUDED.last_updated
                """, (total_documents, total_chunks, total_words, datetime.now()))
                
                self.conn.commit()
                print(f"📊 Estadísticas actualizadas: {total_documents} docs, {total_chunks} chunks, {total_words} palabras")
                
        except Exception as e:
            print(f"❌ Error actualizando estadísticas: {e}")
            self.conn.rollback()
    
    def search_documents(self, query: str, limit: int = 5):
        """Buscar documentos usando búsqueda de texto completo"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT c.id, c.content, c.title, c.document_id,
                           ts_rank(to_tsvector('spanish', c.content), plainto_tsquery('spanish', %s)) as relevance
                    FROM chunks c
                    WHERE to_tsvector('spanish', c.content) @@ plainto_tsquery('spanish', %s)
                    ORDER BY relevance DESC
                    LIMIT %s
                """, (query, query, limit))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            return []
    
    def get_database_stats(self):
        """Obtener estadísticas de la base de datos"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT total_documents, total_chunks, total_words, last_updated FROM statistics ORDER BY id DESC LIMIT 1")
                result = cursor.fetchone()
                
                if result:
                    return {
                        'total_documents': result[0],
                        'total_chunks': result[1],
                        'total_words': result[2],
                        'last_updated': result[3]
                    }
                else:
                    return {'total_documents': 0, 'total_chunks': 0, 'total_words': 0, 'last_updated': None}
                    
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def run_migration(self):
        """Ejecutar la migración completa"""
        print("🚀 Iniciando migración a PostgreSQL...")
        
        if not self.connect():
            return False
        
        try:
            # Crear tablas
            if not self.create_tables():
                return False
            
            # Migrar documentos
            docs_migrated = self.migrate_documents()
            
            # Migrar fragmentos
            chunks_migrated = self.migrate_chunks()
            
            # Actualizar estadísticas
            self.update_statistics()
            
            print(f"\n🎉 Migración completada:")
            print(f"   📄 Documentos migrados: {docs_migrated}")
            print(f"   🧩 Fragmentos migrados: {chunks_migrated}")
            
            # Mostrar estadísticas finales
            stats = self.get_database_stats()
            print(f"\n📊 Estadísticas de la base de datos:")
            print(f"   📚 Total documentos: {stats.get('total_documents', 0)}")
            print(f"   🧩 Total fragmentos: {stats.get('total_chunks', 0)}")
            print(f"   📝 Total palabras: {stats.get('total_words', 0)}")
            print(f"   🕒 Última actualización: {stats.get('last_updated', 'N/A')}")
            
            return True
            
        finally:
            self.disconnect()

def main():
    """Función principal"""
    print("🗄️  Migrador de Base de Datos - JSON a PostgreSQL")
    print("=" * 50)
    
    # Verificar si DATABASE_URL está configurada
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL no encontrada en variables de entorno")
        print("💡 Configura la variable DATABASE_URL con la URL de tu base de datos PostgreSQL")
        return
    
    # Crear migrador y ejecutar migración
    migrator = DatabaseMigrator(database_url)
    success = migrator.run_migration()
    
    if success:
        print("\n✅ Migración exitosa!")
        print("🎯 Tu base de datos está lista para usar en Railway")
    else:
        print("\n❌ La migración falló")
        sys.exit(1)

if __name__ == "__main__":
    main() 