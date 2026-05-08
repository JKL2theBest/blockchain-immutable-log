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


def draw_divider() -> None:
    st.markdown('<div class="binary-divider"></div>', unsafe_allow_html=True)


def hash_log_line(line: str) -> str:
    return hashlib.sha256(line.strip().encode("utf-8")).hexdigest()


def extract_critical_logs(file_content: str) -> dict:
    critical_logs = {}
    for line in file_content.splitlines():
        if "SECURITY" in line or "admin" in line or "root" in line:
            h = hash_log_line(line)
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
        return BlockchainServiceMock()
    try:
        return RealBlockchainService(abi=abi)
    except Exception as e:
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
                    except Exception:
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

tab1, tab2 = st.tabs(["Регистрация событий", "Аудит инцидентов"])
with tab1:
    icon_header("Сбор критических событий", "file")
    uploaded_file_register = st.file_uploader(
        "Загрузите лог-файл (.txt)", type=["txt"], key="up_reg"
    )
    if uploaded_file_register:
        content = uploaded_file_register.getvalue().decode("utf-8")
        critical_logs = extract_critical_logs(content)
        if critical_logs:
            st.markdown(
                f"<div class='custom-alert'>Обнаружено критических событий: {len(critical_logs)}</div>",
                unsafe_allow_html=True,
            )
            st.json(critical_logs)
            if st.button("Записать в блокчейн"):
                try:
                    shadow_db = {}
                    if os.path.exists(SHADOW_DB_PATH):
                        with open(SHADOW_DB_PATH, "r") as f:
                            shadow_db = json.load(f)
                    progress_bar = st.progress(0)
                    for idx, (h, text) in enumerate(critical_logs.items()):
                        if h not in shadow_db:
                            blockchain_service.register_hash(h)
                            shadow_db[h] = text
                            time.sleep(2)
                        progress_bar.progress((idx + 1) / len(critical_logs))

                    with open(SHADOW_DB_PATH, "w") as f:
                        json.dump(shadow_db, f, indent=4, ensure_ascii=False)
                    st.markdown(
                        "<div class='custom-alert'>Данные защищены.</div>",
                        unsafe_allow_html=True,
                    )

                except Exception as e:
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
        "Загрузите журнал для проверки (.txt)", type=["txt"], key="up_aud"
    )
    if uploaded_audit:
        if st.button("Инициировать проверку", type="primary"):
            with st.spinner("Анализ криптографических следов..."):
                content = uploaded_audit.getvalue().decode("utf-8")
                file_hashes = set(extract_critical_logs(content).keys())
                shadow_db = {}
                if os.path.exists(SHADOW_DB_PATH):
                    with open(SHADOW_DB_PATH, "r") as f:
                        shadow_db = json.load(f)
                blockchain_hashes = set(shadow_db.keys())
                missing_hashes = blockchain_hashes - file_hashes
                if len(missing_hashes) == 0:
                    st.markdown(
                        "<div class='custom-alert'>Целостность журнала подтверждена.</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<div class='custom-alert custom-error'>Внимание: обнаружена компрометация журнала. Выявлено удаление записей.</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown("### Восстановленные фрагменты:")
                    for h in missing_hashes:
                        original_text = shadow_db.get(
                            h, "Не удалось восстановить текст"
                        )
                        st.markdown(
                            f"> <span class='shadow-text'>{original_text}</span>",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"Хэш-доказательство: {h}")
st.markdown(
    '<div style="margin-top:150px; opacity:0.1; text-align:center; font-family:monospace;">01011001 01001011 01000001</div>',
    unsafe_allow_html=True,
)
