import pytest
import pandas as pd
from io import BytesIO

from app.services.data_processor import DataProcessor


class TestDataProcessor:
    """Tests unitarios para DataProcessor"""

    def test_process_csv_file_success(self, sample_csv_bytes):
        """Test procesamiento exitoso de CSV"""
        result = DataProcessor.process_file(sample_csv_bytes, "test.csv")

        # Verificar estructura de respuesta
        assert "resumen_general" in result
        assert "analisis_columnas" in result
        assert "estadisticas_pandas" in result

        # Verificar resumen general
        resumen = result["resumen_general"]
        assert resumen["nombre_archivo"] == "test.csv"
        assert resumen["total_filas"] == 5
        assert resumen["total_columnas"] == 3
        assert set(resumen["columnas"]) == {"nombre", "edad", "salario"}

    def test_process_excel_file_success(self, sample_excel_content):
        """Test procesamiento exitoso de Excel"""
        result = DataProcessor.process_file(sample_excel_content, "test.xlsx")

        # Verificar estructura
        assert "resumen_general" in result
        resumen = result["resumen_general"]
        assert resumen["total_filas"] == 4
        assert resumen["total_columnas"] == 4

    def test_analyze_numeric_column_edad(self, sample_csv_bytes):
        """Test análisis específico de columna edad"""
        result = DataProcessor.process_file(sample_csv_bytes, "test.csv")

        edad_analysis = result["analisis_columnas"]["edad"]

        # Verificar tipo y estadísticas
        assert edad_analysis["tipo_datos"] == "Numérico"
        assert edad_analysis["valores_totales"] == 5
        assert edad_analysis["valores_vacios"] == 0

        # Verificar interpretación específica para edad
        interpretaciones = edad_analysis["interpretacion"]
        assert any("Edad promedio" in interp for interp in interpretaciones)
        assert any("años" in interp for interp in interpretaciones)

    def test_analyze_numeric_column_salario(self, sample_csv_bytes):
        """Test análisis específico de columna salario"""
        result = DataProcessor.process_file(sample_csv_bytes, "test.csv")

        salario_analysis = result["analisis_columnas"]["salario"]

        # Verificar interpretación específica para salario
        interpretaciones = salario_analysis["interpretacion"]
        assert any("Salario promedio: $" in interp for interp in interpretaciones)
        assert any("más bajo" in interp for interp in interpretaciones)
        assert any("más alto" in interp for interp in interpretaciones)

    def test_analyze_text_column(self, sample_csv_bytes):
        """Test análisis de columna de texto"""
        result = DataProcessor.process_file(sample_csv_bytes, "test.csv")

        nombre_analysis = result["analisis_columnas"]["nombre"]

        # Verificar tipo
        assert nombre_analysis["tipo_datos"] == "Texto"

        # Verificar estadísticas de texto
        stats = nombre_analysis["estadisticas"]
        assert "valor_mas_comun" in stats
        assert "frecuencia" in stats
        assert "valores_unicos" in stats

    def test_get_column_type_numeric(self):
        """Test detección de tipo numérico"""
        series_int = pd.Series([1, 2, 3, 4, 5])
        series_float = pd.Series([1.1, 2.2, 3.3])

        assert DataProcessor._get_column_type(series_int) == "Numérico"
        assert DataProcessor._get_column_type(series_float) == "Numérico"

    def test_get_column_type_text(self):
        """Test detección de tipo texto"""
        series_text = pd.Series(["A", "B", "C"])

        assert DataProcessor._get_column_type(series_text) == "Texto"

    def test_analyze_empty_numeric_column(self):
        """Test análisis de columna numérica vacía"""
        empty_series = pd.Series([None, None, None], dtype=float)

        result = DataProcessor._analyze_numeric_column(empty_series, "test_col")

        # Verificar que maneja columnas vacías correctamente
        assert "interpretacion" in result
        # Puede ser string o lista, ambos son válidos
        if isinstance(result["interpretacion"], str):
            assert "No hay datos numéricos válidos" in result["interpretacion"]
        else:
            assert "No hay datos numéricos válidos" in result["interpretacion"]

    def test_analyze_empty_text_column(self):
        """Test análisis de columna de texto vacía"""
        empty_series = pd.Series([None, None, None])

        result = DataProcessor._analyze_text_column(empty_series, "test_col")

        # Verificar que maneja columnas vacías correctamente
        assert "interpretacion" in result
        # Puede ser string o lista, ambos son válidos
        if isinstance(result["interpretacion"], str):
            assert "No hay datos de texto válidos" in result["interpretacion"]
        else:
            assert "No hay datos de texto válidos" in result["interpretacion"]

    def test_departamento_column_recognition(self):
        """Test reconocimiento específico de columna departamento"""
        # Crear datos con columna departamento
        csv_content = """empleado,departamento,salario
Juan,IT,50000
María,Marketing,45000
Pedro,IT,55000
Ana,RRHH,48000
Carlos,IT,52000""".encode('utf-8')

        result = DataProcessor.process_file(csv_content, "empleados.csv")
        dept_analysis = result["analisis_columnas"]["departamento"]

        # Verificar interpretación específica para departamento
        interpretaciones = dept_analysis["interpretacion"]
        assert any("Departamento más común" in interp for interp in interpretaciones)
        assert any("departamentos diferentes" in interp for interp in interpretaciones)

    def test_unsupported_file_format(self):
        """Test error con formato no soportado"""
        with pytest.raises(ValueError, match="Formato de archivo no soportado"):
            DataProcessor.process_file(b"contenido", "archivo.txt")

    def test_malformed_csv(self):
        """Test error con CSV malformado"""
        malformed_csv = b"esta,no,es\nuna,estructura,csv,valida,con,demasiadas,columnas"

        # Debería procesar sin error pero manejar inconsistencias
        result = DataProcessor.process_file(malformed_csv, "test.csv")
        assert "resumen_general" in result

    @pytest.mark.slow
    def test_large_file_processing(self, large_csv_content):
        """Test procesamiento de archivo grande"""
        large_bytes = large_csv_content.encode('utf-8')

        result = DataProcessor.process_file(large_bytes, "large.csv")

        # Verificar que maneja archivos grandes
        assert result["resumen_general"]["total_filas"] == 1000
        assert "edad" in result["analisis_columnas"]
        assert "salario" in result["analisis_columnas"]