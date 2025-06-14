import pygame
import os
from pygame import Vector2
from src.utils import scale_factor, offset, viewport, font

# Constants for base resolution
BASE_WIDTH = 1920
BASE_HEIGHT = 1080

class UIElement:
    """Базовый класс для всех элементов пользовательского интерфейса"""
    def __init__(self, x, y, width, height):
        self.base_x, self.base_y = x, y
        self.base_width, self.base_height = width, height
        self.update_rect(scale_factor, offset)
    
    def update_rect(self, scale_factor, offset):
        self.rect = pygame.Rect(
            int(self.base_x * scale_factor + offset.x),
            int(self.base_y * scale_factor + offset.y),
            int(self.base_width * scale_factor),
            int(self.base_height * scale_factor)
        )
    
    def draw(self, surface):
        pass
    
    def update(self, mouse_pos, mouse_pressed=False):
        pass

class Button(UIElement):
    """Кнопка пользовательского интерфейса"""
    def __init__(self, text, x=None, y=None, width=None, height=None, pos=None, font=None, normal_color=(255, 255, 255), hover_color=(150, 150, 150), size=None):
        # Поддержка как старого, так и нового формата параметров
        if pos is not None:
            # Новый формат (с центром кнопки)
            x = pos[0] - (size[0] / 2 if size else 100)
            y = pos[1] - (size[1] / 2 if size else 30)
            width = size[0] if size else 200
            height = size[1] if size else 60
        
        # Увеличим ширину кнопки по умолчанию для размещения текста
        if width is None:
            width = 300  # Больший размер кнопки по умолчанию
        
        super().__init__(x, y, width, height)
        self.text = text
        self.font = font
        self.color = normal_color
        self.hover_color = hover_color
        self.current_color = self.color
        self.hovered = False
        
        # Дополнительные визуальные эффекты
        self.border_radius = int(10 * scale_factor)
        self.border_width = int(2 * scale_factor)
        self.bg_color = (50, 50, 50, 180)
        self.hover_bg_color = (70, 70, 70, 200)
        self.current_bg_color = self.bg_color
    
    def draw(self, surface):
        # Отрисовываем фон кнопки (прямоугольник с закругленными углами)
        pygame.draw.rect(
            surface, 
            self.current_bg_color, 
            self.rect, 
            border_radius=self.border_radius
        )
        
        # Отрисовываем рамку кнопки
        pygame.draw.rect(
            surface, 
            self.current_color, 
            self.rect, 
            width=self.border_width,
            border_radius=self.border_radius
        )
        
        # Отрисовываем текст
        text_font = self.font if self.font else font
        if text_font:
            # Рассчитываем размер текста и масштабируем его при необходимости
            text_surface = text_font.render(self.text, True, self.current_color)
            text_width = text_surface.get_width()
            
            # Если текст шире, чем кнопка, масштабируем его
            if text_width > self.rect.width - 20:
                scale_ratio = (self.rect.width - 20) / text_width
                new_width = int(text_width * scale_ratio)
                new_height = int(text_surface.get_height() * scale_ratio)
                text_surface = pygame.transform.scale(text_surface, (new_width, new_height))
            
            text_rect = text_surface.get_rect(center=self.rect.center)
            if viewport.colliderect(text_rect):
                surface.blit(text_surface, text_rect)
    
    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def update(self, mouse_pos, mouse_pressed=False):
        self.hovered = self.is_hovered(mouse_pos)
        if self.hovered:
            self.current_color = self.hover_color
            self.current_bg_color = self.hover_bg_color
        else:
            self.current_color = self.color
            self.current_bg_color = self.bg_color

