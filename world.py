import json
import random
from config import VIEW_SIZE, AIR_HEIGHT, GRASS_HEIGHT, WORLD_SEED
from player import Player

class WorldGenerator:
    """Генератор мира"""
    
    def __init__(self, items_file="items.json"):
        with open(items_file, 'r', encoding='utf-8') as f:
            self.items_data = json.load(f)
        
        self.tree_positions = {}
        self.mushroom_positions = {}
        self.generated_areas = set()
        
    def _get_seed(self, x, y, z=0):
        """Сид для детерминированной генерации"""
        return hash(f"{x}_{y}_{z}_{WORLD_SEED}") % 1000000
    
    def generate_area(self, center_x, center_y):
        """Генерация области (деревья и грибы)"""
        area_key = f"{center_x//50}_{center_y//50}"
        
        if area_key in self.generated_areas:
            return
            
        self.generated_areas.add(area_key)
        radius = 25
        
        for x in range(center_x - radius, center_x + radius + 1):
            for y in range(center_y - radius, center_y + radius + 1):
                seed = self._get_seed(x, y)
                random.seed(seed)
                
                tree_key = f"{x},{y}"
                # Деревья (30%)
                if random.random() < 0.3:
                    self.tree_positions[tree_key] = True
                # Грибы (20%)
                if random.random() < 0.2:
                    self.mushroom_positions[tree_key] = True
    
    def get_block_type(self, x, y, z):
        """Определить тип блока на позиции"""
        # ВОЗДУХ (верхние AIR_HEIGHT блоков)
        if z > AIR_HEIGHT:
            tree_key = f"{x},{y}"
            
            # ДЕРЕВЬЯ
            if tree_key in self.tree_positions:
                if z == AIR_HEIGHT + 1:  # Нижняя листва
                    return "листва"
                elif z == AIR_HEIGHT + 2 or z == AIR_HEIGHT + 3:  # Ствол
                    return "ствол"
                elif z == AIR_HEIGHT + 4:  # Верхняя листва
                    return "листва"
            
            # ГРИБЫ
            if z == AIR_HEIGHT + 1 and tree_key in self.mushroom_positions:
                return "гриб поганка"
            
            return "воздух"
        
        # ТРАВА (ровно на высоте AIR_HEIGHT)
        elif z == AIR_HEIGHT:
            return "трава"
        
        # ЗЕМЛЯ (GRASS_HEIGHT блоков под травой)
        elif AIR_HEIGHT - GRASS_HEIGHT < z < AIR_HEIGHT:
            return "земля"
        
        # КАМЕНЬ и РУДЫ (ниже)
        else:
            depth = AIR_HEIGHT - z - GRASS_HEIGHT
            
            seed = self._get_seed(x * 1000 + y, z)
            random.seed(seed)
            rand_val = random.random()
            
            # Руды по глубине
            if depth >= 25 and depth <= 30:  # Алмазы
                if rand_val < 0.05:
                    return "алмазная руда"
            
            if depth >= 15 and depth <= 25:  # Золото
                if rand_val < 0.07:
                    return "золотая руда"
            
            if depth >= 8 and depth <= 15:  # Железо
                if rand_val < 0.1:
                    return "железная руда"
            
            if depth >= 3 and depth <= 15:  # Уголь (чаще)
                if rand_val < 0.15:
                    return "уголь"
            
            # Камень (основной блок)
            return "камень"
    
    def get_block_data(self, block_type):
        """Получить данные блока"""
        return self.items_data.get("блоки", {}).get(block_type, {})

