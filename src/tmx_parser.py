import xml.etree.ElementTree as ET
import pygame
import os
from pygame import Vector2

TILE_SIZE = 16  # TMX использует тайлы 16x16
GAME_TILE_SIZE = 32  # Размер тайла в игре
LEVEL_SCALE_MULTIPLIER = 3  # Множитель для увеличения размера уровня

class TMXParser:
    """Парсер для TMX файлов из Tiled"""
    
    def __init__(self):
        self.tile_size = TILE_SIZE
        self.game_tile_size = GAME_TILE_SIZE
        self.scale_multiplier = LEVEL_SCALE_MULTIPLIER
        
    def parse_tmx_file(self, tmx_file_path):
        """Парсит TMX файл и возвращает данные уровня"""
        if not os.path.exists(tmx_file_path):
            print(f"TMX файл не найден: {tmx_file_path}")
            return None
            
        try:
            tree = ET.parse(tmx_file_path)
            root = tree.getroot()
            
            # Получаем основные параметры карты
            width = int(root.get('width'))
            height = int(root.get('height'))
            tile_width = int(root.get('tilewidth'))
            tile_height = int(root.get('tileheight'))
            
            print(f"Загружаем уровень {tmx_file_path}: {width}x{height}, тайлы {tile_width}x{tile_height}")
            
            # Парсим тайлсеты
            tilesets = {}
            for tileset in root.findall('tileset'):
                firstgid = int(tileset.get('firstgid'))
                name = tileset.get('name')
                tilecount = int(tileset.get('tilecount'))
                columns = int(tileset.get('columns'))
                
                image_element = tileset.find('image')
                if image_element is not None:
                    source = image_element.get('source')
                    image_width = int(image_element.get('width'))
                    image_height = int(image_element.get('height'))
                    
                    tilesets[firstgid] = {
                        'name': name,
                        'source': source,
                        'tilecount': tilecount,
                        'columns': columns,
                        'image_width': image_width,
                        'image_height': image_height
                    }
            
            # Парсим слои
            layers = []
            for layer in root.findall('layer'):
                layer_name = layer.get('name')
                layer_width = int(layer.get('width'))
                layer_height = int(layer.get('height'))
                
                # Получаем данные тайлов
                data_element = layer.find('data')
                if data_element is not None and data_element.get('encoding') == 'csv':
                    # Парсим CSV данные
                    csv_data = data_element.text.strip()
                    tile_data = []
                    
                    for row in csv_data.split('\n'):
                        row_tiles = []
                        for tile_id in row.split(','):
                            tile_id = tile_id.strip()
                            if tile_id:
                                row_tiles.append(int(tile_id))
                        if row_tiles:
                            tile_data.append(row_tiles)
                    
                    layers.append({
                        'name': layer_name,
                        'width': layer_width,
                        'height': layer_height,
                        'data': tile_data
                    })
            
            return {
                'width': width,
                'height': height,
                'tile_width': tile_width,
                'tile_height': tile_height,
                'tilesets': tilesets,
                'layers': layers
            }
            
        except Exception as e:
            print(f"Ошибка парсинга TMX файла {tmx_file_path}: {e}")
            return None
    
    def convert_to_game_level(self, tmx_data, level_number):
        """Конвертирует TMX данные в формат игрового уровня"""
        if not tmx_data:
            return None
            
        tiles = []
        collision_tiles = []
        
        # Обрабатываем каждый слой
        for layer in tmx_data['layers']:
            layer_name = layer['name'].lower()
            
            # Определяем, какие слои содержат коллизии
            collision_layers = ['tiles', 'edge', 'collision']
            is_collision_layer = any(collision_name in layer_name for collision_name in collision_layers)
            
            for y, row in enumerate(layer['data']):
                for x, tile_id in enumerate(row):
                    if tile_id > 0:  # 0 означает пустой тайл
                        # Позиции с учетом множителя масштаба
                        game_x = x * TILE_SIZE * self.scale_multiplier
                        game_y = y * TILE_SIZE * self.scale_multiplier
                        tile_size = TILE_SIZE * self.scale_multiplier
                        
                        tile_info = {
                            'id': tile_id,
                            'position': Vector2(game_x, game_y),
                            'rect': pygame.Rect(game_x, game_y, tile_size, tile_size),
                            'layer': layer_name
                        }
                        
                        tiles.append(tile_info)
                        
                        # Добавляем в коллизии если это коллизионный слой
                        if is_collision_layer and layer_name != 'back':  # Исключаем фоновые элементы
                            collision_tiles.append(pygame.Rect(game_x, game_y, tile_size, tile_size))
        
        return {
            'tiles': tiles,
            'collision_tiles': collision_tiles,
            'width': tmx_data['width'] * self.scale_multiplier,  # Ширина в тайлах с учетом масштаба
            'height': tmx_data['height'] * self.scale_multiplier,  # Высота в тайлах с учетом масштаба
            'level_number': level_number
        }
    
    def load_level(self, level_number):
        """Загружает уровень по номеру"""
        tmx_file = f'src/Levels/Tiled/{level_number}.tmx'
        
        tmx_data = self.parse_tmx_file(tmx_file)
        if tmx_data:
            return self.convert_to_game_level(tmx_data, level_number)
        
        print(f"Не удалось загрузить уровень {level_number}")
        return None 