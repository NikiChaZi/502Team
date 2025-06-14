import asyncio
import os
import random
import pygame
from pygame import Vector2

from src.player import Player
from src.level import Level, TILE_SIZE
from src.tmx_parser import TILE_SIZE as TMX_TILE_SIZE, LEVEL_SCALE_MULTIPLIER
from src.background import ParallaxBackground
from src.game_objects import Coin, Chest, Fountain, Trap
from src.ui import HUD, pause_buttons, settings_menu_elements, Button, Slider
from src.utils import handle_resize, scale_factor, offset, viewport

class Game:
    def __init__(self, level_number=None):
        # Инициализация pygame
        pygame.init()
        
        # Получаем информацию о разрешении экрана
        info = pygame.display.Info()
        self.screen = pygame.display.set_mode(
            (info.current_w, info.current_h), 
            pygame.NOFRAME
        )
        pygame.display.set_caption("Зеленая зона - Пиксельный платформер")
        
        # Инициализация часов и времени
        self.clock = pygame.time.Clock()
        self.dt = 1 / 60
        
        # Выбор персонажа (Fighter, Samurai, Shinobi, NewCharacter)
        self.character_type = "NewCharacter"  # Используем нового персонажа по умолчанию
        
        # Инициализация игровых компонентов
        self.player = Player(100, 200, character_type=self.character_type)
        
        # Загружаем уровень
        self.current_level_number = level_number if level_number is not None else 1
        self.load_level(self.current_level_number)
            
        # Инициализация фона с эффектом паралакса
        self.background = ParallaxBackground()
        
        # Инициализация камеры
        self.camera = Vector2(0, 0)
        
        # Инициализация HUD
        self.hud = HUD(self.player, self.clock)
        
        # Инициализация переменных игры
        self.running = True
        self.score = 0
        
        # Рассчитываем масштаб для полноэкранного режима
        self.calculate_level_scale()
        
        # Инициализация игровых объектов
        self.initialize_game_objects()
    
    def calculate_level_scale(self):
        """Рассчитывает масштаб уровня для полноэкранного режима"""
        # Получаем размеры экрана и уровня
        screen_width = viewport.width / scale_factor
        screen_height = viewport.height / scale_factor
        
        # Рассчитываем масштаб для заполнения экрана
        scale_x = screen_width / self.level.width
        scale_y = screen_height / self.level.height
        
        # Используем минимальный масштаб, чтобы уровень помещался на экран
        self.level_scale = min(scale_x, scale_y)
        
        # Но не меньше 1.0, чтобы не было слишком мелко
        self.level_scale = max(1.0, self.level_scale)
        
        print(f"Масштаб уровня: {self.level_scale:.2f} (экран: {screen_width:.0f}x{screen_height:.0f}, уровень: {self.level.width}x{self.level.height})")
    
    def load_level(self, level_number):
        """Загружает уровень по номеру"""
        try:
            print(f"Загружаем уровень {level_number}")
            self.level = Level(level_number=level_number)
            self.current_level_number = level_number
            
            # Пересчитываем масштаб после загрузки уровня
            if hasattr(self, 'level_scale'):
                self.calculate_level_scale()
            
            # Сбрасываем позицию игрока при загрузке нового уровня
            if self.player:
                self.player.rect.x = 100
                self.player.rect.y = 200
                
            print(f"Уровень {level_number} успешно загружен")
            
        except Exception as e:
            print(f"Ошибка загрузки уровня {level_number}: {e}")
            # Загружаем случайный уровень в случае ошибки
            self.level = Level()
            self.current_level_number = None
    
    def initialize_game_objects(self):
        """Инициализирует игровые объекты на уровне"""
        self.objects = []
        
        # Размер тайла с учетом масштабирования
        scaled_tile_size = TMX_TILE_SIZE * LEVEL_SCALE_MULTIPLIER
        
        # Получаем список всех платформ (включая землю)
        platforms = []
        collision_rects = []  # Список прямоугольников для всех блоков карты
        for tile in self.level.collision_tiles:
            # Создаем прямоугольник для каждого блока
            collision_rects.append(pygame.Rect(tile.x, tile.y, tile.width, tile.height))
            # Проверяем, есть ли над тайлом свободное место
            has_space_above = True
            for other_tile in self.level.collision_tiles:
                if (other_tile.x == tile.x and 
                    other_tile.y == tile.y - scaled_tile_size):
                    has_space_above = False
                    break
            if has_space_above:
                platforms.append(tile)

        # Сначала размещаем сундуки, чтобы знать их позиции
        chest_rects = []  # Список прямоугольников для проверки пересечений
        if platforms:
            # Отфильтруем платформы, достаточно широкие для сундука
            suitable_platforms = [p for p in platforms if p.width >= scaled_tile_size]
            
            if suitable_platforms:
                for _ in range(min(5, len(suitable_platforms) // 4)):  # Не более 5 сундуков
                    platform = random.choice(suitable_platforms)
                    x = platform.x + random.randint(0, max(0, platform.width - 22))
                    y = platform.y - 22  # Размещаем сундук на платформе
                    chest = Chest(x, y)
                    self.objects.append(chest)
                    # Добавляем прямоугольник с небольшим буфером вокруг сундука
                    chest_rects.append(pygame.Rect(x - 5, y - 5, 32, 32))

        # Добавляем фонтан и получаем его область
        fountain_rect = None
        ground_level = self.level.height - scaled_tile_size * 2  # Уровень земли
        
        # Находим все блоки на уровне земли
        ground_blocks = []
        for tile in self.level.collision_tiles:
            if abs(tile.y - ground_level) <= scaled_tile_size:
                ground_blocks.append(tile)
        
        # Сортируем блоки по X-координате
        ground_blocks.sort(key=lambda b: b.x)
        
        # Ищем самый большой промежуток между блоками
        max_gap_start = 0
        max_gap_width = 0
        current_x = 0
        
        for block in ground_blocks:
            gap_width = block.x - current_x
            if gap_width > max_gap_width and gap_width >= 72:  # 72 - ширина фонтана
                max_gap_width = gap_width
                max_gap_start = current_x
            current_x = block.x + block.width
            
        # Проверяем промежуток от последнего блока до конца уровня
        final_gap_width = self.level.width - current_x
        if final_gap_width > max_gap_width and final_gap_width >= 72:
            max_gap_width = final_gap_width
            max_gap_start = current_x
            
        # Создаем фонтан и сохраняем его область
        if max_gap_width >= 72:
            # Размещаем фонтан в центре найденного промежутка
            x = max_gap_start + (max_gap_width - 72) // 2
            y = ground_level - 72
            print(f"Placing fountain in gap at x={x}, y={y}, gap_width={max_gap_width}")
            fountain = Fountain(x, y)
            self.objects.append(fountain)
            fountain_rect = pygame.Rect(x - scaled_tile_size, y - scaled_tile_size, 72 + 2 * scaled_tile_size, 72 + 2 * scaled_tile_size)
        else:
            # Если нет подходящего промежутка, размещаем фонтан в начале уровня
            x = scaled_tile_size * 2
            y = ground_level - 72
            print(f"No suitable gap found, placing fountain at start: x={x}, y={y}")
            fountain = Fountain(x, y)
            self.objects.append(fountain)
            fountain_rect = pygame.Rect(x - scaled_tile_size, y - scaled_tile_size, 72 + 2 * scaled_tile_size, 72 + 2 * scaled_tile_size)
                
        # Добавляем монеты, избегая области сундуков, фонтана и блоков карты
        for _ in range(20):
            valid_placement = False
            attempts = 10  # Максимальное количество попыток для каждой монеты
            
            while attempts > 0 and not valid_placement:
                if random.random() < 0.7 and platforms:  # 70% монет на платформах
                    platform = random.choice(platforms)
                    x = platform.x + random.randint(0, max(0, platform.width - 24))
                    y = platform.y - 30  # Размещаем над платформой
                else:  # 30% монет в воздухе
                    x = random.randint(100, self.level.width - 100)
                    y = random.randint(50, self.level.height - 150)
                
                # Создаем прямоугольник для проверки пересечений
                coin_rect = pygame.Rect(x, y, 24, 24)
                
                # Проверяем пересечения с блоками карты
                intersects_with_blocks = False
                for block_rect in collision_rects:
                    if coin_rect.colliderect(block_rect):
                        intersects_with_blocks = True
                        break
                
                if intersects_with_blocks:
                    attempts -= 1
                    continue
                
                # Проверяем пересечения с сундуками и фонтаном
                intersects = False
                for chest_rect in chest_rects:
                    if coin_rect.colliderect(chest_rect):
                        intersects = True
                        break
                
                if fountain_rect and coin_rect.colliderect(fountain_rect):
                    intersects = True
                
                if not intersects:
                    self.objects.append(Coin(x, y))
                    valid_placement = True
                else:
                    attempts -= 1

        # Добавляем ловушки на платформы, избегая область фонтана
        if platforms:
            trap_platforms = [p for p in platforms if p.width >= scaled_tile_size * 2]  # Платформы достаточной ширины
            num_traps = min(len(trap_platforms), 8)  # Не более 8 ловушек
            
            for _ in range(num_traps):
                if not trap_platforms:  # Если не осталось подходящих платформ
                    break
                    
                # Пробуем найти место для ловушки, не пересекающееся с фонтаном
                valid_placement = False
                attempts = 10  # Максимальное количество попыток для каждой ловушки
                
                while attempts > 0 and not valid_placement and trap_platforms:
                    platform = random.choice(trap_platforms)
                    x = platform.x + random.randint(0, max(0, platform.width - 32))
                    y = platform.y - 32
                    
                    # Создаем прямоугольник для проверки пересечения
                    trap_rect = pygame.Rect(x, y, 32, 32)
                    
                    # Проверяем, не пересекается ли ловушка с фонтаном
                    if fountain_rect is None or not trap_rect.colliderect(fountain_rect):
                        self.objects.append(Trap(x, y))
                        valid_placement = True
                        trap_platforms.remove(platform)
                    else:
                        attempts -= 1
                        if attempts == 0:  # Если все попытки исчерпаны, убираем платформу
                            trap_platforms.remove(platform)
    
    def reset(self, level_number=None):
        """Сбрасывает игру до начального состояния"""
        # Если передан номер уровня, используем его, иначе текущий
        if level_number is not None:
            self.current_level_number = level_number
        
        self.player = Player(100, 200, character_type=self.character_type)
        
        # Загружаем уровень по номеру
        if self.current_level_number is not None:
            self.load_level(self.current_level_number)
        else:
            # Загружаем случайный уровень, если номер не задан
            self.level = Level()
            
        self.camera = Vector2(0, 0)
        self.hud = HUD(self.player, self.clock)
        self.running = True
        self.score = 0
        self.dt = 1 / 60
        
        # Заново инициализируем игровые объекты
        self.initialize_game_objects()
    
    def change_character(self, character_type):
        """Меняет персонажа игрока"""
        if character_type in ["Fighter", "Samurai", "Shinobi"]:
            self.character_type = character_type
            self.reset()
            return True
        return False
    
    async def run(self, current_menu):
        """Основной игровой цикл"""
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
            
            # Ограничиваем FPS и обновляем время
            self.clock.tick(60)
            self.dt = self.clock.get_time() / 1000.0
            
            # Обновляем экран
            pygame.display.flip()
            
            # Даем другим процессам время выполняться
            await asyncio.sleep(0.001)
        
        # Если игра не running, возвращаемся в главное меню
        if not self.running:
            current_menu[0] = "main"
            current_menu[1] = None
        
        # Сбрасываем игру для следующего запуска
        self.reset()
    
    def handle_events(self, current_menu):
        """Обрабатывает игровые события"""
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
                    # Отладочное сообщение для кнопки R
                    print("Нажата клавиша R - отсоединяем крюк")
                    self.player.release_hook()
                elif event.key == pygame.K_LSHIFT:
                    self.player.dash()
                elif event.key == pygame.K_h:
                    self.player.take_damage(10)  # Для тестирования
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    mouse_pos = Vector2(event.pos)
                    # Отладочное сообщение для клика мышью
                    print(f"Клик мышью для запуска крюка: {mouse_pos}")
                    combined_scale = scale_factor * self.level_scale
                    self.player.launch_hook(mouse_pos, combined_scale, offset, self.camera)
            elif event.type == pygame.FINGERDOWN:
                # Поддержка сенсорных экранов
                mouse_pos = Vector2(event.x * viewport.width, event.y * viewport.height)
                print(f"Сенсорный клик для запуска крюка: {mouse_pos}")
                combined_scale = scale_factor * self.level_scale
                self.player.launch_hook(mouse_pos, combined_scale, offset, self.camera)
        
        # Обработка нажатых клавиш
        keys = pygame.key.get_pressed()
        
        # Перемещение игрока
        if self.player.hook_state != "attached" and self.player.dash_time <= 0:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player.move_left()
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player.move_right()
    
    def handle_pause_events(self, current_menu):
        """Обрабатывает события в меню паузы"""
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
                mouse_pos = Vector2(event.pos) if event.type == pygame.MOUSEBUTTONDOWN else Vector2(event.x * viewport.width, event.y * viewport.height)
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
        """Обрабатывает события в меню настроек"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                mouse_pos = Vector2(event.pos) if event.type == pygame.MOUSEBUTTONDOWN else Vector2(event.x * viewport.width, event.y * viewport.height)
                for element in settings_menu_elements:
                    if isinstance(element, Button) and element.is_hovered(mouse_pos):
                        if element.text == "Назад":
                            if current_menu[1] == "pause":
                                current_menu[0] = "pause"
                                current_menu[1] = "game"
                            else:
                                current_menu[0] = "main"
                                current_menu[1] = None
        
        # Обновляем элементы интерфейса
        for element in settings_menu_elements:
            if isinstance(element, Slider):
                element.update(mouse_pos, mouse_pressed)
            elif isinstance(element, Button):
                element.update(mouse_pos)
    
    def update(self):
        """Обновляет состояние игры"""
        # Обновляем игрока
        self.player.update(self.level, self.dt, pygame.key.get_pressed())
        
        # Обновляем игровые объекты
        for obj in self.objects:
            obj.update(self.dt)
            
            # Проверяем коллизии с игроком
            if obj.collides_with(self.player.rect):
                if isinstance(obj, Coin):
                    # Собираем монету
                    self.score += obj.collect()
                    self.player.collect_coin()
                elif isinstance(obj, Chest) and self.player.on_ground:
                    # Открываем сундук, если игрок на земле
                    if obj.open():
                        # Даем бонус за открытие сундука
                        self.score += 10
                        self.player.heal(20)
                elif isinstance(obj, Trap):
                    # Активируем ловушку
                    damage = obj.trigger(self.player)
                    if damage > 0:
                        self.player.take_damage(damage)
        
        # Обновляем камеру, чтобы следовать за игроком
        self.update_camera()
        
        # Обновляем фон
        self.background.update(self.camera)
    
    def update_camera(self):
        """Обновляет позицию камеры, чтобы следовать за игроком"""
        # Вычисляем размеры уровня в пикселях
        level_width = self.level.width
        level_height = self.level.height
        
        # Используем комбинированный масштаб
        combined_scale = scale_factor * self.level_scale
        
        # Вычисляем желаемую позицию камеры (центрирована на игроке)
        desired_camera_x = self.player.pos.x + self.player.rect.width / 2 - viewport.width / 2 / combined_scale
        desired_camera_y = self.player.pos.y + self.player.rect.height / 2 - viewport.height / 2 / combined_scale
        
        # Плавное следование за игроком
        camera_speed = 0.1
        self.camera.x += (desired_camera_x - self.camera.x) * camera_speed
        self.camera.y += (desired_camera_y - self.camera.y) * camera_speed
        
        # Ограничиваем камеру границами уровня
        max_camera_x = max(0, level_width - viewport.width / combined_scale)
        max_camera_y = max(0, level_height - viewport.height / combined_scale)
        
        self.camera.x = max(0, min(self.camera.x, max_camera_x))
        self.camera.y = max(0, min(self.camera.y, max_camera_y))
        
        # Если уровень меньше экрана, центрируем его
        if level_width * combined_scale < viewport.width:
            self.camera.x = (level_width - viewport.width / combined_scale) / 2
        if level_height * combined_scale < viewport.height:
            self.camera.y = (level_height - viewport.height / combined_scale) / 2
    
    def draw(self):
        """Отрисовывает игру"""
        # Очищаем экран
        self.screen.fill((0, 0, 0))
        
        # Отрисовываем фон
        self.background.draw(self.screen, offset, viewport, scale_factor)
        
        # Отрисовываем уровень с дополнительным масштабированием
        combined_scale = scale_factor * self.level_scale
        self.level.draw(self.screen, self.camera, combined_scale, offset, viewport)
        
        # Отрисовываем игровые объекты с тем же масштабом
        for obj in self.objects:
            obj.draw(self.screen, self.camera, combined_scale, offset, viewport)
        
        # Отрисовываем игрока
        self.draw_player()
        
        # Отрисовываем HUD
        self.hud.draw(self.screen, offset, viewport, self.score)
    
    def draw_player(self):
        """Отрисовывает игрока"""
        # Используем комбинированный масштаб
        combined_scale = scale_factor * self.level_scale
        
        # Вычисляем позицию игрока с учетом камеры
        player_rect = pygame.Rect(
            int((self.player.pos.x - self.camera.x) * combined_scale + offset.x),
            int((self.player.pos.y - self.camera.y) * combined_scale + offset.y),
            int(self.player.rect.width * combined_scale),
            int(self.player.rect.height * combined_scale)
        )
        
        # Отрисовываем эффекты
        self.player.draw_effects(self.screen, self.camera, combined_scale, offset, viewport)
        
        # Отрисовываем крюк и веревку, если они активны - рисуем до персонажа, чтобы персонаж был поверх
        if self.player.hook_state:
            # Вычисляем позицию крюка с учетом камеры
            hook_pos = Vector2(
                int((self.player.hook_pos.x - self.camera.x) * combined_scale + offset.x),
                int((self.player.hook_pos.y - self.camera.y) * combined_scale + offset.y)
            )
            
            # Вычисляем центр игрока
            player_center = Vector2(
                int(player_rect.centerx),
                int(player_rect.centery)
            )
            
            # Отрисовываем веревку и крюк, только если они видны на экране или центр игрока виден
            if viewport.collidepoint(hook_pos) or viewport.collidepoint(player_center):
                # Отрисовываем веревку
                pygame.draw.aaline(  # Использование сглаженной линии для лучшего вида
                    self.screen,
                    (220, 220, 220),
                    player_center,
                    hook_pos,
                )
                
                # Отрисовываем крюк (более заметным)
                pygame.draw.circle(
                    self.screen,
                    (220, 220, 220),
                    (int(hook_pos.x), int(hook_pos.y)),
                    int(6 * scale_factor)
                )
                pygame.draw.circle(
                    self.screen,
                    (100, 100, 100),
                    (int(hook_pos.x), int(hook_pos.y)),
                    int(3 * scale_factor)
                )
        
        # Отрисовываем игрока, только если он виден на экране
        if viewport.colliderect(player_rect):
            frame = self.player.get_current_frame(scale_factor)
            
            # Получаем размеры спрайта
            frame_width = frame.get_width()
            frame_height = frame.get_height()
            
            # Вычисляем позицию отрисовки, чтобы спрайт был центрирован по хитбоксу
            sprite_x = player_rect.x + (player_rect.width - frame_width) // 2
            sprite_y = player_rect.y + (player_rect.height - frame_height) // 2
            
            # Отрисовываем спрайт
            self.screen.blit(frame, (sprite_x, sprite_y))
            
            # Отладочная отрисовка хитбокса (при необходимости)
            # pygame.draw.rect(self.screen, (255, 0, 0), player_rect, 1)
    
    def draw_pause(self):
        """Отрисовывает меню паузы"""
        # Сначала отрисовываем затемненную игру
        self.draw()
        
        # Создаем поверхность для затемнения
        overlay = pygame.Surface((viewport.width, viewport.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Полупрозрачный черный
        self.screen.blit(overlay, (offset.x, offset.y))
        
        # Отрисовываем кнопки паузы
        for button in pause_buttons:
            button.draw(self.screen)
    
    def draw_settings(self):
        """Отрисовывает меню настроек"""
        # Если мы попали сюда из паузы, отрисовываем затемненную игру
        if self.running:
            self.draw()
            
            # Создаем поверхность для затемнения
            overlay = pygame.Surface((viewport.width, viewport.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Полупрозрачный черный
            self.screen.blit(overlay, (offset.x, offset.y))
        else:
            self.screen.fill((0, 0, 0))
        
        # Отрисовываем элементы меню настроек
        for element in settings_menu_elements:
            element.draw(self.screen)

    def update_animation(self, dt):
        # Определение текущего состояния
        if self.health <= 0:
            new_state = "dead"
        elif self.dash_time > 0:
            new_state = "dash"
        elif not self.on_ground:
            if self.vel.y < 0:
                # Если это второй прыжок, используем специальную анимацию двойного прыжка
                if self.jump_count == 2 and "double_jump" in self.animations and self.animations["double_jump"]:
                    new_state = "double_jump"
                else:
                    new_state = "jump"
            else:
                new_state = "fall"
        elif abs(self.vel.x) > 3:
            new_state = "run"
        elif abs(self.vel.x) > 0.5:
            new_state = "walk"
        else:
            new_state = "idle" 