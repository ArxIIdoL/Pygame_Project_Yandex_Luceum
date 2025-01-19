import os
import pickle
import random
import sys
import csv

import pygame
import pygame_gui

# Константы
pygame.mixer.init()
SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL = 600, 900
FPS, CLOCK, SCROLL_SPEED = 60, pygame.time.Clock(), 0.4
SOUNDS_CONFIRMING_1, SOUNDS_CONFIRMING_2 = pygame.mixer.Sound(
    "data/sounds/sounds_confirming_1.wav"), pygame.mixer.Sound(
    "data/sounds/sounds_confirming_2.wav")
BONUSES = {'Bonus': ['more bullets', 'more hp', 'more speed'],
           'Anti bonus': ['attack of masochism', 'dying moment', 'irritated eye'],
           'Super bonus': ['Art of Asclepius', 'neon bullets']}
SCORED, MAX_SCORED_IN_LVL1, MAX_SCORED_IN_LVL2 = 0, 0, 0
SOUNDS_CONFIRMING_1.set_volume(0.12), SOUNDS_CONFIRMING_2.set_volume(0.12)


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


class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_straight = load_image("sprites/spaceship straight.png")  # Основное изображение
        self.image_turn_left = load_image("sprites/spaceship left.png")  # Изображение для поворота налево
        self.image_turn_right = load_image("sprites/spaceship right.png")  # Изображение для поворота направо

        # Растягиваем изображение корабля
        self.image_straight = pygame.transform.scale(self.image_straight, (
            self.image_straight.get_width() * 1.5, self.image_straight.get_height() * 1.5))
        self.image_turn_left = pygame.transform.scale(self.image_turn_left, (
            self.image_turn_left.get_width() * 1.5, self.image_turn_left.get_height() * 1.5))
        self.image_turn_right = pygame.transform.scale(self.image_turn_right, (
            self.image_turn_right.get_width() * 1.5, self.image_turn_right.get_height() * 1.5))

        self.image = self.image_straight

        self.rect = self.image.get_rect(center=(x, y))

        self.sound_of_shot = pygame.mixer.Sound("data/sounds/shot.wav")
        self.sound_of_shot.set_volume(0.12)
        self.bullets, self.last_shot_time = [], 0
        self.shoot_delay = 175

        # Параметры для эффекта вылета
        self.is_flying_in = True
        self.fly_in_speed = 2  # Скорость вылета
        self.target_y = 700  # Конечная позиция корабля (где он должен остановиться)

        # Устанавливаем начальную позицию
        self.rect.y = 900

        self.is_turning = False
        self.turn_direction = None  # Направление поворота (None, 'left' или 'right')

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.rect.x = max(0, min(self.rect.x, 600 - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, 900 - self.rect.height))

    def shoot(self, current_time):
        if is_neon_bullets:
            if current_time - self.last_shot_time > self.shoot_delay:
                self.sound_of_shot.play()
                bullet = Bullet(self.rect.centerx - 45, self.rect.top)
                self.bullets.append(bullet)
                bullet = Bullet(self.rect.centerx, self.rect.top)
                self.bullets.append(bullet)
                bullet = Bullet(self.rect.centerx - 20, self.rect.top)
                self.bullets.append(bullet)
                bullet = Bullet(self.rect.centerx + 25, self.rect.top)
                self.bullets.append(bullet)
                self.last_shot_time = current_time

        elif is_more_bullets:
            if current_time - self.last_shot_time > self.shoot_delay:
                self.sound_of_shot.play()
                bullet = Bullet(self.rect.centerx - 30, self.rect.top)
                self.bullets.append(bullet)
                bullet = Bullet(self.rect.centerx, self.rect.top)
                self.bullets.append(bullet)
                self.last_shot_time = current_time

        else:
            if current_time - self.last_shot_time > self.shoot_delay:
                self.sound_of_shot.play()
                bullet = Bullet(self.rect.centerx - 18, self.rect.top)
                self.bullets.append(bullet)
                self.last_shot_time = current_time

    def turn(self, direction):
        self.is_turning = True
        self.turn_direction = direction

    def reset_turn(self):
        self.is_turning = False
        self.turn_direction = None

    def update(self):
        if self.is_flying_in:
            # Поднимаем корабль из-за нижней границы экрана
            if self.rect.y > self.target_y:
                self.rect.y -= self.fly_in_speed
            else:
                self.is_flying_in = False  # Остановить эффект вылета

        # Обновляем изображение в зависимости от состояния поворота
        if self.is_turning:
            if self.turn_direction == 'left':
                self.image = self.image_turn_left
            elif self.turn_direction == 'right':
                self.image = self.image_turn_right
        else:
            self.image = self.image_straight

        # Обновляем rect для текущего изображения
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw_hitbox(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


class Asteroid(AnimatedSprite):
    def __init__(self, level):
        self.image = load_image('sprites/asteroids_1.png') if level == 1 else load_image('sprites/asteroids_2.png')
        self.size = self.image.get_width()
        self.x = random.randint(0, SCREEN_WIDTH_LEVEL - self.size)
        self.y = random.randint(-30, 0)

        # Генерируем случайные скорости по осям X и Y
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(3, 7)
        self.collision_occurred = False

        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.time = 0

    def move(self):

        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.topleft = (self.x, self.y)

        if self.x < 0 or self.x > SCREEN_WIDTH_LEVEL - self.size:
            self.speed_x = -self.speed_x  # Меняем направление при столкновении со стенкой

        if self.y > SCREEN_HEIGHT_LEVEL:  # Если астероид вышел за нижнюю границу экрана
            self.y = random.randint(-30, 0)  # Возвращаем его на верхнюю границу с новой случайной Y
            self.x = random.randint(0, SCREEN_WIDTH_LEVEL - self.size)  # Новая случайная X
            self.speed_y = random.uniform(3, 7)
            self.speed_x = random.uniform(-3, 3)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)  # Отображаем спрайт на экране


