import os
import time
import json
import streamlit as st

# Корректные импорты из нашего модуля core
from src.core.hashing import (
    calculate_sha256,
    BlockchainServiceMock,
    RealBlockchainService,
)

# --- 1. Конфигурация страницы ---
st.set_page_config(
    page_title="ImmutableLog Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- 2. Функции-хелперы для загрузки и инициализации ---


@st.cache_resource
def load_blockchain_config():
    """Загружает ABI и config, кэширует результат."""
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    BLOCKCHAIN_DIR = os.path.abspath(
        os.path.join(CURRENT_DIR, "..", "..", "blockchain")
    )
    config_path = os.path.join(BLOCKCHAIN_DIR, "config.json")
    abi_path = os.path.join(BLOCKCHAIN_DIR, "abi.json")

    if not os.path.exists(config_path) or not os.path.exists(abi_path):
        st.error(
            f"Не найдены файлы конфигурации Web3! Ожидаемый путь: {BLOCKCHAIN_DIR}"
        )
        return None, None

    with open(config_path, "r") as f:
        config = json.load(f)
    with open(abi_path, "r") as f:
        abi = json.load(f)
    return config, abi


def initialize_blockchain_service():
    """Инициализирует сервис для работы с блокчейном (реальный или мок)."""
    config, abi = load_blockchain_config()
    if not config or not abi:
        st.warning("Конфиги не загружены. Используется Mock-сервис.")
        return BlockchainServiceMock()

    try:
        # Проверяем, есть ли реальные значения в конфиге
        if "<" in config.get("rpc_url", "") or "<" in config.get(
            "contract_address", ""
        ):
            raise ValueError(
                "В config.json не указаны реальные rpc_url или contract_address."
            )

        service = RealBlockchainService(
            rpc_url=config["rpc_url"],
            contract_address=config["contract_address"],
            abi=abi,
        )
        # st.sidebar.success("Подключено к блокчейну")
        return service
    except Exception as e:
        st.sidebar.warning(
            f"Реальный сервис недоступен. Используется Mock. Ошибка: {e}"
        )
        return BlockchainServiceMock()


# --- 3. Управление состоянием (Session State) ---
if "blockchain_service" not in st.session_state:
    st.session_state.blockchain_service = initialize_blockchain_service()
if "golden_hash" not in st.session_state:
    st.session_state.golden_hash = None
if "last_tx" not in st.session_state:
    st.session_state.last_tx = None

# Получаем сервис из состояния сессии
blockchain_service = st.session_state.blockchain_service


# --- 4. Боковая панель ---
with st.sidebar:
    st.title("🛡️ ImmutableLog")
    st.info("Децентрализованная система аудита логов на базе технологии блокчейн.")
    st.header("Параметры системы")

    # Показываем, какой сервис используется
    service_status = (
        "Real" if isinstance(blockchain_service, RealBlockchainService) else "Mock"
    )
    st.metric(label="Статус сервиса", value=service_status)

    st.markdown("---")
    st.subheader("Данные из блокчейна")
    if st.button("🔄 Загрузить реестр логов", use_container_width=True):
        try:
            with st.spinner("Синхронизация с сетью..."):
                all_logs = blockchain_service.get_all_logs()

            if all_logs:
                st.success(f"Найдено записей: {len(all_logs)}")
                st.dataframe(all_logs, use_container_width=True, hide_index=True)
            else:
                st.warning("Смарт-контракт пока пуст.")

        except Exception as e:
            st.error(f"Ошибка при чтении из блокчейна: {e}")


# --- 5. Основной интерфейс ---
st.title("Панель управления безопасностью")
st.markdown("---")

tab1, tab2 = st.tabs(["Регистрация лога", "Аудит целостности"])

# --- ВКЛАДКА 1: Регистрация нового лога ---
with tab1:
    st.header("Шаг 1: Регистрация эталонного файла")
    st.write(
        "Загрузите оригинальный лог-файл. Его хэш будет сохранен в блокчейн как эталон."
    )

    uploaded_file_register = st.file_uploader(
        "Выберите лог-файл для регистрации (.txt)",
        type=["txt"],
        key="register_uploader",
    )

    if uploaded_file_register:
        try:
            file_bytes = uploaded_file_register.getvalue()
            log_hash = calculate_sha256(file_bytes)
            st.info(f"**Вычисленный SHA-256 хэш:** `{log_hash}`")

            if st.button("Записать хэш в блокчейн", key="register_button"):
                with st.spinner("Отправка транзакции в сеть..."):
                    tx_hash = blockchain_service.register_hash(log_hash)

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
        st.warning(
            "Сначала зарегистрируйте эталонный хэш на вкладке 'Регистрация лога'."
        )
    else:
        st.write(
            "Теперь загрузите файл, который вы хотите проверить на предмет изменений."
        )
        st.code(
            f"Эталонный хэш из блокчейна: {st.session_state.golden_hash}",
            language="bash",
        )

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
                        st.success(
                            "✅ УСПЕХ: Файл не был изменен. Целостность подтверждена."
                        )
                    else:
                        st.error(
                            "🚨 АЛЕРТ: Файл был скомпрометирован! Хэши не совпадают."
                        )
                        with st.expander("Показать детали расхождения"):
                            st.text(
                                f"Ожидаемый хэш (из блокчейна): {st.session_state.golden_hash}"
                            )
                            st.text(f"Фактический хэш (проверяемый файл): {audit_hash}")
            except Exception as e:
                st.error(f"Ошибка: {e}")
