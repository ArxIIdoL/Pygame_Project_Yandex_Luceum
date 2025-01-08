import os
import pickle
import sys
import random

import pygame
import pygame_gui

# Константы
SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL = 600, 900
FPS, CLOCK, SCROLL_SPEED = 60, pygame.time.Clock(), 0.4


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect(topleft=(x, y))

    def cut_sheet(self, sheet, columns, rows):
        frame_width = sheet.get_width() // columns
        frame_height = sheet.get_height() // rows
        for j in range(rows):
            for i in range(columns):
                frame_location = (frame_width * i, frame_height * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, (frame_width, frame_height))))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Ship:
    def __init__(self, x, y):
        self.image = pygame.image.load("data/image/sprites/ship.png").convert_alpha()  # Основное изображение
        self.image_turn = pygame.image.load(
            "data/image/sprites/ship_turn.png").convert_alpha()  # Изображение для поворота
        self.rect = self.image.get_rect(topleft=(x, y))
        self.sound_of_shot = pygame.mixer.Sound("data/music/shot.wav")
        self.sound_of_shot.set_volume(0.12)
        self.bullets = []
        self.last_shot_time = 0
        self.shoot_delay = 175

        # Параметры для эффекта вылета
        self.is_flying_in = True
        self.fly_in_speed = 2  # Скорость вылета
        self.target_y = 700  # Конечная позиция корабля (где он должен остановиться)

        # Устанавливаем начальную позицию
        self.rect.y = 900  # Начинаем из нижней части экрана

        self.is_turning = False  # Флаг для отслеживания поворота

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.rect.x = max(0, min(self.rect.x, 600 - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, 900 - self.rect.height))

    def shoot(self, current_time):
        if current_time - self.last_shot_time > self.shoot_delay:
            self.sound_of_shot.play()
            bullet = Bullet(self.rect.centerx, self.rect.top)
            self.bullets.append(bullet)
            self.last_shot_time = current_time

    def turn(self):
        self.is_turning = True  # Устанавливаем флаг поворота

    def reset_turn(self):
        self.is_turning = False  # Сбрасываем флаг поворота

    def update(self):
        if self.is_flying_in:
            # Поднимаем корабль из-за нижней границы экрана
            if self.rect.y > self.target_y:
                self.rect.y -= self.fly_in_speed
            else:
                self.is_flying_in = False  # Остановить эффект вылета

        # # Обновляем изображение в зависимости от состояния поворота
        # if self.is_turning:
        #     self.image = self.image_turn
        # else:
        #     self.image = pygame.image.load(
        #         "data/image/sprites/ship.png").convert_alpha()  # Возвращаем основное изображение


class Asteroid:
    def __init__(self):
        self.size = 30
        self.x = random.randint(0, 570)
        self.y = random.randint(-30, 0)
        self.speed = random.randint(5, 10)
        self.collision_occurred = False

    def move(self):
        self.y += self.speed


def check_collision(ship, asteroids):
    for asteroid in asteroids:
        if (ship.rect.x < asteroid.x + asteroid.size and
                ship.rect.x + 50 > asteroid.x and
                ship.rect.y < asteroid.y + asteroid.size and
                ship.rect.y + 90 > asteroid.y):
            return True  # Возвращаем True при столкновении
    return False  # Возвращаем False, если столкновений не было


class Bullet(AnimatedSprite):
    def __init__(self, x, y):
        sheet = pygame.transform.scale(load_image('sprites/bullet_sprite.png'), (100, 7))
        super().__init__(sheet, 3, 1, x, y)
        self.bullet_speed = 3.5

        # Поворачиваем каждый кадр на 90 градусов влево
        self.frames = [pygame.transform.rotate(frame, 90) for frame in self.frames]
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect(center=self.rect.center)

    def move(self):
        self.rect.y -= self.bullet_speed


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


