import pygame
import sys
import os


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_font(size):
    fullname = os.path.join('data', 'font/PressStart2P-Regular.ttf')
    if not os.path.isfile(fullname):
        print(f"Файл с шрифтом '{fullname}' не найден")
        sys.exit()
    font = pygame.font.Font(fullname, size)
    return font


def terminate():
    pygame.quit()
    sys.exit()


def start_screen(screen_size):
    global FPS
    size = 600, 400
    screen = pygame.display.set_mode(size)
    pygame.display.set_icon(load_image('image/icon.jpg'))
    pygame.display.set_caption('AstroBlast')
    fon = pygame.transform.scale(load_image('image/screen_saver/background.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    # Название игры
    font = load_font(20)
    string_rendered = font.render("AstroBlast", 1, pygame.Color('White'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top, intro_rect.x = 80, 200
    screen.blit(string_rendered, intro_rect)
    # Уровни
    font = load_font(16)
    for x, text in zip((100, 350), ("Уровень 1", "Уровень 2")):
        string_rendered = font.render(text, 1, pygame.Color('White'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top, intro_rect.x = 200, x
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('')
    size = width, height = 600, 900
    screen = pygame.display.set_mode(size)
    FPS, clock, running = 50, pygame.time.Clock(), True
    start_screen((600, 400))
    # while running:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
    #     rect = pygame.Rect(250, height - 90, 50, 90)
    #     rect1 = pygame.Rect(100, 100, 40, 40)
    #     pygame.draw.rect(screen, (255, 0, 255), rect)
    #     pygame.draw.rect(screen, (255, 0, 0), rect1)
    #     pygame.display.flip()
    #     clock.tick(fps)
    # pygame.quit()
