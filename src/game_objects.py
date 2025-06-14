import pygame
import math
import os
from pygame import Vector2

class GameObject:
    """Базовый класс для всех игровых объектов"""
    def __init__(self, x, y, width, height):
        self.pos = Vector2(x, y)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True
        self.image = None
        self.frames = []
        self.frame_index = 0
        self.animation_speed = 0.1  # Время в секундах между кадрами
        self.animation_time = 0
        
    def update(self, dt):
        """Обновляет состояние объекта"""
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        
        # Обновление анимации, если есть кадры
        if self.frames and len(self.frames) > 1:
            self.animation_time += dt
            if self.animation_time >= self.animation_speed:
                # Переходим к следующему кадру
                frames_to_advance = int(self.animation_time / self.animation_speed)
                self.frame_index = (self.frame_index + frames_to_advance) % len(self.frames)
                self.animation_time = self.animation_time % self.animation_speed
                self.image = self.frames[self.frame_index]
    
    def draw(self, surface, camera, scale_factor, offset, viewport):
        """Отрисовывает объект на экране"""
        if not self.active or not self.image:
            return
            
        # Вычисляем позицию объекта с учетом камеры
        screen_x = int(self.pos.x * scale_factor + offset.x - camera.x * scale_factor)
        screen_y = int(self.pos.y * scale_factor + offset.y - camera.y * scale_factor)
        
        # Создаем прямоугольник для проверки видимости
        rect = pygame.Rect(
            screen_x,
            screen_y,
            int(self.width * scale_factor),
            int(self.height * scale_factor)
        )
        
        # Отрисовываем объект только если он виден на экране
        if rect.colliderect(viewport):
            # Масштабируем изображение
            if scale_factor != 1.0:
                scaled_image = pygame.transform.scale(
                    self.image, 
                    (int(self.width * scale_factor), int(self.height * scale_factor))
                )
            else:
                scaled_image = self.image
                
            # Отрисовываем объект
            surface.blit(scaled_image, (screen_x, screen_y))
    
    def collides_with(self, player_rect):
        """Проверяет, сталкивается ли объект с игроком"""
        return self.active and self.rect.colliderect(player_rect)


class Coin(GameObject):
    """Игровой объект монета, который можно собирать"""
    def __init__(self, x, y):
        super().__init__(x, y, 24, 24)
        self.load_frames()
        self.value = 1
        self.animation_speed = 0.15  # Скорость анимации монеты
        
    def load_frames(self):
        """Загружает кадры анимации монеты"""
        try:
            spritesheet_path = 'src/Assets/AnimatedObjects/Money.png'
            if os.path.exists(spritesheet_path):
                spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
                
                # Параметры для спрайтшита Money.png
                frame_width = 24
                frame_height = 24
                
                # Определяем фактическое количество кадров на основе ширины спрайтшита
                sheet_width = spritesheet.get_width()
                frames_count = sheet_width // frame_width
                
                for i in range(frames_count):
                    frame = spritesheet.subsurface((i * frame_width, 0, frame_width, frame_height))
                    self.frames.append(frame)
                
                # Устанавливаем первый кадр как текущее изображение
                if self.frames:
                    self.image = self.frames[0]
                else:
                    # Если кадры не загрузились, создаем заполнитель
                    placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    placeholder.fill((255, 215, 0))  # Золотой цвет для монеты
                    self.frames = [placeholder]
                    self.image = placeholder
            else:
                raise FileNotFoundError(f"Файл спрайт-листа монеты не найден: {spritesheet_path}")
                
        except Exception as e:
            print(f"Ошибка загрузки кадров монеты: {e}")
            # Создаем заполнитель
            placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            placeholder.fill((255, 215, 0))  # Золотой цвет для монеты
            self.frames = [placeholder for _ in range(6)]  # Money.png содержит 6 кадров
            self.image = self.frames[0]

    def collect(self):
        """Собирает монету"""
        if self.active:
            self.active = False
            return self.value
        return 0


