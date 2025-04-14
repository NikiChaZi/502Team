import pygame
import sys

# Инициализация Pygame для работы с графикой и звуком
pygame.init()

# Базовые размеры разрешения для масштабирования интерфейса (используются как эталон)
BASE_WIDTH = 1920
BASE_HEIGHT = 1080

# Текущие размеры окна игры, могут меняться при выборе разрешения
WIDTH = 1920
HEIGHT = 1080

# Создание окна игры с заданным разрешением и заголовком
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Главное меню - Пиксельный платформер")

# Определение цветов в формате RGB
WHITE = (255, 255, 255)  # Белый цвет для текста и элементов
GRAY = (150, 150, 150)   # Серый цвет для выделения при наведении
BLACK = (0, 0, 0)        # Черный цвет для заливки экрана, если фон не загружен

# Функция для масштабирования фонового изображения до размеров окна
def scale_background(image, target_width, target_height):
    if image is None:
        return None  # Возвращаем None, если изображение не загружено
    # Масштабируем изображение до размеров окна, игнорируя соотношение сторон
    scaled_image = pygame.transform.scale(image, (target_width, target_height))
    return scaled_image

# Загрузка и масштабирование фонового изображения
try:
    background = pygame.image.load('src/Assets/background.png')  # Загружаем фоновое изображение
    background = scale_background(background, WIDTH, HEIGHT)  # Масштабируем фон до размеров окна
except Exception as e:
    print(f"Ошибка загрузки фона: {e}")  # Выводим сообщение об ошибке, если фон не загружается
    background = None  # Если загрузка не удалась, фон будет None

# Загрузка и воспроизведение фоновой музыки
try:
    pygame.mixer.music.load('src/Resources/background_music.mp3')  # Загружаем музыкальный файл
    pygame.mixer.music.set_volume(0.5)  # Устанавливаем громкость 50%
    pygame.mixer.music.play(-1)  # Зацикливаем воспроизведение музыки
except:
    print("Не удалось загрузить фоновую музыку")  # Сообщение об ошибке, если музыка не загрузилась

# Функция для получения масштабированного шрифта в зависимости от разрешения
def get_scaled_font():
    scale = min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)  # Вычисляем масштаб относительно базового разрешения
    font_size = int(48 * scale)  # Масштабируем размер шрифта (базовый размер 48)
    try:
        return pygame.font.Font('src/Resources/pixel_font.ttf', font_size)  # Пытаемся загрузить пиксельный шрифт
    except:
        return pygame.font.SysFont('monospace', font_size)  # Если не удалось, используем системный шрифт

# Инициализация шрифта с учетом текущего разрешения
font = get_scaled_font()

# Класс для кнопок меню
class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text  # Текст кнопки
        self.update_rect(x, y, width, height)  # Обновляем размеры и позицию кнопки
        self.color = WHITE  # Цвет текста кнопки
        self.hover_color = GRAY  # Цвет текста при наведении
        self.current_color = self.color  # Текущий цвет текста

    # Метод для обновления размеров и позиции кнопки с учетом масштаба
    def update_rect(self, x, y, width, height):
        scale_x = WIDTH / BASE_WIDTH  # Масштаб по оси X
        scale_y = HEIGHT / BASE_HEIGHT  # Масштаб по оси Y
        self.rect = pygame.Rect(x * scale_x, y * scale_y, width * scale_x, height * scale_y)  # Масштабируем прямоугольник кнопки

    # Метод для отрисовки кнопки на экране
    def draw(self, surface):
        text_surface = font.render(self.text, True, self.current_color)  # Создаем поверхность с текстом
        text_rect = text_surface.get_rect(center=self.rect.center)  # Центрируем текст внутри кнопки
        surface.blit(text_surface, text_rect)  # Отрисовываем текст на экране

    # Метод для проверки, наведен ли курсор на кнопку
    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)  # Возвращаем True, если курсор над кнопкой

    # Метод для обновления состояния кнопки (например, изменение цвета при наведении)
    def update(self, mouse_pos):
        if self.is_hovered(mouse_pos):
            self.current_color = self.hover_color  # Меняем цвет на серый при наведении
        else:
            self.current_color = self.color  # Возвращаем белый цвет, если курсор не над кнопкой

