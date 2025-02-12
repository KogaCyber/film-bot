from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import ADMIN_IDS
from utils.logger import logger

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
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
        "   └ Нажмите «📖 Инструкция»\n\n"
        "🎯 Команды для быстрого доступа:\n"
        "▫️ /start - Перезапуск бота\n"
        "▫️ /help - Это меню\n"
        "▫️ /support - Связь с поддержкой\n\n"
        "🎁 Подпишитесь на наш канал, чтобы\n"
        "первыми узнавать о новинках!"
    )
    
    keyboard = [
        [InlineKeyboardButton("👨‍💻 Написать в поддержку", callback_data="support")]
    ]
    
    await update.message.reply_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    logger.info(f"Пользователь {user_id} запросил помощь")

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    await update.message.reply_text(support_text)
    logger.info(f"Пользователь {user_id} запросил контакты поддержки")