class Bullet(AnimatedSprite):
    def __init__(self, x, y):
        if is_neon_bullets:
            sheet = pygame.transform.scale(load_image('sprites/neon bullets.png'), (30, 7))
            super().__init__(sheet, 1, 1, x, y)
        else:
            sheet = pygame.transform.scale(load_image('sprites/bullet_sprite.png'), (100, 7))
            super().__init__(sheet, 3, 1, x, y)
        self.bullet_speed = 3.5

        # Поворачиваем каждый кадр на 90 градусов влево
        self.frames = [pygame.transform.rotate(frame, 90) for frame in self.frames]
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect(center=self.rect.center)

    def move(self):
        self.rect.y -= self.bullet_speed
        self.bullet_speed += 0.08


class Explosion:
    def __init__(self, x, y, num):
        sheet = load_image(f"sprites/boom{num}.png")
        if num == 3:
            frame_width = sheet.get_width() // 14
            frame_height = sheet.get_height()
            self.sprites = []
            for i in range(14):
                frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                new_width = int(frame_width * 1)
                new_height = int(frame_height * 1)
                scaled_frame = pygame.transform.scale(frame, (new_width, new_height))
                self.sprites.append(scaled_frame)
        else:
            frame_width = sheet.get_width() // 8  # Предполагается, что 8 спрайтов в одной строке
            frame_height = sheet.get_height()
            self.sprites = []
            for i in range(8):
                frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                self.sprites.append(frame)

        self.current_frame = 0  # Индекс текущего кадра
        self.frame_duration = 100  # Продолжительность каждого кадра в мс
        self.last_update = pygame.time.get_ticks()  # Время последнего обновления
        self.rect = self.sprites[0].get_rect(center=(x, y))  # Позиция взрыва
        self.active = True  # Флаг активности анимации

        # Загрузка звука взрыва
        self.explosion_sound = pygame.mixer.Sound("data/sounds/explosion.wav")
        self.explosion_sound.set_volume(0.1)  # Громкость звука
        self.explosion_sound.play()  # Воспроизводим звук взрыва при создании объекта

    def update(self):
        if self.active:
            current_time = pygame.time.get_ticks()
            # Проверяем, пора ли переходить к следующему кадру
            if current_time - self.last_update >= self.frame_duration:
                self.last_update = current_time
                self.current_frame += 1
                # Если анимация завершена, деактивируем её
                if self.current_frame >= len(self.sprites):
                    self.active = False

    def draw(self, surface):
        if self.active:
            surface.blit(self.sprites[self.current_frame], self.rect.topleft)


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


