import pytest
from app.services.pdf_service import PDFService


class TestPDFService:
    """Tests unitarios para PDFService"""

    def test_generate_stats_pdf_with_new_format(self):
        """Test generar PDF con formato nuevo"""
        stats = {
            "resumen_general": {
                "nombre_archivo": "test.csv",
                "total_filas": 100,
                "total_columnas": 3,
                "columnas": ["nombre", "edad", "salario"]
            },
            "analisis_columnas": {
                "edad": {
                    "tipo_datos": "Numérico",
                    "valores_totales": 100,
                    "valores_vacios": 0,
                    "valores_unicos": 25,
                    "interpretacion": [
                        "Edad promedio: 32.5 años",
                        "Rango de edades: 22 a 65 años"
                    ],
                    "estadisticas": {
                        "promedio": 32.5,
                        "minimo": 22,
                        "maximo": 65,
                        "mediana": 31.0
                    }
                }
            }
        }

        file_id = "test-file-123"

        # Generar PDF
        pdf_bytes = PDFService.generate_stats_pdf(stats, file_id)

        # Verificar que se generó un PDF válido
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')  # Signature de PDF

    def test_generate_stats_pdf_with_old_format(self):
        """Test generar PDF con formato antiguo"""
        stats = {
            "columna1": {
                "count": 100,
                "mean": 25.5,
                "std": 5.2,
                "min": 18,
                "max": 35
            },
            "columna2": {
                "count": 100,
                "unique": 50,
                "top": "valor_comun",
                "freq": 10
            }
        }

        file_id = "old-format-test"

        # Generar PDF
        pdf_bytes = PDFService.generate_stats_pdf(stats, file_id)

        # Verificar PDF válido
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_generate_stats_pdf_empty_stats(self):
        """Test generar PDF con estadísticas vacías"""
        stats = {}
        file_id = "empty-stats"

        # Debería generar PDF incluso sin datos
        pdf_bytes = PDFService.generate_stats_pdf(stats, file_id)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_generate_stats_pdf_with_none_values(self):
        """Test generar PDF con valores None"""
        stats = {
            "resumen_general": {
                "nombre_archivo": "test.csv",
                "total_filas": 50,
                "total_columnas": 3
            },
            "analisis_columnas": {
                "col_with_nones": {
                    "tipo_datos": "Numérico",
                    "interpretacion": None,
                    "estadisticas": {
                        "promedio": None,
                        "minimo": 10,
                        "maximo": None
                    }
                }
            }
        }

        file_id = "none-values-test"

        # Debería manejar valores None sin errores
        pdf_bytes = PDFService.generate_stats_pdf(stats, file_id)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_generate_stats_pdf_mixed_format(self):
        """Test generar PDF con formato mixto"""
        stats = {
            "resumen_general": {
                "nombre_archivo": "mixed.csv",
                "total_filas": 25
            },
            "analisis_columnas": {
                "nueva_col": {
                    "tipo_datos": "Numérico",
                    "interpretacion": ["Test interpretación"]
                }
            },
            "columna_antigua": {
                "count": 25,
                "mean": 15.5
            }
        }

        file_id = "mixed-format"

        # Debería manejar ambos formatos
        pdf_bytes = PDFService.generate_stats_pdf(stats, file_id)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_generate_stats_pdf_special_characters(self):
        """Test con caracteres especiales"""
        stats = {
            "resumen_general": {
                "nombre_archivo": "archivo_con_ñ.csv",
                "total_filas": 5,
                "columnas": ["descripción"]
            },
            "analisis_columnas": {
                "descripción": {
                    "tipo_datos": "Texto",
                    "interpretacion": [
                        "Descripción más común: Niño pequeño"
                    ],
                    "estadisticas": {
                        "valor_mas_comun": "Niño pequeño"
                    }
                }
            }
        }

        file_id = "special-chars"

        # Debería manejar caracteres especiales
        pdf_bytes = PDFService.generate_stats_pdf(stats, file_id)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')

    def test_generate_stats_pdf_large_data(self):
        """Test con datos grandes"""
        # Crear muchas columnas para testear paginación
        analisis_columnas = {}
        for i in range(20):
            analisis_columnas[f"columna_{i}"] = {
                "tipo_datos": "Numérico",
                "interpretacion": [f"Interpretación para columna {i}"] * 3,
                "estadisticas": {
                    "promedio": i * 10,
                    "minimo": i,
                    "maximo": i * 100
                }
            }

        stats = {
            "resumen_general": {
                "nombre_archivo": "big_data.csv",
                "total_filas": 10000,
                "total_columnas": 20
            },
            "analisis_columnas": analisis_columnas
        }

        file_id = "big-data-test"

        pdf_bytes = PDFService.generate_stats_pdf(stats, file_id)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
        # PDF debería ser más grande por más contenido
        assert len(pdf_bytes) > 5000