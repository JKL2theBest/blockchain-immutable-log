import os
import json
import hashlib
import time
import base64
from typing import Any

import streamlit as st
from src.core.hashing import (
    BlockchainServiceMock,
    RealBlockchainService,
    BlockchainService,
)


def get_base64(path: str) -> str:
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "assets")
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
SHADOW_DB_PATH = os.path.join(PROJECT_ROOT, "shadow_db.json")
BLOCKCHAIN_DIR = os.path.join(PROJECT_ROOT, "blockchain")

font_b64 = get_base64(os.path.join(ASSETS_DIR, "GlitchGoblin.ttf"))
logo_b64 = get_base64(os.path.join(ASSETS_DIR, "logo.png"))
chain_b64 = get_base64(os.path.join(ASSETS_DIR, "chain.png"))
flower_b64 = get_base64(os.path.join(ASSETS_DIR, "flower.png"))

if not os.path.exists(SHADOW_DB_PATH):
    with open(SHADOW_DB_PATH, "w") as f:
        json.dump({}, f)

st.set_page_config(page_title="ImmutableLog", layout="wide")

custom_css = f"""
<style>
    @font-face {{
        font-family: 'Glitch Goblin';
        src: url(data:font/ttf;base64,{font_b64}) format('truetype');
    }}
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stMarkdown, p, span, label, li, button {{
        font-family: 'JetBrains Mono', monospace !important;
        color: #DAF1DD !important;
    }}
    h1, h2, h3, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, .glitch-text {{
        font-family: 'Glitch Goblin', sans-serif !important;
        color: #8EB69C !important;
        text-transform: none !important;
        letter-spacing: 2px !important;
        font-weight: normal !important;
    }}
    span[data-testid="stIconMaterial"], .material-symbols-rounded {{
        font-family: 'Material Symbols Rounded' !important;
    }}
    header, [data-testid="stHeader"], [data-testid="stSidebarCollapseButton"] {{
        display: none !important;
    }}
    .chain-divider {{
        height: 24px;
        background-image: url(data:image/png;base64,{chain_b64});
        background-repeat: round !important;
        background-size: auto 100% !important;
        margin: 25px 0;
        opacity: 0.6;
    }}
    .fixed-flower {{
        position: fixed; bottom: 25px; left: 25px; width: 65px;
        opacity: 0.5; z-index: 10000; pointer-events: none;
    }}
    .sidebar-logo-container {{
        display: flex; flex-direction: column; align-items: center; margin-bottom: 2rem;
    }}
    .sidebar-logo-container img {{
        width: 140px; filter: drop-shadow(0 0 15px rgba(142, 182, 156, 0.4));
    }}
    .header-with-icon {{ display: flex; align-items: center; gap: 15px; margin: 1.5rem 0; }}
    .header-with-icon img {{ width: 42px; }}
    .stTabs button p {{
        font-family: 'JetBrains Mono', monospace !important;
    }}
    
    .custom-alert {{
        padding: 12px !important;
        border: 1px solid #8EB69C !important;
        background-color: rgba(142, 182, 156, 0.1) !important; /* Прозрачный хвойный */
        color: #DAF1DD !important;
        border-radius: 4px !important;
        margin-bottom: 20px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }}
    .custom-error {{
        border-color: #ff4b4b !important;
        background-color: rgba(255, 75, 75, 0.1) !important;
    }}
</style>

<img src="data:image/png;base64,{flower_b64}" class="fixed-flower">
"""
st.markdown(custom_css, unsafe_allow_html=True)