class Slider(UIElement):
    """Ползунок для настройки параметров"""
    def __init__(self, label, x, y, width, height, min_val, max_val, initial_val):
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        
        # Call parent constructor after setting value
        super().__init__(x, y, width, height)
        
        # Вычисляем размер и положение ручки
        self.update_handle()
    
    def update_rect(self, scale_factor, offset):
        super().update_rect(scale_factor, offset)
        self.update_handle()
    
    def update_handle(self):
        handle_width = int(20 * scale_factor)
        handle_height = int(40 * scale_factor)
        
        # Вычисляем X-координату ручки
        value_ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = int(self.rect.x + value_ratio * (self.rect.width - handle_width))
        
        # Создаем прямоугольник для ручки
        self.handle_rect = pygame.Rect(
            handle_x,
            int(self.rect.y - (handle_height - self.rect.height) / 2),
            handle_width,
            handle_height
        )
    
    def draw(self, surface):
        # Отрисовываем метку
        if font:
            label_surface = font.render(self.label, True, (255, 255, 255))
            label_rect = label_surface.get_rect(
                right=self.rect.left - int(20 * scale_factor), 
                centery=self.rect.centery
            )
            if viewport.colliderect(label_rect):
                surface.blit(label_surface, label_rect)
        
        # Отрисовываем фон ползунка
        bg_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(surface, (50, 50, 50), bg_rect, border_radius=int(5 * scale_factor))
        
        # Отрисовываем заполненную часть ползунка
        fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        fill_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            fill_width,
            self.rect.height
        )
        pygame.draw.rect(surface, (100, 200, 100), fill_rect, border_radius=int(5 * scale_factor))
        
        # Отрисовываем контур ползунка
        pygame.draw.rect(
            surface, 
            (255, 255, 255), 
            self.rect, 
            width=int(2 * scale_factor),
            border_radius=int(5 * scale_factor)
        )
        
        # Отрисовываем ручку
        pygame.draw.rect(
            surface, 
            (150, 150, 150), 
            self.handle_rect, 
            border_radius=int(5 * scale_factor)
        )
        pygame.draw.rect(
            surface, 
            (255, 255, 255), 
            self.handle_rect, 
            width=int(2 * scale_factor),
            border_radius=int(5 * scale_factor)
        )
        
        # Отрисовываем текущее значение
        if font:
            value_text = f"{int(self.value)}%"
            value_surface = font.render(value_text, True, (255, 255, 255))
            value_rect = value_surface.get_rect(
                left=self.rect.right + int(20 * scale_factor), 
                centery=self.rect.centery
            )
            if viewport.colliderect(value_rect):
                surface.blit(value_surface, value_rect)
    
    def update(self, mouse_pos, mouse_pressed):
        # Если нажата кнопка мыши и курсор над ручкой, начинаем перетаскивание
        if mouse_pressed and not self.dragging:
            if self.handle_rect.collidepoint(mouse_pos):
                self.dragging = True
        
        # Если не нажата кнопка мыши, прекращаем перетаскивание
        if not mouse_pressed:
            self.dragging = False
        
        # Если перетаскиваем, обновляем положение ручки и значение
        if self.dragging:
            x_pos = max(self.rect.left, min(mouse_pos[0], self.rect.right))
            relative_pos = x_pos - self.rect.left
            value_ratio = relative_pos / self.rect.width
            self.value = self.min_val + value_ratio * (self.max_val - self.min_val)
            self.update_handle()
            
            # Применяем настройку громкости, если это ползунок громкости
            if self.label == "Громкость":
                try:
                    pygame.mixer.music.set_volume(self.value / 100)
                except:
                    pass

