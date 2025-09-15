"""
Request timing middleware для измерения времени выполнения запросов.
"""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для измерения времени выполнения HTTP запросов.
    Логирует информацию о каждом запросе.
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Обрабатывает HTTP запрос и измеряет время выполнения.
        
        Args:
            request: HTTP запрос
            call_next: Следующий обработчик в цепочке
            
        Returns:
            Response: HTTP ответ с добавленным заголовком времени выполнения
        """
        start_time = time.time()
        
        # Логирование входящего запроса
        logger.info(
            f"Входящий запрос: {request.method} {request.url.path} "
            f"от {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            # Выполнение запроса
            response = await call_next(request)
            
            # Вычисление времени выполнения
            process_time = time.time() - start_time
            
            # Добавление заголовка с временем выполнения
            response.headers["X-Process-Time"] = str(process_time)
            
            # Логирование результата
            logger.info(
                f"Запрос завершен: {request.method} {request.url.path} "
                f"- Статус: {response.status_code} "
                f"- Время: {process_time:.4f}s"
            )
            
            return response
            
        except Exception as e:
            # Логирование ошибки
            process_time = time.time() - start_time
            logger.error(
                f"Ошибка при обработке запроса: {request.method} {request.url.path} "
                f"- Ошибка: {str(e)} "
                f"- Время: {process_time:.4f}s"
            )
            raise