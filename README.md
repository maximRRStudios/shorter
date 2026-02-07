# Shorter

Простой сервис для сокращения ссылок, написанный на Python с использованием FastAPI и SQLite.

## Требования

- Python >= 3.12
- FastAPI
- SQLite

## Установка

1. Склонируй репозиторий:
```bash
git clone https://github.com/maximRRStudios/shorter.git
cd shortener
```

2. Установи зависимости с помощью `UV`:
```bash
uv sync
```

## Запуск приложения

Запустить приложение можно с помощью uvicorn:
```bash
uv run uvicorn app:app --reload
```

После запуска можно перейти в Swagger UI: http://localhost:8000/docs

## Тестирование

Проект покрыт тестами с использованием `pytest`. Запустить тесты можно так:
```bash
uv run pytest
```
