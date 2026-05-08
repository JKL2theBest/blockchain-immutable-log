import pytest
from streamlit.testing.v1 import AppTest
import os
from src.core.hashing import BlockchainServiceMock

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
ORIGINAL_FILE = os.path.join(FIXTURE_DIR, "original_log.txt")
COMPROMISED_FILE = os.path.join(FIXTURE_DIR, "compromised_log.txt")

@pytest.fixture(autouse=True)
def patch_blockchain_service(monkeypatch):
    monkeypatch.setattr("src.app.initialize_blockchain_service", lambda: BlockchainServiceMock())

def test_app_smoke() -> None:
    at = AppTest.from_file("src/app.py").run()
    assert not at.exception

def test_compromised_audit_flow() -> None:
    at = AppTest.from_file("src/app.py").run()

    with open(ORIGINAL_FILE, "rb") as f:
        at.file_uploader(key="reg").upload(content=f.read(), filename="original_log.txt").run()
    at.button("Записать события").click().run()

    at.tabs[1].run()
    with open(COMPROMISED_FILE, "rb") as f:
        at.file_uploader(key="audit").upload(content=f.read(), filename="compromised_log.txt").run()
    at.button("Запустить проверку целостности").click().run()

    assert not at.exception
    assert "ИНЦИДЕНТ ИБ" in at.error[0].value