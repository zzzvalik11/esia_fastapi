"""
Конфигурация приложения.
Управляет всеми настройками через переменные окружения.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Настройки приложения с валидацией через Pydantic."""
    
    # Настройки базы данных
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = "password"
    db_name: str = "ESIA_gateway"
    
    # Настройки ЕСИА
    esia_demo_url: str = "https://demo.gate.esia.pro"
    esia_client_id: str = ""
    esia_client_secret: str = ""
    esia_redirect_uri: str = ""
    
    # Настройки приложения
    secret_key: str = "your-secret-key-here"
    debug: bool = False
    log_level: str = "INFO"
    
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