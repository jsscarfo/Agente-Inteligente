# 🤖 Asistente de IA Multifuncional

Un asistente de inteligencia artificial avanzado capaz de procesar peticiones en texto libre, estructurar tareas automáticamente, conectarse a múltiples fuentes de datos y generar respuestas inteligentes usando **PostgreSQL**, **LangGraph** y **RAG (Retrieval-Augmented Generation)**.

## 🚀 Características Principales

### 🧠 **Procesamiento Inteligente**
- **Comprensión de Lenguaje Natural**: Procesa peticiones complejas en texto libre
- **Descomposición Automática**: Estructura automáticamente tareas complejas
- **Razonamiento Multi-Paso**: Ejecuta flujos de trabajo complejos
- **Memoria Contextual**: Mantiene contexto entre conversaciones

### 🔄 **Arquitectura con LangGraph**
- **Flujos de Trabajo Inteligentes**: Coordinación de tareas usando LangGraph
- **Agente Coordinador**: Orquesta múltiples agentes especializados
- **Ejecución Paralela**: Procesa tareas en paralelo cuando es posible
- **Gestión de Estado**: Mantiene estado consistente durante la ejecución

### 🔍 **Sistema RAG Avanzado**
- **Búsqueda Semántica**: Encuentra información relevante usando embeddings
- **Base de Conocimiento Vectorial**: Almacena y recupera conocimiento eficientemente
- **Generación Aumentada**: Combina información recuperada con generación de texto
- **Múltiples Fuentes**: Integra información de APIs, documentos y bases de datos

### 🔌 **Conectores de Datos**
- **APIs de Clima**: OpenWeather, WeatherAPI
- **APIs de Noticias**: NewsAPI, GNews
- **APIs Financieras**: Alpha Vantage, Yahoo Finance
- **Búsqueda Web**: Google Search, Serper API
- **Bases de Datos Vectoriales**: ChromaDB, Pinecone, Weaviate, FAISS

### 🛠️ **Herramientas Especializadas**
- **Calculadora Avanzada**: Operaciones matemáticas complejas
- **Analizador de Texto**: Análisis de sentimiento, extracción de palabras clave
- **Procesador de Datos**: Filtrado, ordenamiento, agregación
- **Manejador de Archivos**: Operaciones de lectura/escritura
- **Traductor**: Traducción entre idiomas
- **Programador**: Gestión de tareas programadas

### 🗄️ **Base de Datos PostgreSQL**
- **Almacenamiento Robusto**: PostgreSQL para datos estructurados
- **Escalabilidad**: Soporte para grandes volúmenes de datos
- **Concurrencia**: Múltiples usuarios simultáneos
- **Integridad**: Transacciones ACID y constraints

## 📋 Requisitos

- **Python**: 3.8 o superior
- **PostgreSQL**: 12 o superior (para producción)
- **Memoria RAM**: Mínimo 4GB (recomendado 8GB+)
- **Almacenamiento**: 2GB de espacio libre
- **Conexión a Internet**: Para APIs externas

## 🚀 Instalación Rápida

### 1. Configuración Automática (Recomendado)
```bash
# Ejecutar configuración automática
python setup_assistant.py
```

Este comando:
- ✅ Verifica la versión de Python
- ✅ Crea la estructura de directorios
- ✅ Configura el archivo .env
- ✅ Instala todas las dependencias
- ✅ Prueba el sistema
- ✅ Crea scripts de ejemplo

### 2. Configuración Manual

#### Clonar y Configurar
```bash
git clone <repository-url>
cd Nuevo_Proyecto

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

#### Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar .env con tus claves de API
# IMPORTANTE: Configura OPENAI_API_KEY
```

#### Inicializar el Sistema
```bash
# Inicializar base de datos y componentes
python scripts/init_system.py
```

## 🔧 Configuración

### Variables de Entorno Principales

