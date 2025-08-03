<<<<<<< HEAD
# 🤖 Agente Inteligente

Un sistema de agente de inteligencia artificial avanzado capaz de procesar peticiones complejas, coordinar múltiples tareas y generar respuestas estructuradas usando **PostgreSQL**, **LangGraph** y **RAG (Retrieval-Augmented Generation)**.

## 🚀 Características Principales

### 🧠 **Inteligencia Artificial Avanzada**
- **Procesamiento de Lenguaje Natural**: Comprensión profunda de peticiones en texto libre
- **Razonamiento Multi-Paso**: Descomposición automática de tareas complejas
- **Sequential Thinking**: Razonamiento secuencial estructurado para problemas complejos
- **Memoria Contextual**: Mantiene contexto entre conversaciones
- **Aprendizaje Adaptativo**: Mejora respuestas basado en interacciones previas

### 🔄 **Arquitectura Multi-Agente con LangGraph**
- **Flujo de Trabajo Inteligente**: Coordinación de tareas usando LangGraph
- **Agente Coordinador**: Orquesta y gestiona tareas complejas
- **Agente de Investigación**: Búsqueda y recopilación de información
- **Agente de Análisis**: Procesamiento y análisis de datos
- **Agente de Síntesis**: Generación de respuestas estructuradas
- **Agente de Validación**: Verificación de calidad y precisión

### 🔍 **Sistema RAG (Retrieval-Augmented Generation)**
- **Búsqueda Semántica**: Encuentra información relevante usando embeddings
- **Base de Conocimiento Vectorial**: Almacena y recupera conocimiento de forma eficiente
- **Generación Aumentada**: Combina información recuperada con generación de texto
- **Fuentes Múltiples**: Integra información de APIs, documentos y bases de datos

### 🗄️ **Base de Datos PostgreSQL**
- **Almacenamiento Robusto**: PostgreSQL para datos estructurados
- **Escalabilidad**: Soporte para grandes volúmenes de datos
- **Concurrencia**: Múltiples usuarios simultáneos
- **Integridad**: Transacciones ACID y constraints

### 🔌 **Conectores de Datos**
- **APIs REST**: Integración con servicios externos
- **Bases de Datos Vectoriales**: ChromaDB, Pinecone, Weaviate, FAISS
- **Bases de Datos Relacionales**: PostgreSQL, SQLite (desarrollo)
- **APIs de Tiempo Real**: Weather, News, Finance, etc.

### 🛠️ **Herramientas Avanzadas**
- **Procesamiento Asíncrono**: Ejecución paralela de tareas
- **Gestión de Errores**: Manejo robusto de fallos
- **Logging Inteligente**: Registro detallado de operaciones
- **Monitoreo en Tiempo Real**: Métricas de rendimiento

### 🧠 **Sequential Thinking**
- **Razonamiento Estructurado**: Descomposición paso a paso de problemas complejos
- **Análisis Automático**: Identificación de componentes y dependencias
- **Validación de Pasos**: Verificación de cada etapa del proceso
- **Síntesis Inteligente**: Integración de resultados en respuestas coherentes
- **Transparencia Total**: Visibilidad completa del proceso de pensamiento

## 📋 Requisitos

- **Python**: 3.8 o superior
- **PostgreSQL**: 12 o superior (para producción)
- **Memoria RAM**: Mínimo 4GB (recomendado 8GB+)
- **Almacenamiento**: 2GB de espacio libre
- **Conexión a Internet**: Para APIs externas

## 🚀 Instalación Rápida

### 1. Clonar el Proyecto
```bash
git clone <repository-url>
cd Agente_Inteligente
```

### 2. Configurar Entorno Virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
cp env.example .env
# Editar .env con tus claves de API
```

### 5. Configurar PostgreSQL (Opcional)
```bash
# Para desarrollo (SQLite automático)
python scripts/init_system.py