def icon_header(text: str, icon_name: str, is_main: bool = False) -> None:
    icon_path = os.path.join(ASSETS_DIR, f"{icon_name}.png")
    icon_b64 = get_base64(icon_path)
    tag = "h1" if is_main else "h2"
    html = f"""
    <div class="header-with-icon">
        <img src="data:image/png;base64,{icon_b64}">
        <{tag} class="glitch-text" style="margin:0; font-family: 'Glitch Goblin', sans-serif !important;">{text}</{tag}>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def hash_log_line(filename: str, line: str) -> str:
    """Генерирует хэш, привязанный к имени файла."""
    payload = f"{filename}:{line.strip()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def extract_critical_logs(file_content: str, filename: str) -> dict[str, str]:
    """Извлекает критические логи с привязкой к имени файла."""
    critical_logs = {}
    keywords = ["security", "admin", "root"]
    for line in file_content.splitlines():
        if any(k in line.lower() for k in keywords):
            h = hash_log_line(filename, line)
            critical_logs[h] = line.strip()
    return critical_logs


@st.cache_resource
def load_abi() -> list[Any] | None:
    abi_path = os.path.join(BLOCKCHAIN_DIR, "abi.json")
    if not os.path.exists(abi_path):
        return None
    with open(abi_path, "r") as f:
        return json.load(f)


def initialize_blockchain_service() -> BlockchainService:
    abi = load_abi()
    if not abi:
        st.sidebar.markdown(
            "<div class='custom-alert custom-error'>КРИТИЧЕСКАЯ ОШИБКА: ABI не найден!</div>",
            unsafe_allow_html=True,
        )
        return BlockchainServiceMock()
    try:
        return RealBlockchainService(abi=abi)
    except Exception as e:
        st.sidebar.markdown(
            "<div class='custom-alert custom-error' style='text-align:center;'>"
            "<b>СЕТЬ НЕДОСТУПНА</b><br>"
            "<span style='font-size: 0.8em;'>Связь с контрактом потеряна. Активирован режим локальной эмуляции (Mock RAM).</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        print(f"Fallback to Mock: {e}")
        return BlockchainServiceMock()


if "blockchain_service" not in st.session_state:
    st.session_state.blockchain_service = initialize_blockchain_service()
blockchain_service = st.session_state.blockchain_service

with st.sidebar:
    st.markdown(
        f"""
            <div class="sidebar-logo-container">
                <img src="data:image/png;base64,{logo_b64}">
                <div class="glitch-text" style="font-size: 22px; margin-top:15px; font-family: 'Glitch Goblin' !important;">IMMUTABLELOG</div>
            </div>
            """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='text-align:center; font-size: 14px; opacity:0.8;'>Децентрализованная система аудита логов    </p>",
        unsafe_allow_html=True,
    )

    service_status = (
        "ONLINE (GANACHE DEVCHAIN)"
        if isinstance(blockchain_service, RealBlockchainService)
        else "OFFLINE (MOCK RAM)"
    )
    color = "#8EB69C" if "ONLINE" in service_status else "#ff4b4b"
    st.markdown(
        f"<div style='text-align:center; font-family:monospace; color:{color}; border: 1px dashed {color}; padding: 8px; margin-bottom: 15px; background-color: rgba(0,0,0,0.2);'>"
        f"STATUS: {service_status}"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="chain-divider"></div>', unsafe_allow_html=True)

    st.subheader("Реестр блокчейна")

    if st.button("Синхронизировать с сетью", use_container_width=True):
        try:
            with st.spinner("Синхронизация..."):
                raw_logs = blockchain_service.get_all_logs()

            if raw_logs:
                from datetime import datetime

                formatted_data = []

                for log in raw_logs:
                    try:
                        h = log.get("Хэш файла (SHA-256)")
                        t = log.get("Timestamp (Блокчейн)")

                        if h and t:
                            formatted_data.append(
                                {
                                    "Событие (SHA-256)": str(h),
                                    "Дата и время": datetime.fromtimestamp(int(t)),
                                }
                            )
                    except (ValueError, KeyError, TypeError):
                        continue

                if formatted_data:
                    st.markdown(
                        f"<div class='custom-alert'>Извлечено записей: {len(formatted_data)}</div>",
                        unsafe_allow_html=True,
                    )
                    st.dataframe(
                        formatted_data,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Событие (SHA-256)": st.column_config.TextColumn(
                                "Событие (SHA-256)", width="large"
                            ),
                            "Дата и время": st.column_config.DatetimeColumn(
                                "Дата и время", format="DD.MM.YYYY, HH:mm:ss"
                            ),
                        },
                    )
                else:
                    st.markdown(
                        "<div class='custom-alert custom-error'>Данные не соответствуют формату.</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    "<div class='custom-alert'>Реестр пуст.</div>",
                    unsafe_allow_html=True,
                )
        except Exception as e:
            st.markdown(
                f"<div class='custom-alert custom-error'>Ошибка: {e}</div>",
                unsafe_allow_html=True,
            )

    flower_b64 = get_base64(os.path.join(ASSETS_DIR, "flower.png"))
    st.markdown(
        f'<div style="text-align:center; opacity:0.3; margin-top:50px;"><img src="data:image/png;base64,{flower_b64}" width="30"></div>',
        unsafe_allow_html=True,
    )


icon_header("Панель аудитора", "lock", is_main=True)
st.markdown('<div class="chain-divider"></div>', unsafe_allow_html=True)

# Инициализация состояния базы данных
if "shadow_db" not in st.session_state:
    if os.path.exists(SHADOW_DB_PATH):
        with open(SHADOW_DB_PATH, "r", encoding="utf-8") as f:
            try:
                st.session_state.shadow_db = json.load(f)
            except json.JSONDecodeError:
                st.session_state.shadow_db = {}
    else:
        with open(SHADOW_DB_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
        st.session_state.shadow_db = {}

tab1, tab2 = st.tabs(["Регистрация событий", "Аудит инцидентов"])
with tab1:
    icon_header("Сбор критических событий", "file")
    uploaded_file_register = st.file_uploader(
        "Загрузите лог-файл", type=["txt"], key="up_reg"
    )
    if uploaded_file_register:
        content = uploaded_file_register.getvalue().decode("utf-8")
        filename = uploaded_file_register.name

        critical_logs = extract_critical_logs(content, filename)

        if critical_logs:
            st.markdown(
                f"<div class='custom-alert'>Обнаружено критических событий: {len(critical_logs)}</div>",
                unsafe_allow_html=True,
            )
            st.json(critical_logs)

            if st.button("Записать в блокчейн"):
                progress_container = st.empty()
                msg_container = st.empty()

                try:
                    whole_file_hash = hashlib.sha256(content.encode()).hexdigest()
                    seal_id = f"SEAL:{filename}:{whole_file_hash}"

                    if filename not in st.session_state.shadow_db:
                        st.session_state.shadow_db[filename] = {
                            "seal": None,
                            "events": {},
                        }

                    needs_seal = st.session_state.shadow_db[filename]["seal"] != seal_id
                    new_events = {
                        h: txt
                        for h, txt in critical_logs.items()
                        if h not in st.session_state.shadow_db[filename]["events"]
                    }

                    total_steps = (1 if needs_seal else 0) + len(new_events)

                    if total_steps == 0:
                        st.info("Все данные этого файла уже зафиксированы в блокчейне.")
                        st.stop()

                    current_step = 0

                    pbar = progress_container.progress(
                        0, text="Подготовка транзакций..."
                    )

                    if needs_seal:
                        msg_container.info(f"Фиксация мастер-хэша: `{filename}`")
                        blockchain_service.register_hash(seal_id)
                        st.session_state.shadow_db[filename]["seal"] = seal_id
                        current_step += 1
                        pbar.progress(
                            current_step / total_steps,
                            text=f"Выполнено: {current_step}/{total_steps}",
                        )
                        time.sleep(2.1)

                    for h, text in new_events.items():
                        msg_container.info(f"Регистрация события: `{h[:8]}...`")
                        blockchain_service.register_hash(h)
                        st.session_state.shadow_db[filename]["events"][h] = text
                        current_step += 1
                        pbar.progress(
                            current_step / total_steps,
                            text=f"Выполнено: {current_step}/{total_steps}",
                        )
                        time.sleep(2.1)

                    msg_container.empty()
                    progress_container.empty()

                    with open(SHADOW_DB_PATH, "w", encoding="utf-8") as f:
                        json.dump(
                            st.session_state.shadow_db, f, indent=4, ensure_ascii=False
                        )

                    st.success(
                        "Все криптографические якоря успешно зафиксированы в блокчейне."
                    )

                except Exception as e:
                    progress_container.empty()
                    msg_container.empty()

                    error_msg = str(e)
                    if "revert" in error_msg or "execution reverted" in error_msg:
                        st.markdown(
                            """
                                <div class='custom-alert custom-error'>
                                    <b>Блокировка доступа</b><br>
                                    Смарт-контракт отклонил транзакцию. Ваш приватный ключ не принадлежит авторизованному агенту.<br>
                                    <i>Причина: OwnableUnauthorizedAccount</i>
                                </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.error(f"Техническая ошибка: {e}")
