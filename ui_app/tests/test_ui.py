import pytest
from streamlit.testing.v1 import AppTest
from src.core.hashing import BlockchainServiceMock
import os

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
ORIGINAL_FILE = os.path.join(FIXTURE_DIR, "original_log.txt")
COMPROMISED_FILE = os.path.join(FIXTURE_DIR, "compromised_log.txt")
SHADOW_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "shadow_db.json")


@pytest.fixture(autouse=True)
def patch_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.app.initialize_blockchain_service", lambda: BlockchainServiceMock()
    )

    # Очищаем состояние мока, чтобы тесты не влияли друг на друга
    BlockchainServiceMock._MOCK_STORAGE.clear()

    # Очищаем локальную теневую БД
    if os.path.exists(SHADOW_DB_PATH):
        os.remove(SHADOW_DB_PATH)


def test_app_smoke() -> None:
    """Проверка, что приложение запускается без исключений."""
    at = AppTest.from_file("src/app.py").run(timeout=10)
    assert not at.exception


def test_compromised_audit_flow() -> None:
    """Проверка обнаружения компрометации (удаления логов)."""
    at = AppTest.from_file("src/app.py").run(timeout=10)

    # 1. ВКЛАДКА РЕГИСТРАЦИИ (Загружаем оригинал)
    with open(ORIGINAL_FILE, "rb") as f:
        at.file_uploader(key="up_reg").upload(
            content=f.read(), filename="original_log.txt"
        ).run(timeout=10)

    for btn in at.button:
        if btn.label == "Записать в блокчейн":
            btn.click().run(timeout=30)
            break

    # 2. ВКЛАДКА АУДИТА (Загружаем скомпрометированный файл)
    at.tabs[1].run(timeout=10)
    with open(COMPROMISED_FILE, "rb") as f:
        at.file_uploader(key="up_aud").upload(
            content=f.read(), filename="compromised_log.txt"
        ).run(timeout=10)

    for btn in at.button:
        if btn.label == "Инициировать проверку":
            btn.click().run(timeout=15)
            break

    # 3. ПРОВЕРКА РЕЗУЛЬТАТА
    assert not at.exception

    alert_found = False
    for md in at.markdown:
        if "обнаружена компрометация журнала" in md.value:
            alert_found = True
            break

    assert alert_found, "Система не выдала предупреждение о компрометации файла!"
