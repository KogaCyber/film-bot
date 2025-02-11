import sys
import signal
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import Update
from config.settings import BOT_TOKEN
from utils.logger import logger
from handlers.admin import admin_command, users_command
from handlers.user import start
from handlers.channel import handle_channel_post
from handlers.messages import handle_message
from handlers.callbacks import subscription_callback

def signal_handler(sig, frame):
    logger.info("Получен сигнал завершения. Бот останавливается...")
    sys.exit(0)

def main():
    # Добавляем обработчик сигнала
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CallbackQueryHandler(subscription_callback, pattern="^check_subscription$"))
    application.add_handler(MessageHandler(
        (filters.UpdateType.CHANNEL_POST | filters.UpdateType.EDITED_CHANNEL_POST),
        handle_channel_post
    ))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен...")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()