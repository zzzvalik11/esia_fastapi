/*
  # Создание базовой структуры базы данных ЕСИА Gateway

  1. Новые таблицы
    - `users` - пользователи ЕСИА
      - `id` (int, primary key) - внутренний ID пользователя
      - `esia_uid` (varchar(50), unique) - UID пользователя в ЕСИА
      - `first_name` (varchar(100)) - имя пользователя
      - `last_name` (varchar(100)) - фамилия пользователя
      - `middle_name` (varchar(100)) - отчество пользователя
      - `trusted` (boolean) - подтвержденная учетная запись
      - `status` (varchar(50)) - статус пользователя в ЕСИА
      - `verifying` (boolean) - процесс верификации
      - `r_id_doc` (int) - ID документа в ЕСИА
      - `contains_up_cfm_code` (boolean) - содержит код подтверждения
      - `e_tag` (varchar(255)) - ETag для кэширования
      - `updated_on` (int) - время последнего обновления в ЕСИА
      - `state_facts` (json) - факты состояния пользователя
      - `created_at` (datetime) - время создания записи
      - `updated_at` (datetime) - время обновления записи

    - `user_tokens` - токены пользователей
      - `id` (int, primary key) - ID токена
      - `user_id` (int) - ID пользователя
      - `access_token` (text) - токен доступа
      - `refresh_token` (varchar(255)) - токен обновления
      - `token_type` (varchar(50)) - тип токена
      - `expires_in` (int) - время жизни токена в секундах
      - `scope` (varchar(500)) - области доступа
      - `id_token` (text) - ID токен
      - `created_at_timestamp` (int) - время создания токена (timestamp)
      - `created_at` (datetime) - время создания записи
      - `updated_at` (datetime) - время обновления записи
      - `is_active` (boolean) - активность токена

    - `authorization_requests` - запросы авторизации
      - `id` (int, primary key) - ID запроса авторизации
      - `client_id` (varchar(255)) - ID клиентской системы
      - `response_type` (varchar(50)) - тип ответа
      - `provider` (varchar(50)) - провайдер данных
      - `scope` (text) - области доступа
      - `redirect_uri` (varchar(500)) - URI возврата
      - `state` (varchar(255), unique) - состояние запроса
      - `nonce` (varchar(255)) - nonce для предотвращения подделки
      - `authorization_code` (varchar(255)) - полученный код авторизации
      - `error` (varchar(100)) - код ошибки
      - `error_description` (text) - описание ошибки
      - `created_at` (datetime) - время создания запроса
      - `completed_at` (datetime) - время завершения запроса
      - `is_completed` (boolean) - запрос завершен

    - `organizations` - организации ЕСИА
      - `id` (int, primary key) - внутренний ID организации
      - `esia_oid` (int, unique) - OID организации в ЕСИА
      - `prn_oid` (int) - OID родительской организации
      - `full_name` (varchar(500)) - полное наименование организации
      - `short_name` (varchar(255)) - сокращенное наименование организации
      - `ogrn` (varchar(50)) - ОГРН организации
      - `inn` (varchar(20)) - ИНН организации
      - `kpp` (varchar(20)) - КПП организации
      - `org_type` (varchar(50)) - тип организации
      - `leg` (varchar(255)) - ОПФ организации
      - `oktmo` (varchar(20)) - ОКТМО организации
      - `phone` (varchar(50)) - телефон организации
      - `email` (varchar(255)) - email организации
      - `is_chief` (boolean) - руководитель организации
      - `is_admin` (boolean) - администратор организации
      - `is_active` (boolean) - активная организация
      - `has_right_of_substitution` (boolean) - право замещения
      - `has_approval_tab_access` (boolean) - доступ к вкладке согласования
      - `is_liquidated` (boolean) - ликвидированная организация
      - `staff_count` (int) - количество сотрудников
      - `agency_ter_range` (varchar(255)) - территориальная принадлежность ОГВ
      - `agency_type` (varchar(100)) - тип ОГВ
      - `e_tag` (varchar(255)) - ETag для кэширования
      - `created_at` (datetime) - время создания записи
      - `updated_at` (datetime) - время обновления записи

    - `organization_addresses` - адреса организаций
      - `id` (int, primary key) - ID адреса
      - `organization_id` (int, foreign key) - ID организации
      - `address_type` (varchar(50)) - тип адреса (postal, legal)
      - `postal_code` (varchar(10)) - почтовый индекс
      - `country_id` (varchar(10)) - идентификатор страны
      - `address_str` (varchar(500)) - адрес строкой
      - `building` (varchar(20)) - строение
      - `corpus` (varchar(20)) - корпус
      - `house` (varchar(20)) - дом
      - `apartment` (varchar(20)) - квартира
      - `fias_code` (varchar(50)) - код ФИАС
      - `region` (varchar(100)) - регион
      - `city` (varchar(100)) - город
      - `inner_city_district` (varchar(100)) - внутригородской район
      - `district` (varchar(100)) - район
      - `settlement` (varchar(100)) - поселение
      - `additional_territory` (varchar(100)) - дополнительная территория
      - `additional_territory_street` (varchar(100)) - улица на дополнительной территории
      - `street` (varchar(100)) - улица
      - `created_at` (datetime) - время создания записи
      - `updated_at` (datetime) - время обновления записи

    - `organization_groups` - группы доступа организаций
      - `id` (int, primary key) - ID группы
      - `organization_id` (int, foreign key) - ID организации
      - `group_id` (varchar(100)) - мнемоника группы
      - `name` (varchar(255)) - название группы
      - `description` (text) - описание группы
      - `is_system` (boolean) - системная группа
      - `it_system` (varchar(100)) - мнемоника системы-владельца
      - `esia_url` (varchar(500)) - URL группы в ЕСИА
      - `created_at` (datetime) - время создания записи
      - `updated_at` (datetime) - время обновления записи

    - `user_organizations` - связи пользователей с организациями
      - `id` (int, primary key) - ID связи
      - `user_id` (int, foreign key) - ID пользователя
      - `organization_id` (int, foreign key) - ID организации
      - `is_chief` (boolean) - руководитель
      - `is_admin` (boolean) - администратор
      - `has_right_of_substitution` (boolean) - право замещения
      - `has_approval_tab_access` (boolean) - доступ к вкладке согласования
      - `created_at` (datetime) - время создания связи
      - `updated_at` (datetime) - время обновления связи
      - `is_active` (boolean) - активная связь

  2. Индексы
    - Индексы на внешние ключи для оптимизации запросов
    - Индексы на часто используемые поля поиска

  3. Ограничения
    - Внешние ключи для обеспечения целостности данных
    - Уникальные ограничения для предотвращения дублирования
*/

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Внутренний ID пользователя',
    esia_uid VARCHAR(50) NOT NULL UNIQUE COMMENT 'UID пользователя в ЕСИА',
    first_name VARCHAR(100) COMMENT 'Имя пользователя',
    last_name VARCHAR(100) COMMENT 'Фамилия пользователя',
    middle_name VARCHAR(100) COMMENT 'Отчество пользователя',
    trusted BOOLEAN DEFAULT FALSE COMMENT 'Подтвержденная учетная запись',
    status VARCHAR(50) COMMENT 'Статус пользователя в ЕСИА',
    verifying BOOLEAN DEFAULT FALSE COMMENT 'Процесс верификации',
    r_id_doc INT COMMENT 'ID документа в ЕСИА',
    contains_up_cfm_code BOOLEAN DEFAULT FALSE COMMENT 'Содержит код подтверждения',
    e_tag VARCHAR(255) COMMENT 'ETag для кэширования',
    updated_on INT COMMENT 'Время последнего обновления в ЕСИА',
    state_facts JSON COMMENT 'Факты состояния пользователя',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Время создания записи',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Время обновления записи',
    INDEX idx_users_esia_uid (esia_uid),
    INDEX idx_users_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Пользователи ЕСИА';