# Класс для ползунка громкости
class Slider:
    def __init__(self, label, x, y, width, height, min_val, max_val, initial_val):
        self.label = label  # Название настройки (например, "Громкость")
        self.min_val = min_val  # Минимальное значение ползунка (0)
        self.max_val = max_val  # Максимальное значение ползунка (100)
        self.value = initial_val  # Начальное значение ползунка
        self.update_rect(x, y, width, height)  # Обновляем размеры и позицию ползунка

    # Метод для обновления размеров и позиции ползунка с учетом масштаба
    def update_rect(self, x, y, width, height):
        scale_x = WIDTH / BASE_WIDTH  # Масштаб по оси X
        scale_y = HEIGHT / BASE_HEIGHT  # Масштаб по оси Y
        self.rect = pygame.Rect(x * scale_x, y * scale_y, width * scale_x, height * scale_y)  # Масштабируем прямоугольник ползунка
        self.handle_rect = pygame.Rect(self.rect.x + (self.value / self.max_val) * self.rect.width - 10 * scale_x, self.rect.y - 10 * scale_y, 20 * scale_x, 40 * scale_y)  # Масштабируем ручку ползунка

    # Метод для отрисовки ползунка на экране
    def draw(self, surface):
        scale_x = WIDTH / BASE_WIDTH  # Масштаб по оси X
        scale_y = HEIGHT / BASE_HEIGHT  # Масштаб по оси Y
        label_surface = font.render(self.label, True, WHITE)  # Создаем поверхность с названием настройки
        surface.blit(label_surface, (self.rect.x - 350 * scale_x, self.rect.y - 10 * scale_y))  # Отрисовываем название слева от ползунка
        pygame.draw.rect(surface, WHITE, self.rect, int(2 * scale_x))  # Рисуем рамку ползунка
        pygame.draw.rect(surface, GRAY, self.handle_rect)  # Рисуем ручку ползунка
        text_surface = font.render(f"{int(self.value)}%", True, WHITE)  # Создаем поверхность с текущим значением громкости
        surface.blit(text_surface, (self.rect.x + self.rect.width + 20 * scale_x, self.rect.y - 10 * scale_y))  # Отрисовываем значение справа от ползунка

    # Метод для обновления значения ползунка при перемещении
    def update(self, mouse_pos, mouse_pressed):
        scale_x = WIDTH / BASE_WIDTH  # Масштаб по оси X
        if mouse_pressed and self.rect.collidepoint(mouse_pos):  # Если мышь нажата и курсор над ползунком
            self.handle_rect.x = max(self.rect.x, min(mouse_pos[0] - 10 * scale_x, self.rect.x + self.rect.width - 20 * scale_x))  # Ограничиваем движение ручки ползунка
            if self.handle_rect.x <= self.rect.x:  # Если ручка в крайнем левом положении
                self.value = self.min_val  # Устанавливаем минимальное значение (0%)
            elif self.handle_rect.x >= self.rect.x + self.rect.width - 20 * scale_x:  # Если ручка в крайнем правом положении
                self.value = self.max_val  # Устанавливаем максимальное значение (100%)
            else:
                position_ratio = (self.handle_rect.x - self.rect.x) / (self.rect.width - 20 * scale_x)  # Вычисляем пропорцию положения ручки
                self.value = self.min_val + position_ratio * (self.max_val - self.min_val)  # Вычисляем новое значение громкости
            pygame.mixer.music.set_volume(self.value / 100)  # Устанавливаем громкость музыки

