import pygame
import os

class Tileset:
    def __init__(self):
        self.tiles = {}
        self.load_tiles()

    def load_tiles(self):
        """Загружает тайлсет из папки Levels/Tiled или создает простые тайлы"""
        try:
            # Пытаемся загрузить основной тайлсет из папки Levels/Tiled
            tileset_path = 'src/Levels/Tiled/Tileset.png'
            
            if os.path.exists(tileset_path):
                print(f"Загружаем тайлсет из {tileset_path}")
                tileset_image = pygame.image.load(tileset_path).convert_alpha()
                
                # Тайлсет из Tiled имеет размер 16x16 пикселей на тайл
                tile_width = 16
                tile_height = 16
                columns = tileset_image.get_width() // tile_width
                rows = tileset_image.get_height() // tile_height
                
                # Извлекаем каждый тайл
                tile_id = 1
                for row in range(rows):
                    for col in range(columns):
                        x = col * tile_width
                        y = row * tile_height
                        
                        # Извлекаем тайл
                        tile_rect = pygame.Rect(x, y, tile_width, tile_height)
                        tile_surface = tileset_image.subsurface(tile_rect).copy()
                        
                        self.tiles[tile_id] = tile_surface
                        tile_id += 1
                
                print(f"Загружено {len(self.tiles)} тайлов из тайлсета")
            else:
                # Если основной тайлсет не найден, пробуем альтернативные пути
                alternative_paths = [
                    'src/Assets/Tiles',
                    'src/Assets/2 Locations/Tiles',
                    'src/Levels/Tileset'
                ]
                
                tiles_found = False
                for directory in alternative_paths:
                    if os.path.exists(directory):
                        self.load_individual_tiles(directory)
                        if self.tiles:
                            tiles_found = True
                            break
                
                if not tiles_found:
                    print("Тайлсет не найден, создаем простые тайлы")
                    self.create_simple_tiles()
                    
        except Exception as e:
            print(f"Ошибка при загрузке тайлсета: {e}")
            self.create_simple_tiles()

    def load_individual_tiles(self, directory):
        """Загружает отдельные тайлы из директории"""
        try:
            tile_files = [f for f in os.listdir(directory) if f.endswith('.png')]
            
            for tile_file in tile_files:
                try:
                    # Extract the tile ID safely
                    parts = tile_file.split('_')
                    if len(parts) > 1:
                        # Format like "Tile_1.png"
                        tile_id = int(parts[1].split('.')[0])
                    else:
                        # Format like "1.png"
                        tile_id = int(parts[0].split('.')[0])
                        
                    tile_path = os.path.join(directory, tile_file)
                    tile_img = pygame.image.load(tile_path).convert_alpha()
                    self.tiles[tile_id] = tile_img
                except Exception as e:
                    print(f"Ошибка загрузки тайла {tile_file}: {e}")
        
            print(f"Загружено {len(self.tiles)} отдельных тайлов из {directory}")
        except Exception as e:
            print(f"Ошибка при загрузке отдельных тайлов: {e}")

    def create_simple_tiles(self):
        """Создает простые цветные тайлы как заглушки"""
        tile_size = 16
        colors = [
            (100, 100, 100),  # 1 - серый (камень)
            (139, 69, 19),    # 2 - коричневый (земля)
            (34, 139, 34),    # 3 - зеленый (трава)
            (65, 105, 225),   # 4 - синий (вода)
            (160, 82, 45),    # 5 - светло-коричневый (дерево)
            (255, 215, 0),    # 6 - золотой (декор)
        ]
        
        for i, color in enumerate(colors, 1):
            tile = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            tile.fill(color)
            # Добавляем рамку
            pygame.draw.rect(tile, (0, 0, 0), tile.get_rect(), 1)
            self.tiles[i] = tile
            
        print(f"Создано {len(colors)} простых тайлов")

    def get_tile(self, tile_id):
        """Возвращает тайл по его идентификатору"""
        if tile_id in self.tiles:
            return self.tiles[tile_id]
        # Если тайл не найден, возвращаем первый доступный или None
        if self.tiles:
            return list(self.tiles.values())[0]
        return None

    def get_scaled_tile(self, tile_id, scale_factor):
        """Возвращает масштабированный тайл"""
        tile = self.get_tile(tile_id)
        if tile:
            width = int(tile.get_width() * scale_factor)
            height = int(tile.get_height() * scale_factor)
            return pygame.transform.scale(tile, (width, height))
        return None 