class Bonus(pygame.sprite.Sprite):
    def __init__(self, screen_size, bonus_types=('Bonus',)):
        super().__init__()
        self.bonus_type = random.choice(bonus_types)
        self.bonus_name = random.choice(BONUSES[self.bonus_type])
        self.image = load_image(f'sprites/bonuses/{self.bonus_type} {self.bonus_name}.png')
        # Случайная позиция на экране
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_size[0] - self.rect.width)
        self.rect.y = random.randint(0, screen_size[1] - self.rect.height)

        # Время жизни бонуса (в миллисекундах)
        self.lifetime = 10000  # Бонус исчезнет через 10 секунд
        self.start_time = pygame.time.get_ticks()

        # Звук для подбора бонуса
        self.pickup_sound = pygame.mixer.Sound(f'data/sounds/{self.bonus_type}.wav')
        self.pickup_sound.set_volume(0.5)

        # Звук для исчезновения бонуса
        self.vanish_sound = pygame.mixer.Sound('data/sounds/vanish_sound.wav')
        self.vanish_sound.set_volume(0.5)

        # Флаги для эффектов
        self.should_merca, self.is_flashing = False, False
        self.flash_timer, self.flash_start_time = 500, 0  # Мерцать каждые полсекунды

    def update(self, current_time):
        # Проверяем, истекло ли время жизни бонуса
        if current_time - self.start_time >= self.lifetime:
            self.vanish_sound.play()  # Воспроизводим звук перед исчезновением
            self.kill()  # Уничтожаем бонус, если время вышло

        # Проверяем, нужно ли начать мерцание
        if current_time - self.start_time >= self.lifetime - 3000:  # Начнем мерцать за 3 секунды до конца
            self.should_merca = True

        # Реализуем мерцание
        if self.should_merca:
            if current_time - self.flash_start_time >= self.flash_timer:
                self.is_flashing = not self.is_flashing
                self.flash_start_time = current_time

            if self.is_flashing:
                self.image.set_alpha(128)  # Полупрозрачность
            else:
                self.image.set_alpha(255)  # Нормальная видимость

    def apply_effect(self, interface):
        global ship_speed, is_more_bullets, is_irritated_eye, is_neon_bullets
        # Применяем эффект бонуса
        if self.bonus_type == 'Bonus':
            if self.bonus_name == 'more hp':
                interface.change_health(False)
            elif self.bonus_name == 'more bullets':
                is_more_bullets = True
            elif self.bonus_name == 'more speed':
                global ship_speed
                ship_speed = 4.5
        elif self.bonus_type == 'Anti bonus':
            if self.bonus_name == 'attack of masochism':
                interface.change_star(False)
                interface.change_health(True)
            elif self.bonus_name == 'dying moment':
                interface.change_health(True), interface.change_health(True)
            elif self.bonus_name == 'irritated eye':
                is_irritated_eye = True
        elif self.bonus_type == 'Super bonus':
            if self.bonus_name == 'Art of Asclepius':
                interface.change_health(False), interface.change_health(False)
            elif self.bonus_name == 'neon bullets':
                is_neon_bullets = True
        elif self.bonus_type == 'Star':
            interface.change_star()

        # Воспроизводим звук подбора
        self.pickup_sound.play()

    def disable_all_effects(self):
        global ship_speed, is_more_bullets, is_irritated_eye, is_neon_bullets
        ship_speed, is_more_bullets, is_irritated_eye, is_neon_bullets = 2.2, False, False, False


class Interface(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.full_heart = load_image('sprites/full heart.png')
        self.empty_heart = load_image('sprites/empty heart.png')
        # self.full_star = load_image('sprites/full star.png')
        # self.empty_star = load_image('sprites/empty star.png')
        self.x_start, self.y_start = SCREEN_WIDTH_LEVEL - 180, 19
        self.hp_bar, self.dead = [True] * 3, 0  # Список для состояния сердечек (полное или пустое)
        self.star_bar, self.stars = [False] * 3, 0  # Список для состояния звёзд (полная или пустая)

        # Изменяем размер сердечек
        self.full_heart = pygame.transform.scale(self.full_heart, (45, 45))
        self.empty_heart = pygame.transform.scale(self.empty_heart, (45, 45))

    def draw_score_bar(self, screen):
        font = load_font(15)
        scored_text = font.render(f"{SCORED}", True, pygame.Color('White'))
        intro_rect = scored_text.get_rect()
        intro_rect.top, intro_rect.x = SCREEN_HEIGHT_LEVEL - (15 + 20), SCREEN_WIDTH_LEVEL // (
                (len(str(SCORED)) * 10) + 20)
        screen.blit(scored_text, intro_rect)

    def draw_hp_bar(self, screen):
        for is_full, x in zip(self.hp_bar[::-1], range(self.x_start, SCREEN_WIDTH_LEVEL, 50)):
            heart = self.full_heart if is_full else self.empty_heart
            screen.blit(heart, (x, self.y_start))

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

    def change_star(self, take=True):
        if not take:
            if self.stars < len(self.star_bar):  # Проверяем, не превышает ли star количество звёзд
                self.star_bar[self.stars] = False  # Устанавливаем звезду как пустую
                self.stars += 1
        else:
            if self.stars > 0:  # Проверяем, есть ли пустая звезда для пополнения
                self.stars -= 1
                self.star_bar[self.stars] = True  # Устанавливаем звезду как полную


