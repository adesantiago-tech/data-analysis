from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from io import BytesIO

class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False  # True si usás HTTPS
        )
        # Crear el bucket si no existe
        found = self.client.bucket_exists(settings.MINIO_BUCKET)
        if not found:
            self.client.make_bucket(settings.MINIO_BUCKET)

    def save_file(self, filename: str, file_bytes: bytes, content_type: str = "application/octet-stream"):
        try:
            self.client.put_object(
                bucket_name=settings.MINIO_BUCKET,
                object_name=filename,
                data=BytesIO(file_bytes),
                length=len(file_bytes),
                content_type=content_type
            )
            return True
        except S3Error as e:
            print(f"Error subiendo archivo a MinIO: {e}")
            return False
