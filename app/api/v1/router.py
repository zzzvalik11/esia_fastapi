"""
Главный роутер для API версии 1.
Объединяет все роуты приложения.
"""

from fastapi import APIRouter
from app.api.v1 import auth, users, organizations, web

# Создание главного роутера для API v1
api_router = APIRouter()

# Подключение роутеров
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(organizations.router)

# Подключение веб-интерфейса
web_router = APIRouter()
web_router.include_router(web.router)