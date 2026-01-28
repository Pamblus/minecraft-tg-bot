import logging
from telegram import Update
from telegram.ext import ContextTypes
import json

from config import VIEW_SIZE, AIR_HEIGHT
from keyboard import create_game_keyboard
from multiplayer import MultiplayerManager

logger = logging.getLogger(__name__)

# Загружаем эмодзи
def load_emojis():
    try:
        with open("items.json", 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        emojis = {}
        
        # Загружаем блоки
        if "блоки" in items:
            for block_name, block_data in items["блоки"].items():
                if "id" in block_data:
                    emojis[block_name] = block_data["id"]
        
        # Загружаем сущности (если есть)
        if "сущности" in items:
            for entity_name, entity_data in items["сущности"].items():
                if "id" in entity_data:
                    emojis[entity_name] = entity_data["id"]
        
        # Дефолтные значения если нет в файле
        if "воздух" not in emojis:
            emojis["воздух"] = "5463010113440717314"
        if "персонаж" not in emojis:
            emojis["персонаж"] = "5283132635361587188"
        
        # Добавляем остальные дефолтные
        default_emojis = {
            "трава": "5458430926683905591",
            "земля": "5458822138075028493",
            "камень": "5458781211331665562",
            "уголь": "5456408804541340493",
            "железная руда": "5458833133191306560",
            "золотая руда": "5458617543012918174",
            "алмазная руда": "5458420940884942467",
            "ствол": "5458603588664171474",
            "листва": "5462961855188180190",
            "гриб поганка": "5458555278872026193",
            "снег земля": "5458375770713890099"
        }
        
        for name, emoji_id in default_emojis.items():
            if name not in emojis:
                emojis[name] = emoji_id
        
        return emojis
    except Exception as e:
        logger.error(f"Ошибка загрузки эмодзи: {e}")
        # Возвращаем дефолтные
        return {
            "воздух": "5463010113440717314",
            "персонаж": "5283132635361587188",
            "трава": "5458430926683905591",
            "земля": "5458822138075028493",
            "камень": "5458781211331665562",
            "уголь": "5456408804541340493",
            "железная руда": "5458833133191306560",
            "золотая руда": "5458617543012918174",
            "алмазная руда": "5458420940884942467",
            "ствол": "5458603588664171474",
            "листва": "5462961855188180190",
            "гриб поганка": "5458555278872026193",
            "снег земля": "5458375770713890099"
        }

EMOJIS = load_emojis()
multiplayer = MultiplayerManager()

def format_view(view):
    """Форматировать вид"""
    result = ""
    for row in view:
        for block in row:
            emoji_id = EMOJIS.get(block)
            if not emoji_id:
                # Если не нашли, используем воздух
                emoji_id = EMOJIS.get("воздух", "")
            
            if emoji_id:
                result += f'<tg-emoji emoji-id="{emoji_id}">⬜</tg-emoji>'
            else:
                result += "⬜"
        result += "\n"
    return result

async def show_game_world(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                         player_id, message=""):
    """Показать игровой мир"""
    world = multiplayer.get_player_world(player_id)
    if not world:
        await update.message.reply_text("❌ Вы не в мире!\n/join чтобы присоединиться")
        return
    
    player = world.get_player(player_id)
    if not player:
        await update.message.reply_text("❌ Игрок не найден")
        return
    
    view = world.get_view(player_id)
    view_text = format_view(view)
    
    px, py, pz = player.position
    grass_level = AIR_HEIGHT
    
    # Информация о здоровье
    health_bar = "❤️" * player.health + "🤍" * (10 - player.health)
    
    # Подсчет глубины
    if pz < grass_level:
        depth = grass_level - pz
        depth_text = f"⛏️ Глубина: {depth} блоков"
    else:
        depth_text = "🌤️ Над землей"
    
    info = (f"{health_bar}\n"
            f"📍 X:{px} Y:{py} Z:{pz}\n"
            f"🌿 Трава: Z={grass_level}\n"
            f"{depth_text}\n"
            f"📦 Предметов: {sum(player.inventory.values())}\n"
            f"👥 Онлайн: {len(world.players) - 1}\n"
            f"💬 {message}")
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            f"{view_text}\n{info}",
            parse_mode="HTML",
            reply_markup=create_game_keyboard()
        )
    else:
        await update.message.reply_text(
            f"{view_text}\n{info}",
            parse_mode="HTML",
            reply_markup=create_game_keyboard()
        )

