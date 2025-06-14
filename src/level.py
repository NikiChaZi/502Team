import pygame
import os
import random
from pygame import Vector2
from src.tileset import Tileset
from src.tmx_parser import TMXParser, TILE_SIZE as TMX_TILE_SIZE, LEVEL_SCALE_MULTIPLIER

# Размер тайла (стандартный размер из нашего тайлсета)
TILE_SIZE = 32

class Level:
    def __init__(self, level_file=None, level_number=None):
        self.tileset = Tileset()
        self.tmx_parser = TMXParser()
        self.tiles = []
        self.objects = []
        self.width = 0  # Ширина в пикселях
        self.height = 0  # Высота в пикселях
        self.collision_tiles = []
        self.level_number = level_number
        
        # Загружаем уровень
        if level_number is not None:
            # Загружаем уровень по номеру из TMX файлов
            self.load_level_from_tmx(level_number)
        elif level_file and os.path.exists(level_file):
            # Загружаем из текстового файла (старый формат)
            self.load_level_from_file(level_file)
        else:
            # Генерируем случайный уровень
            self.generate_random_level()
    
    def load_level_from_tmx(self, level_number):
        """Загружает уровень из TMX файла"""
        try:
            level_data = self.tmx_parser.load_level(level_number)
            
            if level_data:
                self.tiles = level_data['tiles']
                self.collision_tiles = level_data['collision_tiles']
                # Размеры уже в пикселях с учетом масштабирования
                self.width = level_data['width'] * TMX_TILE_SIZE
                self.height = level_data['height'] * TMX_TILE_SIZE
                self.level_number = level_number
                
                print(f"Успешно загружен уровень {level_number} из TMX файла")
                print(f"Размер уровня: {self.width}x{self.height} пикселей")
                print(f"Количество тайлов: {len(self.tiles)}")
                print(f"Количество коллизионных тайлов: {len(self.collision_tiles)}")
            else:
                print(f"Не удалось загрузить TMX данные для уровня {level_number}")
                self.generate_random_level()
                
        except Exception as e:
            print(f"Ошибка загрузки TMX уровня {level_number}: {e}")
            self.generate_random_level()
            
    def load_level_from_file(self, level_file):
        """Загружает уровень из файла"""
        try:
            with open(level_file, 'r') as f:
                level_data = f.read().splitlines()
                
            self.height = len(level_data)
            self.width = max(len(row) for row in level_data)
            
            # Улучшенный словарь для маппинга символов на идентификаторы тайлов
            tile_mapping = {
                '#': {  # Тайлы земли/платформ
                    'center': [1],      # Центральная часть
                    'edge_left': [2],   # Левый край
                    'edge_right': [3],  # Правый край
                    'single': [4],      # Одиночный блок
                },
                '^': {  # Тайлы травы
                    'normal': [11],     # Обычная трава
                    'edge_left': [12],  # Левый край травы
                    'edge_right': [13], # Правый край травы
                },
                'x': {  # Тайлы препятствий
                    'normal': [21],     # Обычное препятствие
                    'damaged': [22],    # Поврежденное препятствие
                    'special': [23],    # Особое препятствие
                },
                'w': {  # Тайлы воды
                    'normal': [31],     # Обычная вода
                    'deep': [32],       # Глубокая вода
                },
                ' ': None  # Пустое пространство
            }
            
            for y, row in enumerate(level_data):
                for x, cell in enumerate(row):
                    if cell in tile_mapping and tile_mapping[cell]:
                        tile_type = None
                        
                        # Определяем тип тайла на основе контекста
                        if cell == '#':
                            # Проверяем соседние клетки для определения типа блока
                            left_empty = x == 0 or row[x-1] not in '#x'
                            right_empty = x == len(row)-1 or row[x+1] not in '#x'
                            
                            if left_empty and right_empty:
                                tile_type = 'single'
                            elif left_empty:
                                tile_type = 'edge_left'
                            elif right_empty:
                                tile_type = 'edge_right'
                            else:
                                tile_type = 'center'
                                
                        elif cell == '^':
                            # Проверяем соседние клетки для травы
                            left_empty = x == 0 or row[x-1] != '^'
                            right_empty = x == len(row)-1 or row[x+1] != '^'
                            
                            if left_empty:
                                tile_type = 'edge_left'
                            elif right_empty:
                                tile_type = 'edge_right'
                            else:
                                tile_type = 'normal'
                                
                        elif cell == 'x':
                            # Случайный выбор типа препятствия
                            tile_type = random.choice(['normal', 'damaged', 'special'])
                            
                        elif cell == 'w':
                            # Случайный выбор типа воды
                            tile_type = random.choice(['normal', 'deep'])
                        
                        # Выбираем конкретный тайл из доступных вариантов
                        if tile_type:
                            tile_id = random.choice(tile_mapping[cell][tile_type])
                        else:
                            tile_id = random.choice(list(tile_mapping[cell].values())[0])
                            
                        self.tiles.append({
                            'id': tile_id,
                            'position': Vector2(x * TILE_SIZE, y * TILE_SIZE),
                            'rect': pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        })
                        
                        # Если это не вода, добавляем в список тайлов коллизии
                        if cell != 'w':
                            self.collision_tiles.append(pygame.Rect(
                                x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                                
        except Exception as e:
            print(f"Ошибка загрузки уровня из файла {level_file}: {e}")
            self.generate_random_level()
            
    def generate_random_level(self):
        """Генерирует случайный уровень для тестирования"""
        self.width = 50
        self.height = 20
        
        # Создаем "землю" внизу уровня
        ground_level = self.height - 2
        
        for x in range(self.width):
            # Нижний ряд тайлов - земля
            self.tiles.append({
                'id': random.randint(1, 6),
                'position': Vector2(x * TILE_SIZE, ground_level * TILE_SIZE),
                'rect': pygame.Rect(x * TILE_SIZE, ground_level * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            })
            self.collision_tiles.append(pygame.Rect(
                x * TILE_SIZE, ground_level * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                
            # Самый нижний ряд тоже земля
            self.tiles.append({
                'id': random.randint(1, 6),
                'position': Vector2(x * TILE_SIZE, (ground_level + 1) * TILE_SIZE),
                'rect': pygame.Rect(x * TILE_SIZE, (ground_level + 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            })
            self.collision_tiles.append(pygame.Rect(
                x * TILE_SIZE, (ground_level + 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        
        # Добавляем случайные платформы
        for _ in range(20):
            platform_x = random.randint(1, self.width - 6)
            platform_y = random.randint(3, ground_level - 2)
            platform_width = random.randint(3, 8)
            
            for x in range(platform_width):
                tile_x = platform_x + x
                if 0 <= tile_x < self.width:
                    self.tiles.append({
                        'id': random.randint(1, 6),
                        'position': Vector2(tile_x * TILE_SIZE, platform_y * TILE_SIZE),
                        'rect': pygame.Rect(tile_x * TILE_SIZE, platform_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    })
                    self.collision_tiles.append(pygame.Rect(
                        tile_x * TILE_SIZE, platform_y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    def add_object(self, obj_type, position):
        """Добавляет объект на уровень"""
        self.objects.append({
            'type': obj_type,
            'position': position
        })
        
    def draw(self, surface, camera, scale_factor, offset, viewport):
        """Отрисовывает все тайлы уровня"""
        # Размер тайла с учетом масштабирования
        scaled_tile_size = TMX_TILE_SIZE * LEVEL_SCALE_MULTIPLIER
        
        # Вычисляем видимую область
        visible_left = camera.x - scaled_tile_size
        visible_right = camera.x + viewport.width / scale_factor + scaled_tile_size
        visible_top = camera.y - scaled_tile_size
        visible_bottom = camera.y + viewport.height / scale_factor + scaled_tile_size
        
        for tile in self.tiles:
            tile_pos = tile['position']
            
            # Проверяем видимость тайла
            if (tile_pos.x >= visible_left and tile_pos.x <= visible_right and
                tile_pos.y >= visible_top and tile_pos.y <= visible_bottom):
                
                # Вычисляем позицию тайла на экране
                screen_x = int((tile_pos.x - camera.x) * scale_factor + offset.x)
                screen_y = int((tile_pos.y - camera.y) * scale_factor + offset.y)
                
                # Получаем изображение тайла
                tile_image = self.tileset.get_tile(tile['id'])
                if tile_image:
                    # Масштабируем тайл под текущий масштаб
                    scaled_size = int(scaled_tile_size * scale_factor)
                    if scaled_size > 0:
                        scaled_tile = pygame.transform.scale(tile_image, (scaled_size, scaled_size))
                        surface.blit(scaled_tile, (screen_x, screen_y))
                else:
                    # Если тайл не найден, отображаем заглушку
                    rect = pygame.Rect(screen_x, screen_y, int(scaled_tile_size * scale_factor), int(scaled_tile_size * scale_factor))
                    pygame.draw.rect(surface, (0, 255, 255), rect, 1) 