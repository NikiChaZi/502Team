import pygame
import os
from pygame import Vector2
from src.ui import Button
from src.utils import scale_factor, offset, viewport, font

class LevelSelectScreen:
    """Экран выбора уровня"""
    
    def __init__(self):
        self.level_buttons = []
        self.back_button = None
        self.available_levels = [1, 2, 3, 4]  # Доступные уровни
        self.level_previews = {}
        self.selected_level = None
        
        self.init_ui()
        self.load_level_previews()
    
    def init_ui(self):
        """Инициализирует UI элементы"""
        # Создаем кнопки для каждого уровня
        self.level_buttons = []
        
        # Размеры превью и кнопок
        preview_width = int(200 * scale_factor)
        preview_height = int(150 * scale_factor)
        button_width = int(220 * scale_factor)
        button_height = int(180 * scale_factor)
        
        # Расположение в сетке 2x2
        cols = 2
        rows = 2
        
        # Отступы
        margin_x = (viewport.width - (cols * button_width + (cols-1) * int(50 * scale_factor))) // 2
        margin_y = int(150 * scale_factor)
        
        for i, level_num in enumerate(self.available_levels):
            col = i % cols
            row = i // cols
            
            x = margin_x + col * (button_width + int(50 * scale_factor))
            y = margin_y + row * (button_height + int(30 * scale_factor))
            
            # Создаем кнопку уровня
            button = LevelButton(
                level_number=level_num,
                x=x,
                y=y,
                width=button_width,
                height=button_height,
                preview_width=preview_width,
                preview_height=preview_height
            )
            
            self.level_buttons.append(button)
        
        # Кнопка "Назад"
        self.back_button = Button(
            text="Назад",
            pos=(int(100 * scale_factor), viewport.height - int(80 * scale_factor)),
            font=font,
            normal_color=(255, 255, 255),
            hover_color=(255, 100, 100),
            size=(int(150 * scale_factor), int(60 * scale_factor))
        )
    
    def load_level_previews(self):
        """Загружает превью уровней"""
        for level_num in self.available_levels:
            preview_path = f'src/Levels/Preview/{level_num}lvl.jpg'
            if os.path.exists(preview_path):
                try:
                    preview_image = pygame.image.load(preview_path).convert()
                    self.level_previews[level_num] = preview_image
                    print(f"Загружено превью для уровня {level_num}")
                except Exception as e:
                    print(f"Ошибка загрузки превью для уровня {level_num}: {e}")
                    self.level_previews[level_num] = None
            else:
                print(f"Превью для уровня {level_num} не найдено: {preview_path}")
                self.level_previews[level_num] = None
    
    def handle_events(self, events, mouse_pos):
        """Обрабатывает события экрана выбора уровня"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                click_pos = Vector2(event.pos) if event.type == pygame.MOUSEBUTTONDOWN else Vector2(event.x * viewport.width, event.y * viewport.height)
                
                # Проверяем клик по кнопкам уровней
                for level_button in self.level_buttons:
                    if level_button.is_clicked(click_pos):
                        self.selected_level = level_button.level_number
                        return "start_level"
                
                # Проверяем клик по кнопке "Назад"
                if self.back_button.is_hovered(click_pos):
                    return "main_menu"
        
        # Обновляем состояние кнопок
        for level_button in self.level_buttons:
            level_button.update(mouse_pos)
        
        self.back_button.update(mouse_pos)
        
        return None
    
    def draw(self, screen):
        """Отрисовывает экран выбора уровня"""
        # Очищаем экран
        screen.fill((20, 30, 50))
        
        # Отрисовываем заголовок
        if font:
            title_font = pygame.font.Font('src/Resources/pixel_font.ttf', int(48 * scale_factor)) if os.path.exists('src/Resources/pixel_font.ttf') else pygame.font.SysFont('monospace', int(48 * scale_factor))
            title = title_font.render("Выберите уровень", True, (255, 255, 255))
            title_rect = title.get_rect(
                centerx=viewport.centerx,
                top=int(50 * scale_factor)
            )
            screen.blit(title, title_rect)
        
        # Отрисовываем кнопки уровней
        for level_button in self.level_buttons:
            level_button.draw(screen, self.level_previews.get(level_button.level_number))
        
        # Отрисовываем кнопку "Назад"
        self.back_button.draw(screen)


class LevelButton:
    """Кнопка для выбора уровня с превью"""
    
    def __init__(self, level_number, x, y, width, height, preview_width, preview_height):
        self.level_number = level_number
        self.rect = pygame.Rect(x, y, width, height)
        self.preview_rect = pygame.Rect(
            x + (width - preview_width) // 2,
            y + int(10 * scale_factor),
            preview_width,
            preview_height
        )
        
        self.hovered = False
        self.normal_color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.border_color = (255, 255, 255)
        self.hover_border_color = (0, 255, 100)
        
        # Параметры для текста
        self.text_color = (255, 255, 255)
        self.text_hover_color = (0, 255, 100)
    
    def is_clicked(self, pos):
        """Проверяет, был ли клик по кнопке"""
        return self.rect.collidepoint(pos)
    
    def update(self, mouse_pos):
        """Обновляет состояние кнопки"""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen, preview_image):
        """Отрисовывает кнопку уровня"""
        # Определяем цвета в зависимости от состояния
        bg_color = self.hover_color if self.hovered else self.normal_color
        border_color = self.hover_border_color if self.hovered else self.border_color
        text_color = self.text_hover_color if self.hovered else self.text_color
        
        # Отрисовываем фон кнопки
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=int(10 * scale_factor))
        
        # Отрисовываем рамку
        pygame.draw.rect(screen, border_color, self.rect, width=int(3 * scale_factor), border_radius=int(10 * scale_factor))
        
        # Отрисовываем превью уровня
        if preview_image:
            # Масштабируем превью под размер
            scaled_preview = pygame.transform.scale(preview_image, (self.preview_rect.width, self.preview_rect.height))
            screen.blit(scaled_preview, self.preview_rect)
            
            # Рамка вокруг превью
            pygame.draw.rect(screen, border_color, self.preview_rect, width=int(2 * scale_factor))
        else:
            # Если превью нет, рисуем заглушку
            pygame.draw.rect(screen, (50, 50, 50), self.preview_rect)
            pygame.draw.rect(screen, border_color, self.preview_rect, width=int(2 * scale_factor))
            
            # Текст "Нет превью"
            if font:
                no_preview_font = pygame.font.Font('src/Resources/pixel_font.ttf', int(16 * scale_factor)) if os.path.exists('src/Resources/pixel_font.ttf') else pygame.font.SysFont('monospace', int(16 * scale_factor))
                no_preview_text = no_preview_font.render("Нет превью", True, (150, 150, 150))
                no_preview_rect = no_preview_text.get_rect(center=self.preview_rect.center)
                screen.blit(no_preview_text, no_preview_rect)
        
        # Отрисовываем номер уровня
        if font:
            level_font = pygame.font.Font('src/Resources/pixel_font.ttf', int(24 * scale_factor)) if os.path.exists('src/Resources/pixel_font.ttf') else pygame.font.SysFont('monospace', int(24 * scale_factor))
            level_text = level_font.render(f"Уровень {self.level_number}", True, text_color)
            level_rect = level_text.get_rect(
                centerx=self.rect.centerx,
                bottom=self.rect.bottom - int(10 * scale_factor)
            )
            screen.blit(level_text, level_rect) 