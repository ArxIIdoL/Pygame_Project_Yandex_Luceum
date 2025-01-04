import pygame
from pygame.locals import QUIT


class BackgroundManager:
    def __init__(self, screen, backgrounds):
        self.screen = screen
        self.backgrounds = backgrounds
        self.num_backgrounds = len(self.backgrounds)
        self.scroll_speed = 100
        self.start_time = pygame.time.get_ticks()
        self.y = 0
        self.y1 = -screen.get_height()
        self.current_bg_index = 0
        self.next_bg_index = 1

    def update_and_draw(self):
        # Текущее время
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - self.start_time) / 1000.0  # Преобразование миллисекунд в секунды

        # Двигаем фоны вниз
        self.y = int(elapsed_time * self.scroll_speed % (self.num_backgrounds * self.screen.get_height()))
        self.y1 = int(self.y - self.screen.get_height())

        # Проверка условия: если верхний край прошлого фона ушел за верхнюю границу экрана,
        # начинаем показывать следующий фон
        if self.y <= 0:
            self.current_bg_index = (self.current_bg_index + 1) % self.num_backgrounds
            self.next_bg_index = (self.current_bg_index + 1) % self.num_backgrounds

        # Очищаем экран перед новой отрисовкой
        self.screen.fill((0, 0, 0))  # Черный фон

        # Отображаем два слоя фона
        self.screen.blit(
            self.backgrounds[self.current_bg_index],
            (0, self.y)
        )
        self.screen.blit(
            self.backgrounds[self.next_bg_index],
            (0, self.y1)
        )


def main():
    # Инициализируем Pygame
    pygame.init()

    # Устанавливаем размер окна
    screen_width, screen_height = 600, 900
    screen = pygame.display.set_mode((screen_width, screen_height))

    # Загружаем фоны и сохраняем их в списке
    backgrounds = []
    for i in range(1, 10):
        filename = f'data/image/backgrounds image/level 1/Space Background ({i}).png'
        bg = pygame.image.load(filename)
        bg = pygame.transform.scale(bg, (screen_width, screen_height))
        backgrounds.append(bg)

    # Создаем объект менеджера фонов
    background_manager = BackgroundManager(screen, backgrounds)

    # Основная логика игры
    running = True
    clock = pygame.time.Clock()

    while running:
        # Обрабатываем события
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Обновляем и отрисовываем фоны
        background_manager.update_and_draw()

        # Обновляем дисплей
        pygame.display.flip()

        # Ограничиваем FPS до 60 кадров в секунду
        clock.tick(60)

    # Завершаем работу программы
    pygame.quit()


if __name__ == "__main__":
    main()