# Para producción (PostgreSQL)
python scripts/setup_postgres.py
```

### 6. Inicializar el Sistema
```bash
python scripts/init_system.py
```

### 7. Ejecutar el Agente
```bash
python main.py
```

## 🔧 Configuración

### Variables de Entorno Principales

```env
# OpenAI Configuration
OPENAI_API_KEY=tu_clave_de_openai_aqui
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7

# PostgreSQL Configuration (Producción)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=agent_user
POSTGRES_PASSWORD=agent_password
POSTGRES_DATABASE=agent_db
POSTGRES_SSL_MODE=prefer

# SQLite Configuration (Desarrollo)
SQLITE_DATABASE=sqlite:///./data/database/agent.db

# Vector Database Configuration
VECTOR_DB_PATH=./data/knowledge/vector_db
VECTOR_DB_TYPE=chroma

# Redis Configuration
REDIS_URL=redis://localhost:6379

# External APIs (Optional)
WEATHER_API_KEY=tu_clave_weather_api
NEWS_API_KEY=tu_clave_news_api
FINANCE_API_KEY=tu_clave_finance_api

# System Configuration
LOG_LEVEL=INFO
MAX_CONCURRENT_TASKS=10
REQUEST_TIMEOUT=30
ENVIRONMENT=development
```

## 📖 Uso

### Interfaz Web
```bash
# Iniciar servidor web
python web_server.py

# Acceder a la interfaz
# http://localhost:8000
```

### API REST
```bash
# Procesar petición
curl -X POST "http://localhost:8000/api/process" \
     -H "Content-Type: application/json" \
     -d '{"query": "Analiza el clima de Madrid y sugiere actividades"}'

# Obtener estado
curl "http://localhost:8000/api/status"
```

### Uso Programático
```python
from agent import IntelligentAgent

# Crear agente
agent = IntelligentAgent()
await agent.start()

# Procesar petición
response = await agent.process_request(
    "Investiga sobre inteligencia artificial y crea un resumen"
)

print(response.content)

# Añadir conocimiento
await agent.add_knowledge(
    "La inteligencia artificial es un campo de la informática...",
    metadata={"source": "manual", "topic": "AI"}
)

