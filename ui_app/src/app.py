# D:\...\blockchain-immutable-log\ui_app\src\app.py

import streamlit as st
import time

# Важно: Используем относительный импорт, так как app.py и core/ находятся внутри пакета src
# Запускать приложение нужно будет как модуль, чтобы Python правильно понял пути
from core.hashing import calculate_sha256, BlockchainServiceMock

# --- 1. Конфигурация страницы ---
st.set_page_config(
    page_title="ImmutableLog Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Управление состоянием (Session State) ---
# Это "память" приложения между действиями пользователя
if 'golden_hash' not in st.session_state:
    st.session_state.golden_hash = None  # Хэш, "записанный в блокчейн"
if 'last_tx' not in st.session_state:
    st.session_state.last_tx = None      # Хэш последней транзакции

# --- 3. Сайдбар (Боковая панель) ---
with st.sidebar:
    st.title("🛡️ ImmutableLog")
    st.info("Децентрализованная система аудита логов на базе технологии блокчейн.")

    st.header("Параметры системы (Mock)")
    st.metric(label="Статус сети", value="Connected", delta="Lat: 120ms")
    st.metric(label="Всего хэшей в блокчейне", value="1,284")
    
    st.success("Система функционирует в штатном режиме.")

# --- 4. Основной интерфейс ---
st.title("Панель управления безопасностью")
st.markdown("---")

# Инициализируем сервис-заглушку для работы с блокчейном
blockchain_service = BlockchainServiceMock()

# Создаем вкладки для двух основных функций
tab1, tab2 = st.tabs(["Регистрация лога", "Аудит целостности"])

# --- ВКЛАДКА 1: Регистрация нового лога ---
with tab1:
    st.header("Шаг 1: Регистрация эталонного файла")
    st.write("Загрузите оригинальный, немодифицированный лог-файл. Его хэш будет сохранен в блокчейн как эталон.")

    uploaded_file_register = st.file_uploader(
        "Выберите лог-файл для регистрации (.txt)",
        type=["txt"],
        key="register_uploader"
    )

    if uploaded_file_register:
        try:
            file_bytes = uploaded_file_register.getvalue()
            log_hash = calculate_sha256(file_bytes)
            
            st.info(f"**Вычисленный SHA-256 хэш:** `{log_hash}`")

            if st.button("Записать хэш в блокчейн", key="register_button"):
                with st.spinner("Отправка транзакции в сеть... Ожидание подтверждения..."):
                    tx_hash = blockchain_service.register_hash(log_hash)
                    time.sleep(1) # Доп. задержка для красоты
                
                st.success(f"**УСПЕХ!** Хэш зарегистрирован в блокчейне.")
                st.code(f"Хэш транзакции: {tx_hash}", language="bash")

                # Сохраняем хэш в "память" сессии для аудита
                st.session_state.golden_hash = log_hash
                st.session_state.last_tx = tx_hash
                st.balloons()

        except ValueError as e:
            st.error(f"Ошибка: {e}")
        except Exception as e:
            st.error(f"Произошла непредвиденная ошибка: {e}")

# --- ВКЛАДКА 2: Аудит целостности файла ---
with tab2:
    st.header("Шаг 2: Аудит целостности файла")

    if not st.session_state.golden_hash:
        st.warning("Сначала зарегистрируйте эталонный хэш на вкладке 'Регистрация лога'.")
    else:
        st.write("Теперь загрузите файл, который вы хотите проверить на предмет изменений.")
        st.code(f"Эталонный хэш из блокчейна: {st.session_state.golden_hash}", language="bash")

        uploaded_file_audit = st.file_uploader(
            "Выберите лог-файл для проверки (.txt)",
            type=["txt"],
            key="audit_uploader"
        )

        if uploaded_file_audit:
            try:
                file_bytes_audit = uploaded_file_audit.getvalue()
                audit_hash = calculate_sha256(file_bytes_audit)

                st.info(f"**Хэш проверяемого файла:** `{audit_hash}`")

                if st.button("Сверить с эталоном в блокчейне", key="audit_button"):
                    with st.spinner("Сверка хэшей..."):
                        time.sleep(1)
                    
                    if audit_hash == st.session_state.golden_hash:
                        st.success("✅ УСПЕХ: Файл не был изменен. Целостность подтверждена.")
                    else:
                        st.error("🚨 АЛЕРТ: Файл был скомпрометирован! Хэши не совпадают.")
                        with st.expander("Показать детали расхождения"):
                            st.text(f"Ожидаемый хэш (из блокчейна): {st.session_state.golden_hash}")
                            st.text(f"Фактический хэш (проверяемый файл): {audit_hash}")

            except ValueError as e:
                st.error(f"Ошибка: {e}")
            except Exception as e:
                st.error(f"Произошла непредвиденная ошибка: {e}")
