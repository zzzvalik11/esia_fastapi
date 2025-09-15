"""
Репозиторий для работы с организациями.
Обеспечивает абстракцию доступа к данным организаций.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.organization import Organization, OrganizationAddress, OrganizationGroup, UserOrganization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationAddressCreate, OrganizationGroupCreate
import logging

logger = logging.getLogger(__name__)


class OrganizationRepository:
    """
    Репозиторий для управления организациями.
    Предоставляет методы для CRUD операций с организациями.
    """
    
    def __init__(self, db: Session):
        """
        Инициализация репозитория.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    def get_by_id(self, org_id: int) -> Optional[Organization]:
        """
        Получение организации по ID.
        
        Args:
            org_id: ID организации
            
        Returns:
            Organization или None если не найдена
        """
        logger.debug(f"Получение организации по ID: {org_id}")
        return self.db.query(Organization).filter(Organization.id == org_id).first()
    
    def get_by_esia_oid(self, esia_oid: int) -> Optional[Organization]:
        """
        Получение организации по OID из ЕСИА.
        
        Args:
            esia_oid: OID организации в ЕСИА
            
        Returns:
            Organization или None если не найдена
        """
        logger.debug(f"Получение организации по ЕСИА OID: {esia_oid}")
        return self.db.query(Organization).filter(Organization.esia_oid == esia_oid).first()
    
    def create(self, org_data: OrganizationCreate) -> Organization:
        """
        Создание новой организации.
        
        Args:
            org_data: Данные для создания организации
            
        Returns:
            Созданная организация
        """
        logger.info(f"Создание организации с ЕСИА OID: {org_data.esia_oid}")
        
        db_org = Organization(**org_data.model_dump())
        self.db.add(db_org)
        self.db.commit()
        self.db.refresh(db_org)
        
        logger.info(f"Организация создана с ID: {db_org.id}")
        return db_org
    
    def update(self, org_id: int, org_data: OrganizationUpdate) -> Optional[Organization]:
        """
        Обновление организации.
        
        Args:
            org_id: ID организации
            org_data: Данные для обновления
            
        Returns:
            Обновленная организация или None если не найдена
        """
        logger.info(f"Обновление организации с ID: {org_id}")
        
        db_org = self.get_by_id(org_id)
        if not db_org:
            logger.warning(f"Организация с ID {org_id} не найдена для обновления")
            return None
        
        update_data = org_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_org, field, value)
        
        self.db.commit()
        self.db.refresh(db_org)
        
        logger.info(f"Организация с ID {org_id} обновлена")
        return db_org
    
    def delete(self, org_id: int) -> bool:
        """
        Удаление организации.
        
        Args:
            org_id: ID организации
            
        Returns:
            True если удалена, False если не найдена
        """
        logger.info(f"Удаление организации с ID: {org_id}")
        
        db_org = self.get_by_id(org_id)
        if not db_org:
            logger.warning(f"Организация с ID {org_id} не найдена для удаления")
            return False
        
        self.db.delete(db_org)
        self.db.commit()
        
        logger.info(f"Организация с ID {org_id} удалена")
        return True
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        """
        Получение списка организаций с пагинацией.
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список организаций
        """
        logger.debug(f"Получение списка организаций: skip={skip}, limit={limit}")
        return self.db.query(Organization).offset(skip).limit(limit).all()
    
    def get_user_organizations(self, user_id: int) -> List[Organization]:
        """
        Получение организаций пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список организаций пользователя
        """
        logger.debug(f"Получение организаций пользователя: {user_id}")
        return self.db.query(Organization).join(UserOrganization).filter(
            and_(UserOrganization.user_id == user_id, UserOrganization.is_active == True)
        ).all()


