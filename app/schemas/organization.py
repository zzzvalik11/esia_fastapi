"""
Pydantic схемы для организаций.
Обеспечивают валидацию и сериализацию данных организаций.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class OrganizationBase(BaseModel):
    """Базовая схема организации с общими полями."""
    
    esia_oid: int = Field(..., description="OID организации в ЕСИА")
    prn_oid: Optional[int] = Field(None, description="OID родительской организации")
    full_name: Optional[str] = Field(None, description="Полное наименование организации")
    short_name: Optional[str] = Field(None, description="Сокращенное наименование организации")
    ogrn: Optional[str] = Field(None, description="ОГРН организации")
    inn: Optional[str] = Field(None, description="ИНН организации")
    kpp: Optional[str] = Field(None, description="КПП организации")
    org_type: Optional[str] = Field(None, description="Тип организации")


class OrganizationCreate(OrganizationBase):
    """Схема для создания организации."""
    
    leg: Optional[str] = Field(None, description="ОПФ организации")
    oktmo: Optional[str] = Field(None, description="ОКТМО организации")
    phone: Optional[str] = Field(None, description="Телефон организации")
    email: Optional[str] = Field(None, description="Email организации")
    is_chief: Optional[bool] = Field(False, description="Руководитель организации")
    is_admin: Optional[bool] = Field(False, description="Администратор организации")
    is_active: Optional[bool] = Field(True, description="Активная организация")
    has_right_of_substitution: Optional[bool] = Field(False, description="Право замещения")
    has_approval_tab_access: Optional[bool] = Field(False, description="Доступ к вкладке согласования")
    is_liquidated: Optional[bool] = Field(False, description="Ликвидированная организация")
    staff_count: Optional[int] = Field(None, description="Количество сотрудников")
    agency_ter_range: Optional[str] = Field(None, description="Территориальная принадлежность ОГВ")
    agency_type: Optional[str] = Field(None, description="Тип ОГВ")
    e_tag: Optional[str] = Field(None, description="ETag для кэширования")


class OrganizationUpdate(BaseModel):
    """Схема для обновления организации."""
    
    full_name: Optional[str] = Field(None, description="Полное наименование организации")
    short_name: Optional[str] = Field(None, description="Сокращенное наименование организации")
    phone: Optional[str] = Field(None, description="Телефон организации")
    email: Optional[str] = Field(None, description="Email организации")
    is_active: Optional[bool] = Field(None, description="Активная организация")
    staff_count: Optional[int] = Field(None, description="Количество сотрудников")
    e_tag: Optional[str] = Field(None, description="ETag для кэширования")


class Organization(OrganizationBase):
    """Полная схема организации для ответов API."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Внутренний ID организации")
    leg: Optional[str] = Field(None, description="ОПФ организации")
    oktmo: Optional[str] = Field(None, description="ОКТМО организации")
    phone: Optional[str] = Field(None, description="Телефон организации")
    email: Optional[str] = Field(None, description="Email организации")
    is_chief: bool = Field(False, description="Руководитель организации")
    is_admin: bool = Field(False, description="Администратор организации")
    is_active: bool = Field(True, description="Активная организация")
    has_right_of_substitution: bool = Field(False, description="Право замещения")
    has_approval_tab_access: bool = Field(False, description="Доступ к вкладке согласования")
    is_liquidated: bool = Field(False, description="Ликвидированная организация")
    staff_count: Optional[int] = Field(None, description="Количество сотрудников")
    agency_ter_range: Optional[str] = Field(None, description="Территориальная принадлежность ОГВ")
    agency_type: Optional[str] = Field(None, description="Тип ОГВ")
    e_tag: Optional[str] = Field(None, description="ETag для кэширования")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время обновления записи")


class OrganizationAddressBase(BaseModel):
    """Базовая схема адреса организации."""
    
    address_type: str = Field(..., description="Тип адреса (postal, legal)")
    postal_code: Optional[str] = Field(None, description="Почтовый индекс")
    country_id: Optional[str] = Field(None, description="Идентификатор страны")
    address_str: Optional[str] = Field(None, description="Адрес строкой")
    region: Optional[str] = Field(None, description="Регион")
    city: Optional[str] = Field(None, description="Город")
    street: Optional[str] = Field(None, description="Улица")


class OrganizationAddressCreate(OrganizationAddressBase):
    """Схема для создания адреса организации."""
    
    organization_id: int = Field(..., description="ID организации")
    building: Optional[str] = Field(None, description="Строение")
    corpus: Optional[str] = Field(None, description="Корпус")
    house: Optional[str] = Field(None, description="Дом")
    apartment: Optional[str] = Field(None, description="Квартира")
    fias_code: Optional[str] = Field(None, description="Код ФИАС")
    inner_city_district: Optional[str] = Field(None, description="Внутригородской район")
    district: Optional[str] = Field(None, description="Район")
    settlement: Optional[str] = Field(None, description="Поселение")
    additional_territory: Optional[str] = Field(None, description="Дополнительная территория")
    additional_territory_street: Optional[str] = Field(None, description="Улица на дополнительной территории")


class OrganizationAddress(OrganizationAddressBase):
    """Полная схема адреса организации для ответов API."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="ID адреса")
    organization_id: int = Field(..., description="ID организации")
    building: Optional[str] = Field(None, description="Строение")
    corpus: Optional[str] = Field(None, description="Корпус")
    house: Optional[str] = Field(None, description="Дом")
    apartment: Optional[str] = Field(None, description="Квартира")
    fias_code: Optional[str] = Field(None, description="Код ФИАС")
    inner_city_district: Optional[str] = Field(None, description="Внутригородской район")
    district: Optional[str] = Field(None, description="Район")
    settlement: Optional[str] = Field(None, description="Поселение")
    additional_territory: Optional[str] = Field(None, description="Дополнительная территория")
    additional_territory_street: Optional[str] = Field(None, description="Улица на дополнительной территории")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время обновления записи")


class OrganizationGroupBase(BaseModel):
    """Базовая схема группы доступа организации."""
    
    group_id: str = Field(..., description="Мнемоника группы")
    name: Optional[str] = Field(None, description="Название группы")
    description: Optional[str] = Field(None, description="Описание группы")
    is_system: bool = Field(False, description="Системная группа")
    it_system: Optional[str] = Field(None, description="Мнемоника системы-владельца")


class OrganizationGroupCreate(OrganizationGroupBase):
    """Схема для создания группы доступа организации."""
    
    organization_id: int = Field(..., description="ID организации")
    esia_url: Optional[str] = Field(None, description="URL группы в ЕСИА")


class OrganizationGroup(OrganizationGroupBase):
    """Полная схема группы доступа организации для ответов API."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="ID группы")
    organization_id: int = Field(..., description="ID организации")
    esia_url: Optional[str] = Field(None, description="URL группы в ЕСИА")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время обновления записи")


class ESIAOrganizationInfo(BaseModel):
    """Схема информации об организации из ЕСИА."""
    
    sub: str = Field(..., description="Субъект (ID пользователя)")
    info: Dict[str, Any] = Field(..., description="Информация об организации")


class ESIAGroupsInfo(BaseModel):
    """Схема информации о группах доступа из ЕСИА."""
    
    sub: str = Field(..., description="Субъект (ID пользователя)")
    info: Dict[str, Any] = Field(..., description="Информация о группах доступа")