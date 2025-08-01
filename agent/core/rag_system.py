"""
🔍 Sistema RAG (Retrieval-Augmented Generation) del Agente Inteligente

Este módulo implementa un sistema completo de RAG que incluye:
- Procesamiento de documentos
- Generación de embeddings
- Almacenamiento vectorial
- Búsqueda semántica
- Generación de respuestas aumentadas
"""

import asyncio
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma, FAISS
from langchain.schema import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from loguru import logger

from .config import get_config
from .database import get_db_manager, Knowledge


class RAGSystem:
    """
    Sistema RAG del Agente Inteligente
    
    Maneja la recuperación de información y generación de respuestas
    aumentadas con conocimiento externo.
    """
    
    def __init__(self):
        self.config = get_config()
        self.db_manager = get_db_manager()
        
        # Componentes del sistema RAG
        self.embeddings = None
        self.vector_store = None
        self.text_splitter = None
        self.retriever = None
        self.qa_chain = None
        
        # Configuración
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.max_results = 10
        
        self.is_initialized = False
    
    async def initialize(self):
        """Inicializar el sistema RAG"""
        try:
            logger.info("🔍 Inicializando sistema RAG...")
            
            # Inicializar embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.config.openai_api_key,
                model="text-embedding-ada-002"
            )
            
            # Configurar text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            # Inicializar vector store
            await self._initialize_vector_store()
            
            # Configurar retriever
            self._setup_retriever()
            
            # Configurar QA chain
            self._setup_qa_chain()
            
            self.is_initialized = True
            logger.info("✅ Sistema RAG inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando sistema RAG: {e}")
            raise
    
    async def _initialize_vector_store(self):
        """Inicializar el almacén vectorial"""
        try:
            vector_db_path = Path(self.config.vector_db_path)
            vector_db_path.mkdir(parents=True, exist_ok=True)
            
            if self.config.vector_db_type == "chroma":
                self.vector_store = Chroma(
                    persist_directory=str(vector_db_path),
                    embedding_function=self.embeddings,
                    collection_name="agent_knowledge"
                )
            elif self.config.vector_db_type == "faiss":
                # Para FAISS, necesitamos crear un índice inicial
                # Por ahora usamos Chroma como fallback
                self.vector_store = Chroma(
                    persist_directory=str(vector_db_path),
                    embedding_function=self.embeddings,
                    collection_name="agent_knowledge"
                )
            
            logger.info(f"✅ Vector store inicializado: {self.config.vector_db_type}")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando vector store: {e}")
            raise
    
    def _setup_retriever(self):
        """Configurar el retriever"""
        try:
            # Retriever básico
            base_retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.max_results}
            )
            
            # Compresor contextual para mejorar la relevancia
            compressor_prompt = """
            Given the following question and context, extract only the relevant information.
            If the context doesn't contain relevant information, return an empty string.
            
            Question: {question}
            Context: {context}
            
            Relevant information:
            """
            
            compressor = LLMChainExtractor.from_llm(
                ChatOpenAI(
                    openai_api_key=self.config.openai_api_key,
                    model=self.config.openai_model,
                    temperature=0
                ),
                prompt=PromptTemplate.from_template(compressor_prompt)
            )
            
            self.retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=base_retriever
            )
            
            logger.info("✅ Retriever configurado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error configurando retriever: {e}")
            raise
    
    def _setup_qa_chain(self):
        """Configurar la cadena de QA"""
        try:
            # Prompt template para QA
            qa_template = """
            Eres un asistente inteligente experto en proporcionar respuestas precisas y útiles.
            
            Contexto proporcionado:
            {context}
            
            Pregunta: {question}
            
            Instrucciones:
            1. Usa solo la información del contexto proporcionado
            2. Si la información no está en el contexto, indícalo claramente
            3. Proporciona respuestas estructuradas y bien organizadas
            4. Incluye fuentes cuando sea posible
            
            Respuesta:
            """
            
            qa_prompt = PromptTemplate(
                template=qa_template,
                input_variables=["context", "question"]
            )
            
            # Configurar QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(
                    openai_api_key=self.config.openai_api_key,
                    model=self.config.openai_model,
                    temperature=0.3
                ),
                chain_type="stuff",
                retriever=self.retriever,
                chain_type_kwargs={"prompt": qa_prompt},
                return_source_documents=True
            )
            
            logger.info("✅ QA chain configurada correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error configurando QA chain: {e}")
            raise
    
    async def add_document(self, content: str, source: Optional[str] = None,
                          content_type: str = "text", metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Añadir un documento al sistema RAG
        
        Args:
            content: Contenido del documento
            source: Fuente del documento
            content_type: Tipo de contenido
            metadata: Metadatos adicionales
            
        Returns:
            ID del documento añadido
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("Sistema RAG no inicializado")
            
            document_id = str(uuid.uuid4())
            
            # Dividir el contenido en chunks
            chunks = self.text_splitter.split_text(content)
            
            # Crear documentos
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = {
                    "document_id": document_id,
                    "chunk_index": i,
                    "source": source,
                    "content_type": content_type,
                    "created_at": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
                
                doc = Document(
                    page_content=chunk,
                    metadata=doc_metadata
                )
                documents.append(doc)
            
            # Añadir a la base de datos
            await self._save_to_database(document_id, content, source, content_type, metadata)
            
            # Añadir al vector store
            self.vector_store.add_documents(documents)
            
            logger.info(f"✅ Documento añadido: {document_id} ({len(chunks)} chunks)")
            return document_id
            
        except Exception as e:
            logger.error(f"❌ Error añadiendo documento: {e}")
            raise
    
    async def _save_to_database(self, document_id: str, content: str, source: Optional[str],
                               content_type: str, metadata: Optional[Dict[str, Any]]):
        """Guardar documento en la base de datos"""
        try:
            # Crear registro en la base de datos
            knowledge = Knowledge(
                id=document_id,
                content=content,
                content_type=content_type,
                source=source,
                metadata=metadata or {}
            )
            
            # Guardar en la base de datos
            async with self.db_manager.get_async_session() as session:
                session.add(knowledge)
                await session.commit()
                
        except Exception as e:
            logger.error(f"❌ Error guardando en base de datos: {e}")
            raise
    
    async def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Buscar documentos relevantes
        
        Args:
            query: Consulta de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            Lista de documentos relevantes
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("Sistema RAG no inicializado")
            
            # Realizar búsqueda
            docs = self.retriever.get_relevant_documents(
                query,
                k=max_results or self.max_results
            )
            
            # Formatear resultados
            results = []
            for doc in docs:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": doc.metadata.get("score", 0.0)
                }
                results.append(result)
            
            logger.info(f"🔍 Búsqueda completada: {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {e}")
            return []
    
    async def generate_answer(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generar una respuesta usando RAG
        
        Args:
            question: Pregunta del usuario
            context: Contexto adicional
            
        Returns:
            Respuesta generada con fuentes
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("Sistema RAG no inicializado")
            
            # Preparar la pregunta
            if context:
                enhanced_question = f"Contexto: {context}\n\nPregunta: {question}"
            else:
                enhanced_question = question
            
            # Generar respuesta
            result = self.qa_chain({"query": enhanced_question})
            
            # Extraer fuentes
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    source_info = {
                        "content": doc.page_content[:200] + "...",
                        "metadata": doc.metadata,
                        "source": doc.metadata.get("source", "Desconocido")
                    }
                    sources.append(source_info)
            
            response = {
                "answer": result["result"],
                "sources": sources,
                "question": question,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Respuesta generada con {len(sources)} fuentes")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generando respuesta: {e}")
            return {
                "answer": f"Lo siento, ocurrió un error generando la respuesta: {str(e)}",
                "sources": [],
                "question": question,
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def add_knowledge_base(self, knowledge_items: List[Dict[str, Any]]) -> List[str]:
        """
        Añadir múltiples elementos de conocimiento
        
        Args:
            knowledge_items: Lista de elementos de conocimiento
            
        Returns:
            Lista de IDs de documentos añadidos
        """
        try:
            document_ids = []
            
            for item in knowledge_items:
                content = item.get("content")
                source = item.get("source")
                content_type = item.get("content_type", "text")
                metadata = item.get("metadata", {})
                
                if content:
                    doc_id = await self.add_document(
                        content=content,
                        source=source,
                        content_type=content_type,
                        metadata=metadata
                    )
                    document_ids.append(doc_id)
            
            logger.info(f"✅ Base de conocimiento actualizada: {len(document_ids)} documentos")
            return document_ids
            
        except Exception as e:
            logger.error(f"❌ Error actualizando base de conocimiento: {e}")
            raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema RAG"""
        try:
            # Contar documentos en la base de datos
            async with self.db_manager.get_async_session() as session:
                result = await session.execute("SELECT COUNT(*) FROM knowledge")
                total_documents = result.scalar()
                
                result = await session.execute("SELECT COUNT(DISTINCT source) FROM knowledge WHERE source IS NOT NULL")
                unique_sources = result.scalar()
            
            # Obtener información del vector store
            if hasattr(self.vector_store, '_collection'):
                vector_count = self.vector_store._collection.count()
            else:
                vector_count = 0
            
            stats = {
                "total_documents": total_documents or 0,
                "unique_sources": unique_sources or 0,
                "vector_embeddings": vector_count,
                "vector_store_type": self.config.vector_db_type,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "max_results": self.max_results
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    async def clear_knowledge_base(self):
        """Limpiar toda la base de conocimiento"""
        try:
            # Limpiar vector store
            if hasattr(self.vector_store, '_collection'):
                self.vector_store._collection.delete(where={})
            
            # Limpiar base de datos
            async with self.db_manager.get_async_session() as session:
                await session.execute("DELETE FROM knowledge")
                await session.commit()
            
            logger.info("✅ Base de conocimiento limpiada")
            
        except Exception as e:
            logger.error(f"❌ Error limpiando base de conocimiento: {e}")
            raise


# Instancia global del sistema RAG
rag_system = RAGSystem()


def get_rag_system() -> RAGSystem:
    """Obtener el sistema RAG"""
    return rag_system 