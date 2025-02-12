import logging
import os
from logging.handlers import RotatingFileHandler
from config.settings import LOGS_DIR

# Создаем форматтер для логов
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    '%Y-%m-%d %H:%M:%S'
)

# Создаем файловый обработчик с ротацией
file_handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, 'bot.log'),
    maxBytes=10485760,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(formatter)

# Создаем консольный обработчик
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Настраиваем логгер
logger = logging.getLogger('FilmBot')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)