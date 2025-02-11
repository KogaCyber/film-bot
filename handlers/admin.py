from telegram import Update
from telegram.ext import ContextTypes
from config.settings import ADMIN_IDS
from database.users import load_users
from utils.logger import logger

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔️ У вас нет доступа к этой команде!")
        logger.warning(f"Попытка доступа к админ-команде от пользователя {user_id}")
        return
    
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
        "/users - Статистика пользователей\n"
        "kod - Получить ID последнего сообщения"
    )
    
    await update.message.reply_text(admin_text)
    logger.info(f"Админ {user_id} запросил информацию")

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔️ У вас нет доступа к этой команде!")
        logger.warning(f"Попытка доступа к команде /users от пользователя {user_id}")
        return
    
    users_info = load_users()
    users_text = (
        "📊 Статистика пользователей\n\n"
        f"👥 Всего пользователей: {users_info['total_count']}\n"
        f"📅 Последняя активность: {users_info['users'][-1]['joined_date'] if users_info['users'] else 'Нет'}"
    )
    
    await update.message.reply_text(users_text)
    logger.info(f"Админ {user_id} запросил статистику пользователей")