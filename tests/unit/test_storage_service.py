import pytest
from unittest.mock import Mock, patch
from minio.error import S3Error

from app.services.storage_service import StorageService


class TestStorageService:
    """Tests unitarios para StorageService"""

    @patch('app.services.storage_service.Minio')
    def test_storage_service_initialization_bucket_exists(self, mock_minio_class):
        """Test inicialización cuando el bucket existe"""
        mock_client = Mock()
        mock_client.bucket_exists.return_value = True
        mock_minio_class.return_value = mock_client

        service = StorageService()

        # Verificar configuración
        mock_minio_class.assert_called_once_with(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )

        # Verificar que se verificó la existencia del bucket
        mock_client.bucket_exists.assert_called_once_with("data-files")
        # No debería llamar make_bucket si ya existe
        mock_client.make_bucket.assert_not_called()

        assert service.client == mock_client

    @patch('app.services.storage_service.Minio')
    def test_storage_service_initialization_bucket_not_exists(self, mock_minio_class):
        """Test inicialización cuando el bucket no existe"""
        mock_client = Mock()
        mock_client.bucket_exists.return_value = False
        mock_minio_class.return_value = mock_client

        service = StorageService()

        # Verificar que se intentó crear el bucket
        mock_client.make_bucket.assert_called_once_with("data-files")

    @patch('app.services.storage_service.Minio')
    def test_save_file_success(self, mock_minio_class):
        """Test guardar archivo exitosamente"""
        # Configurar mock
        mock_client = Mock()
        mock_client.bucket_exists.return_value = True
        mock_client.put_object.return_value = None
        mock_minio_class.return_value = mock_client

        # Crear servicio
        service = StorageService()

        # Datos de prueba
        filename = "test.csv"
        file_bytes = b"nombre,edad\nJuan,25\nMaria,30"
        content_type = "text/csv"

        # Ejecutar
        result = service.save_file(filename, file_bytes, content_type)

        # Verificar
        assert result is True
        mock_client.put_object.assert_called_once()

    @patch('app.services.storage_service.Minio')
    def test_save_file_success_default_content_type(self, mock_minio_class):
        """Test guardar archivo con content-type por defecto"""
        mock_client = Mock()
        mock_client.bucket_exists.return_value = True
        mock_client.put_object.return_value = None
        mock_minio_class.return_value = mock_client

        service = StorageService()

        filename = "test.xlsx"
        file_bytes = b"fake excel content"

        # Sin especificar content_type (debería usar default)
        result = service.save_file(filename, file_bytes)

        assert result is True
        mock_client.put_object.assert_called_once()

    @patch('app.services.storage_service.Minio')
    def test_save_file_s3_error(self, mock_minio_class):
        """Test error S3 al guardar archivo"""
        mock_client = Mock()
        mock_client.bucket_exists.return_value = True
        mock_client.put_object.side_effect = S3Error(
            "NoSuchBucket",
            "The specified bucket does not exist",
            "", "", "", "", ""
        )
        mock_minio_class.return_value = mock_client

        service = StorageService()

        filename = "test.csv"
        file_bytes = b"test content"

        # Ejecutar
        result = service.save_file(filename, file_bytes)

        # Verificar que retorna False en error
        assert result is False
        mock_client.put_object.assert_called_once()

    @patch('app.services.storage_service.Minio')
    def test_save_empty_file(self, mock_minio_class):
        """Test guardar archivo vacío"""
        mock_client = Mock()
        mock_client.bucket_exists.return_value = True
        mock_client.put_object.return_value = None
        mock_minio_class.return_value = mock_client

        service = StorageService()

        filename = "empty.csv"
        file_bytes = b""

        result = service.save_file(filename, file_bytes)

        assert result is True
        mock_client.put_object.assert_called_once()

    @patch('app.services.storage_service.Minio')
    def test_save_large_file(self, mock_minio_class):
        """Test guardar archivo grande"""
        mock_client = Mock()
        mock_client.bucket_exists.return_value = True
        mock_client.put_object.return_value = None
        mock_minio_class.return_value = mock_client

        service = StorageService()

        filename = "large_file.csv"
        # Simular archivo de 1MB
        file_bytes = b"x" * (1024 * 1024)

        result = service.save_file(filename, file_bytes)

        assert result is True
        mock_client.put_object.assert_called_once()