```bash
# OpenAI (Requerido)
OPENAI_API_KEY=tu_clave_de_openai_aqui
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000

# Base de Datos
ENVIRONMENT=development  # development/production
POSTGRES_HOST=localhost  # Solo para producción
POSTGRES_DATABASE=agent_db

# APIs Externas (Opcionales)
WEATHER_API_KEY=tu_clave_weather
NEWS_API_KEY=tu_clave_news
ALPHA_VANTAGE_API_KEY=tu_clave_finance
GOOGLE_SEARCH_API_KEY=tu_clave_search
```

### Configuración de Herramientas

```bash
# Habilitar/Deshabilitar herramientas
ENABLE_CALCULATOR=true
ENABLE_TEXT_ANALYZER=true
ENABLE_DATA_PROCESSOR=true
ENABLE_FILE_HANDLER=true

# Habilitar/Deshabilitar conectores
ENABLE_WEATHER_CONNECTOR=true
ENABLE_NEWS_CONNECTOR=true
ENABLE_FINANCE_CONNECTOR=true
ENABLE_SEARCH_CONNECTOR=true
```

## 🎯 Uso del Asistente

### 1. Uso Básico

```python
import asyncio
from agent import IntelligentAgent
from agent.core.models import AgentRequest, PriorityLevel

async def main():
    # Crear e inicializar el agente
    agent = IntelligentAgent()
    await agent.start()
    
    # Crear petición
    request = AgentRequest(
        query="¿Cuál es el clima actual en Madrid?",
        priority=PriorityLevel.MEDIUM
    )
    
    # Procesar petición
    response = await agent.process_request(request)
    
    if response.success:
        print(f"Respuesta: {response.content}")
        print(f"Confianza: {response.confidence_score:.1%}")
        print(f"Tiempo: {response.processing_time:.2f}s")
    
    # Detener el agente
    await agent.stop()

asyncio.run(main())
```

### 2. Uso Interactivo

```bash
# Modo interactivo
python main.py

# Con parámetros específicos
python main.py --query "Analiza el mercado de criptomonedas"
python main.py --priority high
python main.py --interactive
```

### 3. Demostración Completa

```bash
# Ejecutar demostración completa
python assistant_demo.py

# O usar el script de demostración
python run_demo.py
```

### 4. Pruebas

```bash
# Prueba básica
python test_basic.py

# Prueba específica
python -m pytest tests/
```

## 📝 Ejemplos de Uso

### Consultas Básicas
```python
# Clima
"¿Cuál es el clima actual en Barcelona?"

# Noticias
"¿Cuáles son las últimas noticias sobre inteligencia artificial?"

# Finanzas
"¿Cuál es el precio actual del Bitcoin?"

# Cálculos
"Calcula la raíz cuadrada de 144 y súmale 25"
```

### Consultas Complejas
```python
# Análisis de mercado
"Analiza el impacto de la IA en el mercado laboral, incluyendo estadísticas recientes y tendencias futuras"

# Planificación
"Crea un plan de marketing digital para una startup de tecnología"

# Investigación
"Investiga y compara las diferentes tecnologías de blockchain"
```

### Consultas con Múltiples Tareas
```python
# Análisis completo
"""
Necesito un análisis completo del mercado de vehículos eléctricos que incluya:
1. Estadísticas actuales de ventas
2. Principales competidores
3. Tendencias tecnológicas
4. Análisis de regulaciones
5. Predicciones de mercado
6. Recomendaciones para inversores
"""
```

## 🔍 Funcionalidades Avanzadas

### Sistema RAG
```python
# Añadir conocimiento al sistema
await agent.add_knowledge(
    content="La IA está transformando la industria...",
    source="Informe McKinsey 2024"
)

# Consultar conocimiento
results = await agent.search_knowledge("impacto de la IA")
```

### Herramientas Especializadas
```python
from agent.core.tools import get_tool_manager, ToolRequest, ToolType

tool_manager = get_tool_manager()

# Usar calculadora
calc_request = ToolRequest(
    tool_type=ToolType.CALCULATOR,
    operation="add",
    parameters={"values": [10, 20, 30]}
)
result = await tool_manager.execute_tool(calc_request)

# Analizar texto
text_request = ToolRequest(
    tool_type=ToolType.TEXT_ANALYZER,
    operation="sentiment",
    parameters={"text": "Este producto es fantástico!"}
)
result = await tool_manager.execute_tool(text_request)
```

