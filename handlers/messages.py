import os
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import CHANNEL_ID, ADMIN_IDS, NEWS_CHANNEL_ID
from utils.logger import logger
from handlers.help import help_command, support_command

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    user_id = str(update.effective_user.id)

    # Обработка кнопок меню
    if message_text == "🎬 Фильмы":
        channel_name = NEWS_CHANNEL_ID.replace('@', '')
        films_text = (
            "🍿 Добро пожаловать в нашу фильмотеку!\n\n"
            "✨ У нас вы найдете:\n"
            "• Премьеры 2024 года\n"
            "• Популярные фильмы\n"
            "• Классику кино\n"
            "• Эксклюзивные подборки\n\n"
            "👇 Перейдите по ссылке и выберите фильм:\n"
            f"https://t.me/{channel_name}\n\n"
            "💡 Не забудьте: после выбора фильма\n"
            "просто отправьте его ID боту"
        )
        await update.message.reply_text(films_text)
        return
    elif message_text == "📖 Инструкция":
        instruction_text = (
            "🎯 Как получить фильм за 30 секунд:\n\n"
            "1️⃣ Откройте наш канал фильмов\n"
            "   └ Нажмите кнопку «🎬 Фильмы»\n\n"
            "2️⃣ Найдите фильм по душе\n"
            "   └ Листайте ленту или используйте поиск\n\n"
            "3️⃣ Найдите ID фильма\n"
            "   └ Это цифры в конце описания: например, #ID123\n\n"
            "4️⃣ Отправьте ID боту\n"
            "   └ Просто напишите число: 123\n\n"
            "🎬 Готово! Фильм уже в пути!\n\n"
            "💡 Совет: Сохраните бота, чтобы быстро\n"
            "находить новые фильмы в следующий раз!"
        )
        await update.message.reply_text(instruction_text)
        return
    elif message_text == "❓ Помощь":
        await help_command(update, context)
        return
    elif message_text == "👨‍💻 Поддержка":
        await support_command(update, context)
        return

    # Обработка команды kod для админов
    if message_text.lower() == "kod" and user_id in ADMIN_IDS:
        last_id = context.bot_data.get('last_message_id', 'Нет данных')
        await update.message.reply_text(
            f"🎬 Последний ID: {last_id}\n"
            f"📝 Следующий ID будет: {last_id + 1 if isinstance(last_id, int) else 'Нет данных'}"
        )
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