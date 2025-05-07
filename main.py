import pygame
import sys
import math
import random
from pygame import Vector2
import asyncio
import platform
import os

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Animation states
STAND = "stand"
WALK = "walk"
IDLE = "idle"
DEAD = "dead"

# Sprite sheet configuration
FRAME_WIDTH = 32
FRAME_HEIGHT = 32
ROWS = {
    STAND: 0,
    WALK: 1,
    IDLE: 4,
    DEAD: 5
}
FRAMES_PER_ROW = 8

# Инициализация Pygame
pygame.init()

# Базовые размеры разрешения для масштабирования
BASE_WIDTH = 1920
BASE_HEIGHT = 1080
ASPECT_RATIO = BASE_WIDTH / BASE_HEIGHT  # 16:9

# Определение начального размера окна на основе экрана
try:
    display_info = pygame.display.get_desktop_sizes()[0]
    WIDTH, HEIGHT = display_info[0], display_info[1]
except:
    WIDTH, HEIGHT = 1280, 720  # Резервное разрешение

# Создание окна с поддержкой изменения размера
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Главное меню - Пиксельный платформер")

# Константы
TILE_SIZE = 32  # Размер тайла
GRAVITY = 0.8   # Гравитация
HOOK_RANGE = 300  # Дальность крюка
HOOK_SPEED = 20   # Скорость крюка
MIN_ROPE_LENGTH = 50  # Минимальная длина веревки
ROPE_SPEED = 5    # Скорость изменения длины веревки
SWING_SPEED = 0.02  # Скорость качания
DASH_DISTANCE = 100  # Дистанция рывка
DASH_COOLDOWN = 0.25  # Кулдаун рывка (0.25 сек)
DASH_DURATION = 0.2  # Длительность рывка (сек)

# Цвета
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)

# Функция для масштабирования фонового изображения
def scale_background(image, target_width, target_height):
    if image is None:
        return None
    try:
        scaled_image = pygame.transform.scale(image, (int(target_width), int(target_height)))
        return scaled_image
    except:
        return None

