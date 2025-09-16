"""
Конфигурация приложения.
Управляет всеми настройками через переменные окружения.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения с валидацией через Pydantic."""
    
    # Настройки базы данных
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "password")
    db_name: str = os.getenv("DB_NAME", "ESIA_gateway")
    
    # Настройки ЕСИА
    esia_demo_url: str = os.getenv("ESIA_DEMO_URL", "https://demo.gate.esia.pro")
    esia_client_id: str = os.getenv("ESIA_CLIENT_ID", "")
    esia_client_secret: str = os.getenv("ESIA_CLIENT_SECRET", "")
    esia_redirect_uri: str = os.getenv("ESIA_REDIRECT_URI", "")
    
    # Настройки приложения
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Настройки API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "ЕСИА Gateway API"
    version: str = "1.0.0"
    
    @property
    def database_url(self) -> str:
        """Формирует URL подключения к базе данных из составных частей."""
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings()