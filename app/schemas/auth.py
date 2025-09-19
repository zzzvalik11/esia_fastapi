"""
Pydantic схемы для авторизации и аутентификации.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from enum import Enum


class ProviderType(str, Enum):
    """Типы провайдеров данных ЕСИА."""
    
    ESIA_OAUTH = "esia_oauth"
    EBS_OAUTH = "ebs_oauth"
    CPG_OAUTH = "cpg_oauth"


class ResponseType(str, Enum):
    """Типы ответов авторизации."""
    
    CODE = "code"


class GrantType(str, Enum):
    """Типы разрешений для получения токенов."""
    
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"


class AuthorizeRequest(BaseModel):
    """Схема запроса авторизации."""
    
    response_type: ResponseType = Field(ResponseType.CODE, description="Тип ответа")
    provider: ProviderType = Field(..., description="Провайдер данных")
    scope: str = Field(..., description="Области доступа")
    redirect_uri: Optional[HttpUrl] = Field(None, description="URI возврата")
    state: str = Field(..., description="Состояние запроса (UUID)")
    nonce: Optional[str] = Field(None, description="Nonce для предотвращения подделки (UUID)")


class TokenRequest(BaseModel):
    """Схема запроса токена доступа."""
    
    grant_type: GrantType = Field(..., description="Тип разрешения")
    redirect_uri: Optional[HttpUrl] = Field(None, description="URI возврата")
    code: Optional[str] = Field(None, description="Авторизационный код")
    refresh_token: Optional[str] = Field(None, description="Токен обновления")


class UserInfoRequest(BaseModel):
    """Схема запроса информации о пользователе."""
    
    scope: Optional[str] = Field(None, description="Конкретные области доступа")


class LogoutRequest(BaseModel):
    """Схема запроса выхода из системы."""
    
    redirect_uri: Optional[HttpUrl] = Field(None, description="URI возврата")
    state: Optional[str] = Field(None, description="Состояние запроса (UUID)")


class AuthorizeResponse(BaseModel):
    """Схема ответа авторизации."""
    
    authorization_url: str = Field(..., description="URL для перенаправления на авторизацию")
    state: str = Field(..., description="Состояние запроса")


class CallbackResponse(BaseModel):
    """Схема ответа callback после авторизации."""
    
    code: Optional[str] = Field(None, description="Авторизационный код")
    state: str = Field(..., description="Состояние запроса")
    error: Optional[str] = Field(None, description="Код ошибки")
    error_description: Optional[str] = Field(None, description="Описание ошибки")


class TokenResponse(BaseModel):
    """Схема ответа с токенами."""
    
    access_token: str = Field(..., description="Токен доступа")
    token_type: str = Field("Bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")
    refresh_token: Optional[str] = Field(None, description="Токен обновления")
    scope: str = Field(..., description="Области доступа")
    created_at: int = Field(..., description="Время создания токена")
    id_token: Optional[str] = Field(None, description="ID токен")


class LogoutResponse(BaseModel):
    """Схема ответа выхода из системы."""
    
    logout_url: str = Field(..., description="URL для выхода из ЕСИА")
    redirect_uri: str = Field(..., description="URI возврата после выхода")