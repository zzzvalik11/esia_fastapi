"""
Pydantic схемы для пользователей.
Обеспечивают валидацию и сериализацию данных пользователей.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    """Базовая схема пользователя с общими полями."""
    
    esia_uid: str = Field(..., description="UID пользователя в ЕСИА")
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    middle_name: Optional[str] = Field(None, description="Отчество пользователя")
    trusted: Optional[bool] = Field(False, description="Подтвержденная учетная запись")
    status: Optional[str] = Field(None, description="Статус пользователя в ЕСИА")


class UserCreate(UserBase):
    """Схема для создания пользователя."""
    
    verifying: Optional[bool] = Field(False, description="Процесс верификации")
    r_id_doc: Optional[int] = Field(None, description="ID документа в ЕСИА")
    contains_up_cfm_code: Optional[bool] = Field(False, description="Содержит код подтверждения")
    e_tag: Optional[str] = Field(None, description="ETag для кэширования")
    updated_on: Optional[int] = Field(None, description="Время последнего обновления в ЕСИА")
    state_facts: Optional[List[str]] = Field(None, description="Факты состояния пользователя")


class UserUpdate(BaseModel):
    """Схема для обновления пользователя."""
    
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    middle_name: Optional[str] = Field(None, description="Отчество пользователя")
    trusted: Optional[bool] = Field(None, description="Подтвержденная учетная запись")
    status: Optional[str] = Field(None, description="Статус пользователя в ЕСИА")
    verifying: Optional[bool] = Field(None, description="Процесс верификации")
    e_tag: Optional[str] = Field(None, description="ETag для кэширования")
    updated_on: Optional[int] = Field(None, description="Время последнего обновления в ЕСИА")
    state_facts: Optional[List[str]] = Field(None, description="Факты состояния пользователя")


class User(UserBase):
    """Полная схема пользователя для ответов API."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Внутренний ID пользователя")
    verifying: Optional[bool] = Field(False, description="Процесс верификации")
    r_id_doc: Optional[int] = Field(None, description="ID документа в ЕСИА")
    contains_up_cfm_code: Optional[bool] = Field(False, description="Содержит код подтверждения")
    e_tag: Optional[str] = Field(None, description="ETag для кэширования")
    updated_on: Optional[int] = Field(None, description="Время последнего обновления в ЕСИА")
    state_facts: Optional[List[str]] = Field(None, description="Факты состояния пользователя")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время обновления записи")


class UserTokenBase(BaseModel):
    """Базовая схема токена пользователя."""
    
    access_token: str = Field(..., description="Токен доступа")
    token_type: str = Field("Bearer", description="Тип токена")
    expires_in: Optional[int] = Field(None, description="Время жизни токена в секундах")
    scope: Optional[str] = Field(None, description="Области доступа")


class UserTokenCreate(UserTokenBase):
    """Схема для создания токена пользователя."""
    
    user_id: int = Field(..., description="ID пользователя")
    refresh_token: Optional[str] = Field(None, description="Токен обновления")
    id_token: Optional[str] = Field(None, description="ID токен")
    created_at_timestamp: Optional[int] = Field(None, description="Время создания токена (timestamp)")


class UserToken(UserTokenBase):
    """Полная схема токена пользователя для ответов API."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="ID токена")
    user_id: int = Field(..., description="ID пользователя")
    refresh_token: Optional[str] = Field(None, description="Токен обновления")
    id_token: Optional[str] = Field(None, description="ID токен")
    created_at_timestamp: Optional[int] = Field(None, description="Время создания токена (timestamp)")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время обновления записи")
    is_active: bool = Field(True, description="Активность токена")


class AuthorizationRequestBase(BaseModel):
    """Базовая схема запроса авторизации."""
    
    client_id: str = Field(..., description="ID клиентской системы")
    response_type: str = Field("code", description="Тип ответа")
    provider: str = Field(..., description="Провайдер данных")
    scope: str = Field(..., description="Области доступа")
    redirect_uri: str = Field(..., description="URI возврата")
    state: str = Field(..., description="Состояние запроса")
    nonce: Optional[str] = Field(None, description="Nonce для предотвращения подделки")


class AuthorizationRequestCreate(AuthorizationRequestBase):
    """Схема для создания запроса авторизации."""
    pass


class AuthorizationRequest(AuthorizationRequestBase):
    """Полная схема запроса авторизации для ответов API."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="ID запроса авторизации")
    authorization_code: Optional[str] = Field(None, description="Полученный код авторизации")
    error: Optional[str] = Field(None, description="Код ошибки")
    error_description: Optional[str] = Field(None, description="Описание ошибки")
    created_at: datetime = Field(..., description="Время создания запроса")
    completed_at: Optional[datetime] = Field(None, description="Время завершения запроса")
    is_completed: bool = Field(False, description="Запрос завершен")


class ESIAUserInfo(BaseModel):
    """Схема информации о пользователе из ЕСИА."""
    
    sub: str = Field(..., description="Субъект (ID пользователя)")
    info: Dict[str, Any] = Field(..., description="Информация о пользователе")


class ESIATokenResponse(BaseModel):
    """Схема ответа с токенами от ЕСИА."""
    
    access_token: str = Field(..., description="Токен доступа")
    token_type: str = Field(..., description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")
    refresh_token: Optional[str] = Field(None, description="Токен обновления")
    scope: str = Field(..., description="Области доступа")
    created_at: int = Field(..., description="Время создания токена")
    id_token: Optional[str] = Field(None, description="ID токен")