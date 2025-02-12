import os
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import CHANNEL_ID, ADMIN_IDS
from utils.logger import logger

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    user_id = str(update.effective_user.id)

    # Обработка команды kod для админов
    if message_text.lower() == "kod" and user_id in ADMIN_IDS:
        await update.message.reply_text(f"🎬 Последний ID: {context.bot_data.get('last_message_id', 'Нет данных')}")
        return

    # Обработка запроса фильма для пользователей
    try:
        film_id = int(message_text)
        logger.info(f"Запрошен фильм с ID: {film_id}")
        try:
            await update.message.reply_text("🔄 Загружаю фильм, пожалуйста, подождите...")
            # Отправляем описание
            await context.bot.copy_message(
                chat_id=update.effective_chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=film_id - 1
            )
            # Отправляем фильм
            await context.bot.copy_message(
                chat_id=update.effective_chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=film_id
            )
            await update.message.reply_text("✅ Приятного просмотра!")
        except Exception as e:
            logger.error(f"Ошибка при отправке фильма: {e}")
            error_text = (
                "❌ К сожалению, фильм с таким ID не найден.\n\n"
                "🔍 Пожалуйста:\n"
                "- Проверьте правильность ID\n"
                "- Убедитесь, что ID указан в нашем канале\n"
                "- Попробуйте снова"
            )
            await update.message.reply_text(error_text)
    except ValueError:
        channel_link = os.getenv("NEWS_CHANNEL_NAME")
        if message_text.lower() != "kod":
            help_text = (
                "❗️ Пожалуйста, отправьте только номер фильма (ID).\n\n"
                f"🔍 ID фильма можно найти в описании к фильму в нашем канале {channel_link}\n"
                "📝 Пример: 123"
            )
            await update.message.reply_text(help_text)