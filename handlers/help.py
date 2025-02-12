from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import ADMIN_IDS
from utils.logger import logger

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    help_text = (
        "📖 Инструкция по использованию бота:\n\n"
        "1️⃣ Найдите интересующий фильм в нашем канале\n"
        "2️⃣ Скопируйте ID фильма (номер в конце описания)\n"
        "3️⃣ Отправьте этот ID боту\n\n"
        "❓ Часто задаваемые вопросы:\n"
        "• Как найти ID фильма? - Смотрите в описании поста\n"
        "• Фильм не загружается? - Проверьте правильность ID\n"
        "• Другие проблемы? - Нажмите кнопку «Поддержка»\n\n"
        "🔍 Команды бота:\n"
        "/start - Перезапустить бота\n"
        "/help - Это меню помощи\n"
        "/support - Связаться с поддержкой"
    )
    
    keyboard = [
        [InlineKeyboardButton("👨‍💻 Поддержка", callback_data="support")]
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
        "🆘 Служба поддержки\n\n"
        "Если у вас возникли проблемы или вопросы,\n"
        "вы можете обратиться к администраторам:\n\n"
        f"👨‍💻 Администраторы: {', '.join(admin_usernames)}\n\n"
        "⚠️ Пожалуйста, опишите вашу проблему максимально подробно"
    )
    
    await update.message.reply_text(support_text)
    logger.info(f"Пользователь {user_id} запросил контакты поддержки")
