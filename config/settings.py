import os
from dotenv import load_dotenv

load_dotenv()

# Токены и ID
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
NEWS_CHANNEL_ID = f"{os.getenv('NEWS_CHANNEL_NAME')}"
ADMIN_IDS = os.getenv('ADMIN_IDS', '').split(',')

# Пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
DATA_DIR = os.path.join(BASE_DIR, 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# Создаем необходимые директории
for directory in [LOGS_DIR, DATA_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)