class OrganizationAddressRepository:
    """
    Репозиторий для управления адресами организаций.
    """
    
    def __init__(self, db: Session):
        """
        Инициализация репозитория.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    def get_by_organization(self, org_id: int) -> List[OrganizationAddress]:
        """
        Получение адресов организации.
        
        Args:
            org_id: ID организации
            
        Returns:
            Список адресов организации
        """
        logger.debug(f"Получение адресов организации: {org_id}")
        return self.db.query(OrganizationAddress).filter(
            OrganizationAddress.organization_id == org_id
        ).all()
    
    def create(self, address_data: OrganizationAddressCreate) -> OrganizationAddress:
        """
        Создание адреса организации.
        
        Args:
            address_data: Данные адреса
            
        Returns:
            Созданный адрес
        """
        logger.info(f"Создание адреса для организации: {address_data.organization_id}")
        
        db_address = OrganizationAddress(**address_data.model_dump())
        self.db.add(db_address)
        self.db.commit()
        self.db.refresh(db_address)
        
        logger.info(f"Адрес создан с ID: {db_address.id}")
        return db_address


class OrganizationGroupRepository:
    """
    Репозиторий для управления группами доступа организаций.
    """
    
    def __init__(self, db: Session):
        """
        Инициализация репозитория.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    def get_by_organization(self, org_id: int) -> List[OrganizationGroup]:
        """
        Получение групп доступа организации.
        
        Args:
            org_id: ID организации
            
        Returns:
            Список групп доступа
        """
        logger.debug(f"Получение групп доступа организации: {org_id}")
        return self.db.query(OrganizationGroup).filter(
            OrganizationGroup.organization_id == org_id
        ).all()
    
    def create(self, group_data: OrganizationGroupCreate) -> OrganizationGroup:
        """
        Создание группы доступа.
        
        Args:
            group_data: Данные группы
            
        Returns:
            Созданная группа
        """
        logger.info(f"Создание группы доступа для организации: {group_data.organization_id}")
        
        db_group = OrganizationGroup(**group_data.model_dump())
        self.db.add(db_group)
        self.db.commit()
        self.db.refresh(db_group)
        
        logger.info(f"Группа доступа создана с ID: {db_group.id}")
        return db_group
    
    def get_by_group_id(self, org_id: int, group_id: str) -> Optional[OrganizationGroup]:
        """
        Получение группы по мнемонике.
        
        Args:
            org_id: ID организации
            group_id: Мнемоника группы
            
        Returns:
            Группа доступа или None
        """
        logger.debug(f"Получение группы {group_id} организации {org_id}")
        return self.db.query(OrganizationGroup).filter(
            and_(
                OrganizationGroup.organization_id == org_id,
                OrganizationGroup.group_id == group_id
            )
        ).first()


class UserOrganizationRepository:
    """
    Репозиторий для управления связями пользователей с организациями.
    """
    
    def __init__(self, db: Session):
        """
        Инициализация репозитория.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    def create_or_update(self, user_id: int, org_id: int, **kwargs) -> UserOrganization:
        """
        Создание или обновление связи пользователя с организацией.
        
        Args:
            user_id: ID пользователя
            org_id: ID организации
            **kwargs: Дополнительные параметры связи
            
        Returns:
            Связь пользователя с организацией
        """
        logger.info(f"Создание/обновление связи пользователя {user_id} с организацией {org_id}")
        
        # Поиск существующей связи
        db_relation = self.db.query(UserOrganization).filter(
            and_(
                UserOrganization.user_id == user_id,
                UserOrganization.organization_id == org_id
            )
        ).first()
        
        if db_relation:
            # Обновление существующей связи
            for field, value in kwargs.items():
                setattr(db_relation, field, value)
            db_relation.is_active = True
            logger.info(f"Связь обновлена: {db_relation.id}")
        else:
            # Создание новой связи
            db_relation = UserOrganization(
                user_id=user_id,
                organization_id=org_id,
                **kwargs
            )
            self.db.add(db_relation)
            logger.info(f"Новая связь создана")
        
        self.db.commit()
        self.db.refresh(db_relation)
        
        return db_relation
    
    def get_user_organizations(self, user_id: int) -> List[UserOrganization]:
        """
        Получение активных связей пользователя с организациями.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список связей с организациями
        """
        logger.debug(f"Получение связей пользователя {user_id} с организациями")
        return self.db.query(UserOrganization).filter(
            and_(
                UserOrganization.user_id == user_id,
                UserOrganization.is_active == True
            )
        ).all()