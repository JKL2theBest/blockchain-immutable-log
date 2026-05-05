import pytest
from streamlit.testing.v1 import AppTest
import os

# Импортируем мок для подмены
from src.core.hashing import BlockchainServiceMock

# Пути к фикстурам
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
ORIGINAL_FILE = os.path.join(FIXTURE_DIR, "original_log.txt")
COMPROMISED_FILE = os.path.join(FIXTURE_DIR, "compromised_log.txt")


@pytest.fixture(autouse=True)
def patch_blockchain_service(monkeypatch):
    """
    Автоматически для всех тестов в этом файле подменяет реальный сервис на мок.
    Это гарантирует, что тесты UI никогда не будут делать реальные сетевые вызовы.
    """
    # Мы "обезвреживаем" функцию инициализации, чтобы она ВСЕГДА возвращала Mock
    monkeypatch.setattr(
        "src.app.initialize_blockchain_service", lambda: BlockchainServiceMock()
    )


def test_app_smoke() -> None:
    """Проверка, что приложение запускается без исключений."""
    at = AppTest.from_file("src/app.py").run()
    assert not at.exception


def test_full_audit_flow() -> None:
    """Интеграционный тест: полная цепочка регистрации и аудита."""
    at = AppTest.from_file("src/app.py").run()

    with open(ORIGINAL_FILE, "rb") as f:
        file_content = f.read()

    # Вкладка 1: Регистрация
    at.file_uploader(key="register_uploader").upload(
        content=file_content, filename="original_log.txt"
    ).run()
    at.button(key="register_button").click().run()

    assert at.session_state.golden_hash is not None
    assert at.success  # Проверяем, что появилось сообщение об успехе

    # Вкладка 2: Аудит
    at.tabs[1].run()  # Переключаемся на вторую вкладку
    at.file_uploader(key="audit_uploader").upload(
        content=file_content, filename="original_log.txt"
    ).run()
    at.button(key="audit_button").click().run()

    assert not at.exception
    assert "УСПЕХ" in at.success[0].value


def test_compromised_audit_flow() -> None:
    """QA-тест: проверка обнаружения подмены файла."""
    at = AppTest.from_file("src/app.py").run()

    # 1. Регистрируем ОРИГИНАЛ
    with open(ORIGINAL_FILE, "rb") as f:
        at.file_uploader(key="register_uploader").upload(
            content=f.read(), filename="original_log.txt"
        ).run()
    at.button(key="register_button").click().run()

    # 2. На вкладке аудита загружаем СКОМПРОМЕТИРОВАННЫЙ файл
    at.tabs[1].run()  # Переключаемся на вторую вкладку
    with open(COMPROMISED_FILE, "rb") as f:
        at.file_uploader(key="audit_uploader").upload(
            content=f.read(), filename="compromised_log.txt"
        ).run()
    at.button(key="audit_button").click().run()

    # 3. Проверяем, что система выдала ошибку (error)
    assert not at.exception
    assert "АЛЕРТ" in at.error[0].value
