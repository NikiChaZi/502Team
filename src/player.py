import pygame
import math
import os
from pygame import Vector2

# Константы
GRAVITY = 0.8
JUMP_POWER = -18  # Улучшенный прыжок
SPEED = 5
DASH_DISTANCE = 150  # Увеличено со 100 для более быстрого рывка
DASH_COOLDOWN = 0.5
DASH_DURATION = 0.2
COLLISION_THRESHOLD = 5
HOOK_RANGE = 400  # Увеличенная дальность крюка
HOOK_SPEED = 25   # Увеличенная скорость крюка
MIN_ROPE_LENGTH = 50
ROPE_SPEED = 5
SWING_SPEED = 0.03  # Улучшенное значение для более плавного качания
HOOK_PULL_STRENGTH = 0.8  # Увеличенная сила притяжения к крюку

# Размеры спрайтов персонажа
CHARACTER_WIDTH = 32  # Базовая ширина персонажа
CHARACTER_HEIGHT = 32  # Базовая высота персонажа

# Количество кадров в разных анимациях для персонажей
FRAMES_COUNT = {
    "idle": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    },
    "run": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    },
    "walk": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    },
    "jump": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    },
    "fall": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    },
    "double_jump": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    },
    "attack_1": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    },
    "dash": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    },
    "dead": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    },
    "attack_2": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    },
    "attack_3": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    },
    "hurt": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    },
    "shield": {
        "SimpleChar": 8  # 8 кадров анимации из спрайт-листа
    }
}

# Доступные персонажи
CHARACTERS = ["SimpleChar"]

