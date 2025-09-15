"""
API роуты для управления организациями.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.exceptions import ESIAGatewayException, AuthenticationError
from app.schemas.organization import Organization, OrganizationCreate, OrganizationUpdate, ESIAOrganizationInfo, ESIAGroupsInfo
from app.services.organization import OrganizationService
from app.services.esia import ESIAService

router = APIRouter(prefix="/organizations", tags=["Организации"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[Organization], summary="Получение списка организаций")
def get_organizations(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    db: Session = Depends(get_db)
):
    """
    Получение списка организаций с пагинацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей
        db: Сессия базы данных
        
    Returns:
        Список организаций
    """
    logger.info(f"Запрос списка организаций: skip={skip}, limit={limit}")
    
    try:
        org_service = OrganizationService(db)
        organizations = org_service.get_organizations(skip=skip, limit=limit)
        
        logger.info(f"Возвращено {len(organizations)} организаций")
        return organizations
        
    except Exception as e:
        logger.error(f"Ошибка при получении списка организаций: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/{org_id}", response_model=Organization, summary="Получение организации по ID")
def get_organization(
    org_id: int,
    db: Session = Depends(get_db)
):
    """
    Получение организации по ID.
    
    Args:
        org_id: ID организации
        db: Сессия базы данных
        
    Returns:
        Данные организации
        
    Raises:
        HTTPException: Если организация не найдена
    """
    logger.info(f"Запрос организации по ID: {org_id}")
    
    try:
        org_service = OrganizationService(db)
        organization = org_service.get_organization_by_id(org_id)
        
        logger.info(f"Организация найдена: {organization.short_name}")
        return organization
        
    except ESIAGatewayException as e:
        logger.error(f"Ошибка при получении организации {org_id}: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении организации {org_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/esia/{esia_oid}", response_model=Organization, summary="Получение организации по ЕСИА OID")
def get_organization_by_esia_oid(
    esia_oid: int,
    db: Session = Depends(get_db)
):
    """
    Получение организации по OID из ЕСИА.
    
    Args:
        esia_oid: OID организации в ЕСИА
        db: Сессия базы данных
        
    Returns:
        Данные организации
        
    Raises:
        HTTPException: Если организация не найдена
    """
    logger.info(f"Запрос организации по ЕСИА OID: {esia_oid}")
    
    try:
        org_service = OrganizationService(db)
        organization = org_service.get_organization_by_esia_oid(esia_oid)
        
        if not organization:
            logger.warning(f"Организация с ЕСИА OID {esia_oid} не найдена")
            raise HTTPException(status_code=404, detail="Организация не найдена")
        
        logger.info(f"Организация найдена: ID {organization.id}")
        return organization
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении организации {esia_oid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/", response_model=Organization, summary="Создание организации")
def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db)
):
    """
    Создание новой организации.
    
    Args:
        org_data: Данные для создания организации
        db: Сессия базы данных
        
    Returns:
        Созданная организация
        
    Raises:
        HTTPException: При ошибке создания
    """
    logger.info(f"Создание организации с ЕСИА OID: {org_data.esia_oid}")
    
    try:
        org_service = OrganizationService(db)
        organization = org_service.create_organization(org_data)
        
        logger.info(f"Организация создана с ID: {organization.id}")
        return organization
        
    except ESIAGatewayException as e:
        logger.error(f"Ошибка при создании организации: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании организации: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.put("/{org_id}", response_model=Organization, summary="Обновление организации")
def update_organization(
    org_id: int,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновление организации.
    
    Args:
        org_id: ID организации
        org_data: Данные для обновления
        db: Сессия базы данных
        
    Returns:
        Обновленная организация
        
    Raises:
        HTTPException: При ошибке обновления
    """
    logger.info(f"Обновление организации с ID: {org_id}")
    
    try:
        org_service = OrganizationService(db)
        organization = org_service.update_organization(org_id, org_data)
        
        logger.info(f"Организация {org_id} обновлена")
        return organization
        
    except ESIAGatewayException as e:
        logger.error(f"Ошибка при обновлении организации {org_id}: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обновлении организации {org_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.delete("/{org_id}", summary="Удаление организации")
def delete_organization(
    org_id: int,
    db: Session = Depends(get_db)
):
    """
    Удаление организации.
    
    Args:
        org_id: ID организации
        db: Сессия базы данных
        
    Returns:
        Подтверждение удаления
        
    Raises:
        HTTPException: При ошибке удаления
    """
    logger.info(f"Удаление организации с ID: {org_id}")
    
    try:
        org_service = OrganizationService(db)
        success = org_service.delete_organization(org_id)
        
        if success:
            logger.info(f"Организация {org_id} удалена")
            return {"message": "Организация успешно удалена"}
        else:
            raise HTTPException(status_code=404, detail="Организация не найдена")
            
    except HTTPException:
        raise
    except ESIAGatewayException as e:
        logger.error(f"Ошибка при удалении организации {org_id}: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Неожиданная ошибка при удалении организации {org_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/users/{user_id}", response_model=List[Organization], summary="Получение организаций пользователя")
def get_user_organizations(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получение организаций пользователя.
    
    Args:
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        Список организаций пользователя
    """
    logger.info(f"Запрос организаций пользователя: {user_id}")
    
    try:
        org_service = OrganizationService(db)
        organizations = org_service.get_user_organizations(user_id)
        
        logger.info(f"Найдено {len(organizations)} организаций для пользователя {user_id}")
        return organizations
        
    except Exception as e:
        logger.error(f"Ошибка при получении организаций пользователя {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/esia/{org_oid}/info", response_model=ESIAOrganizationInfo, summary="Получение данных организации из ЕСИА")
async def get_organization_info_from_esia(
    org_oid: int,
    scopes: List[str] = Query(..., description="Список запрашиваемых областей доступа"),
    authorization: str = Header(..., description="Bearer токен"),
    db: Session = Depends(get_db)
):
    """
    Получение информации об организации из ЕСИА.
    
    Args:
        org_oid: OID организации в ЕСИА
        scopes: Список запрашиваемых областей доступа
        authorization: Заголовок авторизации с Bearer токеном
        db: Сессия базы данных
        
    Returns:
        Информация об организации из ЕСИА
        
    Raises:
        HTTPException: При ошибке получения данных
    """
    logger.info(f"Запрос данных организации {org_oid} из ЕСИА")
    
    try:
        # Извлечение токена из заголовка
        if not authorization.startswith("Bearer "):
            raise AuthenticationError("Неверный формат токена авторизации")
        
        access_token = authorization.replace("Bearer ", "")
        
        # Получение данных организации от ЕСИА
        async with ESIAService() as esia_service:
            org_data = await esia_service.get_organization_info(access_token, org_oid, scopes)
        
        logger.info(f"Данные организации {org_oid} успешно получены из ЕСИА")
        
        return ESIAOrganizationInfo(**org_data)
        
    except AuthenticationError as e:
        logger.error(f"Ошибка аутентификации: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except ESIAGatewayException as e:
        logger.error(f"Ошибка ЕСИА при получении данных организации: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении данных организации: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/esia/{org_oid}/groups", response_model=ESIAGroupsInfo, summary="Получение групп доступа организации из ЕСИА")
async def get_organization_groups_from_esia(
    org_oid: int,
    authorization: str = Header(..., description="Bearer токен"),
    db: Session = Depends(get_db)
):
    """
    Получение информации о группах доступа организации из ЕСИА.
    
    Args:
        org_oid: OID организации в ЕСИА
        authorization: Заголовок авторизации с Bearer токеном
        db: Сессия базы данных
        
    Returns:
        Информация о группах доступа из ЕСИА
        
    Raises:
        HTTPException: При ошибке получения данных
    """
    logger.info(f"Запрос групп доступа организации {org_oid} из ЕСИА")
    
    try:
        # Извлечение токена из заголовка
        if not authorization.startswith("Bearer "):
            raise AuthenticationError("Неверный формат токена авторизации")
        
        access_token = authorization.replace("Bearer ", "")
        
        # Получение данных групп от ЕСИА
        async with ESIAService() as esia_service:
            groups_data = await esia_service.get_groups_info(access_token, org_oid)
        
        logger.info(f"Данные групп доступа организации {org_oid} успешно получены из ЕСИА")
        
        return ESIAGroupsInfo(**groups_data)
        
    except AuthenticationError as e:
        logger.error(f"Ошибка аутентификации: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except ESIAGatewayException as e:
        logger.error(f"Ошибка ЕСИА при получении групп доступа: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении групп доступа: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")