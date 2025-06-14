import pygame
import os
from pygame import Vector2

# Инициализация Pygame (включая шрифты)
pygame.init()

# Получаем разрешение экрана
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
BASE_WIDTH = 1920
BASE_HEIGHT = 1080
ASPECT_RATIO = BASE_WIDTH / BASE_HEIGHT

# Глобальные переменные для размеров и положения
scale_factor = None
offset = None
viewport = None
font = None

# Загрузка и кэширование изображений
menu_background = None
level_background = None
level_background_blurred = None

# Словарь для хранения загруженных изображений
loaded_images = {}

def load_image(path, alpha=True):
    """Загружает изображение из файла или возвращает из кэша"""
    if path in loaded_images:
        return loaded_images[path]
    
    try:
        if alpha:
            image = pygame.image.load(path).convert_alpha()
        else:
            image = pygame.image.load(path).convert()
        loaded_images[path] = image
        return image
    except Exception as e:
        print(f"Ошибка загрузки изображения {path}: {e}")
        return None

def load_backgrounds():
    """Загружает и масштабирует фоновые изображения"""
    global menu_background, level_background, level_background_blurred
    
    try:
        # Загружаем фон для меню
        menu_bg_path = 'src/Assets/Background/Background.png'
        if os.path.exists(menu_bg_path):
            menu_background = load_image(menu_bg_path)
            menu_background = scale_background(menu_background, viewport.width, viewport.height)
        else:
            print(f"Фон меню не найден: {menu_bg_path}")
            menu_background = None
            
        # Загружаем фон для уровня
        level_bg_path = 'src/Assets/Background/Background.png'
        if os.path.exists(level_bg_path):
            level_background = load_image(level_bg_path)
            level_background = scale_background(level_background, viewport.width, viewport.height)
            level_background_blurred = blur_surface(level_background, blur_radius=5)
        else:
            print(f"Фон уровня не найден: {level_bg_path}")
            level_background = None
            level_background_blurred = None
            
    except Exception as e:
        print(f"Ошибка при загрузке фонов: {e}")
        if menu_background is None:
            menu_background = create_placeholder(viewport.width, viewport.height, (0, 50, 0))
        if level_background is None:
            level_background = create_placeholder(viewport.width, viewport.height, (0, 100, 50))
            level_background_blurred = blur_surface(level_background, blur_radius=3)

def create_placeholder(width, height, color=(50, 50, 50)):
    """Создает заполнитель для изображения"""
    surface = pygame.Surface((width, height))
    surface.fill(color)
    return surface

def scale_background(image, target_width, target_height):
    """Масштабирует фоновое изображение"""
    if image is None:
        return None
    try:
        scaled_image = pygame.transform.scale(image, (int(target_width), int(target_height)))
        return scaled_image
    except Exception as e:
        print(f"Ошибка масштабирования изображения: {e}")
        return None

def blur_surface(surface, blur_radius=5):
    """Создает размытую версию поверхности"""
    if surface is None:
        return None
    
    try:
        surface = surface.convert_alpha()
        width, height = surface.get_size()
        
        # Применяем размытие путем даунсэмплинга и апсэмплинга
        for _ in range(blur_radius):
            # Уменьшаем размер (даунсэмплинг)
            scaled_down = pygame.transform.smoothscale(surface, (width // 2, height // 2))
            
            # Увеличиваем обратно (апсэмплинг)
            surface = pygame.transform.smoothscale(scaled_down, (width, height))
            
        # Добавляем немного прозрачности для затемнения
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 64))  # Полупрозрачный черный
        surface.blit(overlay, (0, 0))
        
        return surface
    except Exception as e:
        print(f"Ошибка при размытии поверхности: {e}")
        return surface

def get_scaled_font(scale):
    """Возвращает шрифт подходящего размера"""
    global font
    font_size = int(60 * scale)  # Увеличили размер шрифта с 48 до 60
    
    try:
        font_path = 'src/Resources/pixel_font.ttf'
        if os.path.exists(font_path):
            font = pygame.font.Font(font_path, font_size)
        else:
            print(f"Шрифт не найден: {font_path}, используется системный шрифт")
            font = pygame.font.SysFont('monospace', font_size)
    except Exception as e:
        print(f"Ошибка загрузки шрифта: {e}")
        font = pygame.font.SysFont(None, font_size)
    
    return font

def calculate_viewport():
    """Рассчитывает размер и положение видового окна"""
    global scale_factor, offset, viewport, WIDTH, HEIGHT
    
    # Рассчитываем соотношение сторон окна
    window_aspect = WIDTH / HEIGHT
    
    # Если соотношение сторон окна шире, чем наше базовое
    if window_aspect > ASPECT_RATIO:
        viewport_height = HEIGHT
        viewport_width = int(HEIGHT * ASPECT_RATIO)
        scale_factor = viewport_height / BASE_HEIGHT
        offset = Vector2((WIDTH - viewport_width) / 2, 0)
    else:
        viewport_width = WIDTH
        viewport_height = int(WIDTH / ASPECT_RATIO)
        scale_factor = viewport_width / BASE_WIDTH
        offset = Vector2(0, (HEIGHT - viewport_height) / 2)
    
    viewport = pygame.Rect(offset.x, offset.y, viewport_width, viewport_height)
    
    return scale_factor, offset, viewport

def handle_resize(new_width, new_height):
    """Обрабатывает изменение размера окна"""
    global WIDTH, HEIGHT, menu_background, level_background, level_background_blurred, font, scale_factor, offset, viewport
    from src.ui import main_menu_buttons, settings_menu_elements, pause_buttons
    
    # Обновляем размеры окна
    WIDTH, HEIGHT = new_width, new_height
    
    # Создаем окно без рамки
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    
    # Пересчитываем размеры и положение
    scale_factor, offset, viewport = calculate_viewport()
    
    # Обновляем фоны
    load_backgrounds()
    
    # Обновляем шрифт
    font = get_scaled_font(scale_factor)
    
    # Обновляем элементы интерфейса
    for button in main_menu_buttons:
        button.update_rect(scale_factor, offset)
        
    for element in settings_menu_elements:
        element.update_rect(scale_factor, offset)
        
    for button in pause_buttons:
        button.update_rect(scale_factor, offset)
    
    print(f"Окно изменено: {new_width}x{new_height}, масштаб={scale_factor}, смещение={offset}")

# Инициализация при импорте
scale_factor, offset, viewport = calculate_viewport()
font = get_scaled_font(scale_factor)
load_backgrounds() 