# Buscar conocimiento
results = await agent.search_knowledge("machine learning", limit=5)
```

## 🏗️ Arquitectura del Sistema

```
Agente_Inteligente/
├── 📁 agent/                 # Núcleo del agente
│   ├── 🧠 core/             # Lógica principal
│   │   ├── config.py        # Configuración del sistema
│   │   ├── models.py        # Modelos de datos
│   │   ├── database.py      # Sistema PostgreSQL
│   │   ├── rag_system.py    # Sistema RAG
│   │   ├── workflow_graph.py # LangGraph workflows
│   │   └── intelligent_agent.py # Agente principal
│   ├── 🤖 agents/           # Agentes especializados
│   ├── 🔌 connectors/       # Conectores de datos
│   └── 🛠️ tools/            # Herramientas auxiliares
├── 📁 web/                  # Interfaz web
│   ├── 🌐 api/              # Endpoints REST
│   ├── 🎨 frontend/         # Interfaz de usuario
│   └── 📊 dashboard/        # Panel de control
├── 📁 data/                 # Datos del sistema
│   ├── 🗄️ database/         # Bases de datos
│   ├── 📚 knowledge/        # Base de conocimiento
│   └── 📝 logs/             # Registros del sistema
├── 📁 scripts/              # Scripts de utilidad
│   ├── init_system.py       # Inicialización del sistema
│   └── setup_postgres.py    # Configuración PostgreSQL
├── 📁 tests/                # Pruebas del sistema
└── 📁 docs/                 # Documentación
```

## 🎯 Casos de Uso

### 🔍 **Investigación y Análisis**
- Búsqueda de información en múltiples fuentes usando RAG
- Análisis de tendencias y patrones con LangGraph
- Generación de reportes estructurados

### 💡 **Asistencia Inteligente**
- Respuestas a preguntas complejas con contexto
- Sugerencias personalizadas basadas en historial
- Planificación y organización automática

### 📊 **Procesamiento de Datos**
- Análisis de datasets con PostgreSQL
- Generación de visualizaciones
- Extracción de insights usando RAG

### 🤝 **Integración de Sistemas**
- Conexión con APIs externas
- Automatización de procesos con workflows
- Orquestación de servicios

### 🧠 **Sequential Thinking - Problemas Complejos**
- **Planificación Estratégica**: Análisis paso a paso de decisiones complejas
- **Resolución de Problemas**: Descomposición automática en sub-problemas
- **Análisis de Causa Raíz**: Identificación sistemática de problemas
- **Toma de Decisiones**: Evaluación estructurada de alternativas
- **Optimización de Procesos**: Mejora iterativa de flujos de trabajo

## 🔒 Seguridad

- **Autenticación**: Sistema de autenticación robusto
- **Autorización**: Control de acceso granular
- **Encriptación**: Datos sensibles encriptados
- **Auditoría**: Registro completo de actividades
- **Validación**: Verificación de entrada de datos

## 📈 Monitoreo y Métricas

- **Rendimiento**: Tiempo de respuesta y throughput
- **Calidad**: Precisión de respuestas RAG
- **Uso**: Estadísticas de utilización
- **Errores**: Tracking de fallos y excepciones
- **Recursos**: Uso de CPU, memoria y base de datos

## 🗄️ Base de Datos

### PostgreSQL (Producción)
- **Tablas principales**: conversations, messages, tasks, knowledge, agent_status
- **Extensiones**: uuid-ossp, pg_trgm, btree_gin
- **Índices**: Optimizados para búsquedas y consultas
- **Backup**: Configuración automática de respaldos

### SQLite (Desarrollo)
- **Configuración automática**: No requiere instalación adicional
- **Datos locales**: Almacenamiento en archivo
- **Migración fácil**: A PostgreSQL cuando sea necesario

## 🔍 Sistema RAG

### Componentes
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector Store**: ChromaDB, Pinecone, Weaviate, FAISS
- **Retriever**: ContextualCompressionRetriever
- **QA Chain**: RetrievalQA con prompts optimizados

### Flujo de Trabajo
1. **Ingesta**: Procesamiento de documentos y chunking
2. **Embedding**: Generación de vectores semánticos
3. **Almacenamiento**: Indexación en vector store
4. **Búsqueda**: Recuperación de documentos relevantes
5. **Generación**: Respuesta aumentada con contexto

## 🔄 LangGraph Workflows

### Pasos del Flujo
1. **Análisis de Petición**: Comprensión y clasificación
2. **Planificación**: Descomposición en tareas
3. **Investigación**: Búsqueda de información
4. **Análisis**: Procesamiento de datos
5. **Síntesis**: Generación de respuesta
6. **Validación**: Verificación de calidad
7. **Respuesta Final**: Entrega estructurada

### Características
- **Estado Persistente**: Checkpointing automático
- **Interrupciones**: Pausa y reanudación de workflows
- **Paralelización**: Ejecución concurrente de tareas
- **Monitoreo**: Tracking de progreso en tiempo real

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Documentación**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/agente-inteligente/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/agente-inteligente/discussions)
- **Email**: soporte@agente-inteligente.com

## 💻 Comandos de Uso

### Uso Básico
```bash
# Iniciar agente en modo interactivo
python main.py

# Procesar una consulta específica
python main.py --query "¿Qué es la inteligencia artificial?"

# Mostrar estado del sistema
python main.py --status
```

### Sequential Thinking
```bash
# Resolver problema complejo con Sequential Thinking
python main.py --query "Planificar una fiesta para 20 personas con presupuesto de $500" --sequential-thinking

