# Shorter

Простой сервис для сокращения ссылок, написанный на Python с использованием FastAPI и SQLite.

## Требования

- Python >= 3.12
- FastAPI
- SQLite (включен в стандартную поставку Python)

## Установка

1. Склонируй репозиторий:
```bash
git clone https://github.com/your_username/shorter.git
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

## Тестирование

Проект покрыт тестами с использованием `pytest`. Запустить тесты можно так:
```bash
uv run pytest
```
