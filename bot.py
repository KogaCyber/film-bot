from telegram import Update, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from logging.handlers import RotatingFileHandler
import os
from telegram.error import TelegramError
from datetime import datetime
import pytz
import json
from dotenv import load_dotenv
import sys


# Создаем директорию для логов, если её нет
if not os.path.exists('logs'):
    os.makedirs('logs')

# Форматтер для логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Обычные логи
file_handler = RotatingFileHandler(
    'logs/bot.log',
    maxBytes=1024 * 1024,  # 1 MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Логи ошибок
error_handler = RotatingFileHandler(
    'logs/error.log',
    maxBytes=1024 * 1024,  # 1 MB
    backupCount=5,
    encoding='utf-8'
)
error_handler.setFormatter(formatter)
error_handler.setLevel(logging.ERROR)

# Консольные логи
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)

# Загружаем переменные окружения
load_dotenv()

# После импортов добавляем:
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
NEWS_CHANNEL_ID = f"@{os.getenv('NEWS_CHANNEL_NAME')}"
ADMIN_IDS = os.getenv('ADMIN_IDS', '').split(',')

# Проверка наличия необходимых переменных
if not all([BOT_TOKEN, CHANNEL_ID, NEWS_CHANNEL_ID, ADMIN_IDS]):
    logger.error("Отсутствуют необходимые переменные окружения!")
    sys.exit(1)

USERS_FILE = 'data/users.json'
UZB_TIMEZONE = pytz.timezone('Asia/Tashkent')

# Создаем директорию для данных, если её нет
if not os.path.exists('data'):
    os.makedirs('data')

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
    keyboard = [
        [InlineKeyboardButton("🎬 Присоединиться к MaxFilms", url=f"https://t.me/your_channel_name")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = {
        "id": user.id,
        "username": user.username or "Без username",
        "first_name": user.first_name,
        "last_name": user.last_name or "",
        "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_user(user_data)
    
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

    logger.info(f"Пользователь {update.effective_user.id} запустил бота")
    welcome_text = (
        "👋 Добро пожаловать в наш кинобот!\n\n"
        "🎬 Здесь вы можете получить доступ к фильмам из нашей коллекции.\n"
        "📝 Просто отправьте мне ID фильма, и я пришлю вам фильм вместе с описанием.\n\n"
        "🔍 ID фильма можно найти в нашем канале @channel_name"
    )
    await update.message.reply_text(welcome_text)

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post or update.edited_channel_post:
        message = update.channel_post or update.edited_channel_post
        logger.info(f"Новое сообщение в канале: {message.message_id}")
        # Сохраняем сообщение в контексте
        context.bot_data['last_message'] = message
        logger.info(f"Сохранено сообщение с ID: {message.message_id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    message_text = update.message.text

    # Проверка подписки перед обработкой сообщения
    if user_id not in ADMIN_IDS:  # Пропускаем проверку для админов
        is_subscribed = await check_subscription(update, context)
        if not is_subscribed:
            await update.message.reply_text(
                "🎯 Почти готово!\n\n"
                "💫 Для доступа к фильмам осталось только:\n"
                "• Подписаться на канал MaxFilms\n\n"
                "🎁 Там вы найдете лучшие фильмы и крутые подборки!",
                reply_markup=await get_sub_keyboard()
            )
            return

    # Проверка на админа и команду kod
    if user_id in ADMIN_IDS and message_text.lower() == "kod":
        if 'last_message' in context.bot_data:
            last_message = context.bot_data['last_message']
            logger.info(f"Отправка последнего сообщения админу: {last_message.message_id}")
            admin_text = (
                "📊 Информация о последнем сообщении:\n"
                f"📍 ID: {last_message.message_id}\n"
                "⬇️ Сообщение:"
            )
            await update.message.reply_text(admin_text)
            await context.bot.copy_message(
                chat_id=update.effective_chat.id,
                from_chat_id=CHANNEL_ID,
                message_id=last_message.message_id
            )
        else:
            logger.error("Нет сохраненного последнего сообщения")
            await update.message.reply_text("⚠️ В данный момент нет новых сообщений в канале")
        return

    # Обработка запроса фильма для пользователей
    try:
        film_id = int(message_text)
        logger.info(f"Запрошен фильм с ID: {film_id}")
        
        try:
            await update.message.reply_text("🔄 Загружаю фильм, пожалуйста, подождите...")
            
            # Отправляем описание (предыдущее сообщение)
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
        if message_text.lower() != "kod":
            help_text = (
                "❗️ Пожалуйста, отправьте только номер фильма (ID).\n\n"
                "🔍 ID фильма можно найти в описании к фильму в нашем канале @channel_name\n"
                "📝 Пример: 123"
            )
            await update.message.reply_text(help_text)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in ADMIN_IDS:
        return
    
    users_info = load_users()
    admin_help_text = (
        "👨‍💼 Команды администратора:\n\n"
        "📊 /users - Показать количество пользователей\n"
        "🔍 kod - Получить ID последнего сообщения из канала\n\n"
        f"📈 Всего пользователей: {users_info['total_count']}"
    )
    await update.message.reply_text(admin_help_text)

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in ADMIN_IDS:
        return
    
    users_info = load_users()
    users_text = (
        "📊 Статистика бота:\n\n"
        f"👥 Всего пользователей: {users_info['total_count']}\n"
        f"📅 Последний пользователь: {users_info['users'][-1]['joined_date'] if users_info['users'] else 'Нет'}"
    )
    await update.message.reply_text(users_text)

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    # Обновляем фильтр для канала
    application.add_handler(MessageHandler(
        (filters.UpdateType.CHANNEL_POST | filters.UpdateType.EDITED_CHANNEL_POST),
        handle_channel_post
    ))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()