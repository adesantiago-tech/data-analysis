import redis
import json
import numpy as np
from app.core.config import settings


class CacheService:
    def __init__(self):
        self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def set_stats(self, file_id: str, stats: dict, expire_seconds: int = 3600):
        # Convertir tipos numpy a tipos nativos de Python antes de serializar
        clean_stats = self._convert_numpy_types(stats)
        # Guarda las stats con expiración (por defecto 1h)
        self.client.setex(f"stats:{file_id}", expire_seconds, json.dumps(clean_stats))

    def get_stats(self, file_id: str):
        value = self.client.get(f"stats:{file_id}")
        if value is None:
            return None
        return json.loads(value)

    def delete_stats(self, file_id: str):
        self.client.delete(f"stats:{file_id}")

    def _convert_numpy_types(self, obj):
        """Convierte tipos numpy a tipos nativos de Python recursivamente"""
        if isinstance(obj, dict):
            return {k: self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, 'item'):  # Para otros tipos numpy
            return obj.item()
        else:
            return obj