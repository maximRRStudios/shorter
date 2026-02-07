import datetime
import logging
from typing import Optional, Dict
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UrlRepository:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_urls_table()

    def create_urls_table(self):
        """
        Инициализация БД
        """
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_url TEXT NOT NULL,
                    short_code TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                );
            ''')

    def add_url(self, original_url: str, short_code: str) -> bool:
        """
        Добавляем URL в БД
        """
        with self.conn:
            try:
                now = datetime.datetime.now(datetime.UTC)
                expires_at = now + datetime.timedelta(days=7)  # Срок действия — 7 дней

                # Добавляем запись в базу данных
                self.conn.execute("""
                    INSERT INTO urls (original_url, short_code, created_at, expires_at)
                    VALUES (:original_url, :short_code, :created_at, :expires_at)
                """, {
                    "original_url": original_url,
                    "short_code": short_code,
                    "created_at": now.isoformat(),
                    "expires_at": expires_at.isoformat()
                })
                self.conn.commit()
                return True
            except sqlite3.Error as e:
                logger.error(f"Ошибка при добавлении URL: {e}")
                return False

    def get_url_by_short_code(self, short_code: str) -> Optional[Dict]:
        """
        Получаем исходный URL по коороткому коду
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM urls WHERE short_code = :short_code", {"short_code": short_code})
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))
        return None
