# player.py
import json
from config import MAX_HEALTH, ATTACK_DAMAGE, AIR_HEIGHT

class Player:
    def __init__(self, user_id, username, spawn_x=0, spawn_y=0):
        self.user_id = str(user_id)
        self.username = username or "Игрок"
        self.position = [spawn_x, spawn_y, AIR_HEIGHT + 1]  # На траве
        self.health = MAX_HEALTH
        self.inventory = {}
        self.modified_blocks = {}  # Блоки, измененные этим игроком
        
    def load_from_dict(self, data):
        """Загрузить из словаря"""
        self.position = data.get('position', [0, 0, AIR_HEIGHT + 1])
        self.health = data.get('health', MAX_HEALTH)
        self.inventory = data.get('inventory', {})
        self.modified_blocks = data.get('modified_blocks', {})
    
    def to_dict(self):
        """Сохранить в словарь"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'position': self.position,
            'health': self.health,
            'inventory': self.inventory,
            'modified_blocks': self.modified_blocks
        }
    
    def take_damage(self, damage):
        """Получить урон"""
        self.health = max(0, self.health - damage)
        return self.health > 0  # True если жив
    
    def heal(self, amount):
        """Лечение"""
        self.health = min(MAX_HEALTH, self.health + amount)
    
    def move(self, dx, dy, dz):
        """Перемещение"""
        self.position[0] += dx
        self.position[1] += dy
        self.position[2] += dz
    
    def get_position_key(self):
        """Ключ позиции"""
        x, y, z = self.position
        return f"{x},{y},{z}"
    
    def add_to_inventory(self, item, count=1):
        """Добавить в инвентарь"""
        if item in self.inventory:
            self.inventory[item] += count
        else:
            self.inventory[item] = count
    
    def remove_from_inventory(self, item, count=1):
        """Убрать из инвентаря"""
        if item in self.inventory:
            self.inventory[item] -= count
            if self.inventory[item] <= 0:
                del self.inventory[item]
            return True
        return False
    
    def has_inventory(self, item, count=1):
        """Проверить наличие в инвентаре"""
        return self.inventory.get(item, 0) >= count