class GameWorld:
    """Игровой мир"""
    
    def __init__(self, world_id="default"):
        self.world_id = world_id
        self.generator = WorldGenerator()
        self.players = {}  # user_id: Player
        self.global_modified_blocks = {}
        
        # Генерируем стартовую область
        self.generator.generate_area(0, 0)
    
    def add_player(self, user_id, username, spawn_x=0, spawn_y=0):
        """Добавить игрока"""
        if str(user_id) in self.players:
            return self.players[str(user_id)]
        
        # Случайный спавн в радиусе 50 блоков
        import random
        spawn_x = random.randint(-25, 25)
        spawn_y = random.randint(-25, 25)
        
        player = Player(user_id, username, spawn_x, spawn_y)
        self.players[str(user_id)] = player
        
        # Генерируем область вокруг спавна
        self.generator.generate_area(spawn_x, spawn_y)
        
        return player
    
    def get_player(self, user_id):
        """Получить игрока"""
        return self.players.get(str(user_id))
    
    def get_block(self, x, y, z, player_id=None):
        """Получить блок с учетом изменений"""
        key = f"{x},{y},{z}"
        
        # 1. Проверяем глобальные изменения (строения всех игроков)
        if key in self.global_modified_blocks:
            return self.global_modified_blocks[key]
        
        # 2. Проверяем изменения конкретного игрока
        if player_id:
            player = self.get_player(player_id)
            if player and key in player.modified_blocks:
                return player.modified_blocks[key]
        
        # 3. Генерация мира
        return self.generator.get_block_type(x, y, z)
    
    def set_block(self, x, y, z, block_type, player_id=None):
        """Установить блок - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        key = f"{x},{y},{z}"
        
        if block_type == "воздух":
            # Удаление блока (добыча)
            # Сначала из глобальных
            if key in self.global_modified_blocks:
                del self.global_modified_blocks[key]
            
            # Затем у игрока
            if player_id:
                player = self.get_player(player_id)
                if player and key in player.modified_blocks:
                    del player.modified_blocks[key]
        else:
            # Установка блока (строительство)
            if player_id:
                player = self.get_player(player_id)
                if player:
                    player.modified_blocks[key] = block_type
            else:
                self.global_modified_blocks[key] = block_type
    
    def break_block(self, x, y, z, player_id):
        """Сломать блок и добавить в инвентарь"""
        block_type = self.get_block(x, y, z, player_id)
        
        if block_type == "воздух":
            return None
        
        # Проверяем, можно ли ломать этот блок
        block_data = self.generator.get_block_data(block_type)
        if not block_data.get("добывается", False):
            return None
        
        # Ломаем блок
        self.set_block(x, y, z, "воздух", player_id)
        
        # Получаем дроп
        drop_item = block_data.get("дроп", block_type)
        
        # Добавляем в инвентарь игрока
        player = self.get_player(player_id)
        if player:
            player.add_to_inventory(drop_item)
        
        return drop_item
    
    def can_move_to(self, x, y, z, player_id=None):
        """Можно ли переместиться в клетку"""
        target_block = self.get_block(x, y, z, player_id)
        block_below = self.get_block(x, y, z - 1, player_id)
        
        solid_blocks = ["трава", "земля", "камень", "уголь", 
                       "железная руда", "золотая руда", "алмазная руда",
                       "ствол", "листва", "гриб поганка"]
        
        # Можно стоять на блоке
        if target_block in solid_blocks:
            return True
        
        # Можно идти по воздуху, если есть блок под ногами
        if target_block == "воздух" and block_below in solid_blocks:
            return True
        
        return False
    
    def find_player_at_position(self, x, y, z, exclude_player_id=None):
        """Найти игрока на позиции"""
        for pid, player in self.players.items():
            if pid != exclude_player_id:
                px, py, pz = player.position
                if px == x and py == y and pz == z:
                    return player
        return None
    
    def get_view(self, player_id):
        """Вид вокруг игрока"""
        player = self.get_player(player_id)
        if not player:
            return []
        
        px, py, pz = player.position
        view = []
        half = VIEW_SIZE // 2
        
        for dy in range(-half, half + 1):
            row = []
            for dx in range(-half, half + 1):
                world_x = px + dx
                world_y = py + dy
                
                # Проверяем, есть ли здесь игрок
                other_player = self.find_player_at_position(world_x, world_y, pz, player_id)
                
                if other_player:
                    row.append("персонаж")
                elif dx == 0 and dy == 0:
                    row.append("персонаж")
                else:
                    block = self.get_block(world_x, world_y, pz, player_id)
                    row.append(block)
            view.append(row)
        
        return view
    
    def to_dict(self):
        """Сохранить мир в словарь"""
        return {
            'world_id': self.world_id,
            'global_modified_blocks': self.global_modified_blocks,
            'players': {pid: p.to_dict() for pid, p in self.players.items()}
        }
    
    def load_from_dict(self, data):
        """Загрузить мир из словаря"""
        self.world_id = data.get('world_id', 'default')
        self.global_modified_blocks = data.get('global_modified_blocks', {})
        
        # Загружаем игроков
        self.players = {}
        players_data = data.get('players', {})
        
        for pid, player_data in players_data.items():
            try:
                player = Player(
                    player_data.get('user_id', pid),
                    player_data.get('username', 'Игрок')
                )
                player.load_from_dict(player_data)
                self.players[pid] = player
            except Exception as e:
                print(f"Ошибка загрузки игрока {pid}: {e}")
        
        # Восстанавливаем генерацию деревьев/грибов для загруженных игроков
        for player in self.players.values():
            px, py, _ = player.position
            self.generator.generate_area(px, py)
    
    def get_player_position(self, player_id):
        """Получить позицию игрока"""
        player = self.get_player(player_id)
        return player.position if player else None
    
    def move_player(self, player_id, dx, dy, dz):
        """Переместить игрока"""
        player = self.get_player(player_id)
        if not player:
            return False
        
        new_x = player.position[0] + dx
        new_y = player.position[1] + dy
        new_z = player.position[2] + dz
        
        if self.can_move_to(new_x, new_y, new_z, player_id):
            player.position = [new_x, new_y, new_z]
            
            # Генерируем новую область если вышли далеко
            if abs(new_x) > 50 or abs(new_y) > 50:
                self.generator.generate_area(new_x, new_y)
            
            return True
        
        return False