### Conectores de Datos
```python
from agent.core.connectors import get_connector_manager, DataRequest, DataSource

connector_manager = get_connector_manager()

# Obtener clima
weather_request = DataRequest(
    source=DataSource.WEATHER,
    query="current_weather",
    parameters={"city": "Madrid"}
)
weather_data = await connector_manager.get_data(weather_request)

# Obtener noticias
news_request = DataRequest(
    source=DataSource.NEWS,
    query="AI news",
    parameters={"language": "es", "page_size": 10}
)
news_data = await connector_manager.get_data(news_request)
```

## 📊 Monitoreo y Métricas

### Estado del Sistema
```python
# Obtener estado
status = await agent.get_status()
print(f"Estado: {status.status}")
print(f"Tareas activas: {len(agent.active_tasks)}")
print(f"Tareas completadas: {len(agent.completed_tasks)}")

# Estadísticas RAG
rag_stats = await agent.rag_system.get_statistics()
print(f"Documentos: {rag_stats['total_documents']}")
print(f"Consultas: {rag_stats['total_queries']}")
```

### Logs y Debugging
```python
# Configurar nivel de logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Ver logs en tiempo real
tail -f data/logs/agent.log
```

## 🔧 Personalización

### Configurar Nuevas Herramientas
```python
from agent.core.tools import BaseTool, ToolResponse

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "custom_tool"
        self.description = "Mi herramienta personalizada"
    
    async def execute(self, parameters):
        # Implementar lógica de la herramienta
        return ToolResponse(success=True, result="Resultado")
```

### Configurar Nuevos Conectores
```python
from agent.core.connectors import BaseConnector, DataResponse

class CustomConnector(BaseConnector):
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.custom_api_key
    
    async def get_data(self, request):
        # Implementar lógica del conector
        return DataResponse(success=True, data={})
```

## 🚀 Despliegue

### Desarrollo
```bash
# Usar SQLite (por defecto)
ENVIRONMENT=development
python main.py
```

### Producción
```bash
# Configurar PostgreSQL
ENVIRONMENT=production
POSTGRES_HOST=tu_host
POSTGRES_DATABASE=agent_db

# Usar gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## 🐛 Solución de Problemas

### Errores Comunes

#### 1. OpenAI API Key no configurada
```
❌ Error: OPENAI_API_KEY no configurada
✅ Solución: Configura tu API key en el archivo .env
```

#### 2. Dependencias faltantes
```
❌ Error: ModuleNotFoundError
✅ Solución: pip install -r requirements.txt
```

#### 3. Base de datos no accesible
```
❌ Error: Database connection failed
✅ Solución: Verifica la configuración de PostgreSQL
```

#### 4. APIs externas no disponibles
```
⚠️  Advertencia: Weather API no configurada
ℹ️  Info: El asistente funcionará sin esta funcionalidad
```

### Debugging
```bash
# Modo debug
DEBUG=true python main.py

# Logs detallados
LOG_LEVEL=DEBUG python main.py

# Verificar configuración
python -c "from agent.core.config import get_config; print(get_config().validate_configuration())"
```

## 📚 Documentación Adicional

- [Guía de LangGraph](https://langchain-ai.github.io/langgraph/)
- [Documentación de RAG](https://python.langchain.com/docs/use_cases/question_answering/)
- [PostgreSQL con SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/)
- [OpenAI API](https://platform.openai.com/docs)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- 📧 Email: soporte@asistente-ia.com
- 💬 Discord: [Servidor de la comunidad](https://discord.gg/asistente-ia)
- 📖 Documentación: [docs.asistente-ia.com](https://docs.asistente-ia.com)
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/asistente-ia/issues)

---

**¡Disfruta usando tu Asistente de IA Multifuncional! 🚀** 