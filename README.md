# Data Analysis API - Guía de Instalación

## 📋 Prerrequisitos

- Python 3.13+
- Docker y Docker Compose
- Homebrew (macOS)

## 🚀 Pasos para Levantar el Proyecto

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd data_analysis
```

### 2. Levantar Servicios de Infraestructura
```bash
# Levantar Redis y MinIO con Docker Compose
docker-compose up -d

# Verificar que los servicios estén corriendo
docker-compose ps
```

### 3. Instalar Dependencias del Sistema (macOS)
```bash
# Instalar dependencias necesarias para compilación
brew install freetype pkg-config
```

### 4. Configurar Entorno Virtual de Python
```bash
# Crear entorno virtual limpio
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Actualizar pip
pip install --upgrade pip
```

### 5. Instalar Dependencias de Python
```bash
# Instalar dependencias básicas
pip install fastapi uvicorn pandas numpy python-multipart minio redis aiofiles python-dotenv reportlab loguru openpyxl

# Instalar pydantic (con versiones compatibles)
pip install pydantic pydantic-settings

# Instalar matplotlib (precompilado para evitar problemas de compilación)
pip install --only-binary=matplotlib matplotlib

# Instalar dependencias de testing
pip install pytest httpx pytest-asyncio pytest-cov pytest-mock
```

### 6. Verificar Estructura del Proyecto
```bash
# Verificar que main.py esté en app/
ls -la app/main.py

# Estructura esperada:
# app/main.py (archivo principal)
# app/api/endpoints.py
# app/core/config.py
```

### 7. Levantar la Aplicación
```bash
# Activar entorno virtual (si no está activo)
source .venv/bin/activate

# Levantar FastAPI (main.py está en app/)
uvicorn app.main:app --reload --port 8001
```

## 🌐 URLs de Acceso

Una vez levantado el proyecto, accede a:

- **Documentación API (Swagger)**: http://127.0.0.1:8001/api/v1/docs
- **Documentación Alternativa (ReDoc)**: http://127.0.0.1:8001/api/v1/redoc
- **Health Check**: http://127.0.0.1:8001/api/v1/health
- **Schema OpenAPI**: http://127.0.0.1:8001/api/v1/openapi.json

## 🔧 Servicios Externos

- **MinIO (Object Storage)**: http://localhost:9000
    - Usuario: `minioadmin`
    - Contraseña: `minioadmin`
- **Redis**: `localhost:6379`

## 🐛 Solución de Problemas Comunes

### Error: "Address already in use"
```bash
# Cambiar puerto
uvicorn main:app --reload --port 8002
```

### Error: "Could not import module main"
```bash
# Verificar ubicación de main.py
ls -la app/main.py

# Usar el comando correcto según la ubicación:
# Si main.py está en app/:
uvicorn app.main:app --reload --port 8001

# Si main.py está en la raíz:
uvicorn main:app --reload --port 8001
```

### Error de compilación en macOS
```bash
# Instalar dependencias del sistema
brew install freetype pkg-config

# Usar versiones precompiladas
pip install --only-binary=matplotlib matplotlib
pip install --only-binary=pydantic-core pydantic
```

### Problema con versiones de Python 3.13
```bash
# Usar variable de entorno para compatibilidad
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto
```
data_analysis/
├── main.py                 # Punto de entrada de FastAPI
├── app/
│   ├── api/
│   │   └── endpoints.py    # Endpoints de la API
│   ├── core/
│   │   └── config.py       # Configuración
│   └── services/          # Servicios de negocio
├── docker-compose.yml     # Configuración de servicios
├── requirements.txt       # Dependencias Python
└── tests/                # Tests automatizados
```

## 🧪 Ejecutar Tests
```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar todos los tests
pytest

# Ejecutar tests con coverage
pytest --cov=app

# Ejecutar tests específicos
pytest tests/unit/
```

## 📊 Datos de Prueba

El proyecto incluye archivos CSV de ejemplo en la raíz para probar la funcionalidad de análisis de datos.

## 🔄 Comandos de Desarrollo

```bash
# Activar entorno virtual
source .venv/bin/activate

# Levantar en modo desarrollo (main.py en app/)
uvicorn app.main:app --reload --port 8001

# Ver logs de Docker Compose
docker-compose logs -f

# Parar servicios
docker-compose down

# Rebuild servicios
docker-compose up --build -d
```

## 📝 Notas Importantes

- ⚠️ **macOS Users**: Los pasos de instalación de dependencias del sistema con Homebrew son críticos para evitar errores de compilación
- 🐍 **Python 3.13**: Algunas dependencias pueden requerir configuración especial debido a la versión reciente de Python
- 🔧 **Entorno Virtual**: Siempre activar el entorno virtual antes de trabajar con el proyecto
- 🐳 **Docker**: Asegurar que Docker Desktop esté corriendo antes de ejecutar docker-compose