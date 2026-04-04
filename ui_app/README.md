# 🛡️ ImmutableLog - UI & Audit Module

Этот модуль представляет собой интерфейс системы аудита логов на базе блокчейна. 

## 🚀 Стек технологий
- **Python 3.12+**
- **Streamlit**: Фреймворк для UI/Dashboard
- **Poetry**: Управление зависимостями и окружением
- **Pytest + Streamlit AppTest**: Автоматизированное тестирование
- **Docker & Docker-compose**: Контейнеризация

## 🛠️ Установка и запуск

### 1. Подготовка окружения (Poetry)
1. Убедитесь, что у вас установлен Poetry: `pip install poetry`
2. Находясь в папке `ui_app/`, установите зависимости:
   ```bash
   poetry install
   ```
3. Активируйте виртуальное окружение:
   ```bash
   .venv\Scripts\activate  # Для Windows
   # или
   source .venv/bin/activate # Для Linux/macOS
   ```

### 2. Быстрая проверка логики (Standalone Test)
Вы можете протестировать ядро системы (хэширование и Mock-сервис) без запуска UI:
```bash
python -m src.core.hashing
```
*Этот скрипт проверит расчет SHA-256 и имитирует отправку транзакции в консоли.*

### 3. Запуск веб-интерфейса (Streamlit)
Для корректной работы модульных импортов используйте запуск через флаг `-m`:
```bash
python -m streamlit run src/app.py
```
Приложение откроется по адресу: `http://localhost:8501`

### 4. Запуск через Docker (Enterprise way)
Сборка и запуск всего модуля в изолированном контейнере:
```bash
docker-compose up --build
```

## 🧪 Тестирование и Качество (AQA)
Проект покрыт тестами на двух уровнях: Unit (ядро) и Integration (UI).

- **Полный прогон тестов:** `pytest`
- **Проверка покрытия кода:** `pytest --cov=src`

## 📂 Структура папки
- `src/core/hashing.py`: Бизнес-логика (расчет SHA-256, мок-сервис блокчейна).
- `src/app.py`: Точка входа в UI Streamlit (Dashboard).
- `tests/fixtures/`: Эталонные (`original_log.txt`) и измененные (`compromised_log.txt`) файлы для тестов.
- `Dockerfile` & `docker-compose.yml`: Конфигурация контейнеризации.
