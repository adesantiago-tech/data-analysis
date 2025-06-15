import pytest
from unittest.mock import patch, Mock
from io import BytesIO
import json


@pytest.mark.e2e
class TestCompleteDataAnalysisFlow:
    """Tests end-to-end del flujo completo de análisis"""

    @patch('app.services.storage_service.StorageService.save_file')
    @patch('app.services.cache_service.CacheService.set_stats')
    @patch('app.services.cache_service.CacheService.get_stats')
    @patch('app.services.pdf_service.PDFService.generate_stats_pdf')
    def test_complete_csv_analysis_flow(self, mock_pdf, mock_get_cache, mock_set_cache,
                                        mock_storage, client, sample_csv_bytes):
        """Test flujo completo: Upload CSV → Obtener Stats → Generar PDF"""

        # 1. UPLOAD: Configurar mocks para upload
        mock_storage.return_value = True
        mock_set_cache.return_value = None

        # Upload del archivo
        files = {"file": ("empleados.csv", BytesIO(sample_csv_bytes), "text/csv")}
        upload_response = client.post("/api/v1/files/upload", files=files)

        # Verificar upload exitoso
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        file_id = upload_data["file_id"]

        # Verificar estructura de respuesta del upload
        assert "resumen" in upload_data
        assert "preview_analisis" in upload_data
        assert upload_data["filename"] == "empleados.csv"

        # 2. STATS: Configurar mock para obtener estadísticas
        mock_stats = {
            "resumen_general": {
                "nombre_archivo": "empleados.csv",
                "total_filas": 5,
                "total_columnas": 3,
                "columnas": ["nombre", "edad", "salario"]
            },
            "analisis_columnas": {
                "edad": {
                    "tipo_datos": "Numérico",
                    "interpretacion": ["Edad promedio: 28.4 años", "Rango de edades: 25 a 32 años"]
                },
                "salario": {
                    "tipo_datos": "Numérico",
                    "interpretacion": ["Salario promedio: $58,400", "Salario más bajo: $50,000"]
                }
            }
        }
        mock_get_cache.return_value = mock_stats

        # Obtener estadísticas completas
        stats_response = client.get(f"/api/v1/files/stats/{file_id}")
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        assert stats_data["file_id"] == file_id
        assert "analisis_completo" in stats_data

        # Obtener resumen
        summary_response = client.get(f"/api/v1/files/stats/{file_id}/resumen")
        assert summary_response.status_code == 200
        summary_data = summary_response.json()
        assert "resumen" in summary_data
        assert "interpretaciones" in summary_data

        # 3. PDF: Configurar mock para PDF
        mock_pdf.return_value = b"fake-pdf-content-for-testing"

        # Generar PDF
        pdf_response = client.get(f"/api/v1/files/export/pdf/{file_id}")
        assert pdf_response.status_code == 200
        assert pdf_response.headers["content-type"] == "application/pdf"
        assert "analisis_" in pdf_response.headers["content-disposition"]

        # Verificar que todos los servicios fueron llamados
        mock_storage.assert_called_once()
        mock_set_cache.assert_called_once()
        assert mock_get_cache.call_count == 3  # stats, resumen, pdf
        mock_pdf.assert_called_once()

    @patch('app.services.storage_service.StorageService.save_file')
    @patch('app.services.cache_service.CacheService.set_stats')
    @patch('app.services.cache_service.CacheService.get_stats')
    def test_error_handling_flow(self, mock_get_cache, mock_set_cache, mock_storage, client):
        """Test manejo de errores en el flujo completo"""

        # 1. Test upload con storage failure
        mock_storage.return_value = False

        files = {"file": ("test.csv", BytesIO(b"name,age\nJohn,25"), "text/csv")}
        upload_response = client.post("/api/v1/files/upload", files=files)

        assert upload_response.status_code == 500
        assert "No se pudo guardar el archivo en MinIO" in upload_response.json()["detail"]

        # 2. Test obtener stats de archivo inexistente
        mock_get_cache.return_value = None

        stats_response = client.get("/api/v1/files/stats/nonexistent-id")
        assert stats_response.status_code == 404

        pdf_response = client.get("/api/v1/files/export/pdf/nonexistent-id")
        assert pdf_response.status_code == 404

    @patch('app.services.storage_service.StorageService.save_file')
    @patch('app.services.cache_service.CacheService.set_stats')
    def test_file_format_validation(self, mock_set_cache, mock_storage, client):
        """Test validación de formatos de archivo"""

        # Test archivo con extensión incorrecta pero content-type correcto
        invalid_files = [
            ("document.txt", b"invalid content", "text/plain"),
            ("image.jpg", b"fake image data", "image/jpeg"),
            ("script.py", b"print('hello')", "text/x-python"),
        ]

        for filename, content, content_type in invalid_files:
            files = {"file": (filename, BytesIO(content), content_type)}
            response = client.post("/api/v1/files/upload", files=files)

            assert response.status_code == 400
            assert "Solo se permiten archivos CSV o Excel" in response.json()["detail"]

    @pytest.mark.slow
    @patch('app.services.storage_service.StorageService.save_file')
    @patch('app.services.cache_service.CacheService.set_stats')
    @patch('app.services.cache_service.CacheService.get_stats')
    def test_large_file_processing_flow(self, mock_get_cache, mock_set_cache,
                                        mock_storage, client, large_csv_content):
        """Test procesamiento de archivos grandes"""

        mock_storage.return_value = True
        mock_set_cache.return_value = None

        large_bytes = large_csv_content.encode('utf-8')
        files = {"file": ("large_data.csv", BytesIO(large_bytes), "text/csv")}

        upload_response = client.post("/api/v1/files/upload", files=files)

        # Verificar que procesa archivos grandes sin error
        assert upload_response.status_code == 201
        upload_data = upload_response.json()

        # Verificar que procesó todas las filas
        assert upload_data["resumen"]["total_filas"] == 1000

        # El procesamiento debería ser eficiente incluso con 1000 filas
        assert "preview_analisis" in upload_data

    def test_api_documentation_accessible(self, client):
        """Test que la documentación de API es accesible"""

        # Test Swagger UI
        docs_response = client.get("/api/v1/docs")
        assert docs_response.status_code == 200

        # Test OpenAPI schema
        openapi_response = client.get("/api/v1/openapi.json")
        assert openapi_response.status_code == 200

        # Verificar que el schema es JSON válido
        schema = openapi_response.json()
        assert "openapi" in schema
        assert "paths" in schema
        assert "/api/v1/files/upload" in schema["paths"]

    @patch('app.services.storage_service.StorageService.save_file')
    @patch('app.services.cache_service.CacheService.set_stats')
    def test_concurrent_uploads_simulation(self, mock_set_cache, mock_storage, client, sample_csv_bytes):
        """Test simulación de uploads concurrentes"""

        mock_storage.return_value = True
        mock_set_cache.return_value = None

        # Simular múltiples uploads simultáneos
        file_ids = []
        for i in range(3):
            files = {"file": (f"test_{i}.csv", BytesIO(sample_csv_bytes), "text/csv")}
            response = client.post("/api/v1/files/upload", files=files)

            assert response.status_code == 201
            file_ids.append(response.json()["file_id"])

        # Verificar que todos los file_ids son únicos
        assert len(set(file_ids)) == 3

        # Verificar que cada upload fue procesado independientemente
        assert mock_storage.call_count == 3
        assert mock_set_cache.call_count == 3