import json
import os
from datetime import datetime
from config.settings import DATA_DIR
from utils.logger import logger

FILMS_FILE = os.path.join(DATA_DIR, 'films.json')

def save_film_id(message_id: int, description: str = "") -> None:
    try:
        if os.path.exists(FILMS_FILE):
            with open(FILMS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"films": []}
        
        film_data = {
            "message_id": message_id,
            "description": description,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Проверяем, нет ли уже такого ID
        if not any(film['message_id'] == message_id for film in data['films']):
            data["films"].append(film_data)
            
            with open(FILMS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"Сохранен новый ID фильма: {message_id}")
        else:
            logger.warning(f"ID фильма {message_id} уже существует")
            
    except Exception as e:
        logger.error(f"Ошибка при сохранении ID фильма: {e}")

def get_last_film_id() -> dict:
    try:
        if os.path.exists(FILMS_FILE):
            with open(FILMS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data["films"]:
                    return data["films"][-1]
        logger.info("Запрошен последний ID фильма")
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении последнего ID фильма: {e}")
        return None

def get_all_film_ids() -> list:
    try:
        if os.path.exists(FILMS_FILE):
            with open(FILMS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Запрошен список всех ID фильмов. Всего: {len(data['films'])}")
                return data["films"]
        return []
    except Exception as e:
        logger.error(f"Ошибка при получении списка ID фильмов: {e}")
        return []
