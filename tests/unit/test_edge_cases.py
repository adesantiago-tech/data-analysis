import pytest
import pandas as pd
from io import BytesIO

from app.services.data_processor import DataProcessor


class TestEdgeCases:
    """Tests para casos edge específicos que faltan en cobertura"""

    def test_get_column_type_with_date_detection(self):
        """Test detección de fechas en columnas de texto"""
        # Crear serie con fechas válidas
        date_series = pd.Series(["2023-01-01", "2023-01-02", "2023-01-03"])

        result = DataProcessor._get_column_type(date_series)

        # Debería detectar como "Fecha/Texto"
        assert result == "Fecha/Texto"

    def test_get_column_type_with_invalid_dates(self):
        """Test con texto que no son fechas"""
        text_series = pd.Series(["abc", "def", "ghi"])

        result = DataProcessor._get_column_type(text_series)

        # Debería ser "Texto" normal
        assert result == "Texto"

    def test_get_column_type_other_dtype(self):
        """Test con tipos de datos no comunes"""
        # Crear serie con tipo boolean
        bool_series = pd.Series([True, False, True], dtype='bool')

        result = DataProcessor._get_column_type(bool_series)

        # Debería ser "Otro"
        assert result == "Otro"

    def test_analyze_text_column_with_single_value(self):
        """Test análisis de columna de texto con un solo valor único"""
        single_value_series = pd.Series(["mismo_valor"] * 10)

        result = DataProcessor._analyze_text_column(single_value_series, "test_col")

        # Verificar que maneja correctamente
        assert "estadisticas" in result
        assert result["estadisticas"]["valor_mas_comun"] == "mismo_valor"
        assert result["estadisticas"]["frecuencia"] == 10
        assert result["estadisticas"]["valores_unicos"] == 1

    def test_process_file_with_mixed_data_types(self):
        """Test procesamiento con tipos de datos mixtos"""
        mixed_csv = """nombre,edad,activo,fecha_ingreso
Juan,25,True,2023-01-01
María,30,False,2023-02-01
Pedro,,True,2023-03-01
Ana,35,,2023-04-01""".encode('utf-8')

        result = DataProcessor.process_file(mixed_csv, "mixed.csv")

        # Verificar que procesa todos los tipos
        assert "nombre" in result["analisis_columnas"]
        assert "edad" in result["analisis_columnas"]
        assert "activo" in result["analisis_columnas"]
        assert "fecha_ingreso" in result["analisis_columnas"]

        # Verificar manejo de valores faltantes
        edad_info = result["analisis_columnas"]["edad"]
        assert edad_info["valores_vacios"] == 1  # Pedro no tiene edad

        activo_info = result["analisis_columnas"]["activo"]
        assert activo_info["valores_vacios"] == 1  # Ana no tiene valor activo