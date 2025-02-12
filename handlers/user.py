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
    user = update.effective_user
    user_id = str(user.id)
    
    user_data = {
        "id": user.id,
        "username": user.username or "Без username",
        "first_name": user.first_name,
        "last_name": user.last_name or "",
    }
    save_user(user_data)
    
    # Проверяем, является ли пользователь админом
    if user_id in ADMIN_IDS:
        users_info = load_users()
        total_users = users_info["total_count"]
        last_user = users_info["users"][-1] if users_info["users"] else None
        
        admin_text = (
            "👨‍💼 Панель администратора\n\n"
            f"📊 Всего пользователей: {total_users}\n"
            f"📅 Последний пользователь:\n"
            f"├ ID: {last_user['id'] if last_user else 'Нет'}\n"
            f"├ Имя: {last_user['first_name'] if last_user else 'Нет'}\n"
            f"├ Username: @{last_user['username'] if last_user else 'Нет'}\n"
            f"└ Дата: {last_user['joined_date'] if last_user else 'Нет'}\n\n"
            "📝 Доступные команды:\n"
            "/admin - Панель администратора\n"
            "/users - Статистика пользователей\n"
            "kod - Получить ID последнего сообщения"
        )
        await update.message.reply_text(admin_text)
        logger.info(f"Админ {user_id} запустил бота")
        return

    # Для обычных пользователей проверяем подписку
    if not await check_subscription(update, context):
        await update.message.reply_text(
            "🎬 Добро пожаловать в мир кино!\n\n"
            "💫 Чтобы получить доступ к нашей коллекции фильмов, нужно сделать всего один шаг:\n"
            "• Подпишитесь на канал MaxFilms\n\n"
            "🎁 В канале вы найдете:\n"
            "• Премьеры фильмов\n"
            "• Топовые фильмы\n"
            "• Подборки лучших фильмов\n\n"
            "👉 Присоединяйтесь и возвращайтесь сюда!",
            reply_markup=await get_sub_keyboard()
        )
        return

    logger.info(f"Пользователь {user_id} запустил бота")
    welcome_text = (
        "👋 Добро пожаловать в наш кинобот!\n\n"
        "🎬 Здесь вы можете получить доступ к фильмам из нашей коллекции.\n"
        "📝 Просто отправьте мне ID фильма, и я пришлю вам фильм вместе с описанием.\n\n"
        f"🔍 ID фильма можно найти в нашем канале {NEWS_CHANNEL_ID}"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())