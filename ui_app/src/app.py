import os
import time
import json
import streamlit as st
from web3 import Web3

from src.core.hashing import calculate_sha256, BlockchainServiceMock

# --- 1. Конфигурация страницы ---
st.set_page_config(
    page_title="ImmutableLog Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Вспомогательная функция для Web3 ---
def get_all_logs():
    """Считывает все сохраненные логи напрямую из смарт-контракта."""
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    BLOCKCHAIN_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "blockchain"))
    
    config_path = os.path.join(BLOCKCHAIN_DIR, "config.json")
    abi_path = os.path.join(BLOCKCHAIN_DIR, "abi.json")

    if not os.path.exists(config_path) or not os.path.exists(abi_path):
        st.error(f"Не найдены файлы конфигурации Web3!\nОжидаемый путь: {BLOCKCHAIN_DIR}")
        return []

    with open(config_path, "r") as f:
        config = json.load(f)
    with open(abi_path, "r") as f:
        abi = json.load(f)

    try:
        w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
        if not w3.is_connected():
            st.error("Нет подключения к локальному блокчейну (RPC URL недоступен).")
            return []

        contract = w3.eth.contract(address=config["contract_address"], abi=abi)
        total_logs = contract.functions.getLogsCount().call()
        
        logs = []
        for i in range(total_logs):
            log_data = contract.functions.auditTrail(i).call()
            logs.append({
                "Хэш файла (SHA-256)": log_data[0],
                "Timestamp (Блокчейн)": log_data[1]
            })
        return logs
    except Exception as e:
        st.error(f"Ошибка при работе с блокчейном: {e}")
        return []


# --- 2. Управление состоянием (Session State) ---
if "golden_hash" not in st.session_state:
    st.session_state.golden_hash = None
if "last_tx" not in st.session_state:
    st.session_state.last_tx = None

# Инициализируем сервис-заглушку для ЗАПИСИ (чтение уже реальное)
blockchain_service = BlockchainServiceMock()

# --- 3. Боковая панель ---
with st.sidebar:
    st.title("🛡️ ImmutableLog")
    st.info("Децентрализованная система аудита логов на базе технологии блокчейн.")

    st.header("Параметры системы")
    st.metric(label="Статус UI", value="Active", delta="Local")
    
    st.markdown("---")
    st.subheader("Данные из блокчейна")
    if st.button("🔄 Загрузить реестр логов", use_container_width=True):
        with st.spinner("Синхронизация с сетью..."):
            all_logs = get_all_logs()
            if all_logs:
                st.success(f"Найдено записей: {len(all_logs)}")
                st.dataframe(all_logs, use_container_width=True)
            else:
                st.warning("Смарт-контракт пока пуст.")

# --- 4. Основной интерфейс ---
st.title("Панель управления безопасностью")
st.markdown("---")

tab1, tab2 = st.tabs(["Регистрация лога", "Аудит целостности"])

# --- ВКЛАДКА 1: Регистрация нового лога ---
with tab1:
    st.header("Шаг 1: Регистрация эталонного файла")
    st.write("Загрузите оригинальный лог-файл. Его хэш будет сохранен в блокчейн как эталон.")

    uploaded_file_register = st.file_uploader(
        "Выберите лог-файл для регистрации (.txt)", type=["txt"], key="register_uploader"
    )

    if uploaded_file_register:
        try:
            file_bytes = uploaded_file_register.getvalue()
            log_hash = calculate_sha256(file_bytes)

            st.info(f"**Вычисленный SHA-256 хэш:** `{log_hash}`")

            if st.button("Записать хэш в блокчейн", key="register_button"):
                with st.spinner("Отправка транзакции в сеть..."):
                    tx_hash = blockchain_service.register_hash(log_hash)
                    time.sleep(1)

                st.success("**УСПЕХ!** Хэш зарегистрирован в блокчейне.")
                st.code(f"Хэш транзакции: {tx_hash}", language="bash")

                st.session_state.golden_hash = log_hash
                st.session_state.last_tx = tx_hash
                st.balloons()

        except Exception as e:
            st.error(f"Ошибка: {e}")

# --- ВКЛАДКА 2: Аудит целостности файла ---
with tab2:
    st.header("Шаг 2: Аудит целостности файла")

    if not st.session_state.golden_hash:
        st.warning("Сначала зарегистрируйте эталонный хэш на вкладке 'Регистрация лога'.")
    else:
        st.write("Теперь загрузите файл, который вы хотите проверить на предмет изменений.")
        st.code(f"Эталонный хэш из блокчейна: {st.session_state.golden_hash}", language="bash")

        uploaded_file_audit = st.file_uploader(
            "Выберите лог-файл для проверки (.txt)", type=["txt"], key="audit_uploader"
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

            except Exception as e:
                st.error(f"Ошибка: {e}")
