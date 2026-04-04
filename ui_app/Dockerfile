# Использование легковесного образа Python
FROM python:3.12-slim

# Установка системных зависимостей (только самое необходимое)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install poetry

# Настройка рабочей директории
WORKDIR /app

# Отключение создания виртуальных окружений внутри контейнера
RUN poetry config virtualenvs.create false

# Копирование файлов зависимостей
COPY pyproject.toml ./

# Установка зависимостей (без dev-пакетов и без установки самого проекта)
RUN poetry install --no-interaction --no-ansi --no-root

# Копирование исходного кода
COPY src/ ./src/

# ВАЖНО: Указываем Python, что корень проекта находится в /app
ENV PYTHONPATH=/app

# Открытие порта Streamlit
EXPOSE 8501

# Команда запуска
ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
