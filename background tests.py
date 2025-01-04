import pygame
from pygame.locals import QUIT

# Константы
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 900
SCROLL_SPEED = 2  # Скорость прокрутки


class BackgroundManager:
    def __init__(self, screen, backgrounds):
        self.screen = screen
        self.backgrounds = backgrounds
        self.bg_count = len(backgrounds)
        self.y_offsets = [i * SCREEN_HEIGHT for i in range(self.bg_count)]  # Смещение для каждого фона

    def update_and_draw(self):
        # Двигаем фоны вниз
        for i in range(self.bg_count):
            self.y_offsets[i] += SCROLL_SPEED

            # Если фон уходит вниз, сбрасываем его на верхнюю позицию
            if self.y_offsets[i] >= SCREEN_HEIGHT:
                self.y_offsets[i] = (self.y_offsets[i] - SCREEN_HEIGHT * self.bg_count)

        # Очищаем экран перед новой отрисовкой
        self.screen.fill((0, 0, 0))  # Черный фон

        # Отображаем фоны
        for i in range(self.bg_count):
            self.screen.blit(self.backgrounds[i], (0, self.y_offsets[i]))


def main():
    # Инициализируем Pygame
    pygame.init()

    # Создаем окно
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Загружаем фоны
    backgrounds = []
    for i in range(1, 4):  # Предполагаем, что у вас есть три изображения
        filename = f'data/image/backgrounds image/level 1/Space Background ({i}).png'
        bg = pygame.image.load(filename)
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        backgrounds.append(bg)

    # Создаем объект менеджера фонов
    background_manager = BackgroundManager(screen, backgrounds)

    # Основной игровой цикл
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Обновляем и отрисовываем фон
        background_manager.update_and_draw()

        # Обновляем дисплей
        pygame.display.flip()

        # Ограничиваем FPS до 60 кадров в секунду
        clock.tick(240)

    # Завершаем работу программы
    pygame.quit()


if __name__ == "__main__":
    main()