class Chest(GameObject):
    """Игровой объект сундук, который можно открыть"""
    def __init__(self, x, y):
        super().__init__(x, y, 22, 22)
        self.load_frames()
        self.opened = False
        
    def load_frames(self):
        """Загружает кадры анимации сундука"""
        try:
            spritesheet_path = 'src/Assets/AnimatedObjects/Chest_open.png'
            if os.path.exists(spritesheet_path):
                spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
                
                # Chest_open.png содержит анимацию открытия сундука
                frame_width = 22
                frame_height = 22
                sheet_width = spritesheet.get_width()
                frames_count = sheet_width // frame_width
                
                # Загружаем все кадры анимации
                for i in range(frames_count):
                    frame = spritesheet.subsurface((i * frame_width, 0, frame_width, frame_height))
                    self.frames.append(frame)
                
                # Устанавливаем первый кадр (закрытый сундук)
                if self.frames:
                    self.image = self.frames[0]
                else:
                    raise Exception("Не удалось загрузить кадры сундука")
                
            else:
                raise FileNotFoundError(f"Файл спрайт-листа сундука не найден: {spritesheet_path}")
                
        except Exception as e:
            print(f"Ошибка загрузки спрайта сундука: {e}")
            # Создаем заполнитель
            placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            placeholder.fill((139, 69, 19))  # Коричневый цвет для сундука
            pygame.draw.rect(placeholder, (101, 67, 33), placeholder.get_rect(), 2)  # Добавляем рамку
            self.image = placeholder
            self.frames = [self.image]
    
    def open(self):
        """Открывает сундук"""
        if self.active and not self.opened:
            self.opened = True
            self.active = False  # Сундук исчезает при открытии
            return True
        return False
    
    def update(self, dt):
        """Обновляет состояние сундука"""
        # Обновляем только позицию
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)


class Fountain(GameObject):
    """Игровой объект фонтан с анимацией"""
    def __init__(self, x, y):
        super().__init__(x, y, 72, 72)
        self.load_frames()
        self.animation_speed = 0.2  # Скорость анимации фонтана (чуть медленнее)
        
    def load_frames(self):
        """Загружает кадры анимации фонтана"""
        try:
            spritesheet_path = 'src/Assets/AnimatedObjects/Fountain.png'
            if os.path.exists(spritesheet_path):
                spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
                
                # Параметры для спрайтшита Fountain.png
                frame_width = 72
                frame_height = 72
                
                # Определяем фактическое количество кадров на основе ширины спрайтшита
                sheet_width = spritesheet.get_width()
                frames_count = sheet_width // frame_width
                
                for i in range(frames_count):
                    frame = spritesheet.subsurface((i * frame_width, 0, frame_width, frame_height))
                    self.frames.append(frame)
                
                # Устанавливаем первый кадр как текущее изображение
                if self.frames:
                    self.image = self.frames[0]
                else:
                    # Если кадры не загрузились, создаем заполнитель
                    placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    placeholder.fill((0, 191, 255))  # Голубой цвет для фонтана
                    self.frames = [placeholder]
                    self.image = placeholder
            else:
                raise FileNotFoundError(f"Файл спрайт-листа фонтана не найден: {spritesheet_path}")
                
        except Exception as e:
            print(f"Ошибка загрузки кадров фонтана: {e}")
            # Создаем заполнитель
            placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            placeholder.fill((0, 191, 255))  # Голубой цвет для фонтана
            self.frames = [placeholder for _ in range(4)]  # Fountain.png содержит 4 кадра
            self.image = self.frames[0]


class Trap(GameObject):
    """Игровой объект ловушка, который наносит урон игроку"""
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32)  # Размер соответствует тайлу
        self.damage = 20  # Урон от ловушки
        self.active = True
        self.triggered = False
        self.trigger_cooldown = 1.0  # Время перезарядки ловушки в секундах
        self.trigger_timer = 0
        self.load_frames()
        
    def load_frames(self):
        """Загружает спрайт ловушки"""
        try:
            sprite_path = 'src/Assets/Traps/Trap.png'
            if os.path.exists(sprite_path):
                self.image = pygame.image.load(sprite_path).convert_alpha()
                # Масштабируем изображение до нужного размера, если необходимо
                if self.image.get_width() != self.width or self.image.get_height() != self.height:
                    self.image = pygame.transform.scale(self.image, (self.width, self.height))
            else:
                raise FileNotFoundError(f"Файл спрайта ловушки не найден: {sprite_path}")
        except Exception as e:
            print(f"Ошибка загрузки спрайта ловушки: {e}")
            # Создаем заполнитель
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.image.fill((255, 0, 0, 128))  # Полупрозрачный красный цвет
            # Добавляем шипы для визуального обозначения ловушки
            pygame.draw.polygon(self.image, (200, 0, 0), [
                (16, 0), (32, 16), (16, 32), (0, 16)
            ])
        
        self.frames = [self.image]
    
    def update(self, dt):
        """Обновляет состояние ловушки"""
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        
        # Обновляем таймер перезарядки
        if self.triggered:
            self.trigger_timer += dt
            if self.trigger_timer >= self.trigger_cooldown:
                self.triggered = False
                self.trigger_timer = 0
    
    def trigger(self, player):
        """Активирует ловушку при столкновении с игроком"""
        if self.active and not self.triggered:
            self.triggered = True
            self.trigger_timer = 0
            return self.damage
        return 0 