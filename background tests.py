# import os
# import sys
#
# import pygame
#
# # Константы
# SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL = 600, 900
# FPS, CLOCK, SCROLL_SPEED = 60, pygame.time.Clock(), 0.4
#
#
# class AnimatedSprite(pygame.sprite.Sprite):
#     def __init__(self, sheet, columns, rows, x, y):
#         super().__init__()
#         self.frames = []
#         self.cut_sheet(sheet, columns, rows)
#         self.cur_frame = 0
#         self.image = self.frames[self.cur_frame]
#         self.rect = self.image.get_rect(topleft=(x, y))
#
#     def cut_sheet(self, sheet, columns, rows):
#         frame_width = sheet.get_width() // columns
#         frame_height = sheet.get_height() // rows
#         for j in range(rows):
#             for i in range(columns):
#                 frame_location = (frame_width * i, frame_height * j)
#                 self.frames.append(sheet.subsurface(pygame.Rect(
#                     frame_location, (frame_width, frame_height))))
#
#     def update(self):
#         self.cur_frame = (self.cur_frame + 1) % len(self.frames)
#         self.image = self.frames[self.cur_frame]
#
#
# class Ship(AnimatedSprite):
#     def __init__(self, x, y):
#         sheet = pygame.image.load("data/image/sprites/ship.png").convert_alpha()
#         super().__init__(sheet, 4, 1, x, y)
#         self.sound_of_shot = pygame.mixer.Sound("data/music/shot.wav")
#         self.sound_of_shot.set_volume(0.12)
#         self.bullets = []
#         self.last_shot_time = 0
#         self.shoot_delay = 175
#
#         # Параметры для эффекта вылета
#         self.is_flying_in = True
#         self.fly_in_speed = 2  # Скорость вылета
#         self.target_y = 700  # Конечная позиция корабля (где он должен остановиться)
#
#         # Устанавливаем начальную позицию
#         self.rect.y = 900  # Начинаем из нижней части экрана
#
#     def move(self, dx, dy):
#         self.rect.x += dx
#         self.rect.y += dy
#         self.rect.x = max(0, min(self.rect.x, 600 - self.rect.width))
#         self.rect.y = max(0, min(self.rect.y, 900 - self.rect.height))
#
#     def shoot(self, current_time):
#         if current_time - self.last_shot_time > self.shoot_delay:
#             self.sound_of_shot.play()
#             bullet = Bullet(self.rect.centerx, self.rect.top)
#             self.bullets.append(bullet)
#             self.last_shot_time = current_time
#
#     def update(self):
#         if self.is_flying_in:
#             # Поднимаем корабль из-за нижней границы экрана
#             if self.rect.y > self.target_y:
#                 self.rect.y -= self.fly_in_speed
#             else:
#                 self.is_flying_in = False  # Остановить эффект вылета
#         super().update()
#
#
# class Bullet(AnimatedSprite):
#     def __init__(self, x, y):
#         sheet = pygame.transform.scale(load_image('sprites/bullet 1.png'), (100, 100))
#         # = pygame.image.load("data/image/sprites/bullet 1.png").convert_alpha()
#         super().__init__(sheet, 4, 1, x, y)
#         self.bullet_speed = 1.7
#
#         # Поворачиваем каждый кадр на 90 градусов влево
#         self.frames = [pygame.transform.rotate(frame, 90) for frame in self.frames]
#         self.image = self.frames[self.cur_frame]
#         self.rect = self.image.get_rect(center=self.rect.center)
#
#     def move(self):
#         self.rect.y -= self.bullet_speed
#
#
# class BackgroundManager:
#     def __init__(self, screen, backgrounds):
#         self.screen, self.backgrounds = screen, backgrounds
#         self.bg_count = len(backgrounds)
#         self.y_offsets = [i * SCREEN_HEIGHT_LEVEL for i in range(self.bg_count)]  # Смещение для каждого фона
#
#     def update_and_draw(self):
#         # Двигаем фоны вниз
#         for i in range(self.bg_count):
#             self.y_offsets[i] += SCROLL_SPEED
#             # Если фон уходит вниз, сбрасываем его на верхнюю позицию
#             if self.y_offsets[i] >= SCREEN_HEIGHT_LEVEL:
#                 self.y_offsets[i] = (self.y_offsets[i] - SCREEN_HEIGHT_LEVEL * self.bg_count)
#         # Очищаем экран перед новой отрисовкой
#         self.screen.fill((0, 0, 0))  # Черный фон
#         # Отображаем фоны
#         for i in range(self.bg_count):
#             self.screen.blit(self.backgrounds[i], (0, self.y_offsets[i]))
#
#
# class Interface:
#     def __init__(self):
#         self.full_heart = pygame.transform.scale(load_image(''), (60, 50))
#         self.spent_heart = pygame.transform.scale(load_image(''), (60, 50))
#         # self.player_health = 3
#         self.hp_bar = [True] * 3  # Список справа на лево полное ли сердце
#
#     def draw_hp_bar(self):
#         pass
#         # for full_heart in self.hp_bar[::-1]:
#
#     def change_health(self, take_damage=True):
#         try:
#             if take_damage:
#                 self.hp_bar[self.hp_bar.index(True)] = False
#             else:
#                 self.hp_bar[self.hp_bar.index(False)] = True
#         except ValueError:  # Если повышение или понижение хп превысит границы
#             return
#         self.draw_hp_bar()
#
#
# def load_image(name, colorkey=None):
#     fullname = os.path.join('data/image', name)
#     if not os.path.isfile(fullname):
#         print(f"Файл с изображением '{fullname}' не найден")
#         sys.exit()
#     image = pygame.image.load(fullname)
#     if colorkey is not None:
#         image = image.convert()
#         if colorkey == -1:
#             colorkey = image.get_at((0, 0))
#         image.set_colorkey(colorkey)
#     else:
#         image = image.convert_alpha()
#     return image
#
#
# def load_music(type):
#     fullname = os.path.join('data/music', type)
#     if not os.path.isfile(fullname):
#         print(f"Файл с музыкой '{fullname}' не найден")
#         sys.exit()
#     return fullname
#
#
# def load_font(size):
#     fullname = os.path.join('data', 'font/PressStart2P-Regular.ttf')
#     if not os.path.isfile(fullname):
#         print(f"Файл с шрифтом '{fullname}' не найден")
#         sys.exit()
#     font = pygame.font.Font(fullname, size)
#     return font
#
#
# def terminate():
#     pygame.quit()
#     sys.exit()
#
#
# def start_screen(screen_size):
#     global FPS
#     pygame.init()
#     screen = pygame.display.set_mode(screen_size)
#     # Музыка
#     pygame.mixer.init()
#     pygame.mixer.music.load(load_music('start music background.mp3'))
#     pygame.mixer.music.set_volume(0.15)
#     pygame.mixer.music.play(loops=-1, fade_ms=3 * 1000)
#     pygame.display.set_icon(load_image('icon.jpg'))
#     pygame.display.set_caption('AstroBlast')
#     fon = pygame.transform.scale(load_image('backgrounds image/first_screen_background.jpg'), screen_size)
#     screen.blit(fon, (0, 0))
#     # Название игры
#     font = load_font(20)
#     string_rendered = font.render("AstroBlast", 1, pygame.Color('White'))
#     intro_rect = string_rendered.get_rect()
#     intro_rect.top, intro_rect.x = 80, 200
#     screen.blit(string_rendered, intro_rect)
#     # Уровни
#     font = load_font(16)
#     for x, text in zip((100, 350), ("Уровень 1", "Уровень 2")):
#         string_rendered = font.render(text, 1, pygame.Color('White'))
#         intro_rect = string_rendered.get_rect()
#         intro_rect.top, intro_rect.x = 200, x
#         screen.blit(string_rendered, intro_rect)
#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 terminate()
#             elif event.type == pygame.MOUSEBUTTONDOWN:
#                 if 94 <= event.pos[0] <= 246 and 194 <= event.pos[1] <= 217:  # Окрытие уровня 1
#                     level_one()
#                 elif 342 <= event.pos[0] <= 500 and 194 <= event.pos[1] <= 217:  # Открытие уровня 2
#                     level_two()
#         pygame.display.flip()
#         CLOCK.tick(FPS)
#
#
# def level_one():
#     global CLOCK
#     global FPS
#     # Инициализируем Pygame
#     pygame.init()
#     pygame.mixer.music.load(load_music('music in lvl 1.mp3'))
#     pygame.mixer.music.set_volume(0.15)
#     pygame.mixer.music.play(loops=-1, fade_ms=1 * 1000)
#     # Создаем окно
#     os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (0, 0)
#     os.environ['SDL_VIDEO_CENTERED'] = '0'
#     screen = pygame.display.set_mode((SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))
#     # Загружаем фоны
#     backgrounds = []
#     for i in range(5):
#         filename = f'data/image/backgrounds image/level 1/Space_Stars.png'
#         bg = pygame.transform.scale(pygame.image.load(filename), (SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))
#         backgrounds.append(bg)
#     # Создаем объект менеджера фонов
#     background_manager = BackgroundManager(screen, backgrounds)
#     # Вычисляем начальную позицию по центру экрана
#     ship_x = (600 - 64) // 2  # 64 - ширина корабля (предположим, что корабль имеет ширину 64 пикселя)
#     ship = Ship(ship_x, 900)  # Начинаем из нижней части экрана
#     # Основной игровой цикл
#     while True:
#         current_time = pygame.time.get_ticks()
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 terminate()
#         background_manager.update_and_draw()  # Обновляем и отрисовываем фон
#         keys = pygame.key.get_pressed()
#         ship_speed = 1.2
#         if keys[pygame.K_a]:
#             ship.move(-ship_speed, 0)
#         if keys[pygame.K_d]:
#             ship.move(ship_speed, 0)
#         if keys[pygame.K_w]:
#             ship.move(0, -ship_speed)
#         if keys[pygame.K_s]:
#             ship.move(0, ship_speed)
#         if keys[pygame.K_SPACE]:
#             ship.shoot(current_time)
#         for bullet in ship.bullets:
#             bullet.move()
#             if bullet.rect.y < 0:  # Проверяем, вышла ли пуля за верхнюю границу
#                 ship.bullets.remove(bullet)
#         ship.update()
#         screen.blit(ship.image, ship.rect.topleft)
#         for bullet in ship.bullets:
#             bullet.update()
#             screen.blit(bullet.image, bullet.rect.topleft)
#         pygame.display.flip()  # Обновляем дисплей
#         CLOCK.tick(FPS)
#
#
# def level_two():
#     print('WIP: level_two')
#
#
# if __name__ == '__main__':
#     start_screen((600, 400))




















import pygame

# Определение цветов
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Начальная установка
pygame.init()
screen = pygame.display.set_mode((600, 900))
clock = pygame.time.Clock()


class EnergyCharge(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = RED

    def draw(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.color, rect)


# # Создание спрайта энергетического заряда
# energy_charge = EnergyCharge(100, 100, 8, 35)


# Основной цикл игры
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)
    rect = pygame.Rect(600 - 180, 50, 180, 50)
    pygame.draw.rect(screen, 'Red', rect)
    rect = pygame.Rect(300, 700, 50, 90)
    pygame.draw.rect(screen, 'white', rect)

    pygame.display.flip()
    clock.tick(60)
# def change_health(take_damage=True):
#     global hp_bar
#     try:
#         if take_damage:
#             hp_bar[hp_bar.index(True)] = False
#         else:
#             hp_bar[hp_bar.index(False)] = True
#     except ValueError:
#         print('Xn')
#
#
# hp_bar = [True] * 3
# change_health(take_damage=False)
# change_health(take_damage=False)
# change_health()
# print(hp_bar)
# #