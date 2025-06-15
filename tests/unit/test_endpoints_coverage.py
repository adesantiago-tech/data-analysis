import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from io import BytesIO

from app.main import app


class TestEndpointsCoverage:
    """Tests para cubrir líneas específicas de endpoints.py"""

    @patch('app.services.storage_service.StorageService.save_file')
    @patch('app.services.cache_service.CacheService.set_stats')
    @patch('app.services.data_processor.DataProcessor.process_file')
    def test_upload_file_processing_exception(self, mock_process, mock_cache, mock_storage):
        """Test para cubrir manejo de excepciones en procesamiento"""
        client = TestClient(app)
        mock_storage.return_value = True

        # Simular excepción durante el procesamiento
        mock_process.side_effect = Exception("Error procesando archivo")

        # Archivo válido pero que causará excepción en el mock
        content = b"nombre,edad\nJuan,25\nMaria,30"

        files = {
            "file": ("test.csv", BytesIO(content), "text/csv")
        }

        response = client.post("/api/v1/files/upload", files=files)

        # Debería manejar la excepción y devolver error 400
        assert response.status_code == 400
        assert "Error procesando archivo" in response.json()["detail"]

    def test_get_summary_with_missing_data(self):
        """Test para cubrir línea 99 en get_summary"""
        client = TestClient(app)

        with patch('app.services.cache_service.CacheService.get_stats') as mock_cache:
            # Simular datos incompletos que pueden activar línea 99
            incomplete_stats = {
                "analisis_columnas": {
                    "test_col": {
                        # Sin interpretacion para activar casos edge
                        "tipo_datos": "Numérico"
                    }
                }
            }
            mock_cache.return_value = incomplete_stats

            response = client.get("/api/v1/files/stats/test-id/resumen")

            assert response.status_code == 200
            data = response.json()
            assert "interpretaciones" in data

    @patch('app.services.storage_service.StorageService.save_file')
    @patch('app.services.cache_service.CacheService.set_stats')
    def test_upload_file_boundary_case(self, mock_cache, mock_storage):
        """Test para cubrir líneas específicas en upload"""
        client = TestClient(app)
        mock_storage.return_value = True
        mock_cache.return_value = None

        # CSV con datos que pueden activar líneas específicas
        boundary_content = b"col1,col2\nval1,val2\n,\nempty,values"

        files = {
            "file": ("boundary.csv", BytesIO(boundary_content), "text/csv")
        }

        response = client.post("/api/v1/files/upload", files=files)

        # Debería procesar correctamente
        assert response.status_code == 201