import pytest
from app.services.pdf_service import PDFService


class TestPDFCoverage:
    """Tests para cubrir línea específica 110 de pdf_service.py"""

    def test_generate_pdf_with_estadisticas_none_values(self):
        """Test para cubrir línea 110 en generate_stats_pdf"""
        stats = {
            "analisis_columnas": {
                "test_column": {
                    "tipo_datos": "Numérico",
                    "interpretacion": ["Test interpretation"],
                    "estadisticas": {
                        "promedio": None,  # Valor None
                        "minimo": 10,
                        "maximo": None,    # Otro valor None
                        "lista_valores": ["a", "b", "c"],  # Lista para activar línea específica
                        "texto_normal": "valor_texto"
                    }
                }
            }
        }

        file_id = "test-line-110"

        # Generar PDF - esto debería ejecutar la línea 110
        pdf_bytes = PDFService.generate_stats_pdf(stats, file_id)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_generate_pdf_estadisticas_with_list_conversion(self):
        """Test específico para conversión de listas en estadísticas"""
        stats = {
            "analisis_columnas": {
                "column_with_lists": {
                    "estadisticas": {
                        "top_3_valores": ["valor1: 5 veces", "valor2: 3 veces", "valor3: 2 veces"],
                        "categorias": ["A", "B", "C", "D"],
                        "rangos": [1, 2, 3, 4, 5]
                    }
                }
            }
        }

        file_id = "list-conversion-test"

        pdf_bytes = PDFService.generate_stats_pdf(stats, file_id)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')