async def handle_game_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик игровых действий - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "Игрок"
    action = query.data
    
    # Получаем мир и игрока
    world = multiplayer.get_player_world(user_id)
    if not world:
        # Автоприсоединение к дефолтному миру
        world, player = multiplayer.join_world(user_id, username)
    else:
        player = world.get_player(user_id)
    
    message = ""
    
    # ДВИЖЕНИЕ
    if action == "move_up":
        if world.move_player(user_id, 0, -1, 0):
            message = "↑"
        else:
            message = "❌"
    
    elif action == "move_down":
        if world.move_player(user_id, 0, 1, 0):
            message = "↓"
        else:
            message = "❌"
    
    elif action == "move_left":
        if world.move_player(user_id, -1, 0, 0):
            message = "←"
        else:
            message = "❌"
    
    elif action == "move_right":
        if world.move_player(user_id, 1, 0, 0):
            message = "→"
        else:
            message = "❌"
    
    elif action == "level_up":
        if world.move_player(user_id, 0, 0, 1):
            message = "🔺"
        else:
            message = "❌"
    
    elif action == "level_down":
        if world.move_player(user_id, 0, 0, -1):
            message = "🔻"
        else:
            message = "❌"
    
    # ДОБЫЧА БЛОКОВ - ИСПРАВЛЕНО!
    elif action in ["break_up", "break_down", "break_left", "break_right"]:
        px, py, pz = player.position
        
        # Определяем направление
        if action == "break_up":
            target_x, target_y = px, py - 1
        elif action == "break_down":
            target_x, target_y = px, py + 1
        elif action == "break_left":
            target_x, target_y = px - 1, py
        else:  # break_right
            target_x, target_y = px + 1, py
        
        # Сначала проверяем, НЕТ ЛИ ТАМ ИГРОКА
        target_username, damage = multiplayer.attack_player(user_id, target_x, target_y, pz)
        
        if target_username:
            # Если есть игрок - атакуем
            message = f"⚔️ Атаковал {target_username} (-{damage}❤️)"
        else:
            # Если нет игрока - ломаем блок
            dropped_item = world.break_block(target_x, target_y, pz, user_id)
            
            if dropped_item:
                message = f"⛏️ {dropped_item}"
            else:
                # Проверяем, что за блок
                block = world.get_block(target_x, target_y, pz, user_id)
                if block == "воздух":
                    message = "💨 Воздух"
                else:
                    # Проверяем данные блока
                    try:
                        with open("items.json", 'r', encoding='utf-8') as f:
                            items_data = json.load(f)
                        
                        block_data = items_data.get("блоки", {}).get(block, {})
                        if not block_data.get("добывается", False):
                            message = f"❌ Нельзя сломать {block}"
                        else:
                            message = f"❌ Ошибка добычи {block}"
                    except:
                        message = f"❌ Ошибка с {block}"
    
    # РАЗМЕЩЕНИЕ БЛОКОВ
    elif action == "place_stone":
        px, py, pz = player.position
        if player.has_inventory("камень"):
            # Проверяем, можно ли поставить блок
            target_block = world.get_block(px, py + 1, pz, user_id)
            if target_block == "воздух":
                world.set_block(px, py + 1, pz, "камень", user_id)
                player.remove_from_inventory("камень")
                message = "🪨 Камень"
            else:
                message = "❌ Нельзя поставить"
        else:
            message = "❌ Нет камня"
    
    elif action == "place_dirt":
        px, py, pz = player.position
        if player.has_inventory("земля"):
            target_block = world.get_block(px, py + 1, pz, user_id)
            if target_block == "воздух":
                world.set_block(px, py + 1, pz, "земля", user_id)
                player.remove_from_inventory("земля")
                message = "🌿 Земля"
            else:
                message = "❌ Нельзя поставить"
        else:
            message = "❌ Нет земли"
    
    elif action == "place_wood":
        px, py, pz = player.position
        if player.has_inventory("ствол"):
            target_block = world.get_block(px, py + 1, pz, user_id)
            if target_block == "воздух":
                world.set_block(px, py + 1, pz, "ствол", user_id)
                player.remove_from_inventory("ствол")
                message = "🪵 Дерево"
            else:
                message = "❌ Нельзя поставить"
        else:
            message = "❌ Нет дерева"
    
    # ПРОЧЕЕ
    elif action == "center":
        px, py, pz = player.position
        message = f"📍 X:{px} Y:{py} Z:{pz}"
    
    elif action == "health":
        message = f"❤️ {player.health}/10"
    
    elif action == "inventory":
        if player.inventory:
            items = []
            for item, count in player.inventory.items():
                if count > 0:
                    items.append(f"{item}: {count}")
            
            if items:
                message = "📦 " + ", ".join(items[:5])
                if len(items) > 5:
                    message += f" ... (+{len(items)-5})"
            else:
                message = "📦 Пусто"
        else:
            message = "📦 Пусто"
    
    elif action == "players":
        online = multiplayer.get_online_players(user_id)
        if online:
            players_list = []
            for p in online[:500]:  # Ограничим 5 игроками
                players_list.append(f"👤 {p['username']} ❤️{p['health']}")
            
            message = "👥 Онлайн:\n" + "\n".join(players_list)
            if len(online) > 5:
                message += f"\n... и ещё {len(online)-5}"
        else:
            message = "👥 Онлайн: 0"
    
    elif action == "home":
        # Телепорт на спавн (0, 0, AIR_HEIGHT + 1)
        from config import AIR_HEIGHT
        player.position = [0, 0, AIR_HEIGHT + 1]
        message = "🏠 Телепорт домой!"
    
    # Сохраняем и показываем
    multiplayer.save_worlds()
    await show_game_world(update, context, user_id, message)

# Добавим обработчик команды /debug для тестирования
async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для отладки"""
    user_id = str(update.effective_user.id)
    
    world = multiplayer.get_player_world(user_id)
    if not world:
        await update.message.reply_text("❌ Нет мира")
        return
    
    player = world.get_player(user_id)
    if not player:
        await update.message.reply_text("❌ Нет игрока")
        return
    
    # Информация о блоке под ногами
    px, py, pz = player.position
    block_below = world.get_block(px, py, pz - 1, user_id)
    block_at = world.get_block(px, py, pz, user_id)
    
    info = (f"🔧 Отладка:\n"
            f"Позиция: {px}, {py}, {pz}\n"
            f"Блок в позиции: {block_at}\n"
            f"Блок под ногами: {block_below}\n"
            f"Можно двигаться? {world.can_move_to(px, py, pz, user_id)}\n"
            f"Инвентарь: {player.inventory}\n"
            f"Здоровье: {player.health}")
    
    await update.message.reply_text(info)