class Interface(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.full_heart = load_image('sprites/full heart.png')
        self.empty_heart = load_image('sprites/empty heart.png')
        self.x_start = SCREEN_WIDTH_LEVEL - 180
        self.y_start = 10
        self.hp_bar = [True] * 3  # Список для состояния сердечек (полное или пустое)
        self.dead = 0

    def draw_hp_bar(self, screen):
        for is_full, x in zip(self.hp_bar[::-1], range(self.x_start, SCREEN_WIDTH_LEVEL, 60)):
            heart = self.full_heart if is_full else self.empty_heart
            screen.blit(heart, (x, self.y_start))  # Рисуем сердце на экране

    def check_health(self):
        if self.hp_bar == [False, False, False]:
            return True
        else:
            return False

    def change_health(self, take_damage=True):
        if take_damage:
            if self.dead < len(self.hp_bar):  # Проверяем, не превышает ли dead количество сердечек
                self.hp_bar[self.dead] = False  # Устанавливаем сердце как пустое
                self.dead += 1
        else:
            if self.dead > 0:  # Проверяем, есть ли пустые сердца для восстановления
                self.dead -= 1
                self.hp_bar[self.dead] = True  # Устанавливаем сердце как полное


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


def save_game_state(level_function):
    # Функция для сохранения состояния уровня.
    with open("data/current state of the game/game_state.pkl", "wb") as file:
        pickle.dump(level_function.__dict__, file)


def load_game_state(level_function):
    # Функция для загрузки сохраненного состояния уровня.
    try:
        with open("data/current state of the game/game_state.pkl", "rb") as file:
            level_function.__dict__.update(pickle.load(file))
    except FileNotFoundError:
        pass  # Игры нет, ничего не делаем


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


def input_window(screen_size):
    global nickname
    global FPS
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    manager = pygame_gui.UIManager(screen_size)
    # Музыка
    pygame.mixer.init()
    pygame.mixer.music.load(load_music('start music background.mp3'))
    pygame.mixer.music.set_volume(0.15)
    pygame.mixer.music.play(loops=-1, fade_ms=3 * 1000)
    pygame.display.set_icon(load_image('icon.jpg'))
    pygame.display.set_caption('Entering name')
    fon = pygame.transform.scale(load_image('backgrounds image/first_screen_background.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    # screen.fill(pygame.Color("#00008B"))
    # Название игры
    font = load_font(12)
    string_rendered = font.render("Введите имя", True, pygame.Color("White"))
    intro_rect = string_rendered.get_rect()
    intro_rect.top, intro_rect.x = 90, (screen_size[0] // 2) - 70
    screen.blit(string_rendered, intro_rect)
    clock = pygame.time.Clock()
    enter_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((screen_size[0] // 2) - 50, (screen_size[1] // 2) + 20), (100, 25)),
        text='Ok',
        manager=manager
    )
    user_name = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect(((screen_size[0] // 2) - 110, 120), (210, 30))
    )
    nice_nickname = False

    while True:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                user_name_text = event.text
                if not (user_name_text.replace('', ' ') == '') and (
                        3 <= len(user_name_text) <= 12) and user_name_text.isalpha():
                    nickname, nice_nickname = user_name_text, True
                else:
                    nickname, nice_nickname = '', False
            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == enter_btn:
                if nice_nickname and bool(nickname):
                    start_screen((600, 400))
            manager.process_events(event)
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(FPS)


def start_screen(screen_size):
    global FPS
    global nickname
    print(nickname)
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
    string_rendered = font.render("AstroBlast", True, pygame.Color('White'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top, intro_rect.x = 80, 200
    screen.blit(string_rendered, intro_rect)
    # Уровни
    font = load_font(16)
    for x, text in zip((100, 350), ("Уровень 1", "Уровень 2")):
        string_rendered = font.render(text, False, pygame.Color('White'))
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


def menu():
    global music_volume
    # Размеры окна меню
    menu_widht, menu_height = 400, 300
    # Создание окна меню
    screen_menu = pygame.display.set_mode((menu_widht, menu_height))
    pygame.display.set_caption("Menu")
    # Фон меню
    background = pygame.Surface(screen_menu.get_size())
    background.fill((0, 0, 0))
    # Шрифты
    font = pygame.font.Font(None, 36)
    # Надписи
    music_text = font.render("Music Volume:", True, (255, 255, 255))

    # sound_text = font.render("Sound Volume:", True, (255, 255, 255))

    # Ползунки для регулировки громкости
    def draw_slider(surf, x, y, w, h, color, value):
        pygame.draw.rect(surf, color, (x, y, w, h))
        handle_x = int(x + (w - 10) * value / 100)
        pygame.draw.rect(surf, (255, 0, 0), (handle_x, y, 10, h))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 1:  # Левая кнопка мыши
                    if 20 <= mouse_pos[0] <= 380 and 120 <= mouse_pos[1] <= 140:
                        music_volume = int((mouse_pos[0] - 20) / 360 * 100)
                        pygame.mixer.music.set_volume(music_volume / 100)
        # Очистка экрана
        screen_menu.blit(background, (0, 0))
        # Отображение текста
        screen_menu.blit(music_text, (20, 80))
        # Рисование ползунков
        draw_slider(screen_menu, 20, 120, 360, 20, (255, 255, 255), music_volume)
        # Обновление дисплея
        pygame.display.flip()
    # Возвращаемся к основному окну игры
    pygame.display.set_caption("AstroBlast")
    pygame.display.set_mode((SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))


def check_bullet_collision(bullets, asteroids):
    for bullet in bullets:
        for asteroid in asteroids:
            if (bullet.rect.x < asteroid.x + asteroid.size and
                    bullet.rect.x + bullet.rect.width > asteroid.x and
                    bullet.rect.y < asteroid.y + asteroid.size and
                    bullet.rect.y + bullet.rect.height > asteroid.y):
                asteroids.remove(asteroid)  # Удаляем квадрат
                bullets.remove(bullet)  # Удаляем пулю
                return  # Выходим из функции после первого столкновения


def level_one():
    asteroids = []
    interface = Interface()
    global CLOCK
    global FPS
    pause = False
    explosion_active = False
    explosion_time = 0
    flash_time = 0
    flash_active = False
    explosion_image = pygame.image.load("data/image/sprites/boom.png")  # загружаем изображение взрыва
    explosion_rect = None  # переменная для позиции взрыва
    # Инициализируем Pygame
    pygame.init()
    pygame.mixer.music.load(load_music('music in lvl 1.mp3'))
    pygame.mixer.music.set_volume(0.15)
    pygame.mixer.music.play(loops=-1, fade_ms=1 * 1000)
    # Создаем окно
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (0, 0)
    os.environ['SDL_VIDEO_CENTERED'] = '0'
    screen = pygame.display.set_mode((SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))
    # Загружаем фоны
    backgrounds = []
    for i in range(5):
        filename = f'data/image/backgrounds image/level 1/Space_Stars.png'
        bg = pygame.transform.scale(pygame.image.load(filename), (SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))
        backgrounds.append(bg)
    # Создаем объект менеджера фонов
    background_manager = BackgroundManager(screen, backgrounds)
    # Вычисляем начальную позицию по центру экрана
    ship_x = (600 - 64) // 2  # 64 - ширина корабля (предположим, что корабль имеет ширину 64 пикселя)
    ship = Ship(ship_x, 900)  # Начинаем из нижней части экрана
    # Основной игровой цикл
    while True:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause = not pause
                if pause:
                    save_game_state(level_one)  # Сохраняем текущее состояние уровня
                    menu()  # Переходим в меню
                    pause = False
                    load_game_state(level_one)  # Восстанавливаем состояние уровня после выхода из меню
        if not pause:
            background_manager.update_and_draw()  # Обновляем и отрисовываем фон
            keys = pygame.key.get_pressed()
            ship_speed = 2.2

            # Движение корабля
            if keys[pygame.K_a]:  # Влево
                ship.move(-ship_speed, 0)
                ship.turn()  # Устанавливаем флаг поворота
            elif keys[pygame.K_d]:  # Вправо
                ship.move(ship_speed, 0)
                ship.turn()
            else:
                ship.reset_turn()  # Если не нажаты клавиши A или D, сбрасываем флаг поворота

            if keys[pygame.K_w]:
                ship.move(0, -ship_speed)
            if keys[pygame.K_s]:
                ship.move(0, ship_speed)

            # Проверяем столкновение с астероидами
            for asteroid in asteroids:
                if check_collision(ship, [asteroid]) and not asteroid.collision_occurred:
                    asteroid.collision_occurred = True
                    interface.change_health()
                    if interface.check_health():
                        print("Game Over! Restarting level...")
                        level_one()

                    # Убираем астероид и показываем взрыв
                    explosion_active = True
                    explosion_time = current_time  # сохраняем текущее время
                    explosion_rect = explosion_image.get_rect(
                        center=(asteroid.x + asteroid.size // 2, asteroid.y + asteroid.size // 2))
                    asteroids.remove(asteroid)  # Удаляем астероид


                    flash_active = True
                    flash_time = current_time  # сохраняем текущее время мерцания
                    break  # Выходим из цикла, чтобы избежать изменения списка во время итерации

            # Обработка мерцания корабля
            if flash_active:
                for asteroid in asteroids:
                    asteroids.remove(asteroid)
                if (current_time - flash_time) < 1000:  # мерцание в течение 1 секунды
                    # Мерцание: показываем корабль через 100 мс
                    if (current_time // 100) % 2 == 0:
                        screen.blit(ship.image, ship.rect.topleft)
                else:
                    flash_active = False  # Отключаем мерцание
                    ship.rect.y = 700
                    ship.rect.x = 250  # возвращаем корабль на место


            # Обновляем позицию астероидов, только если корабль не мерцает
            if not flash_active:
                for asteroid in asteroids:
                    asteroid.move()
                    pygame.draw.rect(screen, (255, 0, 0), (asteroid.x, asteroid.y, asteroid.size, asteroid.size))

            # Добавляем новые астероиды
            if pygame.time.get_ticks() % 15 == 0:
                asteroids.append(Asteroid())

            asteroids = [asteroid for asteroid in asteroids if asteroid.y < 900]

            if keys[pygame.K_SPACE]:
                ship.shoot(current_time)
            for bullet in ship.bullets:
                bullet.move()
                if bullet.rect.y < -12:
                    ship.bullets.remove(bullet)

            check_bullet_collision(ship.bullets, asteroids)

            ship.update()

            # Отображаем корабль, если он не мерцает
            if not flash_active:
                screen.blit(ship.image, ship.rect.topleft)

            # Отображаем пули
            for bullet in ship.bullets:
                bullet.update()
                screen.blit(bullet.image, bullet.rect.topleft)

            # Отображаем взрыв, если он активен
            if explosion_active:
                screen.blit(explosion_image, explosion_rect)
                # Проверяем, нужно ли скрыть взрыв
                if current_time - explosion_time >= 1000:  # 1000 мс = 1 секунда
                    explosion_active = False

            pygame.draw.rect(screen, '#4B0082', (410, 0, 200, 70))
            pygame.draw.rect(screen, '#D3D3D3', (410, 0, 200, 70), 3)

            interface.draw_hp_bar(screen)
            pygame.display.flip()  # Обновляем дисплей
        CLOCK.tick(FPS)


def level_two():
    print('WIP: level_two')


if __name__ == '__main__':
    music_volume, nickname = 15, ''
    input_window((400, 300))
    # start_screen((600, 400))
