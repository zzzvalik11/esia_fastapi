"""Создание таблиц для ЕСИА Gateway

Revision ID: 001_create_esia_tables
Revises: 
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001_create_esia_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Создание всех таблиц для ЕСИА Gateway."""
    
    # Создание таблицы пользователей
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False, comment='Внутренний ID пользователя'),
        sa.Column('esia_uid', sa.String(50), nullable=False, comment='UID пользователя в ЕСИА'),
        sa.Column('first_name', sa.String(100), nullable=True, comment='Имя пользователя'),
        sa.Column('last_name', sa.String(100), nullable=True, comment='Фамилия пользователя'),
        sa.Column('middle_name', sa.String(100), nullable=True, comment='Отчество пользователя'),
        sa.Column('trusted', sa.Boolean(), nullable=True, default=False, comment='Подтвержденная учетная запись'),
        sa.Column('status', sa.String(50), nullable=True, comment='Статус пользователя в ЕСИА'),
        sa.Column('verifying', sa.Boolean(), nullable=True, default=False, comment='Процесс верификации'),
        sa.Column('r_id_doc', sa.Integer(), nullable=True, comment='ID документа в ЕСИА'),
        sa.Column('contains_up_cfm_code', sa.Boolean(), nullable=True, default=False, comment='Содержит код подтверждения'),
        sa.Column('e_tag', sa.String(255), nullable=True, comment='ETag для кэширования'),
        sa.Column('updated_on', sa.Integer(), nullable=True, comment='Время последнего обновления в ЕСИА'),
        sa.Column('state_facts', sa.JSON(), nullable=True, comment='Факты состояния пользователя'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время создания записи'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время обновления записи'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('esia_uid'),
        comment='Пользователи ЕСИА'
    )
    op.create_index('idx_users_esia_uid', 'users', ['esia_uid'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])

    # Создание таблицы токенов пользователей
    op.create_table('user_tokens',
        sa.Column('id', sa.Integer(), nullable=False, comment='ID токена'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='ID пользователя'),
        sa.Column('access_token', sa.Text(), nullable=False, comment='Токен доступа'),
        sa.Column('refresh_token', sa.String(255), nullable=True, comment='Токен обновления'),
        sa.Column('token_type', sa.String(50), nullable=True, default='Bearer', comment='Тип токена'),
        sa.Column('expires_in', sa.Integer(), nullable=True, comment='Время жизни токена в секундах'),
        sa.Column('scope', sa.String(500), nullable=True, comment='Области доступа'),
        sa.Column('id_token', sa.Text(), nullable=True, comment='ID токен'),
        sa.Column('created_at_timestamp', sa.Integer(), nullable=True, comment='Время создания токена (timestamp)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время создания записи'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время обновления записи'),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True, comment='Активность токена'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Токены пользователей'
    )
    op.create_index('idx_user_tokens_user_id', 'user_tokens', ['user_id'])
    op.create_index('idx_user_tokens_is_active', 'user_tokens', ['is_active'])
    op.create_index('idx_user_tokens_created_at', 'user_tokens', ['created_at'])

    # Создание таблицы запросов авторизации
    op.create_table('authorization_requests',
        sa.Column('id', sa.Integer(), nullable=False, comment='ID запроса авторизации'),
        sa.Column('client_id', sa.String(255), nullable=False, comment='ID клиентской системы'),
        sa.Column('response_type', sa.String(50), nullable=False, comment='Тип ответа'),
        sa.Column('provider', sa.String(50), nullable=False, comment='Провайдер данных'),
        sa.Column('scope', sa.Text(), nullable=False, comment='Области доступа'),
        sa.Column('redirect_uri', sa.String(500), nullable=False, comment='URI возврата'),
        sa.Column('state', sa.String(255), nullable=False, comment='Состояние запроса'),
        sa.Column('nonce', sa.String(255), nullable=True, comment='Nonce для предотвращения подделки'),
        sa.Column('authorization_code', sa.String(255), nullable=True, comment='Полученный код авторизации'),
        sa.Column('error', sa.String(100), nullable=True, comment='Код ошибки'),
        sa.Column('error_description', sa.Text(), nullable=True, comment='Описание ошибки'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время создания запроса'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='Время завершения запроса'),
        sa.Column('is_completed', sa.Boolean(), nullable=True, default=False, comment='Запрос завершен'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('state'),
        comment='Запросы авторизации'
    )
    op.create_index('idx_authorization_requests_state', 'authorization_requests', ['state'])
    op.create_index('idx_authorization_requests_client_id', 'authorization_requests', ['client_id'])
    op.create_index('idx_authorization_requests_created_at', 'authorization_requests', ['created_at'])
    op.create_index('idx_authorization_requests_is_completed', 'authorization_requests', ['is_completed'])

    # Создание таблицы организаций
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False, comment='Внутренний ID организации'),
        sa.Column('esia_oid', sa.Integer(), nullable=False, comment='OID организации в ЕСИА'),
        sa.Column('prn_oid', sa.Integer(), nullable=True, comment='OID родительской организации'),
        sa.Column('full_name', sa.String(500), nullable=True, comment='Полное наименование организации'),
        sa.Column('short_name', sa.String(255), nullable=True, comment='Сокращенное наименование организации'),
        sa.Column('ogrn', sa.String(50), nullable=True, comment='ОГРН организации'),
        sa.Column('inn', sa.String(20), nullable=True, comment='ИНН организации'),
        sa.Column('kpp', sa.String(20), nullable=True, comment='КПП организации'),
        sa.Column('org_type', sa.String(50), nullable=True, comment='Тип организации'),
        sa.Column('leg', sa.String(255), nullable=True, comment='ОПФ организации'),
        sa.Column('oktmo', sa.String(20), nullable=True, comment='ОКТМО организации'),
        sa.Column('phone', sa.String(50), nullable=True, comment='Телефон организации'),
        sa.Column('email', sa.String(255), nullable=True, comment='Email организации'),
        sa.Column('is_chief', sa.Boolean(), nullable=True, default=False, comment='Руководитель организации'),
        sa.Column('is_admin', sa.Boolean(), nullable=True, default=False, comment='Администратор организации'),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True, comment='Активная организация'),
        sa.Column('has_right_of_substitution', sa.Boolean(), nullable=True, default=False, comment='Право замещения'),
        sa.Column('has_approval_tab_access', sa.Boolean(), nullable=True, default=False, comment='Доступ к вкладке согласования'),
        sa.Column('is_liquidated', sa.Boolean(), nullable=True, default=False, comment='Ликвидированная организация'),
        sa.Column('staff_count', sa.Integer(), nullable=True, comment='Количество сотрудников'),
        sa.Column('agency_ter_range', sa.String(255), nullable=True, comment='Территориальная принадлежность ОГВ'),
        sa.Column('agency_type', sa.String(100), nullable=True, comment='Тип ОГВ'),
        sa.Column('e_tag', sa.String(255), nullable=True, comment='ETag для кэширования'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время создания записи'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время обновления записи'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('esia_oid'),
        comment='Организации ЕСИА'
    )
    op.create_index('idx_organizations_esia_oid', 'organizations', ['esia_oid'])
    op.create_index('idx_organizations_inn', 'organizations', ['inn'])
    op.create_index('idx_organizations_ogrn', 'organizations', ['ogrn'])
    op.create_index('idx_organizations_is_active', 'organizations', ['is_active'])
    op.create_index('idx_organizations_created_at', 'organizations', ['created_at'])

    # Создание таблицы адресов организаций
    op.create_table('organization_addresses',
        sa.Column('id', sa.Integer(), nullable=False, comment='ID адреса'),
        sa.Column('organization_id', sa.Integer(), nullable=False, comment='ID организации'),
        sa.Column('address_type', sa.String(50), nullable=False, comment='Тип адреса (postal, legal)'),
        sa.Column('postal_code', sa.String(10), nullable=True, comment='Почтовый индекс'),
        sa.Column('country_id', sa.String(10), nullable=True, comment='Идентификатор страны'),
        sa.Column('address_str', sa.String(500), nullable=True, comment='Адрес строкой'),
        sa.Column('building', sa.String(20), nullable=True, comment='Строение'),
        sa.Column('corpus', sa.String(20), nullable=True, comment='Корпус'),
        sa.Column('house', sa.String(20), nullable=True, comment='Дом'),
        sa.Column('apartment', sa.String(20), nullable=True, comment='Квартира'),
        sa.Column('fias_code', sa.String(50), nullable=True, comment='Код ФИАС'),
        sa.Column('region', sa.String(100), nullable=True, comment='Регион'),
        sa.Column('city', sa.String(100), nullable=True, comment='Город'),
        sa.Column('inner_city_district', sa.String(100), nullable=True, comment='Внутригородской район'),
        sa.Column('district', sa.String(100), nullable=True, comment='Район'),
        sa.Column('settlement', sa.String(100), nullable=True, comment='Поселение'),
        sa.Column('additional_territory', sa.String(100), nullable=True, comment='Дополнительная территория'),
        sa.Column('additional_territory_street', sa.String(100), nullable=True, comment='Улица на дополнительной территории'),
        sa.Column('street', sa.String(100), nullable=True, comment='Улица'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время создания записи'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время обновления записи'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Адреса организаций'
    )
    op.create_index('idx_organization_addresses_org_id', 'organization_addresses', ['organization_id'])
    op.create_index('idx_organization_addresses_type', 'organization_addresses', ['address_type'])
    op.create_index('idx_organization_addresses_created_at', 'organization_addresses', ['created_at'])

    # Создание таблицы групп доступа организаций
    op.create_table('organization_groups',
        sa.Column('id', sa.Integer(), nullable=False, comment='ID группы'),
        sa.Column('organization_id', sa.Integer(), nullable=False, comment='ID организации'),
        sa.Column('group_id', sa.String(100), nullable=False, comment='Мнемоника группы'),
        sa.Column('name', sa.String(255), nullable=True, comment='Название группы'),
        sa.Column('description', sa.Text(), nullable=True, comment='Описание группы'),
        sa.Column('is_system', sa.Boolean(), nullable=True, default=False, comment='Системная группа'),
        sa.Column('it_system', sa.String(100), nullable=True, comment='Мнемоника системы-владельца'),
        sa.Column('esia_url', sa.String(500), nullable=True, comment='URL группы в ЕСИА'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время создания записи'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время обновления записи'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Группы доступа организаций'
    )
    op.create_index('idx_organization_groups_org_id', 'organization_groups', ['organization_id'])
    op.create_index('idx_organization_groups_group_id', 'organization_groups', ['group_id'])
    op.create_index('idx_organization_groups_is_system', 'organization_groups', ['is_system'])
    op.create_index('idx_organization_groups_created_at', 'organization_groups', ['created_at'])
    op.create_index('uk_organization_groups_org_group', 'organization_groups', ['organization_id', 'group_id'], unique=True)

    # Создание таблицы связей пользователей с организациями
    op.create_table('user_organizations',
        sa.Column('id', sa.Integer(), nullable=False, comment='ID связи'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='ID пользователя'),
        sa.Column('organization_id', sa.Integer(), nullable=False, comment='ID организации'),
        sa.Column('is_chief', sa.Boolean(), nullable=True, default=False, comment='Руководитель'),
        sa.Column('is_admin', sa.Boolean(), nullable=True, default=False, comment='Администратор'),
        sa.Column('has_right_of_substitution', sa.Boolean(), nullable=True, default=False, comment='Право замещения'),
        sa.Column('has_approval_tab_access', sa.Boolean(), nullable=True, default=False, comment='Доступ к вкладке согласования'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время создания связи'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Время обновления связи'),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True, comment='Активная связь'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Связи пользователей с организациями'
    )
    op.create_index('idx_user_organizations_user_id', 'user_organizations', ['user_id'])
    op.create_index('idx_user_organizations_org_id', 'user_organizations', ['organization_id'])
    op.create_index('idx_user_organizations_is_active', 'user_organizations', ['is_active'])
    op.create_index('idx_user_organizations_created_at', 'user_organizations', ['created_at'])
    op.create_index('uk_user_organizations_user_org', 'user_organizations', ['user_id', 'organization_id'], unique=True)


def downgrade() -> None:
    """Удаление всех таблиц ЕСИА Gateway."""
    
    op.drop_table('user_organizations')
    op.drop_table('organization_groups')
    op.drop_table('organization_addresses')
    op.drop_table('organizations')
    op.drop_table('authorization_requests')
    op.drop_table('user_tokens')
    op.drop_table('users')