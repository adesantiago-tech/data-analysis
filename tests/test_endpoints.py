import pytest
from unittest.mock import patch, Mock
import json
from io import BytesIO


@pytest.mark.integration
class TestFileUploadEndpoint:
    """Tests de integración para endpoint de upload"""

    @patch('app.services.storage_service.StorageService.save_file')
    @patch('app.services.cache_service.CacheService.set_stats')
    def test_upload_csv_success(self, mock_cache, mock_storage, client, sample_csv_bytes):
        """Test upload exitoso de CSV"""
        # Configurar mocks
        mock_storage.return_value = True
        mock_cache.return_value = None

        # Preparar archivo
        files = {
            "file": ("test.csv", BytesIO(sample_csv_bytes), "text/csv")
        }

        # Hacer request
        response = client.post("/api/v1/files/upload", files=files)

        # Verificar respuesta
        assert response.status_code == 201
        data = response.json()

        assert "file_id" in data
        assert data["filename"] == "test.csv"
        assert data["size_bytes"] == len(sample_csv_bytes)
        assert "resumen" in data
        assert "preview_analisis" in data
        assert data["message"] == "Archivo subido, procesado y análisis generado exitosamente"

        # Verificar que se llamaron los servicios
        mock_storage.assert_called_once()
        mock_cache.assert_called_once()

    @patch('app.services.storage_service.StorageService.save_file')
    @patch('app.services.cache_service.CacheService.set_stats')
    def test_upload_excel_success(self, mock_cache, mock_storage, client, sample_excel_content):
        """Test upload exitoso de Excel"""
        mock_storage.return_value = True
        mock_cache.return_value = None

        files = {
            "file": ("test.xlsx", BytesIO(sample_excel_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }

        response = client.post("/api/v1/files/upload", files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test.xlsx"

    def test_upload_invalid_file_format(self, client, invalid_file_content):
        """Test error con formato de archivo inválido"""
        files = {
            "file": ("test.txt", BytesIO(invalid_file_content), "text/plain")
        }

        response = client.post("/api/v1/files/upload", files=files)

        assert response.status_code == 400
        assert "Solo se permiten archivos CSV o Excel" in response.json()["detail"]

    @patch('app.services.storage_service.StorageService.save_file')
    def test_upload_storage_failure(self, mock_storage, client, sample_csv_bytes):
        """Test error cuando falla el almacenamiento"""
        mock_storage.return_value = False

        files = {
            "file": ("test.csv", BytesIO(sample_csv_bytes), "text/csv")
        }

        response = client.post("/api/v1/files/upload", files=files)

        assert response.status_code == 500
        assert "No se pudo guardar el archivo en MinIO" in response.json()["detail"]

    def test_upload_malformed_csv(self, client):
        """Test con CSV malformado"""
        malformed_csv = b"esta,no,es\nuna,estructura,csv,valida,con,demasiadas,columnas"

        with patch('app.services.storage_service.StorageService.save_file', return_value=True), \
                patch('app.services.cache_service.CacheService.set_stats'):

            files = {
                "file": ("test.csv", BytesIO(malformed_csv), "text/csv")
            }

            response = client.post("/api/v1/files/upload", files=files)

            # Debería procesar sin error
            assert response.status_code == 201


@pytest.mark.integration
class TestStatsEndpoints:
    """Tests para endpoints de estadísticas"""

    @patch('app.services.cache_service.CacheService.get_stats')
    def test_get_stats_success(self, mock_cache, client):
        """Test obtener estadísticas exitosamente"""
        # Mock de datos en cache
        mock_stats = {
            "resumen_general": {
                "nombre_archivo": "test.csv",
                "total_filas": 5,
                "total_columnas": 3
            },
            "analisis_columnas": {
                "edad": {
                    "tipo_datos": "Numérico",
                    "interpretacion": ["Edad promedio: 28.4 años"]
                }
            }
        }
        mock_cache.return_value = mock_stats

        response = client.get("/api/v1/files/stats/test-file-id")

        assert response.status_code == 200
        data = response.json()
        assert data["file_id"] == "test-file-id"
        assert "analisis_completo" in data

    @patch('app.services.cache_service.CacheService.get_stats')
    def test_get_stats_not_found(self, mock_cache, client):
        """Test estadísticas no encontradas"""
        mock_cache.return_value = None

        response = client.get("/api/v1/files/stats/nonexistent-id")

        assert response.status_code == 404
        assert "No se encontraron stats" in response.json()["detail"]

    @patch('app.services.cache_service.CacheService.get_stats')
    def test_get_summary_success(self, mock_cache, client):
        """Test obtener resumen exitosamente"""
        mock_stats = {
            "resumen_general": {
                "nombre_archivo": "test.csv",
                "total_filas": 5
            },
            "analisis_columnas": {
                "edad": {
                    "interpretacion": ["Edad promedio: 28.4 años"]
                }
            }
        }
        mock_cache.return_value = mock_stats

        response = client.get("/api/v1/files/stats/test-file-id/resumen")

        assert response.status_code == 200
        data = response.json()
        assert "resumen" in data
        assert "interpretaciones" in data


@pytest.mark.integration
class TestPDFExportEndpoint:
    """Tests para endpoint de exportación PDF"""

    @patch('app.services.cache_service.CacheService.get_stats')
    @patch('app.services.pdf_service.PDFService.generate_stats_pdf')
    def test_export_pdf_success(self, mock_pdf, mock_cache, client):
        """Test exportación exitosa de PDF"""
        # Mock de datos
        mock_cache.return_value = {"some": "stats"}
        mock_pdf.return_value = b"fake-pdf-content"

        response = client.get("/api/v1/files/export/pdf/test-file-id")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert "analisis_" in response.headers["content-disposition"]

        # Verificar que se llamó al servicio PDF
        mock_pdf.assert_called_once()

    @patch('app.services.cache_service.CacheService.get_stats')
    def test_export_pdf_not_found(self, mock_cache, client):
        """Test PDF cuando no hay datos"""
        mock_cache.return_value = None

        response = client.get("/api/v1/files/export/pdf/nonexistent-id")

        assert response.status_code == 404


@pytest.mark.integration
class TestHealthEndpoint:
    """Tests para endpoint de health check"""

    def test_health_check(self, client):
        """Test health check básico"""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}