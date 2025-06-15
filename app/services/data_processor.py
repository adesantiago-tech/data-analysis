import pandas as pd
from io import BytesIO
import numpy as np

class DataProcessor:
    @staticmethod
    def process_file(file_bytes: bytes, filename: str) -> dict:
        # Detectar extensión y cargar con pandas
        if filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(file_bytes))
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(file_bytes))
        else:
            raise ValueError("Formato de archivo no soportado")

        # Análisis básico
        total_rows = len(df)
        total_columns = len(df.columns)
        columnas = df.columns.tolist()

        # Análisis por columna más amigable
        column_analysis = {}

        for col in df.columns:
            col_data = df[col]
            col_info = {
                "nombre_columna": col,
                "tipo_datos": DataProcessor._get_column_type(col_data),
                "valores_totales": len(col_data),
                "valores_vacios": col_data.isnull().sum(),
                "valores_unicos": col_data.nunique()
            }

            # Análisis específico según el tipo de datos
            if col_data.dtype in ['int64', 'float64']:
                col_info.update(DataProcessor._analyze_numeric_column(col_data, col))
            else:
                col_info.update(DataProcessor._analyze_text_column(col_data, col))

            column_analysis[col] = col_info

        return {
            "resumen_general": {
                "nombre_archivo": filename,
                "total_filas": total_rows,
                "total_columnas": total_columns,
                "columnas": columnas
            },
            "analisis_columnas": column_analysis,
            "estadisticas_pandas": df.describe(include='all').to_dict()  # Mantenemos las originales por si acaso
        }

    @staticmethod
    def _get_column_type(series):
        """Determina el tipo de datos de manera amigable"""
        if series.dtype in ['int64', 'float64']:
            return "Numérico"
        elif series.dtype == 'object':
            # Intentar determinar si es fecha
            try:
                pd.to_datetime(series.dropna().iloc[0])
                return "Fecha/Texto"
            except:
                return "Texto"
        else:
            return "Otro"

    @staticmethod
    def _analyze_numeric_column(series, col_name):
        """Análisis específico para columnas numéricas"""
        clean_data = series.dropna()

        if len(clean_data) == 0:
            return {"interpretacion": "No hay datos numéricos válidos"}

        promedio = clean_data.mean()
        minimo = clean_data.min()
        maximo = clean_data.max()
        mediana = clean_data.median()

        # Interpretación amigable
        interpretacion = []

        if col_name.lower() in ['edad', 'age']:
            interpretacion.append(f"Edad promedio: {promedio:.1f} años")
            interpretacion.append(f"Rango de edades: {minimo:.0f} a {maximo:.0f} años")
            interpretacion.append(f"La mitad de las personas tiene {mediana:.1f} años o menos")

        elif col_name.lower() in ['salario', 'sueldo', 'salary']:
            interpretacion.append(f"Salario promedio: ${promedio:,.0f}")
            interpretacion.append(f"Salario más bajo: ${minimo:,.0f}")
            interpretacion.append(f"Salario más alto: ${maximo:,.0f}")
            interpretacion.append(f"Salario mediano: ${mediana:,.0f}")

        elif col_name.lower() in ['antiguedad', 'experiencia']:
            interpretacion.append(f"Antigüedad promedio: {promedio:.1f} años")
            interpretacion.append(f"Desde {minimo:.0f} hasta {maximo:.0f} años de antigüedad")

        else:
            interpretacion.append(f"Valor promedio: {promedio:.2f}")
            interpretacion.append(f"Rango: {minimo:.2f} a {maximo:.2f}")
            interpretacion.append(f"Valor central (mediana): {mediana:.2f}")

        return {
            "estadisticas": {
                "promedio": round(promedio, 2),
                "minimo": round(minimo, 2),
                "maximo": round(maximo, 2),
                "mediana": round(mediana, 2),
                "desviacion_estandar": round(clean_data.std(), 2)
            },
            "interpretacion": interpretacion
        }

    @staticmethod
    def _analyze_text_column(series, col_name):
        """Análisis específico para columnas de texto"""
        clean_data = series.dropna()

        if len(clean_data) == 0:
            return {"interpretacion": "No hay datos de texto válidos"}

        value_counts = clean_data.value_counts()
        mas_comun = value_counts.index[0]
        frecuencia_mas_comun = value_counts.iloc[0]

        interpretacion = []

        if col_name.lower() in ['departamento', 'department', 'area']:
            interpretacion.append(f"Departamento más común: {mas_comun} ({frecuencia_mas_comun} personas)")
            interpretacion.append(f"Total de departamentos diferentes: {len(value_counts)}")

        elif col_name.lower() in ['remoto', 'remote', 'trabajo_remoto']:
            interpretacion.append(f"Modalidad más común: {mas_comun} ({frecuencia_mas_comun} personas)")

        else:
            interpretacion.append(f"Valor más frecuente: {mas_comun} (aparece {frecuencia_mas_comun} veces)")
            interpretacion.append(f"Valores únicos: {len(value_counts)}")

        # Top 3 valores más comunes
        top_valores = []
        for i, (valor, count) in enumerate(value_counts.head(3).items()):
            top_valores.append(f"{valor}: {count} veces")

        return {
            "estadisticas": {
                "valor_mas_comun": mas_comun,
                "frecuencia": frecuencia_mas_comun,
                "valores_unicos": len(value_counts),
                "top_3_valores": top_valores
            },
            "interpretacion": interpretacion
        }