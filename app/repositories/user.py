"""
Репозиторий для работы с пользователями.
Обеспечивает абстракцию доступа к данным пользователей.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.user import User, UserToken, AuthorizationRequest
from app.schemas.user import UserCreate, UserUpdate, UserTokenCreate
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Репозиторий для управления пользователями.
    Предоставляет методы для CRUD операций с пользователями.
    """
    
    def __init__(self, db: Session):
        """
        Инициализация репозитория.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Получение пользователя по ID.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            User или None если не найден
        """
        logger.debug(f"Получение пользователя по ID: {user_id}")
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_esia_uid(self, esia_uid: str) -> Optional[User]:
        """
        Получение пользователя по UID из ЕСИА.
        
        Args:
            esia_uid: UID пользователя в ЕСИА
            
        Returns:
            User или None если не найден
        """
        logger.debug(f"Получение пользователя по ЕСИА UID: {esia_uid}")
        return self.db.query(User).filter(User.esia_uid == esia_uid).first()
    
    def create(self, user_data: UserCreate) -> User:
        """
        Создание нового пользователя.
        
        Args:
            user_data: Данные для создания пользователя
            
        Returns:
            Созданный пользователь
        """
        logger.info(f"Создание пользователя с ЕСИА UID: {user_data.esia_uid}")
        
        db_user = User(**user_data.model_dump())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        logger.info(f"Пользователь создан с ID: {db_user.id}")
        return db_user
    
    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Обновление пользователя.
        
        Args:
            user_id: ID пользователя
            user_data: Данные для обновления
            
        Returns:
            Обновленный пользователь или None если не найден
        """
        logger.info(f"Обновление пользователя с ID: {user_id}")
        
        db_user = self.get_by_id(user_id)
        if not db_user:
            logger.warning(f"Пользователь с ID {user_id} не найден для обновления")
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        
        logger.info(f"Пользователь с ID {user_id} обновлен")
        return db_user
    
    def delete(self, user_id: int) -> bool:
        """
        Удаление пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если удален, False если не найден
        """
        logger.info(f"Удаление пользователя с ID: {user_id}")
        
        db_user = self.get_by_id(user_id)
        if not db_user:
            logger.warning(f"Пользователь с ID {user_id} не найден для удаления")
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        
        logger.info(f"Пользователь с ID {user_id} удален")
        return True
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Получение списка пользователей с пагинацией.
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список пользователей
        """
        logger.debug(f"Получение списка пользователей: skip={skip}, limit={limit}")
        return self.db.query(User).offset(skip).limit(limit).all()


class UserTokenRepository:
    """
    Репозиторий для управления токенами пользователей.
    Предоставляет методы для работы с токенами доступа и обновления.
    """
    
    def __init__(self, db: Session):
        """
        Инициализация репозитория.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    def get_active_token(self, user_id: int) -> Optional[UserToken]:
        """
        Получение активного токена пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Активный токен или None
        """
        logger.debug(f"Получение активного токена для пользователя: {user_id}")
        return self.db.query(UserToken).filter(
            and_(UserToken.user_id == user_id, UserToken.is_active == True)
        ).first()
    
    def create(self, token_data: UserTokenCreate) -> UserToken:
        """
        Создание нового токена.
        
        Args:
            token_data: Данные токена
            
        Returns:
            Созданный токен
        """
        logger.info(f"Создание токена для пользователя: {token_data.user_id}")
        
        # Деактивация старых токенов
        self.db.query(UserToken).filter(
            and_(UserToken.user_id == token_data.user_id, UserToken.is_active == True)
        ).update({"is_active": False})
        
        db_token = UserToken(**token_data.model_dump())
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        
        logger.info(f"Токен создан с ID: {db_token.id}")
        return db_token
    
    def deactivate_user_tokens(self, user_id: int) -> None:
        """
        Деактивация всех токенов пользователя.
        
        Args:
            user_id: ID пользователя
        """
        logger.info(f"Деактивация всех токенов пользователя: {user_id}")
        
        self.db.query(UserToken).filter(UserToken.user_id == user_id).update(
            {"is_active": False}
        )
        self.db.commit()


class AuthorizationRequestRepository:
    """
    Репозиторий для управления запросами авторизации.
    Отслеживает процесс авторизации пользователей.
    """
    
    def __init__(self, db: Session):
        """
        Инициализация репозитория.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    def get_by_state(self, state: str) -> Optional[AuthorizationRequest]:
        """
        Получение запроса авторизации по состоянию.
        
        Args:
            state: Состояние запроса
            
        Returns:
            Запрос авторизации или None
        """
        logger.debug(f"Получение запроса авторизации по состоянию: {state}")
        return self.db.query(AuthorizationRequest).filter(
            AuthorizationRequest.state == state
        ).first()
    
    def create(self, request_data: dict) -> AuthorizationRequest:
        """
        Создание запроса авторизации.
        
        Args:
            request_data: Данные запроса
            
        Returns:
            Созданный запрос
        """
        logger.info(f"Создание запроса авторизации с состоянием: {request_data.get('state')}")
        
        db_request = AuthorizationRequest(**request_data)
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        
        logger.info(f"Запрос авторизации создан с ID: {db_request.id}")
        return db_request
    
    def update_with_code(self, state: str, authorization_code: str) -> Optional[AuthorizationRequest]:
        """
        Обновление запроса с кодом авторизации.
        
        Args:
            state: Состояние запроса
            authorization_code: Код авторизации
            
        Returns:
            Обновленный запрос или None
        """
        logger.info(f"Обновление запроса авторизации кодом: {state}")
        
        db_request = self.get_by_state(state)
        if not db_request:
            logger.warning(f"Запрос авторизации с состоянием {state} не найден")
            return None
        
        db_request.authorization_code = authorization_code
        db_request.is_completed = True
        db_request.completed_at = func.now()
        
        self.db.commit()
        self.db.refresh(db_request)
        
        logger.info(f"Запрос авторизации {state} обновлен кодом")
        return db_request
    
    def update_with_error(self, state: str, error: str, error_description: str) -> Optional[AuthorizationRequest]:
        """
        Обновление запроса с ошибкой.
        
        Args:
            state: Состояние запроса
            error: Код ошибки
            error_description: Описание ошибки
            
        Returns:
            Обновленный запрос или None
        """
        logger.warning(f"Обновление запроса авторизации ошибкой: {state} - {error}")
        
        db_request = self.get_by_state(state)
        if not db_request:
            logger.warning(f"Запрос авторизации с состоянием {state} не найден")
            return None
        
        db_request.error = error
        db_request.error_description = error_description
        db_request.is_completed = True
        db_request.completed_at = func.now()
        
        self.db.commit()
        self.db.refresh(db_request)
        
        logger.warning(f"Запрос авторизации {state} обновлен ошибкой: {error}")
        return db_request