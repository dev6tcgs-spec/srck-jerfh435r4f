"""Система логирования для продакшена"""

import logging
import os
from datetime import datetime
from pathlib import Path

# Создаем директорию для логов
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Настройка логирования
def setup_logger():
    """Настройка системы логирования"""
    
    # Формат логов
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Основной логгер
    logger = logging.getLogger('winter_fair_bot')
    logger.setLevel(logging.INFO)
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Файловый обработчик (ротация по дням)
    log_file = LOG_DIR / f"bot_{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Обработчик ошибок (отдельный файл)
    error_log_file = LOG_DIR / "errors.log"
    error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)
    
    return logger

# Глобальный логгер
logger = setup_logger()

def log_error(error: Exception, context: str = ""):
    """Логирование ошибок с контекстом"""
    logger.error(f"ERROR in {context}: {type(error).__name__}: {str(error)}", exc_info=True)

def log_info(message: str, data: dict = None):
    """Логирование информации"""
    if data:
        logger.info(f"{message} | Data: {data}")
    else:
        logger.info(message)

def log_warning(message: str, data: dict = None):
    """Логирование предупреждений"""
    if data:
        logger.warning(f"{message} | Data: {data}")
    else:
        logger.warning(message)

