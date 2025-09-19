"""
Главный файл FastAPI приложения.
Настройка и запуск сервера.
"""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import ESIAGatewayException
from app.middleware.cors import add_cors_middleware
from app.middleware.timing import RequestTimingMiddleware
from app.api.v1.router import api_router, web_router

# Настройка логирования
logger = setup_logging()

# Создание приложения FastAPI
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="API для работы с ЕСИА шлюзом",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# Добавление middleware
add_cors_middleware(app)
app.add_middleware(RequestTimingMiddleware)

# Добавление middleware для доверенных хостов (в продакшене)
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # В продакшене указать конкретные домены
    )

# Подключение роутеров
app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(web_router)  # Веб-интерфейс без префикса


@app.exception_handler(ESIAGatewayException)
async def esia_gateway_exception_handler(request: Request, exc: ESIAGatewayException):
    """
    Обработчик пользовательских исключений приложения.
    
    Args:
        request: HTTP запрос
        exc: Исключение приложения
        
    Returns:
        JSON ответ с информацией об ошибке
    """
    logger.error(f"Ошибка приложения: {exc.message} - {exc.details}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Обработчик HTTP исключений.
    
    Args:
        request: HTTP запрос
        exc: HTTP исключение
        
    Returns:
        JSON ответ с информацией об ошибке
    """
    logger.error(f"HTTP ошибка: {exc.status_code} - {exc.detail}")
    
    # Если detail уже является словарем, используем его как есть
    if isinstance(exc.detail, dict):
        content = exc.detail
        content["status_code"] = exc.status_code
    else:
        content = {
            "error": "HTTP Error",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Обработчик общих исключений.
    
    Args:
        request: HTTP запрос
        exc: Исключение
        
    Returns:
        JSON ответ с информацией об ошибке
    """
    logger.error(f"Неожиданная ошибка: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=400,
        content={
            "error": "Unexpected Error",
            "message": "Произошла неожиданная ошибка при обработке запроса",
            "status_code": 400
        }
    )


@app.get("/", tags=["Система"])
async def root():
    """
    Корневой эндпоинт для проверки работоспособности API.
    
    Returns:
        Информация о статусе API
    """
    return {
        "message": "ЕСИА Gateway API работает",
        "version": settings.version,
        "debug": settings.debug
    }


@app.get("/health", tags=["Система"])
async def health_check():
    """
    Проверка состояния здоровья приложения.
    
    Returns:
        Статус здоровья системы
    """
    return {
        "status": "healthy",
        "version": settings.version,
        "timestamp": "2025-01-27T12:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Запуск {settings.project_name} v{settings.version}")
    logger.info(f"Режим отладки: {settings.debug}")
    logger.info(f"URL базы данных: {settings.database_url}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )