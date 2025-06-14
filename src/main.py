import pygame
import asyncio
import os
import sys
import platform

# Добавим текущий каталог в PYTHONPATH, чтобы импорты работали корректно
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.game import Game
from src.utils import handle_resize, calculate_viewport, scale_factor, offset, viewport, font, menu_background, level_background, level_background_blurred
from src.background import ParallaxBackground
from src.ui import main_menu_buttons, settings_menu_elements, pause_buttons, Button, Slider
from src.player import FRAMES_COUNT
from src.level_select import LevelSelectScreen
from pygame import Vector2

# Инициализация Pygame
pygame.init()

# Доступные персонажи - обновляем пути к ресурсам
CHARACTERS = ["SimpleChar"]

# Глобальные переменные
current_menu = ["main", None]
title_background = None
selected_character = "SimpleChar"  # Выбираем нового персонажа по умолчанию
character_preview_images = {}  # Хранилище для превью персонажей
level_select_screen = None  # Экран выбора уровня

# Словарь с переводом имен персонажей
CHARACTER_NAMES = {
    "SimpleChar": "Простой персонаж"
}

# Описания способностей персонажей
CHARACTER_DESCRIPTIONS = {
    "SimpleChar": "Квадратный персонаж без особых способностей"
}

# Функция для создания простого квадратного спрайта
def create_square_sprite(width=32, height=32, color=(255, 0, 0)):
    """Создает простой квадратный спрайт заданного размера и цвета"""
    square = pygame.Surface((width, height), pygame.SRCALPHA)
    square.fill(color)
    # Добавляем рамку для визуального улучшения
    pygame.draw.rect(square, (0, 0, 0), square.get_rect(), 1)
    return square

