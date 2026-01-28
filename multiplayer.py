import json
import random
from config import WORLD_FILE, PLAYER_SPAWN_RADIUS
from world import GameWorld

class MultiplayerManager:
    def __init__(self):
        self.worlds = {}  # world_id: GameWorld
        self.player_worlds = {}  # user_id: world_id
        
        self.load_worlds()
    
    def load_worlds(self):
        """Загрузить миры из файла"""
        try:
            with open(WORLD_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for world_id, world_data in data.items():
                world = GameWorld(world_id)
                world.load_from_dict(world_data)
                self.worlds[world_id] = world
                
                # Восстанавливаем привязки игроков
                for player_id in world.players.keys():
                    self.player_worlds[player_id] = world_id
                    
        except FileNotFoundError:
            self.worlds = {}
            self.player_worlds = {}
    
    def save_worlds(self):
        """Сохранить миры"""
        data = {world_id: world.to_dict() for world_id, world in self.worlds.items()}
        
        with open(WORLD_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def create_world(self, world_id="default"):
        """Создать новый мир"""
        if world_id in self.worlds:
            return self.worlds[world_id]
        
        world = GameWorld(world_id)
        self.worlds[world_id] = world
        self.save_worlds()
        return world
    
    def join_world(self, user_id, username, world_id="default"):
        """Присоединиться к миру"""
        # Проверяем, есть ли уже мир
        if world_id not in self.worlds:
            world = self.create_world(world_id)
        else:
            world = self.worlds[world_id]
        
        # Добавляем/получаем игрока
        player = world.add_player(user_id, username)
        self.player_worlds[user_id] = world_id
        self.save_worlds()
        
        return world, player
    
    def get_player_world(self, user_id):
        """Получить мир игрока"""
        if user_id in self.player_worlds:
            world_id = self.player_worlds[user_id]
            return self.worlds.get(world_id)
        return None
    
    def get_online_players(self, user_id):
        """Получить список онлайн игроков"""
        world = self.get_player_world(user_id)
        if not world:
            return []
        
        online = []
        for player_id, player in world.players.items():
            if str(player_id) != str(user_id):
                online.append({
                    'username': player.username,
                    'health': player.health,
                    'position': player.position
                })
        
        return online
    
    def attack_player(self, attacker_id, target_x, target_y, target_z):
        """Атака другого игрока"""
        world = self.get_player_world(attacker_id)
        if not world:
            return None, 0
        
        attacker = world.get_player(attacker_id)
        if not attacker:
            return None, 0
        
        # Ищем игрока на этой позиции
        for player_id, player in world.players.items():
            if str(player_id) != str(attacker_id):
                px, py, pz = player.position
                if px == target_x and py == target_y and pz == target_z:
                    # Наносим урон
                    damage = 1  # базовый урон
                    alive = player.take_damage(damage)
                    
                    # Если умер - телепортируем на спавн
                    if not alive:
                        player.position = [0, 0, 21]
                        player.health = 10
                    
                    self.save_worlds()
                    return player.username, damage
        
        return None, 0
