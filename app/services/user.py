"""
Сервис для работы с пользователями.
Содержит бизнес-логику управления пользователями.
"""

import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.user import UserRepository, UserTokenRepository, AuthorizationRequestRepository
from app.schemas.user import UserCreate, UserUpdate, UserTokenCreate, ESIAUserInfo
from app.models.user import User, UserToken
from app.core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class UserService:
    """
    Сервис для управления пользователями.
    Содержит бизнес-логику работы с пользователями и их токенами.
    """
    
    def __init__(self, db: Session):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = UserTokenRepository(db)
        self.auth_repo = AuthorizationRequestRepository(db)
    
    def get_user_by_id(self, user_id: int) -> User:
        """
        Получение пользователя по ID.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Пользователь
            
        Raises:
            NotFoundError: Если пользователь не найден
        """
        logger.debug(f"Получение пользователя по ID: {user_id}")
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"Пользователь с ID {user_id} не найден")
            raise NotFoundError(f"Пользователь с ID {user_id} не найден")
        
        return user
    
    def get_user_by_esia_uid(self, esia_uid: str) -> Optional[User]:
        """
        Получение пользователя по UID из ЕСИА.
        
        Args:
            esia_uid: UID пользователя в ЕСИА
            
        Returns:
            Пользователь или None
        """
        logger.debug(f"Получение пользователя по ЕСИА UID: {esia_uid}")
        return self.user_repo.get_by_esia_uid(esia_uid)
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Создание нового пользователя.
        
        Args:
            user_data: Данные пользователя
            
        Returns:
            Созданный пользователь
            
        Raises:
            ValidationError: Если пользователь уже существует
        """
        logger.info(f"Создание пользователя с ЕСИА UID: {user_data.esia_uid}")
        
        # Проверка существования пользователя
        existing_user = self.user_repo.get_by_esia_uid(user_data.esia_uid)
        if existing_user:
            logger.warning(f"Пользователь с ЕСИА UID {user_data.esia_uid} уже существует")
            raise ValidationError(
                f"Пользователь с ЕСИА UID {user_data.esia_uid} уже существует",
                details={"esia_uid": user_data.esia_uid}
            )
        
        return self.user_repo.create(user_data)
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        Обновление пользователя.
        
        Args:
            user_id: ID пользователя
            user_data: Данные для обновления
            
        Returns:
            Обновленный пользователь
            
        Raises:
            NotFoundError: Если пользователь не найден
        """
        logger.info(f"Обновление пользователя с ID: {user_id}")
        
        updated_user = self.user_repo.update(user_id, user_data)
        if not updated_user:
            logger.warning(f"Пользователь с ID {user_id} не найден для обновления")
            raise NotFoundError(f"Пользователь с ID {user_id} не найден")
        
        return updated_user
    
    def delete_user(self, user_id: int) -> bool:
        """
        Удаление пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если удален
            
        Raises:
            NotFoundError: Если пользователь не найден
        """
        logger.info(f"Удаление пользователя с ID: {user_id}")
        
        # Деактивация токенов пользователя
        self.token_repo.deactivate_user_tokens(user_id)
        
        deleted = self.user_repo.delete(user_id)
        if not deleted:
            logger.warning(f"Пользователь с ID {user_id} не найден для удаления")
            raise NotFoundError(f"Пользователь с ID {user_id} не найден")
        
        return True
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Получение списка пользователей.
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список пользователей
        """
        logger.debug(f"Получение списка пользователей: skip={skip}, limit={limit}")
        return self.user_repo.get_all(skip, limit)
    
    def create_or_update_user_from_esia(self, esia_data: ESIAUserInfo) -> User:
        """
        Создание или обновление пользователя на основе данных из ЕСИА.
        
        Args:
            esia_data: Данные пользователя из ЕСИА
            
        Returns:
            Пользователь
        """
        logger.info(f"Создание/обновление пользователя из ЕСИА: {esia_data.sub}")
        
        user_info = esia_data.info
        esia_uid = user_info.get("uid", esia_data.sub)
        
        # Поиск существующего пользователя
        existing_user = self.user_repo.get_by_esia_uid(esia_uid)
        
        if existing_user:
            # Обновление существующего пользователя
            logger.info(f"Обновление существующего пользователя: {existing_user.id}")
            
            update_data = UserUpdate(
                first_name=user_info.get("firstName"),
                last_name=user_info.get("lastName"),
                middle_name=user_info.get("middleName"),
                trusted=user_info.get("trusted", False),
                status=user_info.get("status"),
                verifying=user_info.get("verifying", False),
                e_tag=user_info.get("eTag"),
                updated_on=user_info.get("updatedOn"),
                state_facts=user_info.get("stateFacts", [])
            )
            
            return self.update_user(existing_user.id, update_data)
        else:
            # Создание нового пользователя
            logger.info(f"Создание нового пользователя из ЕСИА: {esia_uid}")
            
            create_data = UserCreate(
                esia_uid=esia_uid,
                first_name=user_info.get("firstName"),
                last_name=user_info.get("lastName"),
                middle_name=user_info.get("middleName"),
                trusted=user_info.get("trusted", False),
                status=user_info.get("status"),
                verifying=user_info.get("verifying", False),
                r_id_doc=user_info.get("rIdDoc"),
                contains_up_cfm_code=user_info.get("containsUpCfmCode", False),
                e_tag=user_info.get("eTag"),
                updated_on=user_info.get("updatedOn"),
                state_facts=user_info.get("stateFacts", [])
            )
            
            return self.user_repo.create(create_data)
    
    def save_user_token(self, user_id: int, token_data: Dict[str, Any]) -> UserToken:
        """
        Сохранение токена пользователя.
        
        Args:
            user_id: ID пользователя
            token_data: Данные токена от ЕСИА
            
        Returns:
            Сохраненный токен
        """
        logger.info(f"Сохранение токена для пользователя: {user_id}")
        
        token_create = UserTokenCreate(
            user_id=user_id,
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in"),
            refresh_token=token_data.get("refresh_token"),
            scope=token_data.get("scope"),
            id_token=token_data.get("id_token"),
            created_at_timestamp=token_data.get("created_at")
        )
        
        return self.token_repo.create(token_create)
    
    def get_user_active_token(self, user_id: int) -> Optional[UserToken]:
        """
        Получение активного токена пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Активный токен или None
        """
        logger.debug(f"Получение активного токена пользователя: {user_id}")
        return self.token_repo.get_active_token(user_id)
    
    def deactivate_user_tokens(self, user_id: int) -> None:
        """
        Деактивация всех токенов пользователя.
        
        Args:
            user_id: ID пользователя
        """
        logger.info(f"Деактивация токенов пользователя: {user_id}")
        self.token_repo.deactivate_user_tokens(user_id)