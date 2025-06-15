from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO

class PDFService:
    @staticmethod
    def generate_stats_pdf(stats: dict, file_id: str) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=inch, leftMargin=inch,
                                topMargin=inch, bottomMargin=inch)

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor("#2E86AB")
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor("#A23B72")
        )

        story = []

        # Título principal
        title = Paragraph(f"📊 Análisis de Datos - Archivo ID: {file_id[:8]}...", title_style)
        story.append(title)
        story.append(Spacer(1, 12))

        # Resumen general (si existe en el nuevo formato)
        if "resumen_general" in stats:
            resumen = stats["resumen_general"]
            story.append(Paragraph("📋 Resumen General", heading_style))

            resumen_data = [
                ["Nombre del archivo:", resumen.get("nombre_archivo", "N/A")],
                ["Total de filas:", f"{resumen.get('total_filas', 'N/A'):,}"],
                ["Total de columnas:", str(resumen.get('total_columnas', 'N/A'))],
                ["Columnas encontradas:", ", ".join(resumen.get('columnas', []))]
            ]

            resumen_table = Table(resumen_data, colWidths=[2*inch, 4*inch])
            resumen_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F0F8FF")),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.HexColor("#F9F9F9")]),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#DDDDDD"))
            ]))

            story.append(resumen_table)
            story.append(Spacer(1, 20))

        # Análisis por columnas (nuevo formato)
        if "analisis_columnas" in stats:
            story.append(Paragraph("🔍 Análisis Detallado por Columna", heading_style))

            for col_name, col_info in stats["analisis_columnas"].items():
                # Título de la columna
                col_title = Paragraph(f"<b>Columna: {col_name}</b> ({col_info.get('tipo_datos', 'N/A')})",
                                      styles['Heading3'])
                story.append(col_title)

                # Información básica
                basic_info = [
                    ["Tipo de datos:", col_info.get('tipo_datos', 'N/A')],
                    ["Valores totales:", str(col_info.get('valores_totales', 'N/A'))],
                    ["Valores vacíos:", str(col_info.get('valores_vacios', 'N/A'))],
                    ["Valores únicos:", str(col_info.get('valores_unicos', 'N/A'))]
                ]

                info_table = Table(basic_info, colWidths=[1.5*inch, 2*inch])
                info_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#E8F4F8")),
                    ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 9),
                    ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#CCCCCC"))
                ]))

                story.append(info_table)
                story.append(Spacer(1, 10))

                # Interpretación amigable - LÍNEA CORREGIDA
                if 'interpretacion' in col_info and col_info['interpretacion'] is not None:
                    story.append(Paragraph("<b>📖 Interpretación:</b>", styles['Normal']))
                    for interpretacion in col_info['interpretacion']:
                        bullet_point = Paragraph(f"• {interpretacion}", styles['Normal'])
                        story.append(bullet_point)

                # Estadísticas específicas
                if 'estadisticas' in col_info:
                    story.append(Paragraph("<b>📊 Estadísticas:</b>", styles['Normal']))

                    stats_data = []
                    for key, value in col_info['estadisticas'].items():
                        if isinstance(value, list):
                            value = ", ".join(map(str, value))
                        stats_data.append([key.replace('_', ' ').title() + ":", str(value)])

                    if stats_data:
                        stats_table = Table(stats_data, colWidths=[1.5*inch, 3*inch])
                        stats_table.setStyle(TableStyle([
                            ('FONTSIZE', (0,0), (-1,-1), 8),
                            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#EEEEEE")),
                            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FAFAFA"))
                        ]))
                        story.append(stats_table)

                story.append(Spacer(1, 15))

        # Si solo tenemos el formato antiguo, mostrarlo de manera más limpia
        else:
            story.append(Paragraph("📊 Estadísticas Técnicas", heading_style))
            story.append(Paragraph("<i>Nota: Estas son estadísticas técnicas generadas automáticamente</i>",
                                   styles['Normal']))
            story.append(Spacer(1, 10))

            for col_name, col_stats in stats.items():
                story.append(Paragraph(f"<b>Columna: {col_name}</b>", styles['Heading3']))

                # Filtrar valores None y organizarlos mejor
                clean_stats = {}
                for key, value in col_stats.items():
                    if value is not None:
                        if isinstance(value, float):
                            clean_stats[key] = f"{value:.2f}"
                        else:
                            clean_stats[key] = str(value)

                if clean_stats:
                    stats_data = [[key.title() + ":", value] for key, value in clean_stats.items()]

                    stats_table = Table(stats_data, colWidths=[1.5*inch, 2.5*inch])
                    stats_table.setStyle(TableStyle([
                        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0,0), (-1,-1), 9),
                        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#DDDDDD")),
                        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F9F9F9"))
                    ]))

                    story.append(stats_table)

                story.append(Spacer(1, 12))

        # Footer
        story.append(Spacer(1, 30))
        footer = Paragraph(
            f"<i>Reporte generado automáticamente • ID: {file_id}</i>",
            styles['Normal']
        )
        story.append(footer)

        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()