def load_image(name):
    fullname = os.path.join('data/image', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
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


def write_results_to_csv(nickname, max_score_lvl1, max_score_lvl2, filename='data/results.csv'):
    # Проверка, существует ли файл
    existing_results = {}
    if os.path.isfile(filename):
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_results[row['nickname']] = {
                    'MAX_SCORED_IN_LVL1': int(row['MAX_SCORED_IN_LVL1']),
                    'MAX_SCORED_IN_LVL2': int(row['MAX_SCORED_IN_LVL2']),
                }

    # Проверяем, есть ли уже запись для данного ника
    if nickname in existing_results:
        # Обновляем максимальные очки, если новые больше
        if max_score_lvl1 > existing_results[nickname]['MAX_SCORED_IN_LVL1']:
            existing_results[nickname]['MAX_SCORED_IN_LVL1'] = max_score_lvl1
        if max_score_lvl2 > existing_results[nickname]['MAX_SCORED_IN_LVL2']:
            existing_results[nickname]['MAX_SCORED_IN_LVL2'] = max_score_lvl2
    else:
        # Если ника нет, добавляем нового игрока
        existing_results[nickname] = {
            'MAX_SCORED_IN_LVL1': max_score_lvl1,
            'MAX_SCORED_IN_LVL2': max_score_lvl2,
        }

    # Записываем обновленные результаты обратно в файл
    with open(filename, mode='w', newline='') as file:
        fieldnames = ['nickname', 'MAX_SCORED_IN_LVL1', 'MAX_SCORED_IN_LVL2']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()  # Записываем заголовки
        for nick, scores in existing_results.items():
            writer.writerow({
                'nickname': nick,
                'MAX_SCORED_IN_LVL1': scores['MAX_SCORED_IN_LVL1'],
                'MAX_SCORED_IN_LVL2': scores['MAX_SCORED_IN_LVL2'],
            })


def terminate():
    global nickname
    pygame.quit()
    if len(nickname) >= 3:
        write_results_to_csv(nickname, MAX_SCORED_IN_LVL1, MAX_SCORED_IN_LVL2)
    sys.exit()


def input_window(screen_size):
    global nickname, MAX_SCORED_IN_LVL1, MAX_SCORED_IN_LVL2
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    manager = pygame_gui.UIManager(screen_size)

    # Музыка
    pygame.mixer.init()
    pygame.mixer.music.load(load_music('music background.mp3'))
    pygame.mixer.music.set_volume(0.15)
    pygame.mixer.music.play(loops=-1, fade_ms=3 * 1000)

    # Загрузка звука для нажатия клавиши
    key_press_sound = pygame.mixer.Sound('data/sounds/button-11.wav')
    key_press_sound.set_volume(0.1)

    pygame.display.set_icon(load_image('icon.jpg'))
    pygame.display.set_caption('Entering name')
    fon = pygame.transform.scale(load_image('backgrounds image/first_screen_background.jpg'), screen_size)
    screen.blit(fon, (0, 0))

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

            if event.type == pygame.KEYDOWN:
                # Воспроизводим звук при нажатии любой клавиши
                key_press_sound.play()

                if event.key == pygame.K_F1:
                    level_one()
                elif event.key == pygame.K_F2:
                    level_two()

            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                user_name_text = event.text
                if not (user_name_text.replace('', ' ') == '') and (
                        3 <= len(user_name_text) <= 12) and user_name_text.isalpha():
                    SOUNDS_CONFIRMING_2.play()
                    nickname, nice_nickname = user_name_text, True
                else:
                    nickname, nice_nickname = '', False
            elif event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == enter_btn:
                if nice_nickname and bool(nickname):
                    # Обновление констант максимальных очков для игрока при вводе ника из .csv файла
                    with open('data/results.csv', 'r', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                        for row in reader:
                            if row[0] == nickname:
                                MAX_SCORED_IN_LVL1 = int(row[1])
                                MAX_SCORED_IN_LVL2 = int(row[2])
                    SOUNDS_CONFIRMING_1.play()
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
    # # Музыка
    # pygame.mixer.init()
    # pygame.mixer.music.load(load_music('start music background.mp3'))
    # pygame.mixer.music.set_volume(0.15)
    # pygame.mixer.music.play(loops=-1, fade_ms=3 * 1000)
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
                    SOUNDS_CONFIRMING_1.play()
                    level_one()
                elif 342 <= event.pos[0] <= 500 and 194 <= event.pos[1] <= 217:  # Открытие уровня 2
                    SOUNDS_CONFIRMING_1.play()
                    level_two()
        pygame.display.flip()
        CLOCK.tick(FPS)


def menu():
    global music_volume

    # Размеры окна меню
    menu_width, menu_height = 400, 300

    # Создание окна меню
    screen_menu = pygame.display.set_mode((menu_width, menu_height))
    pygame.display.set_caption("Menu")

    # Инициализация менеджера интерфейсов
    manager = pygame_gui.UIManager((menu_width, menu_height))

    # Создаем ползунок для регулировки громкости музыки
    slider_rect = pygame.Rect((50, 150), (300, 30))  # Позиция и размер ползунка
    music_volume_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=slider_rect,
        start_value=music_volume,  # Начальное значение
        value_range=(0, 100),
        manager=manager
    )

    # Шрифты
    font = pygame.font.Font(None, 36)
    # Надписи
    music_text = font.render("Music Volume:", True, (255, 255, 255))

    # Основной цикл программы
    clock = pygame.time.Clock()
    running = True

    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == music_volume_slider:
                    music_volume = round(event.value)  # Обновляем глобальную переменную
                    pygame.mixer.music.set_volume(music_volume / 100)  # Устанавливаем уровень громкости
            manager.process_events(event)
        manager.update(time_delta)
        screen_menu.fill((0, 0, 0))  # Заливаем экран черным цветом
        screen_menu.blit(music_text, (110, 80))
        manager.draw_ui(screen_menu)  # Отображаем элементы интерфейса
        pygame.display.update()
    # Возвращаемся к основному окну игры
    SOUNDS_CONFIRMING_1.play()
    pygame.display.set_caption("AstroBlast")
    pygame.display.set_mode((SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))


def check_collision(ship, asteroids):
    for asteroid in asteroids:
        if (ship.rect.x < asteroid.x + asteroid.size and
                ship.rect.x + ship.rect.width > asteroid.x and
                ship.rect.y < asteroid.y + asteroid.size and
                ship.rect.y + ship.rect.height > asteroid.y):
            return True  # Возвращаем True при столкновении
    return False


def check_bullet_collision(bullets, asteroids, explosions):
    global SCORED
    for bullet in bullets:
        for asteroid in asteroids:
            if (bullet.rect.x < asteroid.x + asteroid.size and
                    bullet.rect.x + bullet.rect.width > asteroid.x and
                    bullet.rect.y < asteroid.y + asteroid.size and
                    bullet.rect.y + bullet.rect.height > asteroid.y):
                if is_neon_bullets:
                    explosions.append(Explosion(asteroid.rect.centerx, asteroid.rect.centery, 3))
                else:
                    explosions.append(Explosion(asteroid.rect.centerx, asteroid.rect.centery, 1))
                asteroids.remove(asteroid)  # Удаляем астероид
                SCORED += 10
                bullets.remove(bullet)  # Удаляем пулю
                return  # Выходим из функции после первого столкновения


def level_one():
    global SCORED, CLOCK, FPS, music_volume, ship_speed, is_more_bullets, is_irritated_eye, is_neon_bullets
    ship_speed, is_more_bullets, is_irritated_eye, is_neon_bullets = 2.2, False, False, False
    SCORED = 0
    asteroids, active_bonuses = [], []
    interface = Interface()
    pause, explosions = False, []  # Список для хранения активных взрывов
    flash_time, flash_active = 0, False
    ship_flash_duration = 1000  # Длительность мерцания в мс
    show_hitbox = False  # Флаг для отображения хитбокса
    bonuses = pygame.sprite.Group()

    # Инициализируем Pygame и музыку
    pygame.init()
    pygame.mixer.music.load(load_music('music in lvl 1.mp3'))
    pygame.mixer.music.play(loops=-1, fade_ms=1 * 1000)

    # Создаем окно
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (0, 0)
    os.environ['SDL_VIDEO_CENTERED'] = '0'
    screen = pygame.display.set_mode((SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))

    # Загружаем фоны
    backgrounds = []
    for i in range(5):
        filename = f'data/image/backgrounds image/Space_Stars.png'
        bg = pygame.transform.scale(pygame.image.load(filename), (SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))
        backgrounds.append(bg)

    # Создаем объект менеджера фонов
    background_manager = BackgroundManager(screen, backgrounds)

    # Вычисляем начальную позицию по центру экрана
    ship_x = (600 - 64) // 2  # 64 - ширина корабля (предположим, что корабль имеет ширину 64 пикселя)
    ship = Ship(ship_x, 900)  # Начинаем из нижней части экрана

    last_event_time = pygame.time.get_ticks()  # Время первого запуска
    time_application = pygame.time.get_ticks()
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
                    pygame.mixer.music.pause()
                    menu()  # Переходим в меню
                    pygame.mixer.music.unpause()
                    pause = False
                    load_game_state(level_one)  # Восстанавливаем состояние уровня после выхода из меню
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                show_hitbox = not show_hitbox  # Переключаем отображение хитбокса
                is_neon_bullets = True

        if not pause:
            background_manager.update_and_draw()  # Обновляем и отрисовываем фон
            keys = pygame.key.get_pressed()

            # Движение корабля
            if keys[pygame.K_a]:  # Влево
                ship.move(-ship_speed, 0)
                ship.turn('left')  # Устанавливаем флаг поворота
            elif keys[pygame.K_d]:  # Вправо
                ship.move(ship_speed, 0)
                ship.turn('right')
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
                    SCORED = max(0, SCORED - 50)

                    # Убираем астероид и создаем взрыв
                    explosion = Explosion(ship.rect.centerx, ship.rect.centery, 2)  # Позиция взрыва - позиция корабля
                    explosions.append(explosion)  # Добавляем взрыв в список
                    asteroids.remove(asteroid)  # Удаляем астероид

                    if interface.check_health():
                        pygame.mixer.music.pause()
                        game_over()

                    # Запускаем мерцание
                    flash_active = True
                    flash_time = current_time  # Сохраняем текущее время мерцания
                    break  # Выходим из цикла, чтобы избежать изменения списка во время итерации

                # Обработка мерцания корабля            if flash_active:
                if (current_time - flash_time) < ship_flash_duration:  # мерцание в течение установленной длительности
                    # Мерцание: показываем корабль через 100 мс
                    if (current_time // 100) % 2 == 0:
                        screen.blit(ship.image, ship.rect.topleft)
                else:
                    flash_active = False  # Отключаем мерцание
                    # ship.rect.y = 700  # Сброс позиции корабля при необходимости
                    # ship.rect.x = 250  # Сброс позиции корабля при необходимости

            # Обновляем и отображаем взрывы
            for explosion in explosions:
                explosion.update()
                explosion.draw(screen)
            # Обновляем позицию астероидов
            for asteroid in asteroids:
                asteroid.move()
                asteroid.draw(screen)

            # Добавляем новые астероиды
            if current_time % 35 == 0:
                asteroids.append(Asteroid(1))
            if (current_time - last_event_time) >= 20000:  # 20000
                last_event_time = current_time
                new_bonus = Bonus((SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))
                bonuses.add(new_bonus)

            asteroids = [asteroid for asteroid in asteroids if asteroid.y < 900]

            if keys[pygame.K_SPACE]:
                ship.shoot(current_time)
            for bullet in ship.bullets:
                bullet.move()
                if bullet.rect.y < -12:
                    ship.bullets.remove(bullet)

            check_bullet_collision(ship.bullets, asteroids, explosions)

            ship.update()
            # Отображаем хитбокс, если флаг активен
            if show_hitbox:
                ship.draw_hitbox(screen)

            # Отображаем корабль, если он не мерцает
            if not flash_active:
                screen.blit(ship.image, ship.rect.topleft)

            # Отображаем пули
            for bullet in ship.bullets:
                bullet.update()
                screen.blit(bullet.image, bullet.rect.topleft)

            # Обновляем спрайты бонусов
            bonuses.update(current_time)

            # Проверка столкновений между кораблем и бонусами
            collisions = pygame.sprite.spritecollide(ship, bonuses, True)
            for bonus in collisions:
                bonus.apply_effect(interface)
                time_application = current_time

            if (current_time - time_application) / 1000 >= 4:
                for bonus in bonuses:
                    bonus.disable_all_effects()

            # Отображаем все спрайты
            bonuses.draw(screen)
            frame_image = pygame.image.load('data/image/sprites/hp_window.png')
            stretched_image = pygame.transform.scale(frame_image, (600 - 390, 80))
            screen.blit(stretched_image, (390, 0))
            interface.draw_hp_bar(screen)
            interface.draw_score_bar(screen)
            pygame.display.flip()  # Обновляем дисплей
        CLOCK.tick(FPS)


def level_two():
    global SCORED, CLOCK, FPS, music_volume, ship_speed, is_more_bullets, is_irritated_eye, is_neon_bullets
    ship_speed, is_more_bullets, is_irritated_eye, is_neon_bullets = 2.2, False, False, True
    SCORED = 0
    asteroids, active_bonuses = [], []
    interface = Interface()
    pause, explosions = False, []  # Список для хранения активных взрывов
    flash_time, flash_active = 0, False
    ship_flash_duration = 1000  # Длительность мерцания в мс
    show_hitbox = False  # Флаг для отображения хитбокса
    bonuses = pygame.sprite.Group()

    # Инициализируем Pygame и музыку
    pygame.init()
    pygame.mixer.music.load('data/music/music in lvl 2.mp3')
    pygame.mixer.music.play(loops=-1, fade_ms=1 * 1000)

    # Создаем окно
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (0, 0)
    os.environ['SDL_VIDEO_CENTERED'] = '0'
    screen = pygame.display.set_mode((SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))

    # Загружаем фоны
    backgrounds = []
    for i in range(5):
        filename = f'data/image/backgrounds image/Space_Stars.png'
        bg = pygame.transform.scale(pygame.image.load(filename), (SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL))
        backgrounds.append(bg)
    # Создаем объект менеджера фонов
    background_manager = BackgroundManager(screen, backgrounds)

    # Вычисляем начальную позицию по центру экрана
    ship_x = (600 - 64) // 2  # 64 - ширина корабля (предположим, что корабль имеет ширину 64 пикселя)
    ship = Ship(ship_x, 900)  # Начинаем из нижней части экрана

    last_event_time = pygame.time.get_ticks()  # Время первого запуска
    time_application = pygame.time.get_ticks()
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
                    pygame.mixer.music.pause()
                    menu()  # Переходим в меню
                    pygame.mixer.music.unpause()
                    pause = False
                    load_game_state(level_one)  # Восстанавливаем состояние уровня после выхода из меню
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                show_hitbox = not show_hitbox  # Переключаем отображение хитбокса

        if not pause:
            background_manager.update_and_draw()  # Обновляем и отрисовываем фон
            keys = pygame.key.get_pressed()

            # Движение корабля
            if keys[pygame.K_a]:  # Влево
                ship.move(-ship_speed, 0)
                ship.turn('left')  # Устанавливаем флаг поворота
            elif keys[pygame.K_d]:  # Вправо
                ship.move(ship_speed, 0)
                ship.turn('right')
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
                    SCORED = max(0, SCORED - 50)

                    # Убираем астероид и создаем взрыв
                    explosion = Explosion(ship.rect.centerx, ship.rect.centery, 2)  # Позиция взрыва - позиция корабля
                    explosions.append(explosion)  # Добавляем взрыв в список
                    asteroids.remove(asteroid)  # Удаляем астероид

                    if interface.check_health():
                        pygame.mixer.music.pause()
                        game_over(2)

                    # Запускаем мерцание
                    flash_active = True
                    flash_time = current_time  # Сохраняем текущее время мерцания
                    break  # Выходим из цикла, чтобы избежать изменения списка во время итерации

            # Обработка мерцания корабля
            if flash_active:
                if (current_time - flash_time) < ship_flash_duration:  # мерцание в течение установленной длительности
                    # Мерцание: показываем корабль через 100 мс
                    if (current_time // 100) % 2 == 0:
                        screen.blit(ship.image, ship.rect.topleft)
                else:
                    flash_active = False  # Отключаем мерцание
                    # ship.rect.y = 700  # Сброс позиции корабля при необходимости
                    # ship.rect.x = 250  # Сброс позиции корабля при необходимости

            # Обновляем и отображаем взрывы
            for explosion in explosions:
                explosion.update()
                explosion.draw(screen)
            # Обновляем позицию астероидов
            for asteroid in asteroids:
                asteroid.move()
                if not is_irritated_eye:
                    asteroid.draw(screen)

            # Добавляем новые астероиды
            if current_time % 25 == 0:
                asteroids.append(Asteroid(2))
            if (current_time - last_event_time) >= 5000:  # 20000
                last_event_time = current_time
                new_bonus = Bonus((SCREEN_WIDTH_LEVEL, SCREEN_HEIGHT_LEVEL),
                                  bonus_types=tuple(BONUSES.keys()))
                bonuses.add(new_bonus)

            asteroids = [asteroid for asteroid in asteroids if asteroid.y < 900]

            if keys[pygame.K_SPACE]:
                ship.shoot(current_time)
            for bullet in ship.bullets:
                bullet.move()
                if bullet.rect.y < -12:
                    ship.bullets.remove(bullet)

            check_bullet_collision(ship.bullets, asteroids, explosions)

            ship.update()
            # Отображаем хитбокс, если флаг активен
            if show_hitbox:
                ship.draw_hitbox(screen)

            # Отображаем корабль, если он не мерцает
            if not flash_active:
                screen.blit(ship.image, ship.rect.topleft)

            # Отображаем пули
            for bullet in ship.bullets:
                bullet.update()
                screen.blit(bullet.image, bullet.rect.topleft)

            # Обновляем спрайты бонусов
            bonuses.update(current_time)

            # Проверка столкновений между кораблем и бонусами
            collisions = pygame.sprite.spritecollide(ship, bonuses, True)
            for bonus in collisions:
                bonus.apply_effect(interface)
                time_application = current_time

            if (current_time - time_application) / 1000 >= 3:
                for bonus in bonuses:
                    bonus.disable_all_effects()

            # Отображаем все спрайты
            bonuses.draw(screen)
            frame_image = pygame.image.load('data/image/sprites/hp_window.png')
            stretched_image = pygame.transform.scale(frame_image, (600 - 390, 80))
            screen.blit(stretched_image, (390, 0))
            interface.draw_hp_bar(screen)
            interface.draw_score_bar(screen)
            pygame.display.flip()  # Обновляем дисплей
        CLOCK.tick(FPS)


def read_best_scores_from_csv(filename='results.csv'):
    best_scores = {'MAX_SCORED_IN_LVL1': 0, 'MAX_SCORED_IN_LVL2': 0}

    if os.path.isfile(filename):
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row['MAX_SCORED_IN_LVL1']) > best_scores['MAX_SCORED_IN_LVL1']:
                    best_scores['MAX_SCORED_IN_LVL1'] = int(row['MAX_SCORED_IN_LVL1'])
                if int(row['MAX_SCORED_IN_LVL2']) > best_scores['MAX_SCORED_IN_LVL2']:
                    best_scores['MAX_SCORED_IN_LVL2'] = int(row['MAX_SCORED_IN_LVL2'])

    return best_scores


def game_over(level=1):
    global FPS, SCORED, MAX_SCORED_IN_LVL1, MAX_SCORED_IN_LVL2
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(load_music('music background.mp3'))
    pygame.mixer.music.set_volume(0.15)
    pygame.mixer.music.play(loops=-1, fade_ms=3 * 1000)
    squish = pygame.mixer.Sound(f'data/sounds/squish.mp3')
    squish.set_volume(5)
    screen_size = 550, 350
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Game over')
    font = load_font(20)
    string_rendered = font.render("GAME OVER", True, pygame.Color('White'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top, intro_rect.x = 80, 180
    frame_image = load_image('sprites/hp_window.png')
    stretched_image = pygame.transform.scale(frame_image, (300, 80))
    screen.blit(string_rendered, intro_rect), screen.blit(stretched_image, (120, 45))
    if SCORED >= MAX_SCORED_IN_LVL1 and level == 1:
        MAX_SCORED_IN_LVL1 = SCORED
    elif SCORED >= MAX_SCORED_IN_LVL2 and level == 2:
        MAX_SCORED_IN_LVL2 = SCORED
    font = load_font(15)
    for text, y in zip((f"Лучший результат: {MAX_SCORED_IN_LVL1 if level == 1 else MAX_SCORED_IN_LVL2}",
                        f"Текущий результат: {SCORED}"), (260, 290)):
        string_rendered = font.render(text, True, pygame.Color('White'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top, intro_rect.x = y, 30
        screen.blit(string_rendered, intro_rect)

    font = load_font(16)
    for x, text in zip((110, 350), ("Меню", "Рестарт")):
        string_rendered = font.render(text, False, pygame.Color('White'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top, intro_rect.x = 180, x
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 100 <= event.pos[0] <= 177 and 168 <= event.pos[1] <= 204:  # Окрытие меню
                    SOUNDS_CONFIRMING_1.play()
                    start_screen((600, 400))
                elif 343 <= event.pos[0] <= 466 and 170 <= event.pos[1] <= 210:  # Открытие уровня
                    SOUNDS_CONFIRMING_1.play()
                    level_one() if level == 1 else level_two()
                elif 125 <= event.pos[0] <= 409 and 46 <= event.pos[1] <= 120:
                    squish.play()
        pygame.display.flip()
        CLOCK.tick(FPS)


if __name__ == '__main__':
    ship_speed, is_more_bullets, is_irritated_eye, is_neon_bullets = 2.2, False, False, False  # Параметры для бонусов
    music_volume, nickname = 19, ''
    input_window((400, 300))
