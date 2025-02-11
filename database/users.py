import json
from datetime import datetime
import pytz
from config.settings import USERS_FILE
from utils.logger import logger

UZB_TIMEZONE = pytz.timezone('Asia/Tashkent')

def get_uzb_time():
    return datetime.now(UZB_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

def load_users():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": [], "total_count": 0}

def save_user(user_data):
    users_info = load_users()
    if not any(user["id"] == user_data["id"] for user in users_info["users"]):
        user_data["joined_date"] = get_uzb_time()
        users_info["users"].append(user_data)
        users_info["total_count"] = len(users_info["users"])
        
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_info, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Новый пользователь сохранен: {user_data.get('username', 'Без username')}")