"""
Настройка подключения к базе данных.
Использует SQLAlchemy 2.0 с асинхронным подходом.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Создание движка базы данных
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Генератор для получения сессии базы данных.
    Используется как зависимость в FastAPI.
    
    Yields:
        Session: Сессия базы данных
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()