# Modo interactivo con comandos
python main.py --interactive
# Luego usar: /st "Mi empresa está perdiendo clientes, ¿qué hacer?"
```

### Scripts de Prueba
```bash
# Test de Sequential Thinking
python test_sequential_thinking.py

# Demo completo de Sequential Thinking
python sequential_thinking_demo.py
```

### Comandos Interactivos
```
/query <texto>     - Procesar consulta normal
/st <texto>        - Procesar con Sequential Thinking
/status            - Mostrar estado del sistema
/help              - Mostrar ayuda
/quit              - Salir
```

## 🎉 Agradecimientos

- OpenAI por proporcionar las APIs de IA
- LangChain por el framework de LangGraph
- PostgreSQL por la base de datos robusta
- La comunidad de desarrolladores de Python
- Todos los contribuidores del proyecto

---

**¿Listo para experimentar la inteligencia artificial del futuro con PostgreSQL, LangGraph, RAG y Sequential Thinking?** 🚀🧠 
=======
# 🤖 Agente Inteligente

Un sistema de agente de inteligencia artificial avanzado capaz de procesar peticiones complejas, coordinar múltiples tareas y generar respuestas estructuradas usando **PostgreSQL**, **LangGraph** y **RAG (Retrieval-Augmented Generation)**.

## 🚀 Características Principales

### 🧠 **Inteligencia Artificial Avanzada**
- **Procesamiento de Lenguaje Natural**: Comprensión profunda de peticiones en texto libre
- **Razonamiento Multi-Paso**: Descomposición automática de tareas complejas
- **Memoria Contextual**: Mantiene contexto entre conversaciones
- **Aprendizaje Adaptativo**: Mejora respuestas basado en interacciones previas

### 🔄 **Arquitectura Multi-Agente con LangGraph**
- **Flujo de Trabajo Inteligente**: Coordinación de tareas usando LangGraph
- **Agente Coordinador**: Orquesta y gestiona tareas complejas
- **Agente de Investigación**: Búsqueda y recopilación de información
- **Agente de Análisis**: Procesamiento y análisis de datos
- **Agente de Síntesis**: Generación de respuestas estructuradas
- **Agente de Validación**: Verificación de calidad y precisión

### 🔍 **Sistema RAG (Retrieval-Augmented Generation)**
- **Búsqueda Semántica**: Encuentra información relevante usando embeddings
- **Base de Conocimiento Vectorial**: Almacena y recupera conocimiento de forma eficiente
- **Generación Aumentada**: Combina información recuperada con generación de texto
- **Fuentes Múltiples**: Integra información de APIs, documentos y bases de datos

### 🗄️ **Base de Datos PostgreSQL**
- **Almacenamiento Robusto**: PostgreSQL para datos estructurados
- **Escalabilidad**: Soporte para grandes volúmenes de datos
- **Concurrencia**: Múltiples usuarios simultáneos
- **Integridad**: Transacciones ACID y constraints

### 🔌 **Conectores de Datos**
- **APIs REST**: Integración con servicios externos
- **Bases de Datos Vectoriales**: ChromaDB, Pinecone, Weaviate, FAISS
- **Bases de Datos Relacionales**: PostgreSQL, SQLite (desarrollo)
- **APIs de Tiempo Real**: Weather, News, Finance, etc.

### 🛠️ **Herramientas Avanzadas**
- **Procesamiento Asíncrono**: Ejecución paralela de tareas
- **Gestión de Errores**: Manejo robusto de fallos
- **Logging Inteligente**: Registro detallado de operaciones
- **Monitoreo en Tiempo Real**: Métricas de rendimiento

## 📋 Requisitos

- **Python**: 3.8 o superior
- **PostgreSQL**: 12 o superior (para producción)
- **Memoria RAM**: Mínimo 4GB (recomendado 8GB+)
- **Almacenamiento**: 2GB de espacio libre
- **Conexión a Internet**: Para APIs externas

## 🚀 Instalación Rápida

### 1. Clonar el Proyecto
```bash
git clone <repository-url>
cd Agente_Inteligente
```

### 2. Configurar Entorno Virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
cp env.example .env
# Editar .env con tus claves de API
```

