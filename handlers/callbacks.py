from telegram import Update
from telegram.ext import ContextTypes
from config.settings import NEWS_CHANNEL_ID
from handlers.user import check_subscription, get_sub_keyboard
from utils.logger import logger

async def subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if await check_subscription(update, context):
        welcome_text = (
            "👋 Добро пожаловать в наш кинобот!\n\n"
            "🎬 Здесь вы можете получить доступ к фильмам из нашей коллекции.\n"
            "📝 Просто отправьте мне ID фильма, и я пришлю вам фильм вместе с описанием.\n\n"
            f"🔍 ID фильма можно найти в нашем канале {NEWS_CHANNEL_ID}"
        )
        await query.message.edit_text(welcome_text)
    else:
        await query.message.reply_text(
            "🔔 Для использования бота необходимо подписаться на наш канал новостей!",
            reply_markup=await get_sub_keyboard()
        )