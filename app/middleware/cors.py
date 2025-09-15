"""
CORS middleware для разрешения запросов с любых доменов.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def add_cors_middleware(app: FastAPI) -> None:
    """
    Добавляет CORS middleware к приложению FastAPI.
    
    Args:
        app: Экземпляр FastAPI приложения
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Разрешить запросы с любых доменов
        allow_credentials=True,
        allow_methods=["*"],  # Разрешить все HTTP методы
        allow_headers=["*"],  # Разрешить все заголовки
    )