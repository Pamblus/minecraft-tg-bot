import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import TOKEN
from keyboard import create_menu_keyboard
from game_handlers import handle_game_action, show_game_world
from multiplayer import MultiplayerManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

multiplayer = MultiplayerManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "🎮 Мультиплеерный мир Minecraft-like\n\n"
        "🌍 Особенности:\n"
        "• Онлайн с другими игроками\n"
        "• 10 сердечек здоровья\n"
        "• Атака других игроков\n"
        "• Случайный спавн\n\n"
        "Используйте кнопки ниже для начала:",
        reply_markup=create_menu_keyboard()
    )

async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Новая игра"""
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "Игрок"
    
    world, player = multiplayer.join_world(user_id, username, "default")
    
    await show_game_world(update, context, user_id, "🎮 Добро пожаловать!")

async def continue_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Продолжить игру"""
    user_id = str(update.effective_user.id)
    
    world = multiplayer.get_player_world(user_id)
    if world:
        await show_game_world(update, context, user_id, "▶️ Продолжаем!")
    else:
        await update.message.reply_text("❌ Нет сохраненной игры\n/newgame - начать")

async def join_world(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Присоединиться к миру"""
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "Игрок"
    
    # Можно добавить выбор мира, пока дефолтный
    world, player = multiplayer.join_world(user_id, username, "default")
    
    await show_game_world(update, context, user_id, "👥 Присоединились к миру!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    await update.message.reply_text(
        "🕹️ Управление:\n"
        "• Стрелки - движение\n"
        "• ⛏️ - ломать блоки/атаковать\n"
        "• 🪨🌿🪵 - ставить блоки\n"
        "• 🔺🔻 - менять высоту\n\n"
        "❤️ Здоровье:\n"
        "• 10 сердечек\n"
        "• Атакуйте других игроков ⛏️\n"
        "• При смерти - телепорт на спавн\n\n"
        "👥 Мультиплеер:\n"
        "• Случайный спавн в радиусе 50 блоков\n"
        "• Все в одном мире"
    )

def main():
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()
    
    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("newgame", new_game))
    application.add_handler(CommandHandler("continue", continue_game))
    application.add_handler(CommandHandler("join", join_world))
    application.add_handler(CommandHandler("help", help_command))
    
    # Обработчик игровых кнопок
    application.add_handler(CallbackQueryHandler(handle_game_action))
    
    logger.info("🎮 Мультиплеерный бот запущен!")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()
