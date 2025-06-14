import pygame
import os
from pygame import Vector2

class ParallaxBackground:
    def __init__(self):
        self.layers = []
        self.width = 0
        self.height = 0
        self.load_layers()
        
    def load_layers(self):
        """Загружает слои фона из обновленной структуры папок"""
        try:
            # Пробуем разные возможные пути к фонам
            possible_directories = [
                'src/Assets/2 Locations/Background',
                'src/Assets/Background',
                'src/Levels/Tiled/Backgrounds'
            ]
            
            backgrounds_found = False
            
            for directory in possible_directories:
                if os.path.exists(directory):
                    print(f"Найдена директория фонов: {directory}")
                    self.load_backgrounds_from_directory(directory)
                    if self.layers:
                        backgrounds_found = True
                        break
            
            if not backgrounds_found:
                print("Фоны не найдены, создаем простой градиентный фон")
                self.create_simple_background()
                
        except Exception as e:
            print(f"Ошибка при загрузке фоновых слоев: {e}")
            self.create_simple_background()
            
    def load_backgrounds_from_directory(self, directory):
        """Загружает фоны из конкретной директории"""
        try:
            # Поиск файлов фона с числовыми именами и общих файлов
            all_files = os.listdir(directory)
            bg_files = []
            
            # Ищем основной файл Background.png
            if "Background.png" in all_files:
                bg_files.append("Background.png")
                
            # Ищем пронумерованные файлы
            numbered_files = [f for f in all_files if f.replace('.png', '').isdigit()]
            numbered_files.sort(key=lambda x: int(x.split('.')[0]))
            bg_files.extend(numbered_files)
            
            # Если не нашли пронумерованные, добавляем все PNG файлы
            if not numbered_files:
                png_files = [f for f in all_files if f.endswith('.png') and f != "Background.png"]
                bg_files.extend(png_files)
                
            for i, bg_file in enumerate(bg_files):
                try:
                    bg_path = os.path.join(directory, bg_file)
                    bg_img = pygame.image.load(bg_path).convert_alpha()
                    
                    # Коэффициент паралакса (дальние слои движутся медленнее)
                    parallax_factor = 0.1 * (i + 1)
                    
                    self.layers.append({
                        'image': bg_img,
                        'parallax_factor': parallax_factor,
                        'position': Vector2(0, 0)
                    })
                    
                    # Обновляем максимальные размеры слоев
                    self.width = max(self.width, bg_img.get_width())
                    self.height = max(self.height, bg_img.get_height())
                    
                    print(f"Загружен фоновый слой: {bg_file}")
                except Exception as e:
                    print(f"Ошибка загрузки фона {bg_file}: {e}")
            
            print(f"Загружено {len(self.layers)} слоев фона из {directory}")
        except Exception as e:
            print(f"Ошибка при загрузке фонов из {directory}: {e}")
    
    def create_simple_background(self):
        """Создает простой градиентный фон как заглушку"""
        try:
            # Создаем простой градиентный фон
            bg_surface = pygame.Surface((1920, 1080))
            
            # Градиент от темно-синего к светло-голубому
            for y in range(1080):
                color_ratio = y / 1080
                red = int(20 + (135 - 20) * color_ratio)
                green = int(30 + (206 - 30) * color_ratio)
                blue = int(50 + (235 - 50) * color_ratio)
                
                pygame.draw.line(bg_surface, (red, green, blue), (0, y), (1920, y))
            
            self.layers.append({
                'image': bg_surface,
                'parallax_factor': 0.1,
                'position': Vector2(0, 0)
            })
            
            self.width = 1920
            self.height = 1080
            
            print("Создан простой градиентный фон")
        except Exception as e:
            print(f"Ошибка создания простого фона: {e}")
            
    def update(self, camera):
        """Обновляет позиции слоев фона на основе положения камеры"""
        for layer in self.layers:
            # Обновляем X-координату слоя с учетом коэффициента параллакса
            layer['position'].x = -camera.x * layer['parallax_factor']
            # Y-координату обновляем аналогично
            layer['position'].y = -camera.y * layer['parallax_factor'] * 0.5
            
    def draw(self, surface, offset, viewport, scale_factor=1.0):
        """Отрисовывает все слои фона"""
        if not self.layers:
            return
            
        for layer in self.layers:
            img = layer['image']
            
            # Масштабируем изображение
            if scale_factor != 1.0:
                width = int(img.get_width() * scale_factor)
                height = int(img.get_height() * scale_factor)
                img = pygame.transform.scale(img, (width, height))
                
            # Вычисляем позицию для отрисовки
            pos_x = int(layer['position'].x * scale_factor + offset.x)
            pos_y = int(layer['position'].y * scale_factor + offset.y)
            
            # Отрисовываем слой
            surface.blit(img, (pos_x, pos_y))
            
            # Если изображение меньше экрана, повторяем его по горизонтали
            img_width = img.get_width()
            viewport_width = viewport.width
            
            if img_width < viewport_width:
                repeats = int(viewport_width / img_width) + 2
                for i in range(1, repeats):
                    surface.blit(img, (pos_x + img_width * i, pos_y)) 