import os
import sys

import pygame


def load_image(name, colorkey=None):
    fullname = os.path.join('data/image', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_music(type):
    fullname = os.path.join('data/music', type)
    if not os.path.isfile(fullname):
        print(f"Файл с музыкой '{fullname}' не найден")
        sys.exit()
    return fullname


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
    screen = pygame.display.set_mode(screen_size)
    # Музыка
    pygame.mixer.init()
    pygame.mixer.music.load(load_music('start music background.mp3'))
    pygame.mixer.music.set_volume(0.15)
    pygame.mixer.music.play(loops=-1, fade_ms=6 * 1000)
    pygame.display.set_icon(load_image('icon.jpg'))  # Загрузка исконки
    pygame.display.set_caption('AstroBlast')  # Загрузка названия
    fon = pygame.transform.scale(load_image('screen_saver/background.jpg'), screen_size)  # Загрузка шрифта
    screen.blit(fon, (0, 0))
    # Название игры
    font = load_font(20)
    # Название игры на экране
    string_rendered = font.render("AstroBlast", 1, pygame.Color('White'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top, intro_rect.x = 80, 200
    screen.blit(string_rendered, intro_rect)
    # текст с выбором уровня на экране
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 94 <= event.pos[0] <= 246 and 194 <= event.pos[1] <= 217:  # Окрытие уровня 1
                    level_one()
                elif 342 <= event.pos[0] <= 500 and 194 <= event.pos[1] <= 217:  # Открытие уровня 2
                    level_two()
        pygame.display.flip()
        clock.tick(FPS)


def level_one():
    print('WIP: level_one')


def level_two():
    print('WIP: level_two')


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('')
    FPS, clock = 50, pygame.time.Clock()
    start_screen((600, 400))
