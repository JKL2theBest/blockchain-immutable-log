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

### 2. Запуск веб-интерфейса (Streamlit)
Для корректной работы модульных импортов используйте запуск через флаг `-m`:
```bash
python -m streamlit run src/app.py
```
Приложение откроется по адресу: `http://localhost:8501`

### 3. Запуск через Docker
Сборка и запуск всего модуля в изолированном контейнере:
```bash
docker-compose up --build
```

## Тестирование и Качество (AQA)
Проект покрыт тестами на двух уровнях: Unit (ядро) и Integration (UI).

- **Полный прогон тестов:** `pytest`
- **Проверка покрытия кода:** `pytest --cov=src`
