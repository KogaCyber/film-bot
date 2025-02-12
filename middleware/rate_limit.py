from collections import defaultdict
from datetime import datetime
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger

class RateLimiter:
    def __init__(self):
        self.last_request = defaultdict(lambda: datetime.min)
        self.COOLDOWN = 5  # секунд между сообщениями
        
    def is_rate_limited(self, user_id: str) -> bool:
        """Проверяет, прошло ли достаточно времени с последнего сообщения"""
        current_time = datetime.now()
        last_time = self.last_request[user_id]
        time_passed = (current_time - last_time).total_seconds()
        
        if time_passed < self.COOLDOWN:
            logger.info(f"Rate limit для пользователя {user_id}. Прошло {time_passed:.1f} сек.")
            return True
            
        self.last_request[user_id] = current_time
        return False

# Создаем глобальный экземпляр
rate_limiter = RateLimiter()

def rate_limit():
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            if not update.effective_user:
                return await func(update, context, *args, **kwargs)
                
            user_id = str(update.effective_user.id)
            
            if rate_limiter.is_rate_limited(user_id):
                logger.debug(f"Сообщение от {user_id} проигнорировано (rate limit)")
                return
                
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator 