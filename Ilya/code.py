import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH = 1920
HEIGHT = 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Главное меню - Пиксельный платформер")

# Цвета
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)

# Загрузка фонового изображения
try:
    background = pygame.image.load('main-background.png')  # Замените 'background.png' на путь к вашему изображению
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))  # Масштабирование под размер окна
except:
    background = None  # Если изображение не удалось загрузить, фон будет черным

# Загрузка пиксельного шрифта (замените 'pixel_font.ttf' на путь к вашему шрифту)
try:
    font = pygame.font.Font('Bloq.ttf', 48)  # Размер шрифта можно настроить
except:
    font = pygame.font.SysFont('monospace', 48)  # Резервный шрифт, если файл не найден

# Класс для кнопок
class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = WHITE
        self.hover_color = GRAY
        self.current_color = self.color

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, 2)  # Отрисовка рамки кнопки
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def update(self, mouse_pos):
        if self.is_hovered(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

# Создание кнопок
button_width = 300
button_height = 80
button_spacing = 20

play_button = Button("Играть", (WIDTH // 2 - button_width // 2), HEIGHT // 2 - button_height - button_spacing, button_width, button_height)
settings_button = Button("Настройки", (WIDTH // 2 - button_width // 2), HEIGHT // 2, button_width, button_height)
exit_button = Button("Выход", (WIDTH // 2 - button_width // 2), HEIGHT // 2 + button_height + button_spacing, button_width, button_height)

buttons = [play_button, settings_button, exit_button]

# Основной цикл
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_button.is_hovered(mouse_pos):
                print("Запуск игры!")  # Здесь можно добавить переход к игре
            elif settings_button.is_hovered(mouse_pos):
                print("Открытие настроек!")  # Здесь можно добавить переход к настройкам
            elif exit_button.is_hovered(mouse_pos):
                running = False

    # Обновление состояния кнопок
    for button in buttons:
        button.update(mouse_pos)

    # Отрисовка
    if background:  # Если фоновое изображение загружено, отрисовываем его
        screen.blit(background, (0, 0))
    else:  # Иначе заливаем фон черным
        screen.fill(BLACK)

    for button in buttons:
        button.draw(screen)

    pygame.display.flip()

# Завершение
pygame.quit()
sys.exit()