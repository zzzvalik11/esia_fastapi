"""
Модели организаций для работы с ЕСИА.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Organization(Base):
    """
    Модель организации из ЕСИА.
    Хранит основную информацию об организации.
    """
    
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True, comment="Внутренний ID организации")
    esia_oid = Column(Integer, unique=True, index=True, nullable=False, comment="OID организации в ЕСИА")
    prn_oid = Column(Integer, comment="OID родительской организации")
    full_name = Column(String(500), comment="Полное наименование организации")
    short_name = Column(String(255), comment="Сокращенное наименование организации")
    ogrn = Column(String(50), comment="ОГРН организации")
    inn = Column(String(20), comment="ИНН организации")
    kpp = Column(String(20), comment="КПП организации")
    org_type = Column(String(50), comment="Тип организации")
    leg = Column(String(255), comment="ОПФ организации")
    oktmo = Column(String(20), comment="ОКТМО организации")
    
    # Контактная информация
    phone = Column(String(50), comment="Телефон организации")
    email = Column(String(255), comment="Email организации")
    
    # Статусы и флаги
    is_chief = Column(Boolean, default=False, comment="Руководитель организации")
    is_admin = Column(Boolean, default=False, comment="Администратор организации")
    is_active = Column(Boolean, default=True, comment="Активная организация")
    has_right_of_substitution = Column(Boolean, default=False, comment="Право замещения")
    has_approval_tab_access = Column(Boolean, default=False, comment="Доступ к вкладке согласования")
    is_liquidated = Column(Boolean, default=False, comment="Ликвидированная организация")
    
    # Дополнительные данные
    staff_count = Column(Integer, comment="Количество сотрудников")
    agency_ter_range = Column(String(255), comment="Территориальная принадлежность ОГВ")
    agency_type = Column(String(100), comment="Тип ОГВ")
    e_tag = Column(String(255), comment="ETag для кэширования")
    
    # Системные поля
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Время создания записи")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Время обновления записи")
    
    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, esia_oid={self.esia_oid}, name='{self.short_name}')>"


class OrganizationAddress(Base):
    """
    Модель адресов организации.
    Хранит почтовые и юридические адреса организаций.
    """
    
    __tablename__ = "organization_addresses"
    
    id = Column(Integer, primary_key=True, index=True, comment="ID адреса")
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, comment="ID организации")
    address_type = Column(String(50), nullable=False, comment="Тип адреса (postal, legal)")
    
    # Компоненты адреса
    postal_code = Column(String(10), comment="Почтовый индекс")
    country_id = Column(String(10), comment="Идентификатор страны")
    address_str = Column(String(500), comment="Адрес строкой")
    building = Column(String(20), comment="Строение")
    corpus = Column(String(20), comment="Корпус")
    house = Column(String(20), comment="Дом")
    apartment = Column(String(20), comment="Квартира")
    fias_code = Column(String(50), comment="Код ФИАС")
    region = Column(String(100), comment="Регион")
    city = Column(String(100), comment="Город")
    inner_city_district = Column(String(100), comment="Внутригородской район")
    district = Column(String(100), comment="Район")
    settlement = Column(String(100), comment="Поселение")
    additional_territory = Column(String(100), comment="Дополнительная территория")
    additional_territory_street = Column(String(100), comment="Улица на дополнительной территории")
    street = Column(String(100), comment="Улица")
    
    # Системные поля
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Время создания записи")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Время обновления записи")
    
    # Связи
    organization = relationship("Organization", backref="addresses")
    
    def __repr__(self) -> str:
        return f"<OrganizationAddress(id={self.id}, org_id={self.organization_id}, type='{self.address_type}')>"


class OrganizationGroup(Base):
    """
    Модель групп доступа организации.
    Хранит информацию о группах доступа и правах пользователей.
    """
    
    __tablename__ = "organization_groups"
    
    id = Column(Integer, primary_key=True, index=True, comment="ID группы")
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, comment="ID организации")
    group_id = Column(String(100), nullable=False, comment="Мнемоника группы")
    name = Column(String(255), comment="Название группы")
    description = Column(Text, comment="Описание группы")
    is_system = Column(Boolean, default=False, comment="Системная группа")
    it_system = Column(String(100), comment="Мнемоника системы-владельца")
    esia_url = Column(String(500), comment="URL группы в ЕСИА")
    
    # Системные поля
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Время создания записи")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Время обновления записи")
    
    # Связи
    organization = relationship("Organization", backref="groups")
    
    def __repr__(self) -> str:
        return f"<OrganizationGroup(id={self.id}, group_id='{self.group_id}', name='{self.name}')>"


class UserOrganization(Base):
    """
    Модель связи пользователей с организациями.
    Хранит информацию о принадлежности пользователей к организациям.
    """
    
    __tablename__ = "user_organizations"
    
    id = Column(Integer, primary_key=True, index=True, comment="ID связи")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="ID пользователя")
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, comment="ID организации")
    
    # Роли и права
    is_chief = Column(Boolean, default=False, comment="Руководитель")
    is_admin = Column(Boolean, default=False, comment="Администратор")
    has_right_of_substitution = Column(Boolean, default=False, comment="Право замещения")
    has_approval_tab_access = Column(Boolean, default=False, comment="Доступ к вкладке согласования")
    
    # Системные поля
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Время создания связи")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Время обновления связи")
    is_active = Column(Boolean, default=True, comment="Активная связь")
    
    def __repr__(self) -> str:
        return f"<UserOrganization(id={self.id}, user_id={self.user_id}, org_id={self.organization_id})>"