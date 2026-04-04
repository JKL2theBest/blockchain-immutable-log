import hashlib
import time
from abc import ABC, abstractmethod
from typing import final


class BlockchainService(ABC):
    """
    Абстрактный базовый класс для сервиса взаимодействия с блокчейном.
    Определяет контракт, которому должны следовать все реализации (реальные или моки).
    """

    @abstractmethod
    def register_hash(self, file_hash: str) -> str:
        """
        Регистрирует хэш файла в смарт-контракте.

        Args:
            file_hash: SHA-256 хэш файла в виде hex-строки.

        Returns:
            Строку с хэшем транзакции в блокчейне.
        """
        pass


@final
class BlockchainServiceMock(BlockchainService):
    """
    Класс-заглушка (Mock) для имитации работы с блокчейном.
    Используется для локальной разработки и тестирования UI без реальных транзакций.
    """

    def register_hash(self, file_hash: str) -> str:
        """
        Имитирует отправку хэша в смарт-контракт.

        Args:
            file_hash: SHA-256 хэш файла.

        Returns:
            Сгенерированный хэш фейковой транзакции.
        """
        print(f"[*] Имитация отправки хэша '{file_hash[:10]}...' в блокчейн...")
        time.sleep(1.5)  # Имитация задержки сети
        # Генерируем фейковый хэш транзакции, похожий на настоящий
        mock_tx_hash = f"0x{hashlib.sha256(file_hash.encode()).hexdigest()[:40]}"
        print(f"[+] Хэш успешно зарегистрирован в транзакции: {mock_tx_hash}")
        return mock_tx_hash


def calculate_sha256(file_bytes: bytes) -> str:
    """
    Вычисляет SHA-256 хэш для содержимого файла.

    Функция безопасна для больших файлов, так как работает с уже
    прочитанными в память байтами. Обработка MemoryError
    должна происходить на уровне UI при чтении файла.

    Args:
        file_bytes: Содержимое файла в виде байтовой строки.

    Returns:
        SHA-256 хэш в виде hex-строки.

    Raises:
        ValueError: Если на вход поданы пустые данные.
    """
    if not file_bytes:
        raise ValueError("Нельзя хэшировать пустой файл.")

    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_bytes)
    return sha256_hash.hexdigest()


# --- Блок для самостоятельного запуска и проверки ---
if __name__ == "__main__":
    print("--- Запуск демонстрации модуля hashing.py ---")

    # 1. Создаем экземпляр нашего мок-сервиса
    blockchain_service = BlockchainServiceMock()

    # 2. Готовим тестовые данные (как будто прочитали из файла)
    test_log_data = (
        b"[2026-03-12 10:00:00] User 'admin' logged in successfully from 192.168.1.100"
    )
    print(f"\n[1] Тестирование с корректными данными:\n    '{test_log_data.decode()}'")

    # 3. Вычисляем хэш
    try:
        log_hash = calculate_sha256(test_log_data)
        print(f"[+] Вычислен SHA-256 хэш: {log_hash}")

        # 4. "Отправляем" хэш в блокчейн
        tx = blockchain_service.register_hash(log_hash)
        print(f"[+] Получен хэш транзакции: {tx}")
    except ValueError as e:
        print(f"[!] Ошибка: {e}")

    # 5. Тестирование с некорректными (пустыми) данными
    print("\n[2] Тестирование с пустым файлом:")
    empty_data = b""
    try:
        calculate_sha256(empty_data)
    except ValueError as e:
        print(f"[+] Успешно перехвачена ошибка: {e}")

    print("\n--- Демонстрация завершена ---")
