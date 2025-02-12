from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import NEWS_CHANNEL_ID, ADMIN_IDS
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

async def support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    admin_usernames = []
    
    for admin_id in ADMIN_IDS:
        try:
            admin = await context.bot.get_chat(admin_id)
            if admin.username:
                admin_usernames.append(f"@{admin.username}")
        except Exception as e:
            logger.error(f"Ошибка при получении информации об админе {admin_id}: {e}")
    
    support_text = (
        "👋 Привет! Мы всегда на связи!\n\n"
        "✨ Наша поддержка поможет:\n"
        "• Найти нужный фильм\n"
        "• Решить технические проблемы\n"
        "• Ответить на ваши вопросы\n\n"
        "📝 Как написать в поддержку:\n"
        "1. Выберите администратора\n"
        "2. Опишите вашу ситуацию\n"
        "3. Получите быстрый ответ\n\n"
        f"👨‍💻 Администраторы онлайн:\n{', '.join(admin_usernames)}\n\n"
        "⚡️ Среднее время ответа: 5-10 минут\n"
        "🎯 Работаем 24/7"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_help")]
    ]
    
    await query.message.edit_text(
        support_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    logger.info(f"Пользователь {user_id} запросил поддержку через кнопку")


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    help_text = (
        "🎬 Добро пожаловать в мир кино!\n\n"
        "🔥 Что умеет наш бот:\n"
        "• Мгновенный доступ к фильмам\n"
        "• Автоматическая отправка описаний\n"
        "• Быстрый поиск по ID\n\n"
        "💫 Популярные вопросы:\n"
        "❓ Не приходит фильм?\n"
        "   └ Проверьте правильность ID\n"
        "❓ Где найти новые фильмы?\n"
        "   └ Нажмите «🎬 Фильмы»\n"
        "❓ Как получить фильм?\n"
        "   └ Нажмите «📖 Инструкция»"
    )
    
    keyboard = [
        [InlineKeyboardButton("👨‍💻 Написать в поддержку", callback_data="support")]
    ]
    
    await query.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )