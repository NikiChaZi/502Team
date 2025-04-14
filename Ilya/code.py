import pygame
import sys
pygame.init()

WIDTH = 1920
HEIGHT = 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Главное меню - Пиксельный платформер")

WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)

try:
    background = pygame.image.load('main-background.png')
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    background = None

try:
    font = pygame.font.Font('Bloq.ttf', 48)
except:
    font = pygame.font.SysFont('monospace', 48)
class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = WHITE
        self.hover_color = GRAY
        self.current_color = self.color

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, 2)
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
button_width = 300
button_height = 80
button_spacing = 20

play_button = Button("Играть", (WIDTH // 2 - button_width // 2), HEIGHT // 2 - button_height - button_spacing, button_width, button_height)
settings_button = Button("Настройки", (WIDTH // 2 - button_width // 2), HEIGHT // 2, button_width, button_height)
exit_button = Button("Выход", (WIDTH // 2 - button_width // 2), HEIGHT // 2 + button_height + button_spacing, button_width, button_height)

buttons = [play_button, settings_button, exit_button]
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_button.is_hovered(mouse_pos):
                print("Запуск игры!")
            elif settings_button.is_hovered(mouse_pos):
                print("Открытие настроек!")
            elif exit_button.is_hovered(mouse_pos):
                running = False
    for button in buttons:
        button.update(mouse_pos)
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BLACK)
    for button in buttons:
        button.draw(screen)
    pygame.display.flip()
pygame.quit()
sys.exit()