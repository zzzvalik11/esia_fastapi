"""
Пользовательские исключения для приложения.
Обеспечивает централизованную обработку ошибок.
"""

from typing import Any, Dict, Optional


class ESIAGatewayException(Exception):
    """Базовое исключение для приложения ЕСИА Gateway."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(ESIAGatewayException):
    """Ошибка аутентификации."""
    
    def __init__(self, message: str = "Ошибка аутентификации", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 401, details)


class AuthorizationError(ESIAGatewayException):
    """Ошибка авторизации."""
    
    def __init__(self, message: str = "Недостаточно прав доступа", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 403, details)


class ValidationError(ESIAGatewayException):
    """Ошибка валидации данных."""
    
    def __init__(self, message: str = "Ошибка валидации данных", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 422, details)


class NotFoundError(ESIAGatewayException):
    """Ресурс не найден."""
    
    def __init__(self, message: str = "Ресурс не найден", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 404, details)


class ExternalServiceError(ESIAGatewayException):
    """Ошибка внешнего сервиса."""
    
    def __init__(self, message: str = "Ошибка внешнего сервиса", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 502, details)


class ESIAServiceError(ExternalServiceError):
    """Ошибка сервиса ЕСИА."""
    
    def __init__(self, message: str = "Ошибка сервиса ЕСИА", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class DatabaseError(ESIAGatewayException):
    """Ошибка базы данных."""
    
    def __init__(self, message: str = "Ошибка базы данных", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 503, details)


class ConfigurationError(ESIAGatewayException):
    """Ошибка конфигурации."""
    
    def __init__(self, message: str = "Ошибка конфигурации", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)