class Player:
    def __init__(self, x, y, character_type="SimpleChar"):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.rect = pygame.Rect(x, y, CHARACTER_WIDTH, CHARACTER_HEIGHT)
        self.speed = SPEED
        self.jump_power = JUMP_POWER
        self.on_ground = False
        self.jump_count = 2  # Счетчик прыжков (0 - на земле, 1 - первый прыжок, 2 - двойной прыжок)
        self.max_jumps = 2   # Максимальное количество прыжков
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
        self.max_health = 100
        self.coins = 0
        self.last_movement_time = pygame.time.get_ticks()
        
        # Эффекты
        self.effects = []
        
        # Устанавливаем тип персонажа
        if character_type in CHARACTERS:
            self.character_type = character_type
        else:
            self.character_type = "SimpleChar"  # По умолчанию
            
        # Установка особых способностей в зависимости от типа персонажа
        self.max_jumps = 2  # Двойной прыжок для всех персонажей
        
        # Загрузка спрайтов персонажа
        self.load_animations()
        
        # Установка начального состояния и кадра
        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.2
        self.animation_time = 0
        
    def load_animations(self):
        """Загружает все анимации персонажа"""
        self.animations = {
            "idle": [],
            "run": [],
            "walk": [],
            "jump": [],
            "fall": [],
            "dash": [],
            "dead": [],
            "attack_1": [],
            "attack_2": [],
            "attack_3": [],
            "hurt": [],
            "shield": [],
            "double_jump": []  # Добавляем анимацию двойного прыжка
        }
        
        # Загружаем спрайты для выбранного персонажа
        try:
            # Специальная обработка для SimpleChar - используем спрайт-лист из temp_card
            if self.character_type == "SimpleChar":
                card_sprite_path = 'temp_card/Card.png'
                if os.path.exists(card_sprite_path):
                    print(f"Загружаем спрайт-лист из temp_card: {card_sprite_path}")
                    # Загружаем спрайт-лист карты
                    card_sprite_sheet = pygame.image.load(card_sprite_path).convert_alpha()
                    
                    # Размеры спрайт-листа (192x24), каждый кадр 24x24
                    sheet_width = card_sprite_sheet.get_width()
                    sheet_height = card_sprite_sheet.get_height()
                    frame_width = 24  # Ширина одного кадра
                    frame_height = 24  # Высота одного кадра
                    frames_count = sheet_width // frame_width  # Количество кадров (8)
                    
                    # Извлекаем кадры из спрайт-листа
                    frames = []
                    for i in range(frames_count):
                        # Вырезаем кадр из спрайт-листа
                        frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                        frame = card_sprite_sheet.subsurface(frame_rect).copy()
                        # Масштабируем кадр до размера персонажа
                        scaled_frame = pygame.transform.scale(frame, (CHARACTER_WIDTH, CHARACTER_HEIGHT))
                        frames.append(scaled_frame)
                    
                    # Заполняем все анимации кадрами из спрайт-листа
                    for animation_name in self.animations:
                        self.animations[animation_name] = frames.copy()
                    
                    self.image_loaded = True
                    return
                else:
                    print(f"Спрайт-лист карты не найден: {card_sprite_path}, используем стандартную загрузку")
                    
            character_dir = f'src/Assets/Characters/{self.character_type}'
            if not os.path.exists(character_dir):
                print(f"Директория с персонажем не найдена: {character_dir}, проверяем альтернативные пути")
                # Проверяем разные возможные пути к персонажам
                possible_dirs = [
                    f'src/Assets/1 Main Characters/{self.character_type}',
                    f'src/Assets/Characters/{self.character_type}',
                    f'src/Assets/{self.character_type}',
                    'src/Assets/Characters/SimpleChar',
                    'src/Assets/1 Main Characters/SimpleChar'
                ]
                
                character_dir = None
                for possible_dir in possible_dirs:
                    if os.path.exists(possible_dir):
                        character_dir = possible_dir
                        print(f"Найдена директория персонажа: {character_dir}")
                        break
                
                if character_dir is None:
                    print("Не найдена ни одна директория с персонажами, используем SimpleChar")
                character_dir = 'src/Assets/Characters/SimpleChar'
                self.character_type = "SimpleChar"
            
            # Загружаем каждый тип анимации
            for animation_name in self.animations:
                sprite_file = os.path.join(character_dir, f"{animation_name.capitalize()}.png")
                
                # Особая обработка для двойного прыжка
                if animation_name == "double_jump":
                    double_jump_file = os.path.join(character_dir, "Double_Jump.png")
                    if os.path.exists(double_jump_file):
                        self.load_animation("double_jump", double_jump_file)
                    else:
                        # Если нет специальной анимации, используем обычный прыжок
                        jump_file = os.path.join(character_dir, "Jump.png")
                        if os.path.exists(jump_file):
                            self.load_animation("double_jump", jump_file)
                # Некоторые анимации могут иметь другое название файла
                elif animation_name == "fall" and not os.path.exists(sprite_file):
                    # Для падения используем кадр прыжка или Fall.png
                    fall_file = os.path.join(character_dir, "Fall.png")
                    if os.path.exists(fall_file):
                        self.load_animation("fall", fall_file)
                    else:
                        jump_file = os.path.join(character_dir, "Jump.png")
                        if os.path.exists(jump_file):
                            self.load_animation("fall", jump_file, 1, 1)  # Берем только первый кадр
                elif animation_name == "dash" and not os.path.exists(sprite_file):
                    # Для даша используем бег
                    run_file = os.path.join(character_dir, "Run.png")
                    if os.path.exists(run_file):
                        self.load_animation("dash", run_file)
                elif os.path.exists(sprite_file):
                    self.load_animation(animation_name, sprite_file)
            
            # Проверяем и заполняем недостающие анимации
            if not self.animations["fall"]:
                if self.animations["jump"]:
                    self.animations["fall"] = [self.animations["jump"][-1]]
                else:
                    self.animations["fall"] = self.animations["idle"][:1]
                    
            if not self.animations["dash"]:
                self.animations["dash"] = self.animations["run"]
                
            if not self.animations["double_jump"] and self.animations["jump"]:
                self.animations["double_jump"] = self.animations["jump"]
            
            self.image_loaded = True
        except Exception as e:
            print(f"Ошибка загрузки спрайтов персонажа: {e}")
            self.image_loaded = False
            
            # Создаем заполнители вместо спрайтов
            for state in self.animations:
                placeholder = pygame.Surface((CHARACTER_WIDTH, CHARACTER_HEIGHT), pygame.SRCALPHA)
                placeholder.fill((255, 0, 255))
                self.animations[state] = [placeholder for _ in range(4)]
    
    def load_animation(self, animation_name, spritesheet_path, start_frame=0, num_frames=None):
        """Загружает конкретную анимацию из спрайтшита или одиночного изображения"""
        if not os.path.exists(spritesheet_path):
            print(f"Файл спрайта не найден: {spritesheet_path}")
            return
            
        try:
            # Загружаем изображение
            sprite_image = pygame.image.load(spritesheet_path).convert_alpha()
            
            # Получаем количество кадров из конфигурации для конкретного персонажа
            frames_count = 1  # По умолчанию для единичного изображения
            
            # Проверяем, есть ли в конфигурации FRAMES_COUNT информация о количестве кадров
            if animation_name in FRAMES_COUNT and self.character_type in FRAMES_COUNT[animation_name]:
                frames_count = FRAMES_COUNT[animation_name][self.character_type]
            
            # Если явно указано количество кадров, используем его
            if num_frames is not None:
                frames_count = num_frames
            
            # Если количество кадров больше 1, обрабатываем как спрайтшит
            if frames_count > 1:
                # Вычисляем размер кадра
                sheet_width = sprite_image.get_width()
                sheet_height = sprite_image.get_height()
                frame_width = sheet_width // frames_count
                
                # Создаем список кадров
                frames = []
                for i in range(start_frame, min(start_frame + frames_count, frames_count)):
                    if i * frame_width >= sheet_width:
                        break
                        
                    # Вырезаем кадр из спрайтшита
                    frame = sprite_image.subsurface((i * frame_width, 0, frame_width, sheet_height))
                    frames.append(frame)
            else:
                # Для одиночного изображения просто используем его как кадр
                frames = [sprite_image]
                
            # Сохраняем анимацию
            self.animations[animation_name] = frames
            
        except Exception as e:
            print(f"Ошибка при загрузке анимации {animation_name}: {e}")
            # Создаем заполнитель
            placeholder = pygame.Surface((CHARACTER_WIDTH, CHARACTER_HEIGHT), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255))
            self.animations[animation_name] = [placeholder]
    
    def update_animation(self, dt, keys):
        """Обновляет анимацию в зависимости от текущего состояния"""
        now = pygame.time.get_ticks()
        moving = False

        # Movement and state logic
        if self.health <= 0:
            self.state = "dead"
        else:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                moving = True
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                moving = True

            if self.hook_state == "attached":
                self.state = "walk"  # Используем walk для качания
            elif self.vel.y != 0 and not self.on_ground:
                self.state = "walk"  # Используем walk для прыжков
            elif moving:
                self.state = "walk"
                self.last_movement_time = now
            else:
                if now - self.last_movement_time > 1000:
                    self.state = "idle"
                else:
                    self.state = "idle"

        # Animation frame update with fixed frame rate
        if not hasattr(self, 'last_update'):
            self.last_update = now
        if not hasattr(self, 'frame_rate'):
            self.frame_rate = 100  # milliseconds

        if now - self.last_update > self.frame_rate:
            if len(self.animations[self.state]) > 0:
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.state])
            self.last_update = now
    
    def get_current_frame(self, scale_factor):
        """Возвращает текущий кадр анимации с учетом направления и масштаба"""
        if not hasattr(self, 'animations') or self.state not in self.animations or not self.animations[self.state]:
            # Возвращаем пустое изображение, если анимации нет
            placeholder = pygame.Surface((int(CHARACTER_WIDTH * scale_factor), int(CHARACTER_HEIGHT * scale_factor)), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255))
            return placeholder
            
        frames = self.animations[self.state]
        frame_index = min(self.frame_index, len(frames) - 1)
        frame = frames[frame_index]
        
        # Масштабируем кадр
        scaled_width = int(frame.get_width() * scale_factor)
        scaled_height = int(frame.get_height() * scale_factor)
        scaled_frame = pygame.transform.scale(frame, (scaled_width, scaled_height))
        
        # Отражаем кадр, если персонаж смотрит влево
        if not self.facing_right:
            scaled_frame = pygame.transform.flip(scaled_frame, True, False)
            
        return scaled_frame
    
    def update(self, level, dt, keys):
        """Обновляет состояние игрока"""
        # Обработка таймера дэша
        if self.dash_timer > 0:
            self.dash_timer -= dt
            
        # Обработка состояния дэша
        if self.dash_time > 0:
            self.handle_dash(level, dt)
        # Обработка состояния крюка
        elif self.hook_state == "attached":
            self.handle_swinging(level)
        else:
            # Обычная физика движения
            self.apply_physics(level)
            
            # Обновление крюка при его перемещении
            if self.hook_state in ["extending", "retracting"]:
                self.handle_hook_motion(level)
        
        # Обновляем прямоугольник коллизии
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        
        # Обновляем анимацию
        self.update_animation(dt, keys)
        
        # Обновляем направление лица
        if self.hook_state != "attached" and abs(self.vel.x) > 0.5:
            self.facing_right = self.vel.x > 0
            
        # Обновляем эффекты
        self.update_effects(dt)
    
    def update_effects(self, dt):
        """Обновляет все активные эффекты"""
        # Обновляем время жизни каждого эффекта и удаляем истекшие
        i = 0
        while i < len(self.effects):
            self.effects[i]["time"] -= dt
            if self.effects[i]["time"] <= 0:
                self.effects.pop(i)
            else:
                i += 1
    
    def apply_physics(self, level):
        """Применяет физику к игроку"""
        # Гравитация
        self.acc = Vector2(0, GRAVITY)
        
        # Обновляем скорость
        self.vel += self.acc
        
        # Трение по X
        self.vel.x *= 0.9
        
        # Ограничиваем скорость падения
        self.vel.y = min(self.vel.y, 20)
        
        # Перемещаем по Y и проверяем коллизии
        self.pos.y += self.vel.y
        self.rect.y = int(self.pos.y)
        self.check_collision_y(level)
        
        # Перемещаем по X и проверяем коллизии
        self.pos.x += self.vel.x
        self.rect.x = int(self.pos.x)
        self.check_collision_x(level)
    
    def check_collision_x(self, level):
        """Проверяет коллизии по оси X"""
        for tile in level.collision_tiles:
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
        """Проверяет коллизии по оси Y"""
        # Сначала проверяем, находимся ли мы на земле
        self.on_ground = False
        
        for tile in level.collision_tiles:
            if self.rect.colliderect(tile):
                if self.vel.y > 0:  # Падаем
                    self.rect.bottom = tile.top
                    self.pos.y = self.rect.y
                    self.vel.y = 0
                    self.on_ground = True
                    self.jump_count = 0  # Сбрасываем счетчик прыжков при приземлении
                elif self.vel.y < 0:  # Прыгаем
                    self.rect.top = tile.bottom
                    self.pos.y = self.rect.y
                    self.vel.y = 0
                    
        # Дополнительная проверка на земле ли мы (проверяем пиксель под ногами)
        if not self.on_ground:
            # Создаем тестовый прямоугольник чуть ниже персонажа
            test_rect = pygame.Rect(self.rect.x + 2, self.rect.bottom, self.rect.width - 4, 2)
            for tile in level.collision_tiles:
                if test_rect.colliderect(tile):
                    self.on_ground = True
                    break
    
    def move_left(self):
        """Перемещает игрока влево"""
        self.vel.x = -self.speed
        self.facing_right = False
    
    def move_right(self):
        """Перемещает игрока вправо"""
        self.vel.x = self.speed
        self.facing_right = True
    
    def jump(self):
        """Заставляет игрока прыгать"""
        # Первый прыжок можно делать только на земле
        if self.on_ground:
            self.vel.y = self.jump_power
            self.on_ground = False
            self.jump_count = 1
            return True
        # Двойной прыжок только если разрешено
        elif self.jump_count < self.max_jumps:
            # Стандартная сила прыжка
            self.vel.y = self.jump_power * 0.9  # Немного слабее для второго прыжка
            
            self.jump_count = 2
            
            # Добавляем эффект двойного прыжка
            self.add_double_jump_effect()
            
            # Меняем состояние на double_jump, если есть такая анимация
            if self.animations["double_jump"]:
                self.state = "double_jump"
                self.frame_index = 0
                self.animation_time = 0
            
            return True
        return False
    
    def add_double_jump_effect(self):
        """Добавляет визуальный эффект двойного прыжка"""
        # Центр игрока
        center_x = self.pos.x + self.rect.width / 2
        center_y = self.pos.y + self.rect.height / 2
        
        # Цвет эффекта для SimpleChar
        color = (0, 255, 0)  # Зеленый для простого персонажа
            
        # Добавляем эффект в список активных эффектов
        self.effects.append({
            "type": "double_jump",
            "pos": Vector2(center_x, center_y),
            "time": 0.5,  # Время жизни эффекта в секундах
            "radius": 30,  # Начальный радиус
            "max_radius": 60,  # Максимальный радиус
            "color": color
        })
    
    def dash(self):
        """Активирует рывок в текущем направлении"""
        if self.dash_timer <= 0:
            self.dash_time = self.dash_duration
            self.dash_timer = self.dash_cooldown
            
            # Определяем направление дэша на основе направления персонажа
            self.dash_direction = 1 if self.facing_right else -1
    
    def handle_dash(self, level, dt):
        """Обрабатывает состояние дэша"""
        dash_speed = DASH_DISTANCE / self.dash_duration
        self.dash_time -= dt
        if self.dash_time <= 0:
            self.dash_time = 0
            return
        move_x = self.dash_direction * dash_speed * dt
        old_pos = Vector2(self.pos)
        self.pos.x += move_x
        self.rect.x = int(self.pos.x)
        for tile in level.collision_tiles:
            if self.rect.colliderect(tile):
                if self.dash_direction > 0:
                    self.rect.right = tile.left
                else:
                    self.rect.left = tile.right
                self.pos.x = self.rect.x
                self.dash_time = 0
                break
    
    def launch_hook(self, target_pos, scale_factor, offset, camera):
        """Запускает крюк в указанном направлении"""
        if self.hook_state:
            return
        self.hook_state = "extending"
        self.hook_pos = Vector2(self.pos.x + CHARACTER_WIDTH/2, self.pos.y)
        self.hook_origin = Vector2(self.pos.x + CHARACTER_WIDTH/2, self.pos.y)
        adjusted_target_pos = Vector2(
            (target_pos.x - offset.x) / scale_factor + camera.x,
            (target_pos.y - offset.y) / scale_factor + camera.y
        )
        direction = adjusted_target_pos - self.hook_pos
        if direction.length() > 0:
            direction = direction.normalize()
        self.hook_vel = direction * HOOK_SPEED
        self.rope_length = 0
    
    def handle_hook_motion(self, level):
        """Обрабатывает движение крюка"""
        if self.hook_state == "extending":
            old_hook_pos = Vector2(self.hook_pos)
            self.hook_pos += self.hook_vel
            distance = (self.hook_pos - self.hook_origin).length()
            if distance > HOOK_RANGE:
                self.hook_state = "retracting"
                self.set_retract_velocity()
                return
            
            # Проверка столкновения с тайлами
            for tile in level.collision_tiles:
                tile_rect = pygame.Rect(tile.x, tile.y, tile.width, tile.height)
                # Простая проверка попадания крюка в тайл
                if tile_rect.collidepoint(self.hook_pos.x, self.hook_pos.y):
                    self.hook_state = "attached"
                    self.vel = Vector2(0, 0)
                    self.swing_angle = math.atan2(self.pos.y - self.hook_pos.y, self.pos.x - self.hook_pos.x)
                    self.swing_speed = 0
                    self.rope_length = (self.pos - self.hook_pos).length()
                    return
                    
        elif self.hook_state == "retracting":
            self.hook_pos += self.hook_vel
            distance = (self.hook_pos - Vector2(self.pos.x + CHARACTER_WIDTH/2, self.pos.y)).length()
            if distance < 10:
                self.hook_state = None
                self.hook_pos = None
                self.hook_vel = None
                self.hook_origin = None
                self.rope_length = 0
            else:
                self.set_retract_velocity()
    
    def set_retract_velocity(self):
        """Устанавливает скорость возврата крюка"""
        direction = Vector2(self.pos.x + CHARACTER_WIDTH/2, self.pos.y) - self.hook_pos
        if direction.length() > 0:
            direction = direction.normalize()
            self.hook_vel = direction * HOOK_SPEED
    

    
    def handle_swinging(self, level):
        """Обрабатывает качание на крюке"""
        keys = pygame.key.get_pressed()
        new_rope_length = self.rope_length
        if keys[pygame.K_w] and self.hook_state == "attached":
            new_rope_length -= ROPE_SPEED
        if keys[pygame.K_s] and self.hook_state == "attached":
            new_rope_length += ROPE_SPEED
        new_rope_length = max(MIN_ROPE_LENGTH, min(new_rope_length, HOOK_RANGE))
        old_pos = Vector2(self.pos)
        test_pos = Vector2(self.hook_pos.x + math.cos(self.swing_angle) * new_rope_length, 
                          self.hook_pos.y + math.sin(self.swing_angle) * new_rope_length)
        test_rect = self.rect.copy()
        test_rect.x = int(test_pos.x)
        test_rect.y = int(test_pos.y)
        collision = False
        for tile in level.collision_tiles:
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
        for tile in level.collision_tiles:
            if self.rect.colliderect(tile):
                self.release_hook()
                break
    
    def release_hook(self):
        """Отсоединяет крюк"""
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
    
    def take_damage(self, amount):
        """Наносит урон игроку"""
        self.health = max(0, self.health - amount)
        return self.health <= 0
    
    def heal(self, amount):
        """Восстанавливает здоровье игроку"""
        self.health = min(self.max_health, self.health + amount)
    
    def collect_coin(self):
        """Увеличивает количество собранных монет"""
        self.coins += 1
        
    def draw_effects(self, surface, camera, scale_factor, offset, viewport):
        """Отрисовывает все активные эффекты игрока"""
        for effect in self.effects:
            if effect["type"] == "double_jump":
                # Вычисляем позицию эффекта с учетом камеры
                effect_pos = Vector2(
                    int((effect["pos"].x - camera.x) * scale_factor + offset.x),
                    int((effect["pos"].y - camera.y) * scale_factor + offset.y)
                )
                
                # Вычисляем текущий радиус эффекта (увеличивается со временем)
                progress = 1.0 - effect["time"] / 0.5  # от 0 до 1
                radius = effect["radius"] + (effect["max_radius"] - effect["radius"]) * progress
                radius = int(radius * scale_factor)
                
                # Вычисляем прозрачность (уменьшается со временем)
                alpha = int(255 * (1.0 - progress))
                
                # Создаем поверхность для эффекта
                effect_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                
                # Рисуем круг с прозрачностью
                color_with_alpha = effect["color"] + (alpha,)
                pygame.draw.circle(effect_surface, color_with_alpha, (radius, radius), radius)
                
                # Отрисовываем эффект, только если он виден на экране
                effect_rect = effect_surface.get_rect(center=(int(effect_pos.x), int(effect_pos.y)))
                if viewport.colliderect(effect_rect):
                    surface.blit(effect_surface, effect_rect.topleft) 