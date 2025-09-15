"""
Сервис для работы с организациями.
Содержит бизнес-логику управления организациями.
"""

import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.organization import (
    OrganizationRepository, 
    OrganizationAddressRepository, 
    OrganizationGroupRepository,
    UserOrganizationRepository
)
from app.schemas.organization import (
    OrganizationCreate, 
    OrganizationUpdate, 
    OrganizationAddressCreate,
    OrganizationGroupCreate,
    ESIAOrganizationInfo,
    ESIAGroupsInfo
)
from app.models.organization import Organization
from app.core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class OrganizationService:
    """
    Сервис для управления организациями.
    Содержит бизнес-логику работы с организациями, их адресами и группами доступа.
    """
    
    def __init__(self, db: Session):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.org_repo = OrganizationRepository(db)
        self.address_repo = OrganizationAddressRepository(db)
        self.group_repo = OrganizationGroupRepository(db)
        self.user_org_repo = UserOrganizationRepository(db)
    
    def get_organization_by_id(self, org_id: int) -> Organization:
        """
        Получение организации по ID.
        
        Args:
            org_id: ID организации
            
        Returns:
            Организация
            
        Raises:
            NotFoundError: Если организация не найдена
        """
        logger.debug(f"Получение организации по ID: {org_id}")
        
        organization = self.org_repo.get_by_id(org_id)
        if not organization:
            logger.warning(f"Организация с ID {org_id} не найдена")
            raise NotFoundError(f"Организация с ID {org_id} не найдена")
        
        return organization
    
    def get_organization_by_esia_oid(self, esia_oid: int) -> Optional[Organization]:
        """
        Получение организации по OID из ЕСИА.
        
        Args:
            esia_oid: OID организации в ЕСИА
            
        Returns:
            Организация или None
        """
        logger.debug(f"Получение организации по ЕСИА OID: {esia_oid}")
        return self.org_repo.get_by_esia_oid(esia_oid)
    
    def create_organization(self, org_data: OrganizationCreate) -> Organization:
        """
        Создание новой организации.
        
        Args:
            org_data: Данные организации
            
        Returns:
            Созданная организация
            
        Raises:
            ValidationError: Если организация уже существует
        """
        logger.info(f"Создание организации с ЕСИА OID: {org_data.esia_oid}")
        
        # Проверка существования организации
        existing_org = self.org_repo.get_by_esia_oid(org_data.esia_oid)
        if existing_org:
            logger.warning(f"Организация с ЕСИА OID {org_data.esia_oid} уже существует")
            raise ValidationError(
                f"Организация с ЕСИА OID {org_data.esia_oid} уже существует",
                details={"esia_oid": org_data.esia_oid}
            )
        
        return self.org_repo.create(org_data)
    
    def update_organization(self, org_id: int, org_data: OrganizationUpdate) -> Organization:
        """
        Обновление организации.
        
        Args:
            org_id: ID организации
            org_data: Данные для обновления
            
        Returns:
            Обновленная организация
            
        Raises:
            NotFoundError: Если организация не найдена
        """
        logger.info(f"Обновление организации с ID: {org_id}")
        
        updated_org = self.org_repo.update(org_id, org_data)
        if not updated_org:
            logger.warning(f"Организация с ID {org_id} не найдена для обновления")
            raise NotFoundError(f"Организация с ID {org_id} не найдена")
        
        return updated_org
    
    def delete_organization(self, org_id: int) -> bool:
        """
        Удаление организации.
        
        Args:
            org_id: ID организации
            
        Returns:
            True если удалена
            
        Raises:
            NotFoundError: Если организация не найдена
        """
        logger.info(f"Удаление организации с ID: {org_id}")
        
        deleted = self.org_repo.delete(org_id)
        if not deleted:
            logger.warning(f"Организация с ID {org_id} не найдена для удаления")
            raise NotFoundError(f"Организация с ID {org_id} не найдена")
        
        return True
    
    def get_organizations(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        """
        Получение списка организаций.
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список организаций
        """
        logger.debug(f"Получение списка организаций: skip={skip}, limit={limit}")
        return self.org_repo.get_all(skip, limit)
    
    def get_user_organizations(self, user_id: int) -> List[Organization]:
        """
        Получение организаций пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список организаций пользователя
        """
        logger.debug(f"Получение организаций пользователя: {user_id}")
        return self.org_repo.get_user_organizations(user_id)
    
    def create_or_update_organization_from_esia(self, esia_data: ESIAOrganizationInfo, user_id: int) -> Organization:
        """
        Создание или обновление организации на основе данных из ЕСИА.
        
        Args:
            esia_data: Данные организации из ЕСИА
            user_id: ID пользователя
            
        Returns:
            Организация
        """
        logger.info(f"Создание/обновление организации из ЕСИА для пользователя: {user_id}")
        
        org_info = esia_data.info
        esia_oid = org_info.get("oid")
        
        if not esia_oid:
            logger.error("OID организации не найден в данных ЕСИА")
            raise ValidationError("OID организации не найден в данных ЕСИА")
        
        # Поиск существующей организации
        existing_org = self.org_repo.get_by_esia_oid(esia_oid)
        
        if existing_org:
            # Обновление существующей организации
            logger.info(f"Обновление существующей организации: {existing_org.id}")
            
            update_data = OrganizationUpdate(
                full_name=org_info.get("fullName"),
                short_name=org_info.get("shortName"),
                phone=org_info.get("phone"),
                email=org_info.get("email"),
                is_active=not org_info.get("isLiquidated", False),
                staff_count=org_info.get("staffCount"),
                e_tag=org_info.get("eTag")
            )
            
            organization = self.update_organization(existing_org.id, update_data)
        else:
            # Создание новой организации
            logger.info(f"Создание новой организации из ЕСИА: {esia_oid}")
            
            create_data = OrganizationCreate(
                esia_oid=esia_oid,
                prn_oid=org_info.get("prnOid"),
                full_name=org_info.get("fullName"),
                short_name=org_info.get("shortName"),
                ogrn=org_info.get("ogrn"),
                inn=org_info.get("inn"),
                kpp=org_info.get("kpp"),
                org_type=org_info.get("type"),
                leg=org_info.get("leg"),
                phone=org_info.get("phone"),
                email=org_info.get("email"),
                is_chief=org_info.get("chief", False),
                is_admin=org_info.get("admin", False),
                is_active=org_info.get("active", True),
                has_right_of_substitution=org_info.get("hasRightOfSubstitution", False),
                has_approval_tab_access=org_info.get("hasApprovalTabAccess", False),
                is_liquidated=org_info.get("isLiquidated", False),
                staff_count=org_info.get("staffCount"),
                e_tag=org_info.get("eTag")
            )
            
            organization = self.org_repo.create(create_data)
        
        # Создание или обновление связи пользователя с организацией
        self.user_org_repo.create_or_update(
            user_id=user_id,
            org_id=organization.id,
            is_chief=org_info.get("chief", False),
            is_admin=org_info.get("admin", False),
            has_right_of_substitution=org_info.get("hasRightOfSubstitution", False),
            has_approval_tab_access=org_info.get("hasApprovalTabAccess", False)
        )
        
        return organization
    
    def process_organizations_from_esia(self, user_info: Dict[str, Any], user_id: int) -> List[Organization]:
        """
        Обработка списка организаций из данных пользователя ЕСИА.
        
        Args:
            user_info: Информация о пользователе из ЕСИА
            user_id: ID пользователя
            
        Returns:
            Список обработанных организаций
        """
        logger.info(f"Обработка организаций из ЕСИА для пользователя: {user_id}")
        
        organizations = []
        orgs_data = user_info.get("orgs", [])
        
        for org_data in orgs_data:
            try:
                # Создание объекта ESIAOrganizationInfo для каждой организации
                esia_org_info = ESIAOrganizationInfo(
                    sub=str(user_id),
                    info=org_data
                )
                
                organization = self.create_or_update_organization_from_esia(esia_org_info, user_id)
                organizations.append(organization)
                
            except Exception as e:
                logger.error(f"Ошибка обработки организации {org_data.get('oid', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Обработано {len(organizations)} организаций для пользователя {user_id}")
        return organizations
    
    def process_groups_from_esia(self, groups_data: ESIAGroupsInfo, user_id: int) -> None:
        """
        Обработка групп доступа из ЕСИА.
        
        Args:
            groups_data: Данные групп из ЕСИА
            user_id: ID пользователя
        """
        logger.info(f"Обработка групп доступа из ЕСИА для пользователя: {user_id}")
        
        group_info = groups_data.info
        esia_oid = group_info.get("oid")
        
        if not esia_oid:
            logger.warning("OID организации не найден в данных групп")
            return
        
        # Поиск организации
        organization = self.org_repo.get_by_esia_oid(esia_oid)
        if not organization:
            logger.warning(f"Организация с OID {esia_oid} не найдена для обработки групп")
            return
        
        # Обработка групп организации
        grps_data = group_info.get("grps", {})
        if "elements" in grps_data:
            for group_url in grps_data["elements"]:
                try:
                    # Извлечение ID группы из URL
                    group_id = group_url.split("/grps/")[-1]
                    
                    # Проверка существования группы
                    existing_group = self.group_repo.get_by_group_id(organization.id, group_id)
                    if not existing_group:
                        # Создание новой группы
                        group_create = OrganizationGroupCreate(
                            organization_id=organization.id,
                            group_id=group_id,
                            esia_url=group_url,
                            is_system=True  # Группы из ЕСИА считаются системными
                        )
                        self.group_repo.create(group_create)
                        logger.debug(f"Создана группа {group_id} для организации {organization.id}")
                        
                except Exception as e:
                    logger.error(f"Ошибка обработки группы {group_url}: {str(e)}")
                    continue
        
        logger.info(f"Обработка групп доступа завершена для организации {esia_oid}")