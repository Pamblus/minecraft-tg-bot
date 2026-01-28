from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_game_keyboard():
    """Основная игровая клавиатура"""
    keyboard = [
        [
            InlineKeyboardButton("⛏️⬆️", callback_data="break_up"),
            InlineKeyboardButton("⬆️", callback_data="move_up"),
            InlineKeyboardButton("⛏️⬆️", callback_data="break_up")
        ],
        [
            InlineKeyboardButton("⛏️⬅️", callback_data="break_left"),
            InlineKeyboardButton("⬅️", callback_data="move_left"),
            InlineKeyboardButton("🎯", callback_data="center"),
            InlineKeyboardButton("➡️", callback_data="move_right"),
            InlineKeyboardButton("⛏️➡️", callback_data="break_right")
        ],
        [
            InlineKeyboardButton("⛏️⬇️", callback_data="break_down"),
            InlineKeyboardButton("⬇️", callback_data="move_down"),
            InlineKeyboardButton("⛏️⬇️", callback_data="break_down")
        ],
        [
            InlineKeyboardButton("🔺", callback_data="level_up"),
            InlineKeyboardButton("❤️", callback_data="health"),
            InlineKeyboardButton("🔻", callback_data="level_down")
        ],
        [
            InlineKeyboardButton("🎒", callback_data="inventory"),
            InlineKeyboardButton("👥", callback_data="players"),
            InlineKeyboardButton("🏠", callback_data="home")
        ],
        [
            InlineKeyboardButton("🪨", callback_data="place_stone"),
            InlineKeyboardButton("🌿", callback_data="place_dirt"),
            InlineKeyboardButton("🪵", callback_data="place_wood")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def create_menu_keyboard():
    """Клавиатура меню"""
    keyboard = [
        [
            InlineKeyboardButton("🎮 Новая игра", callback_data="new_game"),
            InlineKeyboardButton("▶️ Продолжить", callback_data="continue_game")
        ],
        [
            InlineKeyboardButton("👥 Присоединиться", callback_data="join_world"),
            InlineKeyboardButton("🌍 Создать мир", callback_data="create_world")
        ],
        [
            InlineKeyboardButton("❓ Помощь", callback_data="help"),
            InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)
