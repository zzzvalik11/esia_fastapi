"""
Конфигурация среды Alembic для миграций базы данных.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Добавление корневой директории проекта в путь
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.database import Base

# Конфигурация Alembic
config = context.config

# Установка URL базы данных из настроек приложения
config.set_main_option("sqlalchemy.url", settings.database_url)

# Интерпретация файла конфигурации для логирования Python
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Добавление метаданных модели для поддержки 'autogenerate'
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Запуск миграций в 'offline' режиме.
    
    Это настраивает контекст только с URL
    и не с движком, хотя движок также приемлем
    здесь. Пропуская создание движка
    мы даже не нуждаемся в DBAPI для доступности.
    
    Вызовы context.execute() здесь выдают данную строку в
    выходной файл скрипта.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Запуск миграций в 'online' режиме.
    
    В этом сценарии нам нужно создать движок
    и связать соединение с контекстом.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()