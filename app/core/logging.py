"""
Настройка логирования приложения.
Создает ежедневные файлы логов с ротацией.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """
    Настраивает систему логирования с ежедневной ротацией файлов.
    Создает отдельные логи для разных уровней важности.
    """
    
    # Создание директории для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настройка форматирования
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Очистка существующих обработчиков
    root_logger.handlers.clear()
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # Файловый обработчик для всех логов
    all_logs_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir / "app.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    all_logs_handler.setFormatter(formatter)
    all_logs_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(all_logs_handler)
    
    # Файловый обработчик для ошибок
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir / "errors.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)
    
    # Логгер для ЕСИА операций
    esia_logger = logging.getLogger("esia")
    esia_logger.handlers.clear()  # Очистка существующих обработчиков для предотвращения дублей
    esia_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir / "esia.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    esia_handler.setFormatter(formatter)
    esia_logger.addHandler(esia_handler)
    esia_logger.setLevel(logging.INFO)
    esia_logger.propagate = False  # Предотвращение передачи логов в родительский логгер
    
    return root_logger


# Инициализация логирования
logger = setup_logging()