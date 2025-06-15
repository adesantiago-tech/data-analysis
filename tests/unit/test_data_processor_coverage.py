import pytest
import pandas as pd
from io import BytesIO

from app.services.data_processor import DataProcessor


class TestDataProcessorCoverage:
    """Tests para cubrir líneas específicas de data_processor.py"""

    def test_get_column_type_with_empty_series(self):
        """Test para cubrir líneas 96-97 en _get_column_type"""
        # Serie de objetos vacía que puede activar la excepción
        empty_object_series = pd.Series([], dtype='object')

        result = DataProcessor._get_column_type(empty_object_series)

        # Debería manejar serie vacía y devolver "Texto"
        assert result in ["Texto", "Fecha/Texto"]

    def test_get_column_type_with_invalid_date_object(self):
        """Test para cubrir el except en detección de fechas"""
        # Serie con objetos que no son fechas válidas
        non_date_series = pd.Series([{"key": "value"}, None, 123])

        result = DataProcessor._get_column_type(non_date_series)

        # Debería caer en el except y devolver "Texto"
        assert result == "Texto"

    def test_analyze_text_column_with_special_column_names(self):
        """Test para cubrir línea 134 en _analyze_text_column"""
        # Serie con nombre de columna que no coincide con casos especiales
        series = pd.Series(["A", "B", "A", "C", "A"])

        # Probar con nombre de columna que no está en los casos especiales
        result = DataProcessor._analyze_text_column(series, "columna_especial_no_reconocida")

        # Debería ejecutar la línea 134 (else del análisis de nombres de columna)
        assert "interpretacion" in result
        interpretaciones = result["interpretacion"]

        # Verificar que usa el caso genérico (línea 134)
        assert any("Valor más frecuente" in interp for interp in interpretaciones)
        assert any("Valores únicos" in interp for interp in interpretaciones)

    def test_process_file_with_complex_data_types(self):
        """Test para cubrir más líneas en el procesamiento"""
        # CSV con tipos de datos complejos
        complex_csv = """id,timestamp,status,metadata
1,2023-01-01T10:00:00,active,"{""key"": ""value""}"
2,2023-01-02T11:00:00,inactive,null
3,2023-01-03T12:00:00,pending,"{""another"": ""data""}"
4,2023-01-04T13:00:00,active,""simple_string""
5,invalid_timestamp,unknown,complex_data""".encode('utf-8')

        result = DataProcessor.process_file(complex_csv, "complex.csv")

        # Verificar que procesa todos los tipos correctamente
        assert "timestamp" in result["analisis_columnas"]
        assert "status" in result["analisis_columnas"]
        assert "metadata" in result["analisis_columnas"]

        # Verificar estadísticas
        assert "estadisticas_pandas" in result