with tab2:
    icon_header("Проверка целостности", "file_search")
    uploaded_audit = st.file_uploader(
        "Загрузите журнал для проверки", type=["txt"], key="up_aud"
    )
    if uploaded_audit:
        if st.button("Инициировать проверку", type="primary"):
            with st.spinner("Анализ криптографических следов..."):
                content = uploaded_audit.getvalue().decode("utf-8")
                filename = uploaded_audit.name
                current_whole_hash = hashlib.sha256(content.encode()).hexdigest()
                current_file_hashes = set(
                    extract_critical_logs(content, filename).keys()
                )

                try:
                    onchain_logs = [
                        log["Хэш файла (SHA-256)"]
                        for log in blockchain_service.get_all_logs()
                    ]
                except Exception:
                    onchain_logs = []

                seal_id = f"SEAL:{filename}:{current_whole_hash}"
                seal_exists = seal_id in onchain_logs

                if not seal_exists:
                    st.error(
                        "КРИТИЧЕСКАЯ ОШИБКА: Общий хэш файла не совпадает с эталоном в блокчейне!"
                    )
                else:
                    st.success(
                        "Мастер-хэш подтвержден: структура файла соответствует оригиналу."
                    )

                missing_hashes = []
                if filename in st.session_state.shadow_db:
                    file_data = st.session_state.shadow_db[filename]
                    for h in file_data["events"].keys():
                        if h in onchain_logs and h not in current_file_hashes:
                            missing_hashes.append(h)

                if len(missing_hashes) > 0:
                    st.markdown(
                        f"<div class='custom-alert custom-error'>Выявлено удаление критических записей: {len(missing_hashes)}</div>",
                        unsafe_allow_html=True,
                    )
                    for h in missing_hashes:
                        orig_text = st.session_state.shadow_db[filename]["events"].get(
                            h
                        )
                        st.markdown(f"> `{orig_text}`")
st.markdown(
    '<div style="margin-top:150px; opacity:0.1; text-align:center; font-family:monospace;">01011001 01001011 01000001</div>',
    unsafe_allow_html=True,
)
