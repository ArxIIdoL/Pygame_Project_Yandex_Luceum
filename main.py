import pygame
import random


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


class Ship(AnimatedSprite):
    def __init__(self, x, y):
        sheet = pygame.image.load("data/image/ship_sprite/ship.png").convert_alpha()
        super().__init__(sheet, 4, 1, x, y)

        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.x = x
        self.y = y
        self.bullets = []
        self.last_shot_time = 0
        self.shoot_delay = 175

        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.x = max(0, min(self.x, 600 - self.width))
        self.y = max(0, min(self.y, 900 - self.height))
        self.rect.topleft = (self.x, self.y)

    def shoot(self, current_time):
        if current_time - self.last_shot_time > self.shoot_delay:
            bullet = Bullet(self.x + self.width // 2, self.y)
            self.bullets.append(bullet)
            self.last_shot_time = current_time


class Bullet(AnimatedSprite):
    def __init__(self, x, y):
        sheet = pygame.image.load("data/image/bullet_sprite/All_Fire_Bullet_Pixel_16x16_00.png").convert_alpha()
        super().__init__(sheet, 4, 1, x, y)
        self.bullet_speed = 1.7

        # Поворачиваем каждый кадр на 90 градусов влево
        self.frames = [pygame.transform.rotate(frame, 90) for frame in self.frames]
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect(center=self.rect.center)

    def move(self):
        self.rect.y -= self.bullet_speed


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 900))
    clock = pygame.time.Clock()
    ship = Ship(275, 700)

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        ship_speed = 1.2
        if keys[pygame.K_a]:
            ship.move(-ship_speed, 0)
        if keys[pygame.K_d]:
            ship.move(ship_speed, 0)
        if keys[pygame.K_w]:
            ship.move(0, -ship_speed)
        if keys[pygame.K_s]:
            ship.move(0, ship_speed)
        if keys[pygame.K_SPACE]:
            ship.shoot(current_time)

        for bullet in ship.bullets:
            bullet.move()
            if bullet.rect.y < 0:  # Проверяем, вышла ли пуля за верхнюю границу
                ship.bullets.remove(bullet)

        screen.fill((0, 0, 0))
        ship.update()
        screen.blit(ship.image, ship.rect.topleft)
        for bullet in ship.bullets:
            bullet.update()
            screen.blit(bullet.image, bullet.rect.topleft)

        pygame.display.flip()
        clock.tick(240)

    pygame.quit()


if __name__ == "__main__":
    main()
