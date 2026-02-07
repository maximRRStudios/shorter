import datetime
from urllib.parse import urlparse
from uuid import uuid4
from segno import make_qr

from io import BytesIO
import requests

from repository import UrlRepository

class UrlService:
    def __init__(self, repository: UrlRepository):
        self.repository = repository

    def __validate_url_format(self, url: str) -> bool:
        """
        Проверяет, что URL имеет корректный формат.
        """
        parsed_url = urlparse(url)
        return all([parsed_url.scheme, parsed_url.netloc])

    def __check_url_availability(self, url: str) -> bool:
        """
        Проверяет доступность ресурса (статус 200).
        """
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def shorten_url(self, original_url: str) -> str:
        """
        Сокращает URL, предварительно проверив его формат и доступность.
        """
        if not self.__validate_url_format(original_url):
            raise ValueError("Некорректный URL")

        if not self.__check_url_availability(original_url):
            raise ValueError("Сайт недоступен")

        short_code = str(uuid4())[:8]
        success = self.repository.add_url(original_url, short_code)
        if success:
            return short_code
        else:
            raise ValueError("Ошибка при сокращении URL")

    def handle_redirect(self, short_code: str) -> str:
        """
        Возвращает оригинальный URL по короткому коду.
        """
        url_data = self.repository.get_url_by_short_code(short_code)
        if url_data:
            current_time = datetime.datetime.now(datetime.UTC)
            # Проверяем срок действия ссылки
            if current_time <= datetime.datetime.fromisoformat(url_data["expires_at"]):
                return url_data["original_url"]
            else:
                raise ValueError("Срок действия ссылки истёк")
        return None

    def generate_qr_code(self, short_code: str) -> bytes:
        """
        Генерирует QR-код для заданного короткого кода.
        """
        url_data = self.repository.get_url_by_short_code(short_code)
        if url_data:
            original_url = url_data["original_url"]
            qr = make_qr(original_url)
            buffer = BytesIO()
            qr.save(buffer, kind="png")
            buffer.seek(0)
            return buffer.read()
        else:
            print('asdaaaa')
            raise ValueError("Короткий код не найден")
