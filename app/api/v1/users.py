"""
API роуты для управления пользователями.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.exceptions import ESIAGatewayException
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Пользователи"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[User], summary="Получение списка пользователей")
def get_users(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    db: Session = Depends(get_db)
):
    """
    Получение списка пользователей с пагинацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей
        db: Сессия базы данных
        
    Returns:
        Список пользователей
    """
    logger.info(f"Запрос списка пользователей: skip={skip}, limit={limit}")
    
    try:
        user_service = UserService(db)
        users = user_service.get_users(skip=skip, limit=limit)
        
        logger.info(f"Возвращено {len(users)} пользователей")
        return users
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка пользователей: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/{user_id}", response_model=User, summary="Получение пользователя по ID")
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получение пользователя по ID.
    
    Args:
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        Данные пользователя
        
    Raises:
        HTTPException: Если пользователь не найден
    """
    logger.info(f"Запрос пользователя по ID: {user_id}")
    
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        
        logger.info(f"Пользователь найден: {user.esia_uid}")
        return user
        
    except ESIAGatewayException as e:
        logger.error(f"Ошибка при получении пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/esia/{esia_uid}", response_model=User, summary="Получение пользователя по ЕСИА UID")
def get_user_by_esia_uid(
    esia_uid: str,
    db: Session = Depends(get_db)
):
    """
    Получение пользователя по UID из ЕСИА.
    
    Args:
        esia_uid: UID пользователя в ЕСИА
        db: Сессия базы данных
        
    Returns:
        Данные пользователя
        
    Raises:
        HTTPException: Если пользователь не найден
    """
    logger.info(f"Запрос пользователя по ЕСИА UID: {esia_uid}")
    
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_esia_uid(esia_uid)
        
        if not user:
            logger.warning(f"Пользователь с ЕСИА UID {esia_uid} не найден")
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        logger.info(f"Пользователь найден: ID {user.id}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении пользователя {esia_uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/", response_model=User, summary="Создание пользователя")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Создание нового пользователя.
    
    Args:
        user_data: Данные для создания пользователя
        db: Сессия базы данных
        
    Returns:
        Созданный пользователь
        
    Raises:
        HTTPException: При ошибке создания
    """
    logger.info(f"Создание пользователя с ЕСИА UID: {user_data.esia_uid}")
    
    try:
        user_service = UserService(db)
        user = user_service.create_user(user_data)
        
        logger.info(f"Пользователь создан с ID: {user.id}")
        return user
        
    except ESIAGatewayException as e:
        logger.error(f"Ошибка при создании пользователя: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании пользователя: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.put("/{user_id}", response_model=User, summary="Обновление пользователя")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновление пользователя.
    
    Args:
        user_id: ID пользователя
        user_data: Данные для обновления
        db: Сессия базы данных
        
    Returns:
        Обновленный пользователь
        
    Raises:
        HTTPException: При ошибке обновления
    """
    logger.info(f"Обновление пользователя с ID: {user_id}")
    
    try:
        user_service = UserService(db)
        user = user_service.update_user(user_id, user_data)
        
        logger.info(f"Пользователь {user_id} обновлен")
        return user
        
    except ESIAGatewayException as e:
        logger.error(f"Ошибка при обновлении пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обновлении пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.delete("/{user_id}", summary="Удаление пользователя")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Удаление пользователя.
    
    Args:
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        Подтверждение удаления
        
    Raises:
        HTTPException: При ошибке удаления
    """
    logger.info(f"Удаление пользователя с ID: {user_id}")
    
    try:
        user_service = UserService(db)
        success = user_service.delete_user(user_id)
        
        if success:
            logger.info(f"Пользователь {user_id} удален")
            return {"message": "Пользователь успешно удален"}
        else:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
            
    except HTTPException:
        raise
    except ESIAGatewayException as e:
        logger.error(f"Ошибка при удалении пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Неожиданная ошибка при удалении пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")