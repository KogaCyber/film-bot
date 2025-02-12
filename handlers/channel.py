from telegram import Update
from telegram.ext import ContextTypes
from config.settings import CHANNEL_ID
from utils.logger import logger
from database.film_ids import save_film_id

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.channel_post and not update.edited_channel_post:
        return
    
    post = update.channel_post or update.edited_channel_post
    if str(post.chat.id) != CHANNEL_ID:
        return
        
    message_id = post.message_id
    # Сохраняем ID сообщения в JSON
    save_film_id(message_id)
    logger.info(f"Новый пост в канале. ID: {message_id}")