"""
⚙️ Configuración del Agente Inteligente

Este módulo maneja toda la configuración del sistema de agente inteligente,
incluyendo variables de entorno, configuraciones de base de datos, APIs,
y parámetros del sistema.
"""

import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class AgentConfig(BaseSettings):
    """Configuración principal del agente"""
    
    # =============================================================================
    # 🔑 OPENAI CONFIGURATION
    # =============================================================================
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # =============================================================================
    # 🗄️ DATABASE CONFIGURATION
    # =============================================================================
    # PostgreSQL Configuration (Producción)
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="agent_user", env="POSTGRES_USER")
    postgres_password: str = Field(default="agent_password", env="POSTGRES_PASSWORD")
    postgres_database: str = Field(default="agent_db", env="POSTGRES_DATABASE")
    postgres_ssl_mode: str = Field(default="prefer", env="POSTGRES_SSL_MODE")
    
    # SQLite Configuration (Desarrollo)
    sqlite_database: str = Field(default="sqlite:///./data/database/agent.db", env="SQLITE_DATABASE")
    
    # Vector Database Configuration
    vector_db_path: str = Field(default="./data/knowledge/vector_db", env="VECTOR_DB_PATH")
    vector_db_type: str = Field(default="chroma", env="VECTOR_DB_TYPE")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # =============================================================================
    # 🌐 EXTERNAL APIs CONFIGURATION
    # =============================================================================
    # Weather APIs
    weather_api_key: Optional[str] = Field(default=None, env="WEATHER_API_KEY")
    openweather_api_key: Optional[str] = Field(default=None, env="OPENWEATHER_API_KEY")
    
    # News APIs
    news_api_key: Optional[str] = Field(default=None, env="NEWS_API_KEY")
    gnews_api_key: Optional[str] = Field(default=None, env="GNEWS_API_KEY")
    
    # Finance APIs
    alpha_vantage_api_key: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_API_KEY")
    yahoo_finance_api_key: Optional[str] = Field(default=None, env="YAHOO_FINANCE_API_KEY")
    
    # Search APIs
    google_search_api_key: Optional[str] = Field(default=None, env="GOOGLE_SEARCH_API_KEY")
    serper_api_key: Optional[str] = Field(default=None, env="SERPER_API_KEY")
    
    # Translation APIs
    google_translate_api_key: Optional[str] = Field(default=None, env="GOOGLE_TRANSLATE_API_KEY")
    deepl_api_key: Optional[str] = Field(default=None, env="DEEPL_API_KEY")
    
    # Email APIs
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: Optional[int] = Field(default=None, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # =============================================================================
    # ⚙️ SYSTEM CONFIGURATION
    # =============================================================================
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_concurrent_tasks: int = Field(default=10, env="MAX_CONCURRENT_TASKS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # Agent Configuration
    agent_name: str = Field(default="Asistente IA", env="AGENT_NAME")
    agent_version: str = Field(default="1.0.0", env="AGENT_VERSION")
    agent_description: str = Field(default="Asistente de IA multifuncional", env="AGENT_DESCRIPTION")
    
    # RAG Configuration
    rag_chunk_size: int = Field(default=1000, env="RAG_CHUNK_SIZE")
    rag_chunk_overlap: int = Field(default=200, env="RAG_CHUNK_OVERLAP")
    rag_max_results: int = Field(default=10, env="RAG_MAX_RESULTS")
    rag_embedding_model: str = Field(default="text-embedding-ada-002", env="RAG_EMBEDDING_MODEL")
    
    # LangGraph Configuration
    langgraph_max_iterations: int = Field(default=10, env="LANGGRAPH_MAX_ITERATIONS")
    langgraph_checkpoint_dir: str = Field(default="./data/checkpoints", env="LANGGRAPH_CHECKPOINT_DIR")
    
    # =============================================================================
    # 🔒 SECURITY CONFIGURATION
    # =============================================================================
    secret_key: str = Field(default="", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    
    # =============================================================================
    # 📊 MONITORING CONFIGURATION
    # =============================================================================
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    enable_health_check: bool = Field(default=True, env="ENABLE_HEALTH_CHECK")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    # =============================================================================
    # 🌍 ENVIRONMENT
    # =============================================================================
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:8000"], env="CORS_ORIGINS")
    
    # =============================================================================
    # 📧 NOTIFICATIONS CONFIGURATION
    # =============================================================================
    slack_webhook_url: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    discord_webhook_url: Optional[str] = Field(default=None, env="DISCORD_WEBHOOK_URL")
    telegram_bot_token: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    
    # =============================================================================
    # 🛠️ TOOLS CONFIGURATION
    # =============================================================================
    enable_calculator: bool = Field(default=True, env="ENABLE_CALCULATOR")
    enable_text_analyzer: bool = Field(default=True, env="ENABLE_TEXT_ANALYZER")
    enable_data_processor: bool = Field(default=True, env="ENABLE_DATA_PROCESSOR")
    enable_file_handler: bool = Field(default=True, env="ENABLE_FILE_HANDLER")
    enable_web_scraper: bool = Field(default=False, env="ENABLE_WEB_SCRAPER")
    enable_translator: bool = Field(default=False, env="ENABLE_TRANSLATOR")
    enable_scheduler: bool = Field(default=False, env="ENABLE_SCHEDULER")
    enable_email_sender: bool = Field(default=False, env="ENABLE_EMAIL_SENDER")
    
    # =============================================================================
    # 🔌 CONNECTORS CONFIGURATION
    # =============================================================================
    enable_weather_connector: bool = Field(default=True, env="ENABLE_WEATHER_CONNECTOR")
    enable_news_connector: bool = Field(default=True, env="ENABLE_NEWS_CONNECTOR")
    enable_finance_connector: bool = Field(default=True, env="ENABLE_FINANCE_CONNECTOR")
    enable_search_connector: bool = Field(default=True, env="ENABLE_SEARCH_CONNECTOR")
    
    # =============================================================================
    # 📁 PATHS CONFIGURATION
    # =============================================================================
    data_dir: str = Field(default="./data", env="DATA_DIR")
    logs_dir: str = Field(default="./data/logs", env="LOGS_DIR")
    temp_dir: str = Field(default="./data/temp", env="TEMP_DIR")
    uploads_dir: str = Field(default="./data/uploads", env="UPLOADS_DIR")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Asegurar que los directorios necesarios existan"""
        directories = [
            self.data_dir,
            self.logs_dir,
            self.temp_dir,
            self.uploads_dir,
            self.vector_db_path,
            self.langgraph_checkpoint_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get_database_url(self) -> str:
        """Obtener URL de base de datos asíncrona"""
        if self.environment == "production" and self.postgres_host:
            return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
        else:
            return self.sqlite_database.replace("sqlite:///", "sqlite+aiosqlite:///")
    
    def get_sync_database_url(self) -> str:
        """Obtener URL de base de datos síncrona"""
        if self.environment == "production" and self.postgres_host:
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
        else:
            return self.sqlite_database
    
    def get_redis_url(self) -> str:
        """Obtener URL de Redis"""
        return self.redis_url
    
    def is_production(self) -> bool:
        """Verificar si está en producción"""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Verificar si está en desarrollo"""
        return self.environment.lower() == "development"
    
    def get_enabled_tools(self) -> List[str]:
        """Obtener herramientas habilitadas"""
        enabled_tools = []
        
        if self.enable_calculator:
            enabled_tools.append("calculator")
        if self.enable_text_analyzer:
            enabled_tools.append("text_analyzer")
        if self.enable_data_processor:
            enabled_tools.append("data_processor")
        if self.enable_file_handler:
            enabled_tools.append("file_handler")
        if self.enable_web_scraper:
            enabled_tools.append("web_scraper")
        if self.enable_translator:
            enabled_tools.append("translator")
        if self.enable_scheduler:
            enabled_tools.append("scheduler")
        if self.enable_email_sender:
            enabled_tools.append("email_sender")
        
        return enabled_tools
    
    def get_enabled_connectors(self) -> List[str]:
        """Obtener conectores habilitados"""
        enabled_connectors = []
        
        if self.enable_weather_connector and (self.weather_api_key or self.openweather_api_key):
            enabled_connectors.append("weather")
        if self.enable_news_connector and (self.news_api_key or self.gnews_api_key):
            enabled_connectors.append("news")
        if self.enable_finance_connector and self.alpha_vantage_api_key:
            enabled_connectors.append("finance")
        if self.enable_search_connector and (self.google_search_api_key or self.serper_api_key):
            enabled_connectors.append("search")
        
        return enabled_connectors
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validar configuración y devolver estado"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "missing_apis": [],
            "available_features": []
        }
        
        # Validar OpenAI
        if not self.openai_api_key:
            validation_result["errors"].append("OPENAI_API_KEY no configurada")
            validation_result["valid"] = False
        else:
            validation_result["available_features"].append("OpenAI Integration")
        
        # Validar base de datos
        if self.is_production() and not self.postgres_host:
            validation_result["warnings"].append("PostgreSQL no configurado para producción")
        
        # Validar APIs externas
        if not self.weather_api_key and not self.openweather_api_key:
            validation_result["missing_apis"].append("Weather API")
        
        if not self.news_api_key and not self.gnews_api_key:
            validation_result["missing_apis"].append("News API")
        
        if not self.alpha_vantage_api_key:
            validation_result["missing_apis"].append("Finance API")
        
        if not self.google_search_api_key and not self.serper_api_key:
            validation_result["missing_apis"].append("Search API")
        
        # Verificar características disponibles
        if validation_result["valid"]:
            validation_result["available_features"].extend([
                "RAG System",
                "LangGraph Workflows",
                "Database Storage",
                "Task Management"
            ])
            
            # Añadir herramientas disponibles
            enabled_tools = self.get_enabled_tools()
            if enabled_tools:
                validation_result["available_features"].append(f"Tools: {', '.join(enabled_tools)}")
            
            # Añadir conectores disponibles
            enabled_connectors = self.get_enabled_connectors()
            if enabled_connectors:
                validation_result["available_features"].append(f"Connectors: {', '.join(enabled_connectors)}")
        
        return validation_result
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtener información del sistema"""
        return {
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "agent_description": self.agent_description,
            "environment": self.environment,
            "debug": self.debug,
            "openai_model": self.openai_model,
            "database_type": "PostgreSQL" if self.is_production() else "SQLite",
            "vector_db_type": self.vector_db_type,
            "enabled_tools": self.get_enabled_tools(),
            "enabled_connectors": self.get_enabled_connectors(),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "request_timeout": self.request_timeout,
            "rag_chunk_size": self.rag_chunk_size,
            "langgraph_max_iterations": self.langgraph_max_iterations
        }


# Instancia global de configuración
_config = None


def get_config() -> AgentConfig:
    """Obtener instancia global de configuración"""
    global _config
    if _config is None:
        _config = AgentConfig()
    return _config


def reload_config() -> AgentConfig:
    """Recargar configuración desde archivo .env"""
    global _config
    _config = AgentConfig()
    return _config 