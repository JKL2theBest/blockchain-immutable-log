from streamlit.testing.v1 import AppTest
import os

# Пути к фикстурам
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
ORIGINAL_FILE = os.path.join(FIXTURE_DIR, "original_log.txt")


def test_app_smoke():
    """Проверка, что приложение запускается без исключений."""
    at = AppTest.from_file("src/app.py").run()
    assert not at.exception


def test_full_audit_flow():
    """Интеграционный тест: полная цепочка регистрации и аудита."""
    at = AppTest.from_file("src/app.py").run()

    with open(ORIGINAL_FILE, "rb") as f:
        file_content = f.read()

    # Передаем и контент, и имя файла
    at.file_uploader(key="register_uploader").upload(
        content=file_content, filename="original_log.txt"
    ).run()

    # Нажимаем кнопку регистрации
    at.button(key="register_button").click().run()

    # Проверка, что хэш сохранился в состоянии сессии
    assert at.session_state.golden_hash is not None

    # Имитируем аудит того же файла
    at.file_uploader(key="audit_uploader").upload(
        content=file_content, filename="original_log.txt"
    ).run()

    at.button(key="audit_button").click().run()

    # Проверяем, что в интерфейсе нет критических ошибок
    assert not at.exception
    # Проверяем, что в UI появилось сообщение об успехе (индекс [0] в списке success-элементов)
    assert "УСПЕХ" in at.success[0].value