# Функция для размытия изображения
def blur_surface(surface, blur_radius=5):
    if surface is None:
        return None
    # Конвертируем поверхность в 32-битный формат
    surface = surface.convert_alpha()
    width, height = surface.get_size()
    for _ in range(blur_radius):
        surface = pygame.transform.smoothscale(surface, (width // 2, height // 2))
        surface = pygame.transform.smoothscale(surface, (width, height))
    return surface

# Загрузка фонового изображения для меню
try:
    menu_background = pygame.image.load('src/Assets/background_play1.png')
except Exception as e:
    print(f"Ошибка загрузки фона меню: {e}")
    menu_background = None

# Загрузка фонового изображения для уровней
try:
    level_background = pygame.image.load('src/Assets/level_background.png')
except Exception as e:
    print(f"Ошибка загрузки фона уровня: {e}")
    level_background = None

# Загрузка фоновой музыки
try:
    pygame.mixer.music.load('src/Resources/background_music.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Ошибка загрузки музыки: {e}")

# Функция для получения масштабированного шрифта
def get_scaled_font(scale):
    font_size = int(48 * scale)
    try:
        return pygame.font.Font('src/Resources/pixel_font.ttf', font_size)
    except:
        return pygame.font.SysFont('monospace', font_size)

# Функция для расчета области отображения
def calculate_viewport():
    global WIDTH, HEIGHT
    window_aspect = WIDTH / HEIGHT
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
    return scale_factor, offset, pygame.Rect(offset.x, offset.y, viewport_width, viewport_height)

# Инициализация масштаба и области отображения
scale_factor, offset, viewport = calculate_viewport()
font = get_scaled_font(scale_factor)
if menu_background:
    menu_background = scale_background(menu_background, viewport.width, viewport.height)
if level_background:
    level_background = scale_background(level_background, viewport.width, viewport.height)
    level_background_blurred = blur_surface(level_background, blur_radius=5)

# Класс для кнопок меню
class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.base_x, self.base_y = x, y
        self.base_width, self.base_height = width, height
        self.update_rect(scale_factor, offset)
        self.color = WHITE
        self.hover_color = GRAY
        self.current_color = self.color

    def update_rect(self, scale_factor, offset):
        self.rect = pygame.Rect(
            int(self.base_x * scale_factor + offset.x),
            int(self.base_y * scale_factor + offset.y),
            int(self.base_width * scale_factor),
            int(self.base_height * scale_factor)
        )

    def draw(self, surface):
        text_surface = font.render(self.text, True, self.current_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        if viewport.colliderect(text_rect):
            surface.blit(text_surface, text_rect)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def update(self, mouse_pos):
        if self.is_hovered(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

# Класс для ползунка громкости
class Slider:
    def __init__(self, label, x, y, width, height, min_val, max_val, initial_val):
        self.label = label
        self.base_x, self.base_y = x, y
        self.base_width, self.base_height = width, height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.update_rect(scale_factor, offset)

    def update_rect(self, scale_factor, offset):
        self.rect = pygame.Rect(
            int(self.base_x * scale_factor + offset.x),
            int(self.base_y * scale_factor + offset.y),
            int(self.base_width * scale_factor),
            int(self.base_height * scale_factor)
        )
        handle_width = int(20 * scale_factor)
        self.handle_rect = pygame.Rect(
            int(self.rect.x + (self.value / self.max_val) * self.rect.width - handle_width / 2),
            int(self.rect.y - 10 * scale_factor),
            handle_width,
            int(40 * scale_factor)
        )

    def draw(self, surface):
        label_surface = font.render(self.label, True, WHITE)
        label_rect = label_surface.get_rect(topleft=(self.rect.x - int(350 * scale_factor), self.rect.y - int(10 * scale_factor)))
        if viewport.colliderect(label_rect):
            surface.blit(label_surface, label_rect)
        pygame.draw.rect(surface, WHITE, self.rect, int(2 * scale_factor))
        pygame.draw.rect(surface, GRAY, self.handle_rect)
        text_surface = font.render(f"{int(self.value)}%", True, WHITE)
        text_rect = text_surface.get_rect(topleft=(self.rect.x + self.rect.width + int(20 * scale_factor), self.rect.y - int(10 * scale_factor)))
        if viewport.colliderect(text_rect):
            surface.blit(text_surface, text_rect)

    def update(self, mouse_pos, mouse_pressed):
        if mouse_pressed and self.rect.collidepoint(mouse_pos):
            handle_width = int(20 * scale_factor)
            self.handle_rect.x = max(self.rect.x, min(mouse_pos[0] - handle_width / 2, self.rect.x + self.rect.width - handle_width))
            if self.handle_rect.x <= self.rect.x:
                self.value = self.min_val
            elif self.handle_rect.x >= self.rect.x + self.rect.width - handle_width:
                self.value = self.max_val
            else:
                position_ratio = (self.handle_rect.x - self.rect.x) / (self.rect.width - handle_width)
                self.value = self.min_val + position_ratio * (self.max_val - self.min_val)
            try:
                pygame.mixer.music.set_volume(self.value / 100)
            except:
                pass

def get_animation_frames(spritesheet, row):
    frames = []
    try:
        for col in range(FRAMES_PER_ROW):
            frame = spritesheet.subsurface((col * FRAME_WIDTH, row * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT))
            frames.append(frame)
    except Exception as e:
        print(f"Ошибка извлечения кадров для строки {row}: {e}")
        # Добавляем пустой красный кадр в случае ошибки
        fallback_frame = pygame.Surface((FRAME_WIDTH, FRAME_HEIGHT), pygame.SRCALPHA)
        fallback_frame.fill(RED)
        frames.append(fallback_frame)
    return frames

# Класс игрока
class Player:
    def __init__(self, x, y):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.rect = pygame.Rect(x, y, 24, 32)
        self.speed = 5
        self.jump_power = -15
        self.on_ground = False
        self.hook_state = None
        self.hook_pos = None
        self.hook_vel = None
        self.hook_origin = None
        self.swing_angle = 0
        self.swing_speed = 0
        self.facing_right = True
        self.rope_length = 0
        self.dash_timer = 0
        self.dash_cooldown = DASH_COOLDOWN
        self.dash_time = 0
        self.dash_duration = DASH_DURATION
        self.dash_direction = 0
        self.health = 100
        self.last_movement_time = pygame.time.get_ticks()

        # Загрузка спрайт-листа
        SPRITESHEET_PATH = 'src/Assets/character_spritesheet.png'
        try:
            spritesheet = pygame.image.load(SPRITESHEET_PATH).convert_alpha()
            self.animations = {
                STAND: get_animation_frames(spritesheet, ROWS[STAND]),
                WALK: get_animation_frames(spritesheet, ROWS[WALK]),
                IDLE: get_animation_frames(spritesheet, ROWS[IDLE]),
                DEAD: get_animation_frames(spritesheet, ROWS[DEAD])
            }
            self.image_loaded = True
        except Exception as e:
            print(f"Ошибка загрузки спрайт-листа: {e}")
            self.image_loaded = False
            self.animations = {state: [pygame.Surface((24, 32), pygame.SRCALPHA)] for state in [STAND, WALK, IDLE, DEAD]}
            for state in self.animations:
                self.animations[state][0].fill(RED)

        self.state = STAND
        self.frame_index = 0
        self.image = self.animations[self.state][self.frame_index]
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100  # milliseconds

    def update_animation(self, dt, keys):
        now = pygame.time.get_ticks()
        moving = False

        # Movement and state logic
        if self.health <= 0:
            self.state = DEAD
        else:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.move_left()
                moving = True
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.move_right()
                moving = True
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.vel.y = -self.speed
                moving = True
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.vel.y = self.speed
                moving = True

            if self.hook_state == "attached":
                self.state = WALK  # Используем WALK для качания
            elif self.vel.y != 0 and not self.on_ground:
                self.state = WALK  # Используем WALK для прыжков
            elif moving:
                self.state = WALK
                self.last_movement_time = now
            else:
                if now - self.last_movement_time > 1000:
                    self.state = IDLE
                else:
                    self.state = STAND

        # Animation frame update
        if now - self.last_update > self.frame_rate:
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.state])
            self.last_update = now

        self.image = self.animations[self.state][self.frame_index]

    def get_current_frame(self, scale_factor):
        scaled_frame = pygame.transform.scale(self.image, (int(24 * scale_factor), int(32 * scale_factor)))
        if not self.facing_right:
            scaled_frame = pygame.transform.flip(scaled_frame, True, False)
        return scaled_frame

    def update(self, level, dt, keys):
        if self.dash_timer > 0:
            self.dash_timer -= dt
        if self.dash_time > 0:
            self.handle_dash(level, dt)
        if self.hook_state == "attached":
            self.handle_swinging(level)
        else:
            self.apply_physics(level)
            if self.hook_state in ["extending", "retracting"]:
                self.handle_hook_motion(level)
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        # Обновление анимации
        self.update_animation(dt, keys)
        # Обновление направления для поворота спрайта
        if self.hook_state != "attached" and self.vel.x != 0:
            self.facing_right = self.vel.x > 0

    def apply_physics(self, level):
        self.acc.y = GRAVITY
        self.vel += self.acc
        self.vel.x *= 0.9
        self.vel.y = min(self.vel.y, 20)
        self.pos.y += self.vel.y
        self.rect.y = int(self.pos.y)
        self.check_collision_y(level)
        self.pos.x += self.vel.x
        self.rect.x = int(self.pos.x)
        self.check_collision_x(level)

    def check_collision_x(self, level):
        for tile in level.tiles:
            if self.rect.colliderect(tile):
                if self.vel.x > 0:
                    self.rect.right = tile.left
                    self.pos.x = self.rect.x
                    self.vel.x = 0
                elif self.vel.x < 0:
                    self.rect.left = tile.right
                    self.pos.x = self.rect.x
                    self.vel.x = 0

    def check_collision_y(self, level):
        self.on_ground = False
        for tile in level.tiles:
            if self.rect.colliderect(tile):
                if self.vel.y > 0:
                    self.rect.bottom = tile.top
                    self.pos.y = self.rect.y
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = tile.bottom
                    self.pos.y = self.rect.y
                    self.vel.y = 0

    def move_left(self):
        self.vel.x = -self.speed

    def move_right(self):
        self.vel.x = self.speed

    def jump(self):
        if self.on_ground:
            self.vel.y = self.jump_power
            self.on_ground = False

    def dash(self):
        if self.dash_timer <= 0:
            self.dash_timer = self.dash_cooldown
            self.dash_time = self.dash_duration
            self.dash_direction = 1 if self.facing_right else -1

    def handle_dash(self, level, dt):
        dash_speed = DASH_DISTANCE / self.dash_duration
        self.dash_time -= dt
        if self.dash_time <= 0:
            self.dash_time = 0
            return
        move_x = self.dash_direction * dash_speed * dt
        old_pos = Vector2(self.pos)
        self.pos.x += move_x
        self.rect.x = int(self.pos.x)
        for tile in level.tiles:
            if self.rect.colliderect(tile):
                if self.dash_direction > 0:
                    self.rect.right = tile.left
                else:
                    self.rect.left = tile.right
                self.pos.x = self.rect.x
                self.dash_time = 0
                break

    def launch_hook(self, mouse_pos, scale_factor, offset, camera):
        if self.hook_state:
            return
        self.hook_state = "extending"
        self.hook_pos = Vector2(self.pos.x + 12, self.pos.y)
        self.hook_origin = Vector2(self.pos.x + 12, self.pos.y)
        adjusted_mouse_pos = Vector2(
            (mouse_pos.x - offset.x) / scale_factor + camera.x,
            (mouse_pos.y - offset.y) / scale_factor + camera.y
        )
        direction = adjusted_mouse_pos - self.hook_pos
        if direction.length() > 0:
            direction = direction.normalize()
        self.hook_vel = direction * HOOK_SPEED
        self.rope_length = 0

    def handle_hook_motion(self, level):
        if self.hook_state == "extending":
            old_hook_pos = Vector2(self.hook_pos)
            self.hook_pos += self.hook_vel
            distance = (self.hook_pos - self.hook_origin).length()
            if distance > HOOK_RANGE:
                self.hook_state = "retracting"
                self.set_retract_velocity()
                return
            hits = []
            for tile in level.tiles:
                tile_rect = pygame.Rect(tile.x, tile.y, tile.width, tile.height)
                dx = self.hook_pos.x - old_hook_pos.x
                dy = self.hook_pos.y - old_hook_pos.y
                hit = False
                hit_pos = Vector2(self.hook_pos)
                hit_side = None
                hit_t = float('inf')
                if dx != 0 or dy != 0:
                    # Проверка верхней грани
                    if dy != 0 and old_hook_pos.y >= tile_rect.top >= self.hook_pos.y:
                        t = (tile_rect.top - old_hook_pos.y) / dy
                        if 0 <= t <= 1:
                            x = old_hook_pos.x + t * dx
                            if tile_rect.left <= x <= tile_rect.right:
                                hit = True
                                hit_pos = Vector2(x, tile_rect.top)
                                hit_side = 'top'
                                hit_t = t
                    # Проверка нижней грани
                    elif dy != 0 and old_hook_pos.y <= tile_rect.bottom <= self.hook_pos.y:
                        t = (tile_rect.bottom - old_hook_pos.y) / dy
                        if 0 <= t <= 1:
                            x = old_hook_pos.x + t * dx
                            if tile_rect.left <= x <= tile_rect.right:
                                hit = True
                                hit_pos = Vector2(x, tile_rect.bottom)
                                hit_side = 'bottom'
                                hit_t = t
                    # Проверка правой грани
                    if dx != 0 and old_hook_pos.x <= tile_rect.left <= self.hook_pos.x:
                        t = (tile_rect.left - old_hook_pos.x) / dx
                        if 0 <= t <= 1:
                            y = old_hook_pos.y + t * dy
                            if tile_rect.top <= y <= tile_rect.bottom:
                                hit = True
                                hit_pos = Vector2(tile_rect.left, y)
                                hit_side = 'left'
                                hit_t = t
                    # Проверка левой грани
                    elif dx != 0 and self.hook_pos.x <= tile_rect.right <= old_hook_pos.x:
                        t = (tile_rect.right - old_hook_pos.x) / dx
                        if 0 <= t <= 1:
                            y = old_hook_pos.y + t * dy
                            if tile_rect.top <= y <= tile_rect.bottom:
                                hit = True
                                hit_pos = Vector2(tile_rect.right, y)
                                hit_side = 'right'
                                hit_t = t
                if hit:
                    hits.append((hit_t, hit_pos, hit_side, tile_rect))
            if hits:
                hits.sort(key=lambda x: x[0])
                for hit_t, hit_pos, hit_side, tile_rect in hits:
                    valid = False
                    offset = Vector2(0, 0)
                    if hit_side == 'top' and self.hook_vel.y < 0:
                        valid = True
                        offset = Vector2(0, 2)
                    elif hit_side == 'bottom' and self.hook_vel.y > 0:
                        valid = True
                        offset = Vector2(0, -2)
                    elif hit_side == 'left' and self.hook_vel.x > 0:
                        valid = True
                        offset = Vector2(-2, 0)
                    elif hit_side == 'right' and self.hook_vel.x < 0:
                        valid = True
                        offset = Vector2(2, 0)
                    if not valid:
                        normal = {'top': Vector2(0, -1), 'bottom': Vector2(0, 1), 'left': Vector2(-1, 0), 'right': Vector2(1, 0)}[hit_side]
                        dot_product = self.hook_vel.dot(normal)
                        if dot_product < 0:
                            valid = True
                            offset = {'top': Vector2(0, 2), 'bottom': Vector2(0, -2), 'left': Vector2(-2, 0), 'right': Vector2(2, 0)}[hit_side]
                    if valid:
                        dist_to_surface = abs({'top': hit_pos.y - tile_rect.top, 'bottom': hit_pos.y - tile_rect.bottom, 'left': hit_pos.x - tile_rect.left, 'right': hit_pos.x - tile_rect.right}[hit_side])
                        if dist_to_surface < 10:
                            self.hook_state = "attached"
                            self.hook_pos = hit_pos + offset
                            self.hook_pos.x = max(tile_rect.left, min(self.hook_pos.x, tile_rect.right))
                            self.hook_pos.y = max(tile_rect.top, min(self.hook_pos.y, tile_rect.bottom))
                            self.vel = Vector2(0, 0)
                            self.swing_angle = math.atan2(self.pos.y - self.hook_pos.y, self.pos.x - self.hook_pos.x)
                            self.swing_speed = 0
                            self.rope_length = (self.pos - self.hook_pos).length()
                            return
                self.hook_state = "retracting"
                self.set_retract_velocity()
        elif self.hook_state == "retracting":
            self.hook_pos += self.hook_vel
            distance = (self.hook_pos - Vector2(self.pos.x + 12, self.pos.y)).length()
            if distance < 10:
                self.hook_state = None
                self.hook_pos = None
                self.hook_vel = None
                self.hook_origin = None
                self.rope_length = 0
            else:
                self.set_retract_velocity()

    def set_retract_velocity(self):
        direction = Vector2(self.pos.x + 12, self.pos.y) - self.hook_pos
        if direction.length() > 0:
            direction = direction.normalize()
            self.hook_vel = direction * HOOK_SPEED

    def handle_swinging(self, level):
        keys = pygame.key.get_pressed()
        new_rope_length = self.rope_length
        if keys[pygame.K_w] and self.hook_state == "attached":
            new_rope_length -= ROPE_SPEED
        if keys[pygame.K_s] and self.hook_state == "attached":
            new_rope_length += ROPE_SPEED
        new_rope_length = max(MIN_ROPE_LENGTH, min(new_rope_length, HOOK_RANGE))
        old_pos = Vector2(self.pos)
        test_pos = Vector2(self.hook_pos.x + math.cos(self.swing_angle) * new_rope_length, self.hook_pos.y + math.sin(self.swing_angle) * new_rope_length)
        test_rect = self.rect.copy()
        test_rect.x = int(test_pos.x)
        test_rect.y = int(test_pos.y)
        collision = False
        for tile in level.tiles:
            if test_rect.colliderect(tile):
                collision = True
                break
        if not collision:
            self.rope_length = new_rope_length
            self.pos = test_pos
        else:
            self.pos = old_pos
        if keys[pygame.K_a] and self.hook_state == "attached":
            self.swing_speed += SWING_SPEED
        if keys[pygame.K_d] and self.hook_state == "attached":
            self.swing_speed -= SWING_SPEED
        self.swing_speed = max(min(self.swing_speed, 0.1), -0.1)
        self.swing_speed *= 0.9
        self.swing_angle += self.swing_speed
        self.pos.x = self.hook_pos.x + math.cos(self.swing_angle) * self.rope_length
        self.pos.y = self.hook_pos.y + math.sin(self.swing_angle) * self.rope_length
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        for tile in level.tiles:
            if self.rect.colliderect(tile):
                self.release_hook()
                break

    def release_hook(self):
        if self.hook_state == "attached":
            tangential_vel = self.swing_speed * self.rope_length
            self.vel.x = -math.sin(self.swing_angle) * tangential_vel
            self.vel.y = math.cos(self.swing_angle) * tangential_vel
        self.hook_state = None
        self.hook_pos = None
        self.hook_vel = None
        self.hook_origin = None
        self.swing_angle = 0
        self.swing_speed = 0
        self.rope_length = 0

# Класс уровня
class Level:
    def __init__(self):
        self.tiles = []
        self.width = 0
        self.height = 0
        self.load_level()

    def load_level(self):
        level_map = [
            "████████████████████████████████████████████████",
            "█                                              █",
            "█                                              █",
            "█          ████                                █",
            "█                                              █",
            "█                                              █",
            "█      ████                                    █",
            "█                                              █",
            "█                                              █",
            "█              ████                            █",
            "█                                              █",
            "█                                              █",
            "█  ████                                        █",
            "█                                              █",
            "█                                              █",
            "█                      ████                    █",
            "█                                              █",
            "█                                              █",
            "█      ████                                    █",
            "█                                              █",
            "█                                              █",
            "████████████████████████████████████████████████",
        ]
        self.height = len(level_map)
        self.width = len(level_map[0]) if level_map else 0
        for y, row in enumerate(level_map):
            for x, tile in enumerate(row):
                if tile == "█":
                    self.tiles.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def draw(self, surface, camera, scale_factor, offset, viewport):
        for tile in self.tiles:
            rect = pygame.Rect(
                int(tile.x * scale_factor + offset.x - camera.x * scale_factor),
                int(tile.y * scale_factor + offset.y - camera.y * scale_factor),
                int(TILE_SIZE * scale_factor),
                int(TILE_SIZE * scale_factor)
            )
            if rect.colliderect(viewport):
                pygame.draw.rect(surface, CYAN, rect, 1)

# Класс HUD
class HUD:
    def __init__(self, player, clock):
        self.player = player
        self.clock = clock
        self.update_font(scale_factor)

    def update_font(self, scale_factor):
        self.font = pygame.font.SysFont('monospace', int(36 * scale_factor))

    def draw(self, surface, offset, viewport):
        hud_x = int(offset.x + 10 * scale_factor)
        hud_y = int(offset.y + 10 * scale_factor)
        hook_status = "Hook: " + (self.player.hook_state or "Ready")
        text = self.font.render(hook_status, True, WHITE)
        text_rect = text.get_rect(topleft=(hud_x, hud_y))
        if viewport.colliderect(text_rect):
            surface.blit(text, text_rect)
        fps = str(int(self.clock.get_fps()))
        fps_text = self.font.render(f"FPS: {fps}", True, WHITE)
        fps_rect = fps_text.get_rect(topleft=(hud_x, hud_y + int(40 * scale_factor)))
        if viewport.colliderect(fps_rect):
            surface.blit(fps_text, fps_rect)
        rope_length_text = f"Rope Length: {int(self.player.rope_length)}"
        rope_text = self.font.render(rope_length_text, True, WHITE)
        rope_rect = rope_text.get_rect(topleft=(hud_x, hud_y + int(80 * scale_factor)))
        if viewport.colliderect(rope_rect):
            surface.blit(rope_text, rope_rect)
        dash_text = f"Dash: {'Ready' if self.player.dash_timer <= 0 else f'{self.player.dash_timer:.1f}s'}"
        dash_text_surface = self.font.render(dash_text, True, WHITE)
        dash_rect = dash_text_surface.get_rect(topleft=(hud_x, hud_y + int(120 * scale_factor)))
        if viewport.colliderect(dash_rect):
            surface.blit(dash_text_surface, dash_rect)
        health_text = f"Health: {self.player.health}"
        health_surface = self.font.render(health_text, True, WHITE)
        health_rect = health_surface.get_rect(topleft=(hud_x, hud_y + int(160 * scale_factor)))
        if viewport.colliderect(health_rect):
            surface.blit(health_surface, health_rect)

# Класс игры
class Game:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.player = Player(100, 600)
        self.level = Level()
        self.camera = Vector2(0, 0)
        self.hud = HUD(self.player, self.clock)
        self.running = True
        self.dt = 1 / FPS

    def reset(self):
        """Сброс состояния игры для новой сессии."""
        self.player = Player(100, 600)
        self.level = Level()
        self.camera = Vector2(0, 0)
        self.hud = HUD(self.player, self.clock)
        self.running = True
        self.dt = 1 / FPS

    async def run(self, current_menu):
        while self.running and current_menu[0] in ["game", "pause", "settings"]:
            if current_menu[0] == "game":
                self.handle_events(current_menu)
                self.update()
                self.draw()
            elif current_menu[0] == "pause":
                self.handle_pause_events(current_menu)
                self.draw_pause()
            elif current_menu[0] == "settings":
                self.handle_settings_events(current_menu)
                self.draw_settings()
            self.clock.tick(FPS)
            pygame.display.flip()
            await asyncio.sleep(1.0 / FPS)
        if not self.running:
            current_menu[0] = "main"
            current_menu[1] = None
        self.reset()

    def handle_events(self, current_menu):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_menu[0] = "pause"
                    current_menu[1] = "game"
                elif event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_r:
                    self.player.release_hook()
                elif event.key == pygame.K_LSHIFT:
                    self.player.dash()
                elif event.key == pygame.K_h:
                    self.player.health -= 1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = Vector2(event.pos)
                    self.player.launch_hook(mouse_pos, scale_factor, offset, self.camera)
            elif event.type == pygame.FINGERDOWN:
                mouse_pos = Vector2(event.x * WIDTH, event.y * HEIGHT)
                self.player.launch_hook(mouse_pos, scale_factor, offset, self.camera)
        keys = pygame.key.get_pressed()
        if self.player.hook_state != "attached" and self.player.dash_time <= 0:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player.move_left()
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player.move_right()

    def handle_pause_events(self, current_menu):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_menu[0] = "game"
                    current_menu[1] = None
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                mouse_pos = Vector2(event.pos) if event.type == pygame.MOUSEBUTTONDOWN else Vector2(event.x * WIDTH, event.y * HEIGHT)
                for button in pause_buttons:
                    if button.is_hovered(mouse_pos):
                        if button.text == "Продолжить":
                            current_menu[0] = "game"
                            current_menu[1] = None
                        elif button.text == "Настройки":
                            current_menu[0] = "settings"
                            current_menu[1] = "pause"
                        elif button.text == "Главное меню":
                            self.running = False

    def handle_settings_events(self, current_menu):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                mouse_pos = Vector2(event.pos) if event.type == pygame.MOUSEBUTTONDOWN else Vector2(event.x * WIDTH, event.y * HEIGHT)
                for element in settings_menu_elements:
                    if isinstance(element, Button) and element.is_hovered(mouse_pos):
                        if element.text == "Назад":
                            if current_menu[1] == "pause":
                                current_menu[0] = "pause"
                                current_menu[1] = "game"
                            else:
                                current_menu[0] = "main"
                                current_menu[1] = None
        # Обновление состояния элементов меню настроек
        for element in settings_menu_elements:
            if isinstance(element, Slider):
                element.update(mouse_pos, mouse_pressed)
            elif isinstance(element, Button):
                element.update(mouse_pos)

    def update(self):
        self.player.update(self.level, self.dt, pygame.key.get_pressed())
        level_width = self.level.width * TILE_SIZE
        level_height = self.level.height * TILE_SIZE
        half_viewport_width = BASE_WIDTH / 2
        half_viewport_height = BASE_HEIGHT / 2
        self.camera.x = self.player.pos.x - half_viewport_width
        self.camera.y = self.player.pos.y - half_viewport_height
        self.camera.x = max(0, min(self.camera.x, level_width - BASE_WIDTH))
        self.camera.y = max(0, min(self.camera.y, level_height - BASE_HEIGHT))
        if level_width < BASE_WIDTH:
            self.camera.x = (level_width - BASE_WIDTH) / 2
        if level_height < BASE_HEIGHT:
            self.camera.y = (level_height - BASE_HEIGHT) / 2
        self.dt = self.clock.get_time() / 1000.0

    def draw(self):
        self.screen.fill(BLACK)
        if level_background:
            self.screen.blit(level_background, (int(offset.x), int(offset.y)))
        self.level.draw(self.screen, self.camera, scale_factor, offset, viewport)
        player_rect = pygame.Rect(
            int(self.player.rect.x * scale_factor + offset.x - self.camera.x * scale_factor),
            int(self.player.rect.y * scale_factor + offset.y - self.camera.y * scale_factor),
            int(self.player.rect.width * scale_factor),
            int(self.player.rect.height * scale_factor)
        )
        if viewport.colliderect(player_rect):
            frame = self.player.get_current_frame(scale_factor)
            self.screen.blit(frame, player_rect.topleft)
        if self.player.hook_state:
            hook_pos = Vector2(
                int(self.player.hook_pos.x * scale_factor + offset.x - self.camera.x * scale_factor),
                int(self.player.hook_pos.y * scale_factor + offset.y - self.camera.y * scale_factor)
            )
            player_center = Vector2(int(player_rect.centerx), int(player_rect.centery))
            if viewport.collidepoint(hook_pos):
                pygame.draw.line(self.screen, WHITE, player_center, hook_pos, int(2 * scale_factor))
                pygame.draw.circle(self.screen, WHITE, (int(hook_pos.x), int(hook_pos.y)), int(5 * scale_factor))
        self.hud.draw(self.screen, offset, viewport)

    def draw_pause(self):
        if level_background_blurred:
            self.screen.blit(level_background_blurred, (int(offset.x), int(offset.y)))
        else:
            self.screen.fill((0, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
        for button in pause_buttons:
            button.draw(self.screen)

    def draw_settings(self):
        if level_background_blurred:
            self.screen.blit(level_background_blurred, (int(offset.x), int(offset.y)))
        else:
            self.screen.fill((0, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
        for element in settings_menu_elements:
            element.draw(self.screen)

# Функция для обновления элементов интерфейса
def update_ui_elements():
    for button in main_menu_buttons:
        button.update_rect(scale_factor, offset)
    for element in settings_menu_elements:
        button.update_rect(scale_factor, offset)
    for button in pause_buttons:
        button.update_rect(scale_factor, offset)
    game.hud.update_font(scale_factor)

# Функция для обработки изменения размера окна
def handle_resize(new_width, new_height):
    global WIDTH, HEIGHT, screen, menu_background, level_background, level_background_blurred, font, scale_factor, offset, viewport
    WIDTH, HEIGHT = new_width, new_height
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    scale_factor, offset, viewport = calculate_viewport()
    try:
        if menu_background:
            menu_background = scale_background(pygame.image.load('src/Assets/background_play1.png'), viewport.width, viewport.height)
        if level_background:
            level_background = scale_background(pygame.image.load('src/Assets/level_background.png'), viewport.width, viewport.height)
            level_background_blurred = blur_surface(level_background, blur_radius=5)
    except Exception as e:
        print(f"Ошибка обновления фона: {e}")
    font = get_scaled_font(scale_factor)
    update_ui_elements()

# Создание кнопок главного меню
button_width = 300
button_height = 80
button_spacing = 20
play_button = Button("Играть", BASE_WIDTH // 2 - button_width // 2, BASE_HEIGHT // 2 - button_height - button_spacing, button_width, button_height)
settings_button = Button("Настройки", BASE_WIDTH // 2 - button_width // 2, BASE_HEIGHT // 2, button_width, button_height)
exit_button = Button("Выход", BASE_WIDTH // 2 - button_width // 2, BASE_HEIGHT // 2 + button_height + button_spacing, button_width, button_height)
main_menu_buttons = [play_button, settings_button, exit_button]

# Создание элементов меню настроек
volume_slider = Slider("Громкость", BASE_WIDTH // 2 + 0, BASE_HEIGHT // 2 - 80, 300, 20, 0, 100, 50)
back_button = Button("Назад", BASE_WIDTH // 2 - button_width // 2, BASE_HEIGHT // 2 + 80, button_width, button_height)
settings_menu_elements = [volume_slider, back_button]

# Создание кнопок меню паузы
pause_button_y = BASE_HEIGHT // 2 - button_height * 1.5
continue_button = Button("Продолжить", BASE_WIDTH // 2 - button_width // 2, pause_button_y, button_width, button_height)
settings_pause_button = Button("Настройки", BASE_WIDTH // 2 - button_width // 2, pause_button_y + button_height + button_spacing, button_width, button_height)
main_menu_pause_button = Button("Главное меню", BASE_WIDTH // 2 - button_width // 2, pause_button_y + (button_height + button_spacing) * 2, button_width, button_height)
pause_buttons = [continue_button, settings_pause_button, main_menu_pause_button]

# Инициализация игры
game = Game()

# Основной игровой цикл
async def main():
    global current_menu
    current_menu = ["main", None]  # Инициализация с двумя элементами: текущее состояние, предыдущее состояние
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        # Обработка событий
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event.w, event.h)

        if current_menu[0] == "main":
            # Обработка событий для главного меню
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                    mouse_pos = Vector2(event.pos) if event.type == pygame.MOUSEBUTTONDOWN else Vector2(event.x * WIDTH, event.y * HEIGHT)
                    for button in main_menu_buttons:
                        if button.is_hovered(mouse_pos):
                            if button.text == "Играть":
                                game.reset()
                                current_menu = ["game", "main"]
                                await game.run(current_menu)
                            elif button.text == "Настройки":
                                current_menu = ["settings", "main"]
                            elif button.text == "Выход":
                                running = False
            # Обновление состояния кнопок
            for button in main_menu_buttons:
                button.update(mouse_pos)
            # Отрисовка главного меню
            screen.fill(BLACK)
            if menu_background:
                screen.blit(menu_background, (int(offset.x), int(offset.y)))
            for button in main_menu_buttons:
                button.draw(screen)

        elif current_menu[0] == "settings":
            # Обработка событий для меню настроек
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                    mouse_pos = Vector2(event.pos) if event.type == pygame.MOUSEBUTTONDOWN else Vector2(event.x * WIDTH, event.y * HEIGHT)
                    for button in main_menu_buttons:
                        button.update(mouse_pos)
                    for element in settings_menu_elements:
                        if isinstance(element, Button) and element.is_hovered(mouse_pos):
                            if element.text == "Назад":
                                if current_menu[1] == "pause":
                                    current_menu = ["pause", "game"]
                                else:
                                    current_menu = ["main", None]
            # Обновление состояния элементов
            for element in settings_menu_elements:
                if isinstance(element, Slider):
                    element.update(mouse_pos, mouse_pressed)
                elif isinstance(element, Button):
                    element.update(mouse_pos)
            # Отрисовка меню настроек
            screen.fill(BLACK)
            if menu_background and (current_menu[1] is None or current_menu[1] != "pause"):
                screen.blit(menu_background, (int(offset.x), int(offset.y)))
            elif level_background_blurred and current_menu[1] == "pause":
                screen.blit(level_background_blurred, (int(offset.x), int(offset.y)))
            for element in settings_menu_elements:
                element.draw(screen)

        elif current_menu[0] in ["game", "pause", "settings"]:
            # Обработка игры и паузы выполняется в game.run()
            pass

        pygame.display.flip()
        await asyncio.sleep(1.0 / FPS)

    pygame.quit()
    sys.exit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())