### 5. Configurar PostgreSQL (Opcional)
```bash
# Para desarrollo (SQLite automático)
python scripts/init_system.py

# Para producción (PostgreSQL)
python scripts/setup_postgres.py
```

### 6. Inicializar el Sistema
```bash
python scripts/init_system.py
```

### 7. Ejecutar el Agente
```bash
python main.py
```

## 🔧 Configuración

### Variables de Entorno Principales

```env
# OpenAI Configuration
OPENAI_API_KEY=tu_clave_de_openai_aqui
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7

# PostgreSQL Configuration (Producción)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=agent_user
POSTGRES_PASSWORD=agent_password
POSTGRES_DATABASE=agent_db
POSTGRES_SSL_MODE=prefer

# SQLite Configuration (Desarrollo)
SQLITE_DATABASE=sqlite:///./data/database/agent.db

# Vector Database Configuration
VECTOR_DB_PATH=./data/knowledge/vector_db
VECTOR_DB_TYPE=chroma

# Redis Configuration
REDIS_URL=redis://localhost:6379

# External APIs (Optional)
WEATHER_API_KEY=tu_clave_weather_api
NEWS_API_KEY=tu_clave_news_api
FINANCE_API_KEY=tu_clave_finance_api

# System Configuration
LOG_LEVEL=INFO
MAX_CONCURRENT_TASKS=10
REQUEST_TIMEOUT=30
ENVIRONMENT=development
```

## 📖 Uso

### Interfaz Web
```bash
# Iniciar servidor web
python web_server.py

# Acceder a la interfaz
# http://localhost:8000
```

### API REST
```bash
# Procesar petición
curl -X POST "http://localhost:8000/api/process" \
     -H "Content-Type: application/json" \
     -d '{"query": "Analiza el clima de Madrid y sugiere actividades"}'

# Obtener estado
curl "http://localhost:8000/api/status"
```

### Uso Programático
```python
from agent import IntelligentAgent

# Crear agente
agent = IntelligentAgent()
await agent.start()

# Procesar petición
response = await agent.process_request(
    "Investiga sobre inteligencia artificial y crea un resumen"
)

print(response.content)

# Añadir conocimiento
await agent.add_knowledge(
    "La inteligencia artificial es un campo de la informática...",
    metadata={"source": "manual", "topic": "AI"}
)

# Buscar conocimiento
results = await agent.search_knowledge("machine learning", limit=5)
```

## 🏗️ Arquitectura del Sistema

```
Agente_Inteligente/
├── 📁 agent/                 # Núcleo del agente
│   ├── 🧠 core/             # Lógica principal
│   │   ├── config.py        # Configuración del sistema
│   │   ├── models.py        # Modelos de datos
│   │   ├── database.py      # Sistema PostgreSQL
│   │   ├── rag_system.py    # Sistema RAG
│   │   ├── workflow_graph.py # LangGraph workflows
│   │   └── intelligent_agent.py # Agente principal
│   ├── 🤖 agents/           # Agentes especializados
│   ├── 🔌 connectors/       # Conectores de datos
│   └── 🛠️ tools/            # Herramientas auxiliares
├── 📁 web/                  # Interfaz web
│   ├── 🌐 api/              # Endpoints REST
│   ├── 🎨 frontend/         # Interfaz de usuario
│   └── 📊 dashboard/        # Panel de control
├── 📁 data/                 # Datos del sistema
│   ├── 🗄️ database/         # Bases de datos
│   ├── 📚 knowledge/        # Base de conocimiento
│   └── 📝 logs/             # Registros del sistema
├── 📁 scripts/              # Scripts de utilidad
│   ├── init_system.py       # Inicialización del sistema
│   └── setup_postgres.py    # Configuración PostgreSQL
├── 📁 tests/                # Pruebas del sistema
└── 📁 docs/                 # Documentación
```

