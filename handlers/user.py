from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from config.settings import NEWS_CHANNEL_ID, ADMIN_IDS
from database.users import save_user, load_users
from utils.logger import logger

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id=NEWS_CHANNEL_ID, user_id=user_id)
        status = member.status
        logger.info(f"Статус подписки пользователя {user_id}: {status}")
        return status in ['member', 'administrator', 'creator']
    except TelegramError as e:
        logger.error(f"Ошибка при проверке подписки пользователя {user_id}: {e}")
        return False

async def get_sub_keyboard():
    channel_name = NEWS_CHANNEL_ID.replace('@', '')
    keyboard = [
        [InlineKeyboardButton("🔔 Подписаться на канал", url=f"https://t.me/{channel_name}")],
        [InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🎬 Фильмы"), KeyboardButton("📖 Инструкция")],
        [KeyboardButton("❓ Помощь"), KeyboardButton("👨‍💻 Поддержка")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # Проверяем, есть ли параметры в команде start (например, ID фильма)
    args = context.args
    if args and args[0].isdigit():
        # Если есть ID фильма, сразу пытаемся его отправить
        film_id = int(args[0])
        try:
            await update.message.reply_text("🔄 Загружаю фильм, пожалуйста, подождите...")
            # Отправляем описание и фильм
            await context.bot.copy_message(
                chat_id=update.effective_chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=film_id - 1
            )
            await context.bot.copy_message(
                chat_id=update.effective_chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=film_id
            )
            welcome_after_film = (
                "✅ Приятного просмотра!\n\n"
                "💫 Хотите больше фильмов?\n"
                f"• Переходите в наш канал: {NEWS_CHANNEL_ID}\n"
                "• Выбирайте любой фильм\n"
                "• Отправляйте его ID боту\n\n"
                "🎯 Используйте кнопки ниже для навигации:"
            )
            await update.message.reply_text(welcome_after_film, reply_markup=get_main_keyboard())
            return
        except Exception as e:
            logger.error(f"Ошибка при отправке фильма: {e}")
            error_text = (
                "❌ Фильм с таким ID не найден.\n\n"
                "🎬 Как получить фильм правильно:\n"
                "1️⃣ Перейдите в наш канал фильмов\n"
                f"└ {NEWS_CHANNEL_ID}\n"
                "2️⃣ Выберите любой фильм\n"
                "3️⃣ Скопируйте его ID (например: 123)\n"
                "4️⃣ Отправьте ID боту\n\n"
                "🎯 Используйте кнопки ниже для навигации"
            )
            await update.message.reply_text(error_text, reply_markup=get_main_keyboard())
            return

    # Стандартное приветствие для новых пользователей
    if not await check_subscription(update, context):
        first_text = (
            "🎬 Добро пожаловать в мир кино!\n\n"
            "💫 Чтобы получить доступ к фильмам:\n"
            "1️⃣ Подпишитесь на канал\n"
            "2️⃣ Нажмите «✅ Я подписался»\n"
            "3️⃣ Отправьте ID нужного фильма\n\n"
            "🎁 В канале вы найдете:\n"
            "• Премьеры фильмов\n"
            "• Топовые фильмы\n"
            "• Подборки лучших фильмов"
        )
        await update.message.reply_text(first_text, reply_markup=await get_sub_keyboard())
        return

    welcome_text = (
        "🎬 Добро пожаловать в Мир Кино!\n\n"
        "📝 Как смотреть фильмы:\n"
        "1️⃣ Найдите ID фильма в канале\n"
        f"└ {NEWS_CHANNEL_ID}\n"
        "2️⃣ Отправьте ID боту\n"
        "└ Например: 123\n\n"
        "🎯 Или используйте кнопки:\n"
        "🎬 Фильмы - Перейти в канал\n"
        "📖 Инструкция - Подробная помощь\n"
        "❓ Помощь - Ответы на вопросы\n"
        "👨‍💻 Поддержка - Связь с админами"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())