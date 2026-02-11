import pytest
from fastapi.testclient import TestClient
from shorter.app import app, get_service
from shorter.repository import UrlRepository
from shorter.service import UrlService

# Заглушка репозитория для тестирования
@pytest.fixture(scope="function")
def test_repository():
    # Создаем временную базу данных для тестов
    db_path = ":memory:"
    repository = UrlRepository(db_path)
    yield repository
    repository.conn.close()

# Клиент для тестирования
@pytest.fixture
def test_client(test_repository):
    # Создаем сервис и передаем тестовый репозиторий
    service = UrlService(test_repository)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_service] = lambda: service
    return TestClient(app)

# Тест укоротителя URL
def test_shorten_valid_url(test_client):
    valid_url = "https://example.com"
    response = test_client.post("/shorten/", json={"long_url": valid_url})
    assert response.status_code == 200
    assert "shortened_url" in response.json()

# Тест на некорректный URL
def test_shorten_invalid_url(test_client):
    invalid_url = "not_a_valid_url"
    response = test_client.post("/shorten/", json={"long_url": invalid_url})
    assert response.status_code == 400
    assert "detail" in response.json()

# Тест редиректа по корректному короткому коду
def test_redirect_valid_short_code(test_client):
    valid_url = "https://example.com"
    response = test_client.post("/shorten/", json={"long_url": valid_url})
    short_code = response.json()["shortened_url"].split("/")[1]
    redirect_response = test_client.get(f"/{short_code}/", follow_redirects=False)
    assert redirect_response.status_code == 301
    assert redirect_response.headers["location"] == valid_url

# Тест редиректа по неверному короткому коду
def test_redirect_invalid_short_code(test_client):
    invalid_code = "nonexistent"
    response = test_client.get(f"/{invalid_code}/")
    assert response.status_code == 404
    assert "detail" in response.json()

# Тест успешной генерации QR-кода
def test_generate_qr_code_success(test_client):
    valid_url = "https://example.com"
    response = test_client.post("/shorten/", json={"long_url": valid_url})
    short_code = response.json()["shortened_url"].split("/")[1]
    response = test_client.get(f"/qr_code/{short_code}/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0

# Тест на ошибку при отсутствии короткого кода
def test_generate_qr_code_not_found(test_client):
    response = test_client.get("/qr_code/nonexistent/")
    assert response.status_code == 404
    assert "detail" in response.json()

# Тест на недопустимый короткий код
def test_generate_qr_code_invalid_short_code(test_client):
    response = test_client.get("/qr_code//")  # Пустой короткий код
    assert response.status_code == 404
    assert "detail" in response.json()
