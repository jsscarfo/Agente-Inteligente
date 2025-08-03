# 🚂 Guía de Despliegue en Railway

## 📋 **Resumen**

Esta guía te ayudará a desplegar el **Asistente de IA Multifuncional** en Railway de manera exitosa, resolviendo el problema del proyecto crasheado.

## 🎯 **Problema Resuelto**

### **Problema Original:**
- ❌ `Procfile` apuntaba a `main.py` (aplicación CLI)
- ❌ Railway necesita una aplicación web que escuche en un puerto
- ❌ Falta de configuración específica para Railway
- ❌ Dependencias problemáticas para el despliegue

### **Solución Implementada:**
- ✅ **Nueva aplicación web**: `railway_app.py` específica para Railway
- ✅ **Procfile corregido**: Apunta a la aplicación web correcta
- ✅ **Configuración Railway**: `railway.json` con health checks
- ✅ **Dependencias optimizadas**: Sin dependencias problemáticas
- ✅ **Variables de entorno**: Configuración específica para Railway

## 🚀 **Despliegue Rápido**

### **Paso 1: Preparar el Repositorio**

```bash
# Asegúrate de que estos archivos estén en tu repositorio:
# ✅ railway_app.py
# ✅ Procfile (actualizado)
# ✅ railway.json
# ✅ requirements.txt (optimizado)
# ✅ runtime.txt
# ✅ setup_railway.py
```

### **Paso 2: Conectar a Railway**

```bash
# Instalar Railway CLI (si no lo tienes)
npm install -g @railway/cli

# Login a Railway
railway login

# Inicializar proyecto
railway init

# Conectar repositorio
railway link
```

### **Paso 3: Configurar Variables de Entorno**

```bash
# Configurar variables críticas
railway variables set OPENAI_API_KEY=tu_api_key_aqui

# Variables opcionales
railway variables set RAILWAY_ENVIRONMENT=production
railway variables set PORT=8000
```

### **Paso 4: Desplegar**

```bash
# Desplegar a Railway
railway up

# Ver logs
railway logs

# Abrir aplicación
railway open
```

## 🔧 **Configuración Detallada**

### **Archivos de Configuración**

#### **1. railway_app.py**
```python
# Aplicación web unificada para Railway
# - FastAPI con endpoints completos
# - Health checks para Railway
# - Manejo de errores robusto
# - Interfaz web integrada
```

#### **2. Procfile**
```
web: python railway_app.py
```

#### **3. railway.json**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python railway_app.py",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### **4. requirements.txt (Optimizado)**
```
# Dependencias críticas para Railway
fastapi>=0.104.1
uvicorn>=0.24.0
pydantic>=2.5.0
openai>=1.6.1
langchain>=0.1.0

# Dependencias de visión comentadas (opcionales)
# pytesseract>=0.3.10
# easyocr>=1.7.0
# opencv-python>=4.8.0
```

### **Variables de Entorno**

#### **Críticas:**
- `OPENAI_API_KEY`: Tu clave de API de OpenAI

#### **Opcionales:**
- `RAILWAY_ENVIRONMENT`: `production` o `development`
- `PORT`: Puerto (Railway lo configura automáticamente)
- `DATABASE_URL`: URL de PostgreSQL (si usas base de datos)
- `GOOGLE_VISION_API_KEY`: Para capacidades de visión
- `AZURE_VISION_ENDPOINT`: Para capacidades de visión

## 🧪 **Verificación del Despliegue**

### **1. Health Check**
```bash
# Verificar que la aplicación responde
curl https://tu-app.railway.app/api/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "environment": "production",
  "port": 8000
}
```

### **2. Status del Sistema**
```bash
# Verificar estado de componentes
curl https://tu-app.railway.app/api/status
```

**Respuesta esperada:**
```json
{
  "status": "running",
  "uptime": 3600.5,
  "version": "2.0.0",
  "environment": "production",
  "components": {
    "assistant": "✅ Activo",
    "multimodal": "❌ Inactivo",
    "pdf_loader": "✅ Activo"
  }
}
```

### **3. Chat Funcional**
```bash
# Probar chat básico
curl -X POST https://tu-app.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, ¿cómo estás?", "mode": "text"}'
```

## 🔍 **Solución de Problemas**

### **Problema: Aplicación no inicia**
```bash
# Verificar logs
railway logs

# Posibles causas:
# 1. Variables de entorno faltantes
# 2. Dependencias no instaladas
# 3. Puerto incorrecto
```

### **Problema: Health check falla**
```bash
# Verificar que railway_app.py existe
# Verificar que el puerto es correcto
# Verificar que FastAPI está funcionando
```

### **Problema: Imports fallan**
```bash
# Ejecutar setup de Railway
python setup_railway.py

# Verificar dependencias
pip install -r requirements.txt
```

### **Problema: Memoria insuficiente**
```bash
# Railway proporciona 512MB por defecto
# Para aplicaciones más grandes, considerar:
# 1. Optimizar imports
# 2. Reducir dependencias
# 3. Usar Railway Pro
```

## 📊 **Monitoreo y Logs**

### **Ver Logs en Tiempo Real**
```bash
railway logs --follow
```

### **Ver Métricas**
```bash
railway status
```

### **Ver Variables de Entorno**
```bash
railway variables
```

## 🎉 **Funcionalidades Disponibles**

### **✅ Funcionalidades Básicas**
- Chat con IA usando OpenAI
- Procesamiento de texto
- Sistema RAG básico
- Interfaz web integrada

### **✅ APIs Disponibles**
- `GET /` - Interfaz web
- `POST /api/chat` - Chat con IA
- `GET /api/status` - Estado del sistema
- `GET /api/health` - Health check
- `POST /api/upload-pdf` - Subir PDFs
- `GET /api/documents` - Listar documentos

### **⚠️ Funcionalidades Opcionales**
- Análisis de imágenes (requiere dependencias adicionales)
- OCR avanzado (requiere Tesseract)
- Base de datos PostgreSQL (requiere configuración)

## 🔄 **Actualizaciones**

### **Actualizar Aplicación**
```bash
# Hacer cambios en el código
git add .
git commit -m "Actualización"
git push

# Railway se actualiza automáticamente
```

### **Rollback**
```bash
# Volver a versión anterior
railway rollback
```

## 📞 **Soporte**

### **Logs de Railway**
```bash
railway logs --help
```

### **Documentación Railway**
- [Railway Docs](https://docs.railway.app/)
- [Railway CLI](https://docs.railway.app/reference/cli)

### **Comandos Útiles**
```bash
# Ver información del proyecto
railway status

# Ver variables de entorno
railway variables

# Conectar a la base de datos
railway connect

# Ejecutar comando en Railway
railway run python setup_railway.py
```

## 🎯 **Conclusión**

Con esta configuración, tu proyecto debería desplegarse exitosamente en Railway sin crashes. La aplicación web unificada (`railway_app.py`) proporciona todas las funcionalidades necesarias y está optimizada para el entorno de Railway.

**¡Tu Asistente de IA ahora está listo para funcionar en Railway! 🚂✨** 