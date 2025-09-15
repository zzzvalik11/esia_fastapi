"""
Модели пользователей для работы с ЕСИА.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """
    Модель пользователя ЕСИА.
    Хранит основную информацию о пользователе из ЕСИА.
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, comment="Внутренний ID пользователя")
    esia_uid = Column(String(50), unique=True, index=True, nullable=False, comment="UID пользователя в ЕСИА")
    first_name = Column(String(100), comment="Имя пользователя")
    last_name = Column(String(100), comment="Фамилия пользователя")
    middle_name = Column(String(100), comment="Отчество пользователя")
    trusted = Column(Boolean, default=False, comment="Подтвержденная учетная запись")
    status = Column(String(50), comment="Статус пользователя в ЕСИА")
    verifying = Column(Boolean, default=False, comment="Процесс верификации")
    r_id_doc = Column(Integer, comment="ID документа в ЕСИА")
    contains_up_cfm_code = Column(Boolean, default=False, comment="Содержит код подтверждения")
    e_tag = Column(String(255), comment="ETag для кэширования")
    updated_on = Column(Integer, comment="Время последнего обновления в ЕСИА")
    state_facts = Column(JSON, comment="Факты состояния пользователя")
    
    # Системные поля
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Время создания записи")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Время обновления записи")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, esia_uid='{self.esia_uid}', name='{self.first_name} {self.last_name}')>"


class UserToken(Base):
    """
    Модель для хранения токенов пользователей.
    Управляет access_token и refresh_token от ЕСИА.
    """
    
    __tablename__ = "user_tokens"
    
    id = Column(Integer, primary_key=True, index=True, comment="ID токена")
    user_id = Column(Integer, index=True, nullable=False, comment="ID пользователя")
    access_token = Column(Text, nullable=False, comment="Токен доступа")
    refresh_token = Column(String(255), comment="Токен обновления")
    token_type = Column(String(50), default="Bearer", comment="Тип токена")
    expires_in = Column(Integer, comment="Время жизни токена в секундах")
    scope = Column(String(500), comment="Области доступа")
    id_token = Column(Text, comment="ID токен")
    created_at_timestamp = Column(Integer, comment="Время создания токена (timestamp)")
    
    # Системные поля
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Время создания записи")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Время обновления записи")
    is_active = Column(Boolean, default=True, comment="Активность токена")
    
    def __repr__(self) -> str:
        return f"<UserToken(id={self.id}, user_id={self.user_id}, active={self.is_active})>"


class AuthorizationRequest(Base):
    """
    Модель для отслеживания запросов авторизации.
    Хранит информацию о процессе авторизации пользователя.
    """
    
    __tablename__ = "authorization_requests"
    
    id = Column(Integer, primary_key=True, index=True, comment="ID запроса авторизации")
    client_id = Column(String(255), nullable=False, comment="ID клиентской системы")
    response_type = Column(String(50), nullable=False, comment="Тип ответа")
    provider = Column(String(50), nullable=False, comment="Провайдер данных")
    scope = Column(Text, nullable=False, comment="Области доступа")
    redirect_uri = Column(String(500), nullable=False, comment="URI возврата")
    state = Column(String(255), nullable=False, unique=True, index=True, comment="Состояние запроса")
    nonce = Column(String(255), comment="Nonce для предотвращения подделки")
    authorization_code = Column(String(255), comment="Полученный код авторизации")
    error = Column(String(100), comment="Код ошибки")
    error_description = Column(Text, comment="Описание ошибки")
    
    # Системные поля
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Время создания запроса")
    completed_at = Column(DateTime(timezone=True), comment="Время завершения запроса")
    is_completed = Column(Boolean, default=False, comment="Запрос завершен")
    
    def __repr__(self) -> str:
        return f"<AuthorizationRequest(id={self.id}, state='{self.state}', completed={self.is_completed})>"