FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

WORKDIR /app

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY src/ ./src/
COPY assets/ ./assets/
COPY .streamlit/ ./.streamlit/

ENV PYTHONPATH=/app

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.enableStaticServing=true", "--server.port=8501", "--server.address=0.0.0.0"]