## 🎯 Casos de Uso

### 🔍 **Investigación y Análisis**
- Búsqueda de información en múltiples fuentes usando RAG
- Análisis de tendencias y patrones con LangGraph
- Generación de reportes estructurados

### 💡 **Asistencia Inteligente**
- Respuestas a preguntas complejas con contexto
- Sugerencias personalizadas basadas en historial
- Planificación y organización automática

### 📊 **Procesamiento de Datos**
- Análisis de datasets con PostgreSQL
- Generación de visualizaciones
- Extracción de insights usando RAG

### 🤝 **Integración de Sistemas**
- Conexión con APIs externas
- Automatización de procesos con workflows
- Orquestación de servicios

## 🔒 Seguridad

- **Autenticación**: Sistema de autenticación robusto
- **Autorización**: Control de acceso granular
- **Encriptación**: Datos sensibles encriptados
- **Auditoría**: Registro completo de actividades
- **Validación**: Verificación de entrada de datos

## 📈 Monitoreo y Métricas

- **Rendimiento**: Tiempo de respuesta y throughput
- **Calidad**: Precisión de respuestas RAG
- **Uso**: Estadísticas de utilización
- **Errores**: Tracking de fallos y excepciones
- **Recursos**: Uso de CPU, memoria y base de datos

## 🗄️ Base de Datos

### PostgreSQL (Producción)
- **Tablas principales**: conversations, messages, tasks, knowledge, agent_status
- **Extensiones**: uuid-ossp, pg_trgm, btree_gin
- **Índices**: Optimizados para búsquedas y consultas
- **Backup**: Configuración automática de respaldos

### SQLite (Desarrollo)
- **Configuración automática**: No requiere instalación adicional
- **Datos locales**: Almacenamiento en archivo
- **Migración fácil**: A PostgreSQL cuando sea necesario

## 🔍 Sistema RAG

### Componentes
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector Store**: ChromaDB, Pinecone, Weaviate, FAISS
- **Retriever**: ContextualCompressionRetriever
- **QA Chain**: RetrievalQA con prompts optimizados

### Flujo de Trabajo
1. **Ingesta**: Procesamiento de documentos y chunking
2. **Embedding**: Generación de vectores semánticos
3. **Almacenamiento**: Indexación en vector store
4. **Búsqueda**: Recuperación de documentos relevantes
5. **Generación**: Respuesta aumentada con contexto

## 🔄 LangGraph Workflows

### Pasos del Flujo
1. **Análisis de Petición**: Comprensión y clasificación
2. **Planificación**: Descomposición en tareas
3. **Investigación**: Búsqueda de información
4. **Análisis**: Procesamiento de datos
5. **Síntesis**: Generación de respuesta
6. **Validación**: Verificación de calidad
7. **Respuesta Final**: Entrega estructurada

### Características
- **Estado Persistente**: Checkpointing automático
- **Interrupciones**: Pausa y reanudación de workflows
- **Paralelización**: Ejecución concurrente de tareas
- **Monitoreo**: Tracking de progreso en tiempo real

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Documentación**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/agente-inteligente/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/agente-inteligente/discussions)
- **Email**: soporte@agente-inteligente.com

## 🎉 Agradecimientos

- OpenAI por proporcionar las APIs de IA
- LangChain por el framework de LangGraph
- PostgreSQL por la base de datos robusta
- La comunidad de desarrolladores de Python
- Todos los contribuidores del proyecto

---

**¿Listo para experimentar la inteligencia artificial del futuro con PostgreSQL, LangGraph y RAG?** 🚀 
>>>>>>> 4caeba3865603c67c51ab60f71b04353770ceb47
