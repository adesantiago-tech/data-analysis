import pytest
import json
import numpy as np
from unittest.mock import Mock, patch

from app.services.cache_service import CacheService


class TestCacheService:
    """Tests unitarios para CacheService"""

    def test_set_stats_simple_dict(self, cache_service_mock, mock_redis):
        """Test guardar estadísticas simples"""
        test_stats = {
            "columna1": {"count": 10, "mean": 25.5},
            "columna2": {"count": 10, "unique": 5}
        }

        cache_service_mock.set_stats("test-id", test_stats)

        # Verificar que se llamó setex con los parámetros correctos
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args

        assert call_args[0][0] == "stats:test-id"
        assert call_args[0][1] == 3600  # expire_seconds por defecto

        # Verificar que el JSON es válido
        stored_json = call_args[0][2]
        parsed_data = json.loads(stored_json)
        assert parsed_data["columna1"]["count"] == 10

    def test_set_stats_with_numpy_types(self, cache_service_mock, mock_redis):
        """Test guardar estadísticas con tipos numpy"""
        test_stats = {
            "columna1": {
                "count": np.int64(10),
                "mean": np.float64(25.5),
                "array": np.array([1, 2, 3])
            }
        }

        cache_service_mock.set_stats("test-id", test_stats)

        # Verificar que se convirtieron los tipos numpy
        call_args = mock_redis.setex.call_args
        stored_json = call_args[0][2]
        parsed_data = json.loads(stored_json)

        # Verificar que son tipos nativos de Python
        assert isinstance(parsed_data["columna1"]["count"], int)
        assert isinstance(parsed_data["columna1"]["mean"], float)
        assert isinstance(parsed_data["columna1"]["array"], list)

    def test_set_stats_custom_expiration(self, cache_service_mock, mock_redis):
        """Test guardar con expiración personalizada"""
        test_stats = {"test": "data"}

        cache_service_mock.set_stats("test-id", test_stats, expire_seconds=7200)

        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 7200

    def test_get_stats_success(self, cache_service_mock, mock_redis):
        """Test obtener estadísticas exitosamente"""
        # Mock de datos en Redis
        test_data = {"columna1": {"count": 10}}
        mock_redis.get.return_value = json.dumps(test_data)

        result = cache_service_mock.get_stats("test-id")

        mock_redis.get.assert_called_once_with("stats:test-id")
        assert result == test_data

    def test_get_stats_not_found(self, cache_service_mock, mock_redis):
        """Test obtener estadísticas no encontradas"""
        mock_redis.get.return_value = None

        result = cache_service_mock.get_stats("nonexistent-id")

        assert result is None

    def test_get_stats_invalid_json(self, cache_service_mock, mock_redis):
        """Test manejar JSON inválido en Redis"""
        mock_redis.get.return_value = "invalid-json"

        with pytest.raises(json.JSONDecodeError):
            cache_service_mock.get_stats("test-id")

    def test_delete_stats(self, cache_service_mock, mock_redis):
        """Test eliminar estadísticas"""
        cache_service_mock.delete_stats("test-id")

        mock_redis.delete.assert_called_once_with("stats:test-id")

    def test_convert_numpy_types_nested_dict(self, cache_service_mock):
        """Test conversión de tipos numpy en diccionarios anidados"""
        nested_data = {
            "level1": {
                "level2": {
                    "numpy_int": np.int64(42),
                    "numpy_float": np.float64(3.14),
                    "normal_int": 10
                }
            }
        }

        result = cache_service_mock._convert_numpy_types(nested_data)

        # Verificar conversión profunda
        assert isinstance(result["level1"]["level2"]["numpy_int"], int)
        assert isinstance(result["level1"]["level2"]["numpy_float"], float)
        assert isinstance(result["level1"]["level2"]["normal_int"], int)

    def test_convert_numpy_types_list(self, cache_service_mock):
        """Test conversión de tipos numpy en listas"""
        list_data = [
            np.int64(1),
            np.float64(2.5),
            [np.int64(3), np.float64(4.5)]
        ]

        result = cache_service_mock._convert_numpy_types(list_data)

        assert isinstance(result[0], int)
        assert isinstance(result[1], float)
        assert isinstance(result[2][0], int)
        assert isinstance(result[2][1], float)

    def test_convert_numpy_array(self, cache_service_mock):
        """Test conversión de numpy arrays"""
        array_data = np.array([1, 2, 3, 4, 5])

        result = cache_service_mock._convert_numpy_types(array_data)

        assert isinstance(result, list)
        assert result == [1, 2, 3, 4, 5]

    def test_convert_numpy_scalar_with_item_method(self, cache_service_mock):
        """Test conversión de escalares numpy con método .item()"""
        # Simular un tipo numpy con método .item()
        class MockNumpyType:
            def item(self):
                return 42

        mock_numpy = MockNumpyType()
        result = cache_service_mock._convert_numpy_types(mock_numpy)

        assert result == 42

    @patch('app.core.config.settings.REDIS_URL', 'redis://localhost:6379/0')
    def test_cache_service_initialization(self):
        """Test inicialización del servicio de cache"""
        with patch('redis.Redis') as mock_redis_class:
            mock_instance = Mock()
            mock_redis_class.from_url.return_value = mock_instance

            service = CacheService()

            mock_redis_class.from_url.assert_called_once_with(
                'redis://localhost:6379/0',
                decode_responses=True
            )
            assert service.client == mock_instance