import os
import sys

import pygame

# Константы
SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL = 600, 900
FPS, CLOCK, SCROLL_SPEED = 60, pygame.time.Clock(), 0.4


class BackgroundManager:
    def __init__(self, screen, backgrounds):
        self.screen, self.backgrounds = screen, backgrounds
        self.bg_count = len(backgrounds)
        self.y_offsets = [i * SCREEN_HEIGHT_LEVEL for i in range(self.bg_count)]  # Смещение для каждого фона

    def update_and_draw(self):
        # Двигаем фоны вниз
        for i in range(self.bg_count):
            self.y_offsets[i] += SCROLL_SPEED
            # Если фон уходит вниз, сбрасываем его на верхнюю позицию
            if self.y_offsets[i] >= SCREEN_HEIGHT_LEVEL:
                self.y_offsets[i] = (self.y_offsets[i] - SCREEN_HEIGHT_LEVEL * self.bg_count)
        # Очищаем экран перед новой отрисовкой
        self.screen.fill((0, 0, 0))  # Черный фон
        # Отображаем фоны
        for i in range(self.bg_count):
            self.screen.blit(self.backgrounds[i], (0, self.y_offsets[i]))


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
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    # Музыка
    pygame.mixer.init()
    pygame.mixer.music.load(load_music('start music background.mp3'))
    pygame.mixer.music.set_volume(0.15)
    pygame.mixer.music.play(loops=-1, fade_ms=3 * 1000)
    pygame.display.set_icon(load_image('icon.jpg'))
    pygame.display.set_caption('AstroBlast')
    fon = pygame.transform.scale(load_image('backgrounds image/first_screen_background.jpg'), screen_size)
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 94 <= event.pos[0] <= 246 and 194 <= event.pos[1] <= 217:  # Окрытие уровня 1
                    level_one()
                elif 342 <= event.pos[0] <= 500 and 194 <= event.pos[1] <= 217:  # Открытие уровня 2
                    level_two()
        pygame.display.flip()
        CLOCK.tick(FPS)


def level_one():
    global CLOCK
    # Инициализируем Pygame
    pygame.init()
    # Создаем окно
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (0, 0)
    os.environ['SDL_VIDEO_CENTERED'] = '0'

    screen = pygame.display.set_mode((SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))
    # Загружаем фоны
    backgrounds = []
    for i in range(1, 10):  # Предполагаем, что у вас есть 9 изображений
        filename = f'data/image/backgrounds image/level 1/Space Background ({i}).png'
        bg = pygame.transform.scale(pygame.image.load(filename), (SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))
        backgrounds.append(bg)
    # Создаем объект менеджера фонов
    background_manager = BackgroundManager(screen, backgrounds)
    # Основной игровой цикл
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        background_manager.update_and_draw()  # Обновляем и отрисовываем фон
        pygame.display.flip()  # Обновляем дисплей
        CLOCK.tick(240)  # Ограничиваем FPS до 60 кадров в секунду


def level_two():
    print('WIP: level_two')


if __name__ == '__main__':
    start_screen((600, 400))