# Класс для настроек с выбором значения (например, разрешение)
class Option:
    def __init__(self, label, x, y, width, values, default_index):
        self.label = label  # Название настройки (например, "Разрешение")
        self.values = values  # Список возможных значений (например, ["1920x1080", "1280x720", "800x600"])
        self.current_index = default_index  # Текущий индекс выбранного значения
        self.update_rect(x, y, width)  # Обновляем размеры и позицию элемента

    # Метод для обновления размеров и позиции элемента с учетом масштаба
    def update_rect(self, x, y, width):
        scale_x = WIDTH / BASE_WIDTH  # Масштаб по оси X
        scale_y = HEIGHT / BASE_HEIGHT  # Масштаб по оси Y
        self.x = x * scale_x  # Масштабируем координату X
        self.y = y * scale_y  # Масштабируем координату Y
        self.width = width * scale_x  # Масштабируем ширину
        self.left_arrow_rect = pygame.Rect(self.x - 100 * scale_x, self.y, 50 * scale_x, 50 * scale_y)  # Масштабируем область левой стрелки
        self.right_arrow_rect = pygame.Rect(self.x + self.width + 50 * scale_x, self.y, 50 * scale_x, 50 * scale_y)  # Масштабируем область правой стрелки

    # Метод для отрисовки элемента на экране
    def draw(self, surface):
        scale_x = WIDTH / BASE_WIDTH  # Масштаб по оси X
        scale_y = HEIGHT / BASE_HEIGHT  # Масштаб по оси Y
        label_surface = font.render(self.label, True, WHITE)  # Создаем поверхность с названием настройки
        surface.blit(label_surface, (self.x - 400 * scale_x, self.y + 5 * scale_y))  # Отрисовываем название слева от значения
        value_surface = font.render(str(self.values[self.current_index]), True, WHITE)  # Создаем поверхность с текущим значением
        surface.blit(value_surface, (self.x, self.y + 5 * scale_y))  # Отрисовываем значение
        surface.blit(font.render("<", True, WHITE), (self.left_arrow_rect.x, self.left_arrow_rect.y + 5 * scale_y))  # Отрисовываем левую стрелку
        surface.blit(font.render(">", True, WHITE), (self.right_arrow_rect.x, self.right_arrow_rect.y + 5 * scale_y))  # Отрисовываем правую стрелку

    # Метод для обновления состояния элемента (переключение значений)
    def update(self, mouse_pos, mouse_pressed):
        if mouse_pressed:  # Если мышь нажата
            if self.left_arrow_rect.collidepoint(mouse_pos) and self.current_index > 0:  # Если нажата левая стрелка и есть предыдущее значение
                self.current_index -= 1  # Уменьшаем индекс значения
                self.apply()  # Применяем новое значение
            elif self.right_arrow_rect.collidepoint(mouse_pos) and self.current_index < len(self.values) - 1:  # Если нажата правая стрелка и есть следующее значение
                self.current_index += 1  # Увеличиваем индекс значения
                self.apply()  # Применяем новое значение

    # Метод для применения выбранного значения
    def apply(self):
        global WIDTH, HEIGHT, screen, background, main_menu_buttons, settings_menu_elements, font
        if self.label == "Разрешение":  # Если настройка - это разрешение
            res = self.values[self.current_index].split("x")  # Разбиваем строку разрешения на ширину и высоту
            new_width, new_height = int(res[0]), int(res[1])  # Преобразуем в числа
            if new_width != WIDTH or new_height != HEIGHT:  # Если новое разрешение отличается от текущего
                WIDTH, HEIGHT = new_width, new_height  # Обновляем глобальные переменные разрешения
                screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Устанавливаем новое разрешение окна
                try:
                    # Заново загружаем и масштабируем фон для нового разрешения
                    background = scale_background(pygame.image.load('src/Assets/background.png'), WIDTH, HEIGHT)
                except Exception as e:
                    print(f"Ошибка обновления фона: {e}")  # Выводим сообщение об ошибке
                    background = None  # Если не удалось обновить фон, устанавливаем None
                font = get_scaled_font()  # Обновляем шрифт с учетом нового масштаба
                button_width = 300  # Ширина кнопок
                button_height = 80  # Высота кнопок
                button_spacing = 20  # Расстояние между кнопками
                # Создаем новые кнопки главного меню с учетом базового разрешения
                play_button = Button("Играть", BASE_WIDTH // 2 - button_width // 2, BASE_HEIGHT // 2 - button_height - button_spacing, button_width, button_height)
                settings_button = Button("Настройки", BASE_WIDTH // 2 - button_width // 2, BASE_HEIGHT // 2, button_width, button_height)
                exit_button = Button("Выход", BASE_WIDTH // 2 - button_width // 2, BASE_HEIGHT // 2 + button_height + button_spacing, button_width, button_height)
                main_menu_buttons.clear()  # Очищаем старый список кнопок
                main_menu_buttons.extend([play_button, settings_button, exit_button])  # Добавляем новые кнопки
                # Создаем новые элементы меню настроек
                volume_slider_new = Slider("Громкость", BASE_WIDTH // 2 + 0, BASE_HEIGHT // 2 - 80, 300, 20, 0, 100, settings_menu_elements[0].value)
                resolution_option_new = Option("Разрешение", BASE_WIDTH // 2 + 50, BASE_HEIGHT // 2, 300, resolutions, self.current_index)
                back_button_new = Button("Назад", BASE_WIDTH // 2 - button_width // 2, BASE_HEIGHT // 2 + 160, button_width, button_height)
                settings_menu_elements.clear()  # Очищаем старый список элементов настроек
                settings_menu_elements.extend([volume_slider_new, resolution_option_new, back_button_new])  # Добавляем новые элементы

# Определение базовых размеров кнопок и расстояния между ними
button_width = 300
button_height = 80
button_spacing = 20

# Создание кнопок главного меню
play_button = Button("Играть", BASE_WIDTH // 2 - button_width // 2, BASE_HEIGHT // 2 - button_height - button_spacing, button_width, button_height)
settings_button = Button("Настройки", BASE_WIDTH // 2 - button_width // 2, BASE_HEIGHT // 2, button_width, button_height)
exit_button = Button("Выход", BASE_WIDTH // 2 - button_width // 2, BASE_HEIGHT // 2 + button_height + button_spacing, button_width, button_height)

# Список кнопок главного меню
main_menu_buttons = [play_button, settings_button, exit_button]

# Создание ползунка громкости
volume_slider = Slider("Громкость", BASE_WIDTH // 2 + 0, BASE_HEIGHT // 2 - 80, 300, 20, 0, 100, 50)

# Список доступных разрешений для выбора
resolutions = ["1920x1080", "1280x720", "800x600"]
# Создание элемента выбора разрешения
resolution_option = Option("Разрешение", BASE_WIDTH // 2 + 50, BASE_HEIGHT // 2, 300, resolutions, 0)

# Создание кнопки "Назад" для меню настроек
back_button = Button("Назад", BASE_WIDTH // 2 - button_width // 2, BASE_HEIGHT // 2 + 160, button_width, button_height)

# Список элементов меню настроек
settings_menu_elements = [volume_slider, resolution_option, back_button]

# Переменная для отслеживания текущего меню (главное меню или настройки)
current_menu = "main"

# Основной игровой цикл
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()  # Получаем текущую позицию курсора мыши
    mouse_pressed = pygame.mouse.get_pressed()[0]  # Проверяем, нажата ли левая кнопка мыши

    # Обработка событий Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Если пользователь закрыл окно
            running = False  # Завершаем цикл

        if current_menu == "main":  # Если текущее меню - главное
            if event.type == pygame.MOUSEBUTTONDOWN:  # Если нажата кнопка мыши
                # Используем текущие кнопки из списка main_menu_buttons
                play_button_current = main_menu_buttons[0]  # Кнопка "Играть" - первый элемент
                settings_button_current = main_menu_buttons[1]  # Кнопка "Настройки" - второй элемент
                exit_button_current = main_menu_buttons[2]  # Кнопка "Выход" - третий элемент
                if play_button_current.is_hovered(mouse_pos):  # Если нажата кнопка "Играть"
                    print("Запуск игры!")  # Выводим сообщение (заглушка для запуска игры)
                elif settings_button_current.is_hovered(mouse_pos):  # Если нажата кнопка "Настройки"
                    current_menu = "settings"  # Переходим в меню настроек
                elif exit_button_current.is_hovered(mouse_pos):  # Если нажата кнопка "Выход"
                    running = False  # Завершаем цикл

        elif current_menu == "settings":  # Если текущее меню - настройки
            if event.type == pygame.MOUSEBUTTONDOWN:  # Если нажата кнопка мыши
                # Находим текущую кнопку "Назад" в списке settings_menu_elements (последний элемент - кнопка "Назад")
                back_button_current = settings_menu_elements[-1]
                if back_button_current.is_hovered(mouse_pos):  # Если нажата кнопка "Назад"
                    current_menu = "main"  # Возвращаемся в главное меню

    # Обновление состояния элементов в зависимости от текущего меню
    if current_menu == "main":  # Если текущее меню - главное
        for button in main_menu_buttons:  # Обновляем состояние каждой кнопки
            button.update(mouse_pos)
    elif current_menu == "settings":  # Если текущее меню - настройки
        for element in settings_menu_elements:  # Обновляем состояние каждого элемента
            if isinstance(element, Slider):  # Если элемент - ползунок
                element.update(mouse_pos, mouse_pressed)
            elif isinstance(element, Option):  # Если элемент - выбор значения
                element.update(mouse_pos, mouse_pressed)
            else:  # Если элемент - кнопка
                element.update(mouse_pos)

    # Отрисовка фона
    if background:
        screen.blit(background, (0, 0))  # Отрисовываем фон, растянутый на всё окно
    else:
        screen.fill(BLACK)  # Если фона нет, заливаем экран черным цветом

    # Отрисовка элементов текущего меню
    if current_menu == "main":  # Если текущее меню - главное
        for button in main_menu_buttons:  # Отрисовываем кнопки главного меню
            button.draw(screen)
    elif current_menu == "settings":  # Если текущее меню - настройки
        for element in settings_menu_elements:  # Отрисовываем элементы меню настроек
            element.draw(screen)

    # Обновление экрана для отображения изменений
    pygame.display.flip()

# Завершение работы Pygame и программы
pygame.quit()
sys.exit()