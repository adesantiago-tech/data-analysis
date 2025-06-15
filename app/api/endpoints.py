from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from io import BytesIO
import uuid
import math

from app.services.data_processor import DataProcessor
from app.services.storage_service import StorageService
from app.services.cache_service import CacheService
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/files", tags=["files"])

storage_service = StorageService()
cache_service = CacheService()

def sanitize_stats(data):
    """Limpia valores NaN e infinitos de las estadísticas"""
    if isinstance(data, dict):
        return {k: sanitize_stats(v) for k, v in data.items()}
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return None
        return data
    else:
        return data

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos CSV o Excel (.csv, .xlsx)"
        )

    contents = await file.read()

    # Guardar en MinIO
    ok = storage_service.save_file(
        filename=file.filename,
        file_bytes=contents,
        content_type=file.content_type or "application/octet-stream"
    )
    if not ok:
        raise HTTPException(status_code=500, detail="No se pudo guardar el archivo en MinIO")

    # Procesar archivo con el nuevo DataProcessor
    try:
        result = DataProcessor.process_file(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando archivo: {str(e)}")

    file_id = str(uuid.uuid4())

    # Preparar datos para cache - ahora usamos toda la estructura mejorada
    cache_data = {
        "resumen_general": result["resumen_general"],
        "analisis_columnas": sanitize_stats(result["analisis_columnas"]),
        # Mantenemos las estadísticas originales por compatibilidad
        "estadisticas_pandas": sanitize_stats(result["estadisticas_pandas"])
    }

    # Guardar en cache
    cache_service.set_stats(file_id, cache_data)

    # Respuesta al usuario con la nueva estructura
    return JSONResponse(
        status_code=201,
        content={
            "file_id": file_id,
            "filename": file.filename,
            "size_bytes": len(contents),
            "resumen": result["resumen_general"],
            "preview_analisis": {
                col: info.get("interpretacion", ["Sin interpretación disponible"])[:2]  # Solo las primeras 2 interpretaciones
                for col, info in result["analisis_columnas"].items()
            },
            "message": "Archivo subido, procesado y análisis generado exitosamente"
        }
    )

@router.get("/stats/{file_id}")
async def get_stats(file_id: str):
    """Obtiene el análisis completo del archivo"""
    stats = cache_service.get_stats(file_id)
    if not stats:
        raise HTTPException(status_code=404, detail="No se encontraron stats para ese file_id")

    return {
        "file_id": file_id,
        "analisis_completo": stats
    }

@router.get("/stats/{file_id}/resumen")
async def get_summary(file_id: str):
    """Obtiene solo el resumen general del archivo"""
    stats = cache_service.get_stats(file_id)
    if not stats:
        raise HTTPException(status_code=404, detail="No se encontraron stats para ese file_id")

    return {
        "file_id": file_id,
        "resumen": stats.get("resumen_general", {}),
        "interpretaciones": {
            col: info.get("interpretacion", [])
            for col, info in stats.get("analisis_columnas", {}).items()
        }
    }

@router.get("/export/pdf/{file_id}")
async def export_stats_pdf(file_id: str):
    """Exporta el análisis completo a PDF"""
    stats = cache_service.get_stats(file_id)
    if not stats:
        raise HTTPException(status_code=404, detail="No se encontraron stats para ese file_id")

    # El PDFService mejorado puede manejar tanto el formato nuevo como el viejo
    pdf_bytes = PDFService.generate_stats_pdf(stats, file_id)

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=analisis_{file_id[:8]}.pdf"}
    )