# Функция для загрузки превью персонажей
def load_character_previews():
    global character_preview_images
    for character in CHARACTERS:
        try:
            # Специальная обработка для SimpleChar - используем спрайт-лист из temp_card
            if character == "SimpleChar":
                card_sprite_path = 'temp_card/Card.png'
                if os.path.exists(card_sprite_path):
                    print(f"Загружаем превью из temp_card: {card_sprite_path}")
                    card_sprite_sheet = pygame.image.load(card_sprite_path).convert_alpha()
                    
                    # Извлекаем первый кадр из спрайт-листа для превью
                    frame_width = 24  # Ширина одного кадра
                    frame_height = 24  # Высота одного кадра
                    first_frame_rect = pygame.Rect(0, 0, frame_width, frame_height)
                    first_frame = card_sprite_sheet.subsurface(first_frame_rect).copy()
                    
                    # Масштабируем для превью
                    scale_multiplier = 4
                    preview_image = pygame.transform.scale(first_frame, (frame_width * scale_multiplier, frame_height * scale_multiplier))
                    
                    # Добавляем рамку к превью
                    pygame.draw.rect(preview_image, (255, 255, 255), preview_image.get_rect(), 2)
                    
                    # Сохраняем также данные для анимации превью
                    character_preview_images[character] = {
                        'static': preview_image,
                        'animated': True,
                        'sprite_sheet': card_sprite_sheet,
                        'frame_width': frame_width,
                        'frame_height': frame_height,
                        'frames_count': card_sprite_sheet.get_width() // frame_width,
                        'current_frame': 0,
                        'last_update': pygame.time.get_ticks(),
                        'frame_rate': 100  # milliseconds - такая же скорость как в игре
                    }
                    continue
            
            # Ищем персонажей в обновленной структуре папок Assets
            # Проверяем разные варианты путей для персонажей
            possible_paths = [
                f'src/Assets/1 Main Characters/{character}/Idle.png',
                f'src/Assets/Characters/{character}/Idle.png',
                f'src/Assets/{character}/Idle.png'
            ]
            
            idle_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    idle_path = path
                    break
            
            if idle_path:
                sprite_sheet = pygame.image.load(idle_path).convert_alpha()
                # Получаем первый кадр из спрайт-листа
                frames_count = 4  # По умолчанию 4 кадра для Idle
                
                # Проверяем фактическое количество кадров для персонажа
                if character in FRAMES_COUNT.get("idle", {}):
                    frames_count = FRAMES_COUNT["idle"][character]
                
                frame_width = sprite_sheet.get_width() // frames_count
                preview_image = pygame.Surface((frame_width, sprite_sheet.get_height()), pygame.SRCALPHA)
                preview_image.blit(sprite_sheet, (0, 0), (0, 0, frame_width, sprite_sheet.get_height()))
                
                # Масштабируем изображение для отображения с улучшенным качеством
                scale_multiplier = 5 if character == "SimpleChar" else 4  # Немного больше для нового персонажа
                preview_image = pygame.transform.scale(preview_image, (frame_width * scale_multiplier, sprite_sheet.get_height() * scale_multiplier))
                
                # Добавляем рамку к превью
                pygame.draw.rect(preview_image, (255, 255, 255), preview_image.get_rect(), 2)
                
                character_preview_images[character] = preview_image
            else:
                # Попробуем загрузить Run.png, если Idle.png не существует
                possible_run_paths = [
                    f'src/Assets/1 Main Characters/{character}/Run.png',
                    f'src/Assets/Characters/{character}/Run.png',
                    f'src/Assets/{character}/Run.png'
                ]
                
                run_path = None
                for path in possible_run_paths:
                    if os.path.exists(path):
                        run_path = path
                        break
                
                if run_path:
                    sprite_sheet = pygame.image.load(run_path).convert_alpha()
                    
                    # Получаем первый кадр из спрайт-листа бега
                    frames_count = 8  # По умолчанию 8 кадров для Run
                    if character in FRAMES_COUNT.get("run", {}):
                        frames_count = FRAMES_COUNT["run"][character]
                    
                    frame_width = sprite_sheet.get_width() // frames_count
                    preview_image = pygame.Surface((frame_width, sprite_sheet.get_height()), pygame.SRCALPHA)
                    preview_image.blit(sprite_sheet, (0, 0), (0, 0, frame_width, sprite_sheet.get_height()))
                    
                    # Масштабируем изображение
                    preview_image = pygame.transform.scale(preview_image, (frame_width * 4, sprite_sheet.get_height() * 4))
                    
                    # Добавляем рамку к превью
                    pygame.draw.rect(preview_image, (255, 255, 255), preview_image.get_rect(), 2)
                    
                    character_preview_images[character] = preview_image
        except Exception as e:
            print(f"Ошибка загрузки превью для {character}: {e}")
            character_preview_images[character] = None
            
    # Проверяем, что у всех персонажей есть превью, иначе создаем заглушку
    for character in CHARACTERS:
        if character not in character_preview_images or character_preview_images[character] is None:
            # Создаем заглушку с именем персонажа
            width, height = 100, 150
            placeholder = pygame.Surface((width, height), pygame.SRCALPHA)
            placeholder.fill((100, 100, 100, 180))  # Полупрозрачный серый фон
            
            # Добавляем имя персонажа на заглушку
            display_name = CHARACTER_NAMES.get(character, character)
            try:
                name_font = pygame.font.Font('src/Resources/pixel_font.ttf', 16) if os.path.exists('src/Resources/pixel_font.ttf') else pygame.font.SysFont('monospace', 16)
                name_text = name_font.render(display_name, True, (255, 255, 255))
                name_rect = name_text.get_rect(center=(width//2, height//2))
                placeholder.blit(name_text, name_rect)
            except:
                # Если не удалось добавить текст, просто используем заглушку
                pass
                
            # Добавляем рамку
            pygame.draw.rect(placeholder, (200, 200, 200), placeholder.get_rect(), 2)
            
            character_preview_images[character] = placeholder

async def main():
    """Основная функция игры"""
    global current_menu, title_background, level_select_screen
    
    # Инициализируем переменные
    running = True
    game = None
    
    # Инициализируем экран pygame
    info = pygame.display.Info()
    screen = pygame.display.set_mode(
        (info.current_w, info.current_h), 
        pygame.NOFRAME
    )
    pygame.display.set_caption("Зеленая зона - Пиксельный платформер")
    
    # Инициализируем экран выбора уровня
    level_select_screen = LevelSelectScreen()
    
    # Загружаем фоновое изображение для меню - обновляем пути
    try:
        # Проверяем разные возможные пути для фона
        background_paths = [
            'src/Assets/2 Locations/Background/Background.png',
            'src/Assets/Background/Background.png',
            'src/Levels/Tiled/Backgrounds/4.png'
        ]
        
        title_background = None
        for bg_path in background_paths:
            if os.path.exists(bg_path):
                title_background = pygame.image.load(bg_path).convert_alpha()
                print(f"Загружен фон: {bg_path}")
                break
        
        if title_background is None:
            print("Фон не найден, используется цветная заливка")
            
    except Exception as e:
        print(f"Ошибка загрузки фона заголовка: {e}")
        title_background = None
    
    # Загружаем превью персонажей
    load_character_previews()
    
    # Основной игровой цикл
    while running:
        # Получаем положение мыши
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Обрабатываем события
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event.w, event.h)
                
        # Обработка разных меню
        if current_menu[0] == "main":
            handle_main_menu(events, mouse_pos, game)
            draw_main_menu(screen)
        elif current_menu[0] == "level_select":
            result = level_select_screen.handle_events(events, mouse_pos)
            if result == "main_menu":
                current_menu = ["main", None]
            elif result == "start_level":
                # Запускаем игру с выбранным уровнем
                selected_level = level_select_screen.selected_level
                game = Game(level_number=selected_level)
                game.character_type = selected_character
                game.reset(level_number=selected_level)
                current_menu = ["game", "main"]
            level_select_screen.draw(screen)
        elif current_menu[0] == "settings" and current_menu[1] is None:
            handle_settings_menu(events, mouse_pos, mouse_pressed)
            draw_settings_menu(screen)
        elif current_menu[0] in ["game", "pause", "settings"] and game is not None:
            # Если мы находимся в игре или связанных с ней меню, передаем управление игре
            await game.run(current_menu)
        
        # Обновляем экран
        pygame.display.flip()
        
        # Небольшая пауза для экономии ресурсов
        await asyncio.sleep(0.001)
    
    # Выход из игры
    pygame.quit()
    sys.exit()

def handle_main_menu(events, mouse_pos, game):
    """Обрабатывает события в главном меню"""
    global current_menu, selected_character
    
    # Проверяем, нажал ли пользователь на одно из превью персонажей
    if pygame.mouse.get_pressed()[0]:
        preview_size = int(100 * scale_factor)
        spacing = int(20 * scale_factor)
        total_width = len(CHARACTERS) * preview_size + (len(CHARACTERS) - 1) * spacing
        
        # Верхняя позиция строки с превью персонажей
        try:
            title_font = pygame.font.Font('src/Resources/pixel_font.ttf', int(52 * scale_factor)) if os.path.exists('src/Resources/pixel_font.ttf') else pygame.font.SysFont('monospace', int(52 * scale_factor))
            character_font = pygame.font.Font('src/Resources/pixel_font.ttf', int(36 * scale_factor)) if os.path.exists('src/Resources/pixel_font.ttf') else pygame.font.SysFont('monospace', int(36 * scale_factor))
            
            # Расчет верхней позиции для превью
            title_height = title_font.get_linesize()
            subtitle_height = title_font.get_linesize()
            char_select_height = character_font.get_linesize()
            
            preview_top = int(offset.y + 50 * scale_factor) + title_height + int(20 * scale_factor) + subtitle_height + int(50 * scale_factor) + char_select_height + int(30 * scale_factor)
            
            start_x = viewport.centerx - total_width / 2
            
            # Проверяем каждое превью персонажа
            for i, character in enumerate(CHARACTERS):
                # Позиция для текущего превью
                preview_x = start_x + i * (preview_size + spacing)
                
                # Получаем превью персонажа
                preview_data = character_preview_images.get(character)
                
                if preview_data:
                    # Получаем изображение (статичное или текущий кадр анимации)
                    if isinstance(preview_data, dict) and preview_data.get('animated'):
                        preview_image = preview_data['static']  # Используем статичное превью для расчета размеров
                    else:
                        preview_image = preview_data
                    
                    # Рассчитываем размеры и положение кнопки
                    aspect_ratio = preview_image.get_width() / preview_image.get_height()
                    preview_height = preview_size
                    preview_width = int(preview_height * aspect_ratio)
                    
                    # Рассчитываем прямоугольник для кнопки
                    button_rect = pygame.Rect(
                        preview_x - int(5 * scale_factor),
                        preview_top - int(5 * scale_factor),
                        preview_width + int(10 * scale_factor),
                        preview_height + int(40 * scale_factor)  # Увеличиваем высоту, чтобы включить имя
                    )
                    
                    # Если клик был в этом прямоугольнике, выбираем персонажа
                    if button_rect.collidepoint(mouse_pos):
                        selected_character = character
        except Exception as e:
            print(f"Ошибка при обработке выбора персонажа: {e}")
    
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            click_pos = Vector2(event.pos) if event.type == pygame.MOUSEBUTTONDOWN else Vector2(event.x * viewport.width, event.y * viewport.height)
            
            for button in main_menu_buttons:
                button.update(mouse_pos)
                if button.is_hovered(click_pos):
                    if button.text == "Играть":
                        # Переходим к экрану выбора уровня
                        current_menu = ["level_select", None]
                    elif button.text == "Настройки":
                        current_menu = ["settings", "main"]
                    elif button.text == "Выход":
                        pygame.quit()
                        sys.exit()
    
    # Обновляем состояние кнопок
    for button in main_menu_buttons:
        if button.text != "Сменить персонажа":  # Убираем кнопку "Сменить персонажа", так как теперь выбор через превью
            button.update(mouse_pos)

def handle_settings_menu(events, mouse_pos, mouse_pressed):
    """Обрабатывает события в меню настроек"""
    global current_menu
    
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            click_pos = Vector2(event.pos) if event.type == pygame.MOUSEBUTTONDOWN else Vector2(event.x * viewport.width, event.y * viewport.height)
            
            for element in settings_menu_elements:
                if isinstance(element, Button) and element.is_hovered(click_pos):
                    if element.text == "Назад":
                        current_menu = ["main", None]
    
    # Обновляем состояние элементов интерфейса
    for element in settings_menu_elements:
        if isinstance(element, Slider):
            element.update(mouse_pos, mouse_pressed)
        elif isinstance(element, Button):
            element.update(mouse_pos)

def draw_main_menu(screen):
    """Отрисовывает главное меню"""
    global selected_character
    
    # Очищаем экран
    screen.fill((0, 0, 0))
    
    # Получаем текущую позицию мыши
    mouse_pos = pygame.mouse.get_pos()
    
    # Отрисовываем фон меню
    if menu_background:
        screen.blit(menu_background, (int(offset.x), int(offset.y)))
    elif title_background:
        # Если у нас нет специального фона для меню, используем title_background
        scaled_bg = pygame.transform.scale(
            title_background, 
            (int(viewport.width), int(viewport.height))
        )
        screen.blit(scaled_bg, (int(offset.x), int(offset.y)))
    
    # Отрисовываем заголовок игры
    if font:
        title_font = pygame.font.Font('src/Resources/pixel_font.ttf', int(52 * scale_factor)) if os.path.exists('src/Resources/pixel_font.ttf') else pygame.font.SysFont('monospace', int(52 * scale_factor))
        title = title_font.render("Зеленая Зона", True, (0, 255, 100))
        title_rect = title.get_rect(
            centerx=viewport.centerx,
            top=int(offset.y + 50 * scale_factor)  # Немного подняли заголовок
        )
        screen.blit(title, title_rect)
        
        subtitle = title_font.render("Пиксельный Платформер", True, (0, 200, 100))
        subtitle_rect = subtitle.get_rect(
            centerx=viewport.centerx,
            top=title_rect.bottom + int(20 * scale_factor)
        )
        screen.blit(subtitle, subtitle_rect)
        
        # Сначала отрисовываем кнопки меню, подняв их выше
        buttons_start_y = subtitle_rect.bottom + int(40 * scale_factor)
    else:
        buttons_start_y = int(viewport.height * 0.25)  # Подняли кнопки выше
    
    # Обновляем позиции кнопок и отрисовываем их
    button_spacing = int(80 * scale_factor)  # Увеличили расстояние между кнопками
    
    for i, button in enumerate(main_menu_buttons):
        button.rect.centerx = viewport.centerx
        button.rect.y = buttons_start_y + i * button_spacing
    
    # Отрисовываем кнопки меню
    for button in main_menu_buttons:
        if button.text != "Сменить персонажа":  # Убираем кнопку "Сменить персонажа", так как теперь выбор через превью
            button.draw(screen)
    
    # Теперь отображаем блок выбора персонажа под кнопками
    if font:
        character_block_top = buttons_start_y + len(main_menu_buttons) * button_spacing + int(40 * scale_factor)
        character_font = pygame.font.Font('src/Resources/pixel_font.ttf', int(36 * scale_factor)) if os.path.exists('src/Resources/pixel_font.ttf') else pygame.font.SysFont('monospace', int(36 * scale_factor))
        
        char_select_text = character_font.render("Выберите персонажа:", True, (255, 255, 255))
        char_select_rect = char_select_text.get_rect(
            centerx=viewport.centerx,
            top=character_block_top
        )
        screen.blit(char_select_text, char_select_rect)
        
        # Отображаем все превью персонажей в ряд
        preview_top = char_select_rect.bottom + int(30 * scale_factor)
        preview_size = int(100 * scale_factor)
        spacing = int(20 * scale_factor)
        total_width = len(CHARACTERS) * preview_size + (len(CHARACTERS) - 1) * spacing
        
        start_x = viewport.centerx - total_width / 2
        
        for i, character in enumerate(CHARACTERS):
            # Позиция для текущего превью
            preview_x = start_x + i * (preview_size + spacing)
            preview_y = preview_top
            
            # Получаем превью персонажа
            preview_data = character_preview_images.get(character)
            
            if preview_data:
                # Проверяем, является ли превью анимированным
                if isinstance(preview_data, dict) and preview_data.get('animated'):
                    # Обновляем анимацию превью с постоянной скоростью
                    now = pygame.time.get_ticks()
                    
                    if now - preview_data['last_update'] > preview_data['frame_rate']:
                        preview_data['current_frame'] = (preview_data['current_frame'] + 1) % preview_data['frames_count']
                        preview_data['last_update'] = now
                    
                    # Извлекаем текущий кадр анимации
                    frame_rect = pygame.Rect(
                        preview_data['current_frame'] * preview_data['frame_width'], 
                        0, 
                        preview_data['frame_width'], 
                        preview_data['frame_height']
                    )
                    current_frame = preview_data['sprite_sheet'].subsurface(frame_rect).copy()
                    
                    # Масштабируем текущий кадр
                    scale_multiplier = 4
                    preview_image = pygame.transform.scale(current_frame, (preview_data['frame_width'] * scale_multiplier, preview_data['frame_height'] * scale_multiplier))
                    
                    # Добавляем рамку
                    pygame.draw.rect(preview_image, (255, 255, 255), preview_image.get_rect(), 2)
                else:
                    # Статичное превью
                    preview_image = preview_data
                
                # Масштабируем превью до нужного размера
                aspect_ratio = preview_image.get_width() / preview_image.get_height()
                preview_height = preview_size
                preview_width = int(preview_height * aspect_ratio)
                scaled_preview = pygame.transform.scale(preview_image, (preview_width, preview_height))
                
                # Позиция для отрисовки превью
                preview_rect = scaled_preview.get_rect(
                    centerx=preview_x + preview_size / 2,
                    top=preview_y
                )
                
                # Если это выбранный персонаж, рисуем вокруг него подсветку
                if character == selected_character:
                    # Рисуем подсветку вокруг выбранного персонажа
                    highlight_rect = pygame.Rect(
                        preview_rect.x - int(5 * scale_factor),
                        preview_rect.y - int(5 * scale_factor),
                        preview_rect.width + int(10 * scale_factor),
                        preview_rect.height + int(10 * scale_factor)
                    )
                    pygame.draw.rect(screen, (0, 255, 0), highlight_rect, width=int(3 * scale_factor), border_radius=int(5 * scale_factor))
                
                # Отрисовываем превью
                screen.blit(scaled_preview, preview_rect)
                
                # Отрисовываем имя персонажа под превью
                small_font = pygame.font.Font('src/Resources/pixel_font.ttf', int(18 * scale_factor)) if os.path.exists('src/Resources/pixel_font.ttf') else pygame.font.SysFont('monospace', int(18 * scale_factor))
                display_name = CHARACTER_NAMES.get(character, character)
                name_text = small_font.render(display_name, True, (255, 255, 255))
                name_rect = name_text.get_rect(
                    centerx=preview_rect.centerx,
                    top=preview_rect.bottom + int(10 * scale_factor)
                )
                screen.blit(name_text, name_rect)
                
                # Добавляем кнопку для выбора персонажа (кликабельная область)
                char_button_rect = pygame.Rect(
                    preview_rect.x - int(5 * scale_factor),
                    preview_rect.y - int(5 * scale_factor),
                    preview_rect.width + int(10 * scale_factor),
                    name_rect.bottom - preview_rect.top + int(10 * scale_factor)
                )
                
                # Проверяем, наведена ли мышь на этого персонажа
                if char_button_rect.collidepoint(mouse_pos):
                    # Добавляем обводку при наведении
                    pygame.draw.rect(screen, (200, 200, 200), char_button_rect, width=int(2 * scale_factor), border_radius=int(5 * scale_factor))
                    
                    # Если кликнули на персонажа, выбираем его
                    if pygame.mouse.get_pressed()[0]:
                        selected_character = character
        
        # Отображаем информацию о выбранном персонаже
        info_top = preview_top + preview_size + int(60 * scale_factor)
        
        # Имя персонажа
        display_name = CHARACTER_NAMES.get(selected_character, selected_character)
        selected_name_text = character_font.render(f"Выбран: {display_name}", True, (255, 255, 255))
        selected_name_rect = selected_name_text.get_rect(
            centerx=viewport.centerx,
            top=info_top
        )
        screen.blit(selected_name_text, selected_name_rect)
        
        # Описание персонажа
        description = CHARACTER_DESCRIPTIONS.get(selected_character, "")
        if description:
            description_font = pygame.font.Font('src/Resources/pixel_font.ttf', int(24 * scale_factor)) if os.path.exists('src/Resources/pixel_font.ttf') else pygame.font.SysFont('monospace', int(24 * scale_factor))
            description_text = description_font.render(description, True, (200, 200, 200))
            description_rect = description_text.get_rect(
                centerx=viewport.centerx,
                top=selected_name_rect.bottom + int(10 * scale_factor)
            )
            screen.blit(description_text, description_rect)


def draw_settings_menu(screen):
    """Отрисовывает меню настроек"""
    # Очищаем экран
    screen.fill((0, 0, 0))
    
    # Отрисовываем фон меню
    if current_menu[1] == "game" or current_menu[1] == "pause":
        # Если пришли из игры или паузы, используем фон уровня
        if level_background_blurred:
            screen.blit(level_background_blurred, (int(offset.x), int(offset.y)))
    else:
        # Если пришли из главного меню, используем фон меню
        if menu_background:
            screen.blit(menu_background, (int(offset.x), int(offset.y)))
    
    # Отрисовываем заголовок меню настроек
    if font:
        title_font = pygame.font.Font('src/Resources/pixel_font.ttf', int(60 * scale_factor)) if os.path.exists('src/Resources/pixel_font.ttf') else pygame.font.SysFont('monospace', int(60 * scale_factor))
        title = title_font.render("Настройки", True, (255, 255, 255))
        title_rect = title.get_rect(
            centerx=viewport.centerx,
            top=int(offset.y + 100 * scale_factor)
        )
        screen.blit(title, title_rect)
    
    # Отрисовываем элементы меню настроек
    for element in settings_menu_elements:
        element.draw(screen)

if platform.system() == "Emscripten":
    # Для запуска в браузере
    asyncio.ensure_future(main())
else:
    # Для запуска на настольной платформе
    if __name__ == "__main__":
        asyncio.run(main()) 