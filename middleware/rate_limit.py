from collections import defaultdict
from datetime import datetime
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger

class RateLimiter:
    def __init__(self):
        self.last_request = defaultdict(lambda: defaultdict(lambda: datetime.min))
        # Разные задержки для разных типов сообщений
        self.COOLDOWNS = {
            'message': 1,    # 1 секунда для обычных сообщений
            'command': 2,    # 2 секунды для команд
            'callback': 0.5  # 0.5 секунды для callback-кнопок
        }
        
    def is_rate_limited(self, user_id: str, action_type: str = 'message') -> bool:
        """Проверяет, прошло ли достаточно времени с последнего действия"""
        current_time = datetime.now()
        last_time = self.last_request[user_id][action_type]
        cooldown = self.COOLDOWNS.get(action_type, 1)
        
        time_passed = (current_time - last_time).total_seconds()
        
        if time_passed < cooldown:
            logger.info(f"Rate limit для пользователя {user_id}. Прошло {time_passed:.1f} сек.")
            return True
            
        self.last_request[user_id][action_type] = current_time
        return False

# Создаем глобальный экземпляр
rate_limiter = RateLimiter()

def rate_limit(action_type: str = 'message'):
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            if not update.effective_user:
                return await func(update, context, *args, **kwargs)
                
            user_id = str(update.effective_user.id)
            
            if rate_limiter.is_rate_limited(user_id, action_type):
                logger.debug(f"Сообщение от {user_id} проигнорировано (rate limit)")
                return
                
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator 