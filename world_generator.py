import json
import random
from config import AIR_HEIGHT, GRASS_HEIGHT, WORLD_SEED

class WorldGenerator:
    def __init__(self, items_file="items.json"):
        with open(items_file, 'r', encoding='utf-8') as f:
            self.items_data = json.load(f)
        
        self.tree_positions = {}
        self.mushroom_positions = {}
        
    def _get_seed(self, x, y, z=0):
        """Сид для координат"""
        return hash(f"{x}_{y}_{z}_{WORLD_SEED}") % 1000000
    
    def generate_terrain(self, x, y, z):
        """Генерация блока на позиции"""
        # Проверяем ручную замену
        key = f"{x},{y},{z}"
        
        # СЛОЙ 1: ВОЗДУХ
        if z > AIR_HEIGHT:
            tree_key = f"{x},{y}"
            
            # ДЕРЕВЬЯ
            if tree_key in self.tree_positions:
                if z == AIR_HEIGHT + 1:
                    return "листва"
                elif z == AIR_HEIGHT + 2 or z == AIR_HEIGHT + 3:
                    return "ствол"
                elif z == AIR_HEIGHT + 4:
                    return "листва"
            
            # ГРИБЫ
            if z == AIR_HEIGHT + 1 and tree_key in self.mushroom_positions:
                return "гриб поганка"
            
            return "воздух"
        
        # СЛОЙ 2: ТРАВА
        elif z == AIR_HEIGHT:
            return "трава"
        
        # СЛОЙ 3: ЗЕМЛЯ
        elif AIR_HEIGHT - GRASS_HEIGHT < z < AIR_HEIGHT:
            return "земля"
        
        # СЛОЙ 4: КАМЕНЬ и РУДЫ
        else:
            depth = AIR_HEIGHT - z - GRASS_HEIGHT
            
            seed = self._get_seed(x * 1000 + y, z)
            random.seed(seed)
            rand_val = random.random()
            
            if depth >= 25 and depth <= 30:
                if rand_val < 0.05:
                    return "алмазная руда"
            
            if depth >= 15 and depth <= 25:
                if rand_val < 0.07:
                    return "золотая руда"
            
            if depth >= 8 and depth <= 15:
                if rand_val < 0.1:
                    return "железная руда"
            
            if depth >= 3 and depth <= 15:
                if rand_val < 0.15:
                    return "уголь"
            
            return "камень"
    
    def generate_area(self, center_x, center_y, radius=20):
        """Генерация области"""
        for x in range(center_x - radius, center_x + radius + 1):
            for y in range(center_y - radius, center_y + radius + 1):
                seed = self._get_seed(x, y)
                random.seed(seed)
                
                tree_key = f"{x},{y}"
                if random.random() < 0.3:
                    self.tree_positions[tree_key] = True
                
                if random.random() < 0.2:
                    self.mushroom_positions[tree_key] = True
    
    def get_block_data(self, block_type):
        """Получить данные блока"""
        return self.items_data["блоки"].get(block_type, {})
