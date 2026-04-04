import pytest
import hashlib
from src.core.hashing import calculate_sha256, BlockchainServiceMock


def test_calculate_sha256_valid_data():
    """Проверка правильности вычисления хэша динамически."""
    # Используем сырые байты, чтобы избежать проблем с кодировками редактора
    data = b"hello blockchain"

    # Считаем хэш эталонным методом hashlib прямо в тесте
    expected = hashlib.sha256(data).hexdigest()

    # Проверяем, что наша функция выдает то же самое
    assert calculate_sha256(data) == expected


def test_calculate_sha256_empty_data():
    with pytest.raises(ValueError, match="Нельзя хэшировать пустой файл"):
        calculate_sha256(b"")


def test_blockchain_mock_registration():
    service = BlockchainServiceMock()
    tx_hash = service.register_hash("some_hash")
    assert isinstance(tx_hash, str)
    assert tx_hash.startswith("0x")