-- Создание таблицы токенов пользователей
CREATE TABLE IF NOT EXISTS user_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID токена',
    user_id INT NOT NULL COMMENT 'ID пользователя',
    access_token TEXT NOT NULL COMMENT 'Токен доступа',
    refresh_token VARCHAR(255) COMMENT 'Токен обновления',
    token_type VARCHAR(50) DEFAULT 'Bearer' COMMENT 'Тип токена',
    expires_in INT COMMENT 'Время жизни токена в секундах',
    scope VARCHAR(500) COMMENT 'Области доступа',
    id_token TEXT COMMENT 'ID токен',
    created_at_timestamp INT COMMENT 'Время создания токена (timestamp)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Время создания записи',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Время обновления записи',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Активность токена',
    INDEX idx_user_tokens_user_id (user_id),
    INDEX idx_user_tokens_is_active (is_active),
    INDEX idx_user_tokens_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Токены пользователей';

-- Создание таблицы запросов авторизации
CREATE TABLE IF NOT EXISTS authorization_requests (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID запроса авторизации',
    client_id VARCHAR(255) NOT NULL COMMENT 'ID клиентской системы',
    response_type VARCHAR(50) NOT NULL COMMENT 'Тип ответа',
    provider VARCHAR(50) NOT NULL COMMENT 'Провайдер данных',
    scope TEXT NOT NULL COMMENT 'Области доступа',
    redirect_uri VARCHAR(500) NOT NULL COMMENT 'URI возврата',
    state VARCHAR(255) NOT NULL UNIQUE COMMENT 'Состояние запроса',
    nonce VARCHAR(255) COMMENT 'Nonce для предотвращения подделки',
    authorization_code VARCHAR(255) COMMENT 'Полученный код авторизации',
    error VARCHAR(100) COMMENT 'Код ошибки',
    error_description TEXT COMMENT 'Описание ошибки',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Время создания запроса',
    completed_at DATETIME COMMENT 'Время завершения запроса',
    is_completed BOOLEAN DEFAULT FALSE COMMENT 'Запрос завершен',
    INDEX idx_authorization_requests_state (state),
    INDEX idx_authorization_requests_client_id (client_id),
    INDEX idx_authorization_requests_created_at (created_at),
    INDEX idx_authorization_requests_is_completed (is_completed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Запросы авторизации';

-- Создание таблицы организаций
CREATE TABLE IF NOT EXISTS organizations (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Внутренний ID организации',
    esia_oid INT NOT NULL UNIQUE COMMENT 'OID организации в ЕСИА',
    prn_oid INT COMMENT 'OID родительской организации',
    full_name VARCHAR(500) COMMENT 'Полное наименование организации',
    short_name VARCHAR(255) COMMENT 'Сокращенное наименование организации',
    ogrn VARCHAR(50) COMMENT 'ОГРН организации',
    inn VARCHAR(20) COMMENT 'ИНН организации',
    kpp VARCHAR(20) COMMENT 'КПП организации',
    org_type VARCHAR(50) COMMENT 'Тип организации',
    leg VARCHAR(255) COMMENT 'ОПФ организации',
    oktmo VARCHAR(20) COMMENT 'ОКТМО организации',
    phone VARCHAR(50) COMMENT 'Телефон организации',
    email VARCHAR(255) COMMENT 'Email организации',
    is_chief BOOLEAN DEFAULT FALSE COMMENT 'Руководитель организации',
    is_admin BOOLEAN DEFAULT FALSE COMMENT 'Администратор организации',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Активная организация',
    has_right_of_substitution BOOLEAN DEFAULT FALSE COMMENT 'Право замещения',
    has_approval_tab_access BOOLEAN DEFAULT FALSE COMMENT 'Доступ к вкладке согласования',
    is_liquidated BOOLEAN DEFAULT FALSE COMMENT 'Ликвидированная организация',
    staff_count INT COMMENT 'Количество сотрудников',
    agency_ter_range VARCHAR(255) COMMENT 'Территориальная принадлежность ОГВ',
    agency_type VARCHAR(100) COMMENT 'Тип ОГВ',
    e_tag VARCHAR(255) COMMENT 'ETag для кэширования',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Время создания записи',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Время обновления записи',
    INDEX idx_organizations_esia_oid (esia_oid),
    INDEX idx_organizations_inn (inn),
    INDEX idx_organizations_ogrn (ogrn),
    INDEX idx_organizations_is_active (is_active),
    INDEX idx_organizations_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Организации ЕСИА';

-- Создание таблицы адресов организаций
CREATE TABLE IF NOT EXISTS organization_addresses (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID адреса',
    organization_id INT NOT NULL COMMENT 'ID организации',
    address_type VARCHAR(50) NOT NULL COMMENT 'Тип адреса (postal, legal)',
    postal_code VARCHAR(10) COMMENT 'Почтовый индекс',
    country_id VARCHAR(10) COMMENT 'Идентификатор страны',
    address_str VARCHAR(500) COMMENT 'Адрес строкой',
    building VARCHAR(20) COMMENT 'Строение',
    corpus VARCHAR(20) COMMENT 'Корпус',
    house VARCHAR(20) COMMENT 'Дом',
    apartment VARCHAR(20) COMMENT 'Квартира',
    fias_code VARCHAR(50) COMMENT 'Код ФИАС',
    region VARCHAR(100) COMMENT 'Регион',
    city VARCHAR(100) COMMENT 'Город',
    inner_city_district VARCHAR(100) COMMENT 'Внутригородской район',
    district VARCHAR(100) COMMENT 'Район',
    settlement VARCHAR(100) COMMENT 'Поселение',
    additional_territory VARCHAR(100) COMMENT 'Дополнительная территория',
    additional_territory_street VARCHAR(100) COMMENT 'Улица на дополнительной территории',
    street VARCHAR(100) COMMENT 'Улица',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Время создания записи',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Время обновления записи',
    INDEX idx_organization_addresses_org_id (organization_id),
    INDEX idx_organization_addresses_type (address_type),
    INDEX idx_organization_addresses_created_at (created_at),
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Адреса организаций';

-- Создание таблицы групп доступа организаций
CREATE TABLE IF NOT EXISTS organization_groups (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID группы',
    organization_id INT NOT NULL COMMENT 'ID организации',
    group_id VARCHAR(100) NOT NULL COMMENT 'Мнемоника группы',
    name VARCHAR(255) COMMENT 'Название группы',
    description TEXT COMMENT 'Описание группы',
    is_system BOOLEAN DEFAULT FALSE COMMENT 'Системная группа',
    it_system VARCHAR(100) COMMENT 'Мнемоника системы-владельца',
    esia_url VARCHAR(500) COMMENT 'URL группы в ЕСИА',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Время создания записи',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Время обновления записи',
    INDEX idx_organization_groups_org_id (organization_id),
    INDEX idx_organization_groups_group_id (group_id),
    INDEX idx_organization_groups_is_system (is_system),
    INDEX idx_organization_groups_created_at (created_at),
    UNIQUE KEY uk_organization_groups_org_group (organization_id, group_id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Группы доступа организаций';

-- Создание таблицы связей пользователей с организациями
CREATE TABLE IF NOT EXISTS user_organizations (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID связи',
    user_id INT NOT NULL COMMENT 'ID пользователя',
    organization_id INT NOT NULL COMMENT 'ID организации',
    is_chief BOOLEAN DEFAULT FALSE COMMENT 'Руководитель',
    is_admin BOOLEAN DEFAULT FALSE COMMENT 'Администратор',
    has_right_of_substitution BOOLEAN DEFAULT FALSE COMMENT 'Право замещения',
    has_approval_tab_access BOOLEAN DEFAULT FALSE COMMENT 'Доступ к вкладке согласования',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Время создания связи',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Время обновления связи',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Активная связь',
    INDEX idx_user_organizations_user_id (user_id),
    INDEX idx_user_organizations_org_id (organization_id),
    INDEX idx_user_organizations_is_active (is_active),
    INDEX idx_user_organizations_created_at (created_at),
    UNIQUE KEY uk_user_organizations_user_org (user_id, organization_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Связи пользователей с организациями';