class HUD:
    """Интерфейс для отображения игровой информации"""
    def __init__(self, player, clock):
        self.player = player
        self.clock = clock
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.update_fonts(scale_factor)
        
        # Загружаем иконки
        self.load_icons()
    
    def load_icons(self):
        """Загружает иконки для HUD"""
        self.icons = {}
        
        try:
            # Иконка монеты
            coin_path = 'src/Assets/AnimatedObjects/Money.png'
            if os.path.exists(coin_path):
                coin_sheet = pygame.image.load(coin_path).convert_alpha()
                # Используем первый кадр из Money.png (размер 24x24)
                self.icons['coin'] = coin_sheet.subsurface((0, 0, 24, 24))
            else:
                self.icons['coin'] = self.create_placeholder(24, 24, (255, 255, 0))
                
            # Иконка здоровья
            self.icons['health'] = self.create_placeholder(24, 24, (255, 0, 0))
            
            # Иконка крюка
            self.icons['hook'] = self.create_placeholder(24, 24, (200, 200, 200))
            
        except Exception as e:
            print(f"Ошибка загрузки иконок HUD: {e}")
            # Создаем заполнители для иконок
            self.icons['coin'] = self.create_placeholder(24, 24, (255, 255, 0))
            self.icons['health'] = self.create_placeholder(24, 24, (255, 0, 0))
            self.icons['hook'] = self.create_placeholder(24, 24, (200, 200, 200))
    
    def create_placeholder(self, width, height, color):
        """Создает заполнитель для иконки"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(color)
        return surface
    
    def update_fonts(self, scale_factor):
        """Обновляет шрифты интерфейса"""
        font_path = 'src/Resources/pixel_font.ttf'
        
        try:
            if os.path.exists(font_path):
                self.font_large = pygame.font.Font(font_path, int(32 * scale_factor))
                self.font_medium = pygame.font.Font(font_path, int(24 * scale_factor))
                self.font_small = pygame.font.Font(font_path, int(18 * scale_factor))
            else:
                print(f"Шрифт не найден: {font_path}, используется системный шрифт")
                self.font_large = pygame.font.SysFont('monospace', int(32 * scale_factor))
                self.font_medium = pygame.font.SysFont('monospace', int(24 * scale_factor))
                self.font_small = pygame.font.SysFont('monospace', int(18 * scale_factor))
        except Exception as e:
            print(f"Ошибка загрузки шрифтов: {e}")
            self.font_large = pygame.font.SysFont(None, int(32 * scale_factor))
            self.font_medium = pygame.font.SysFont(None, int(24 * scale_factor))
            self.font_small = pygame.font.SysFont(None, int(18 * scale_factor))
    
    def draw(self, surface, offset, viewport, score=0):
        """Отрисовывает HUD"""
        if not self.font_medium:
            self.update_fonts(scale_factor)
        
        # Настраиваем отступы и размеры
        hud_x = int(offset.x + 20 * scale_factor)
        hud_y = int(offset.y + 20 * scale_factor)
        item_height = int(30 * scale_factor)
        
        # Отрисовываем FPS
        fps = str(int(self.clock.get_fps()))
        fps_text = self.font_small.render(f"FPS: {fps}", True, (255, 255, 255))
        fps_rect = fps_text.get_rect(topleft=(hud_x, hud_y))
        if viewport.colliderect(fps_rect):
            surface.blit(fps_text, fps_rect)
        
        # Отрисовываем здоровье
        health_y = hud_y + item_height
        self.draw_health_bar(surface, hud_x, health_y, viewport)
        
        # Отрисовываем количество монет
        coin_y = health_y + item_height
        # Используем размер 24x24 для монеты
        coin_icon = pygame.transform.scale(
            self.icons['coin'], 
            (int(24 * scale_factor), int(24 * scale_factor))
        )
        surface.blit(coin_icon, (hud_x, coin_y))
        
        coins_text = self.font_medium.render(f"x {self.player.coins}", True, (255, 255, 255))
        coins_rect = coins_text.get_rect(topleft=(hud_x + int(30 * scale_factor), coin_y))
        if viewport.colliderect(coins_rect):
            surface.blit(coins_text, coins_rect)
        
        # Отрисовываем статус крюка
        hook_y = coin_y + item_height
        hook_status = self.player.hook_state or "Ready"
        hook_text = self.font_medium.render(f"Hook: {hook_status}", True, (255, 255, 255))
        hook_rect = hook_text.get_rect(topleft=(hud_x, hook_y))
        if viewport.colliderect(hook_rect):
            surface.blit(hook_text, hook_rect)
        
        # Отрисовываем статус дэша
        dash_y = hook_y + item_height
        dash_text = f"Dash: {'Ready' if self.player.dash_timer <= 0 else f'{self.player.dash_timer:.1f}s'}"
        dash_text_surface = self.font_medium.render(dash_text, True, (255, 255, 255))
        dash_rect = dash_text_surface.get_rect(topleft=(hud_x, dash_y))
        if viewport.colliderect(dash_rect):
            surface.blit(dash_text_surface, dash_rect)
        
        # Отрисовываем счет
        score_y = dash_y + item_height
        score_text = self.font_large.render(f"Score: {score}", True, (255, 255, 0))
        score_rect = score_text.get_rect(topleft=(hud_x, score_y))
        if viewport.colliderect(score_rect):
            surface.blit(score_text, score_rect)
    
    def draw_health_bar(self, surface, x, y, viewport):
        """Отрисовывает полосу здоровья"""
        # Определяем размеры и цвета
        bar_width = int(200 * scale_factor)
        bar_height = int(20 * scale_factor)
        border_width = int(2 * scale_factor)
        health_percent = self.player.health / self.player.max_health
        
        # Определяем цвет здоровья
        if health_percent > 0.6:
            health_color = (0, 255, 0)  # Зеленый для высокого здоровья
        elif health_percent > 0.3:
            health_color = (255, 255, 0)  # Желтый для среднего здоровья
        else:
            health_color = (255, 0, 0)  # Красный для низкого здоровья
        
        # Отрисовываем фон полосы здоровья
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(surface, (50, 50, 50), bg_rect, border_radius=int(5 * scale_factor))
        
        # Отрисовываем заполненную часть полосы здоровья
        health_width = int(health_percent * bar_width)
        health_rect = pygame.Rect(x, y, health_width, bar_height)
        pygame.draw.rect(surface, health_color, health_rect, border_radius=int(5 * scale_factor))
        
        # Отрисовываем рамку полосы здоровья
        pygame.draw.rect(
            surface, 
            (255, 255, 255), 
            bg_rect, 
            width=border_width,
            border_radius=int(5 * scale_factor)
        )
        
        # Отрисовываем текст со значением здоровья
        health_text = self.font_medium.render(
            f"Health: {self.player.health}/{self.player.max_health}", 
            True, 
            (255, 255, 255)
        )
        health_text_rect = health_text.get_rect(
            center=(x + bar_width / 2, y + bar_height / 2)
        )
        if viewport.colliderect(health_text_rect):
            surface.blit(health_text, health_text_rect)

# Инициализация элементов интерфейса
button_width = 300
button_height = 80
button_spacing = 20

# Инициализация кнопок для главного меню (увеличенные размеры)
main_menu_buttons = [
    Button(
        text="Играть",
        pos=(viewport.centerx, viewport.centery - 50 * scale_factor),
        font=font,
        normal_color=(255, 255, 255),
        hover_color=(0, 255, 100),
        size=(300 * scale_factor, 80 * scale_factor)  # Увеличили размер с 200x60 до 300x80
    ),
    Button(
        text="Настройки",
        pos=(viewport.centerx, viewport.centery + 30 * scale_factor),
        font=font,
        normal_color=(255, 255, 255),
        hover_color=(0, 255, 100),
        size=(300 * scale_factor, 80 * scale_factor)  # Увеличили размер с 200x60 до 300x80
    ),
    Button(
        text="Выход",
        pos=(viewport.centerx, viewport.centery + 110 * scale_factor),
        font=font,
        normal_color=(255, 255, 255),
        hover_color=(0, 255, 100),
        size=(300 * scale_factor, 80 * scale_factor)  # Увеличили размер с 200x60 до 300x80
    )
]

# Элементы меню настроек
volume_slider = Slider(
    "Громкость", 
    BASE_WIDTH // 2 + 100, 
    BASE_HEIGHT // 2 - 80, 
    300, 
    20, 
    0, 
    100, 
    50
)
back_button = Button(
    "Назад", 
    BASE_WIDTH // 2 - button_width // 2, 
    BASE_HEIGHT // 2 + 80, 
    button_width, 
    button_height
)
settings_menu_elements = [volume_slider, back_button]

# Кнопки меню паузы
pause_button_y = BASE_HEIGHT // 2 - button_height * 1.5
continue_button = Button(
    "Продолжить", 
    BASE_WIDTH // 2 - button_width // 2, 
    pause_button_y, 
    button_width, 
    button_height
)
settings_pause_button = Button(
    "Настройки", 
    BASE_WIDTH // 2 - button_width // 2, 
    pause_button_y + button_height + button_spacing, 
    button_width, 
    button_height
)
main_menu_pause_button = Button(
    "Главное меню", 
    BASE_WIDTH // 2 - button_width // 2, 
    pause_button_y + (button_height + button_spacing) * 2, 
    button_width, 
    button_height
)
pause_buttons = [continue_button, settings_pause_button, main_menu_pause_button] 