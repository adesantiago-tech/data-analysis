import pytest
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import tempfile
import os
from io import BytesIO

from app.main import app
from app.services.cache_service import CacheService
from app.services.storage_service import StorageService


@pytest.fixture
def client():
    """Cliente de prueba para FastAPI"""
    return TestClient(app)


@pytest.fixture
def mock_redis():
    """Mock de Redis para tests unitarios"""
    with patch('redis.Redis') as mock:
        redis_instance = Mock()
        mock.from_url.return_value = redis_instance
        yield redis_instance


@pytest.fixture
def mock_minio():
    """Mock de MinIO para tests unitarios"""
    with patch('minio.Minio') as mock:
        minio_instance = Mock()
        minio_instance.bucket_exists.return_value = True
        minio_instance.put_object.return_value = True
        mock.return_value = minio_instance
        yield minio_instance


@pytest.fixture
def sample_csv_content():
    """CSV de ejemplo para tests"""
    return """nombre,edad,salario
Juan,25,50000
María,30,65000
Pedro,28,55000
Ana,32,70000
Carlos,27,52000"""


@pytest.fixture
def sample_excel_content():
    """Excel de ejemplo para tests"""
    df = pd.DataFrame({
        'producto': ['Laptop', 'Mouse', 'Teclado', 'Monitor'],
        'precio': [1200, 25, 80, 300],
        'categoria': ['Electrónicos', 'Periféricos', 'Periféricos', 'Electrónicos'],
        'stock': [50, 200, 150, 30]
    })

    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def sample_csv_bytes(sample_csv_content):
    """CSV como bytes para upload"""
    return sample_csv_content.encode('utf-8')


@pytest.fixture
def invalid_file_content():
    """Archivo inválido para tests de error"""
    return b"This is not a valid CSV or Excel file"


@pytest.fixture
def large_csv_content():
    """CSV grande para tests de performance"""
    data = []
    for i in range(1000):
        data.append(f"Usuario{i},{20 + (i % 30)},{30000 + (i * 100)}")

    return "nombre,edad,salario\n" + "\n".join(data)


@pytest.fixture
def cache_service_mock(mock_redis):
    """CacheService con Redis mockeado"""
    return CacheService()


@pytest.fixture
def storage_service_mock(mock_minio):
    """StorageService con MinIO mockeado"""
    return StorageService()


# Configuración global de pytest
def pytest_configure(config):
    """Configuración global de pytest"""
    config.addinivalue_line(
        "markers", "slow: marca tests que son lentos de ejecutar"
    )
    config.addinivalue_line(
        "markers", "integration: marca tests de integración"
    )
    config.addinivalue_line(
        "markers", "e2e: marca tests end-to-end"
    )