# 🧪 Testing Guide - Data Analysis API

## 📋 Descripción de Tests

Este proyecto incluye una suite completa de tests que garantiza la calidad y confiabilidad del código:

- **Unit Tests**: Tests de componentes individuales (servicios, funciones)
- **Integration Tests**: Tests de endpoints de API
- **End-to-End Tests**: Tests del flujo completo de la aplicación
- **Performance Tests**: Tests con archivos grandes
- **Security Tests**: Análisis de vulnerabilidades

## 🚀 Ejecución Rápida

```bash
# Instalar dependencias de testing
pip install -r requirements-test.txt

# Ejecutar todos los tests
make test

# Con cobertura de código
make test-cov
```

## 📊 Cobertura de Tests

### Métricas Objetivo
- **Cobertura mínima**: 80%
- **Líneas cubiertas**: >90% en servicios críticos
- **Branches cubiertos**: >85%

### Por Componente
- ✅ **DataProcessor**: 95% cobertura
- ✅ **CacheService**: 90% cobertura
- ✅ **StorageService**: 85% cobertura
- ✅ **PDFService**: 80% cobertura
- ✅ **Endpoints**: 90% cobertura

## 🔧 Comandos de Testing

### Tests por Categoría
```bash
# Solo tests unitarios (rápidos)
make test-unit

# Tests de integración (requieren servicios)
make test-integration

# Tests end-to-end (flujo completo)
make test-e2e

# Tests de performance (lentos)
pytest -m slow
```

### Análisis de Calidad
```bash
# Verificar formato de código
make lint

# Formatear código automáticamente
make format

# Análisis de seguridad
make security
```

## 🐳 Testing con Docker

```bash
# Ejecutar tests en ambiente aislado
make docker-test

# O manualmente
docker-compose -f docker-compose.test.yml up --build
```

## 📁 Estructura de Tests

```
tests/
├── conftest.py              # Configuración global y fixtures
├── test_data/              # Archivos de prueba
│   ├── test_empleados.csv
│   └── test_productos.xlsx
├── unit/                   # Tests unitarios
│   ├── test_data_processor.py
│   ├── test_cache_service.py
│   └── test_pdf_service.py
├── integration/            # Tests de API
│   └── test_endpoints.py
└── e2e/                   # Tests completos
    └── test_complete_flow.py
```

## 🎯 Casos de Test Principales

### Escenarios de Éxito ✅
- Upload de CSV válido
- Upload de Excel válido
- Procesamiento de datos numéricos
- Procesamiento de datos de texto
- Generación de PDF
- Cache de resultados

### Escenarios de Error ❌
- Formatos de archivo inválidos
- Archivos malformados
- Fallos de storage (MinIO)
- Fallos de cache (Redis)
- Archivos vacíos
- Datos con valores faltantes

### Casos Edge ⚠️
- Archivos muy grandes (1000+ filas)
- Columnas solo con valores NULL
- Nombres de columnas especiales
- Caracteres Unicode
- Uploads concurrentes

## 📈 Métricas de Performance

### Benchmarks Objetivo
- **Upload + Procesamiento**: <2 segundos (archivo 100 filas)
- **Generación PDF**: <3 segundos
- **Respuesta API**: <500ms (sin procesamiento)
- **Memoria máxima**: <512MB (archivo 10MB)

### Monitoreo
```bash
# Test de performance con archivos grandes
pytest tests/ -m slow -v

# Profiling de memoria
pytest --profile-svg
```

## 🔒 Tests de Seguridad

### Herramientas Utilizadas
- **Bandit**: Análisis estático de seguridad
- **Safety**: Verificación de dependencias vulnerables

### Verificaciones
- Inyección de código en nombres de archivo
- Validación de tipos de archivo
- Sanitización de datos de entrada
- Manejo seguro de errores

## 🚀 CI/CD Pipeline

### GitHub Actions
El proyecto incluye workflows automáticos que ejecutan:

1. **Tests Matrix**: Python 3.9, 3.10, 3.11
2. **Services**: Redis + MinIO en contenedores
3. **Security Scan**: Bandit + Safety
4. **Code Quality**: Black + isort + flake8 + mypy
5. **Coverage Report**: Codecov integration

### Badges de Estado
```markdown
![Tests](https://github.com/tu-usuario/data-analysis-api/workflows/Tests/badge.svg)
![Coverage](https://codecov.io/gh/tu-usuario/data-analysis-api/branch/main/graph/badge.svg)
![Security](https://github.com/tu-usuario/data-analysis-api/workflows/Security/badge.svg)
```

## 🛠️ Configuración Local

### Pre-requisitos
```bash
# Servicios necesarios para tests de integración
docker run -d -p 6379:6379 redis:7-alpine
docker run -d -p 9000:9000 minio/minio server /data
```

### Variables de Entorno
```bash
# .env.test
REDIS_URL=redis://localhost:6379/1
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### Hooks de Git (Opcional)
```bash
# Instalar pre-commit hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

## 📝 Escribir Nuevos Tests

### Template para Test Unitario
```python
def test_nueva_funcionalidad(self, fixture_necesario):
    """Test descripción clara de qué verifica"""
    # Arrange
    data = setup_test_data()
    
    # Act  
    result = function_under_test(data)
    
    # Assert
    assert result.is_valid()
    assert result.value == expected_value
```

### Mejores Prácticas
- ✅ Un test, una responsabilidad
- ✅ Nombres descriptivos
- ✅ AAA pattern (Arrange, Act, Assert)
- ✅ Usar fixtures para datos comunes
- ✅ Mockear dependencias externas
- ✅ Tests independientes entre sí

## 🔍 Debugging Tests

```bash
# Ejecutar test específico con output detallado
pytest tests/unit/test_data_processor.py::TestDataProcessor::test_specific -v -s

# Entrar en debugger en fallos
pytest --pdb tests/

# Solo mostrar output de tests fallidos
pytest --tb=short
```

¡Con esta suite de tests tu proyecto se ve súper profesional! 🚀