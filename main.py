import pygame
import random

class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 90
        self.bullets = []
        self.last_shot_time = 0
        self.shoot_delay = 175

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.x = max(0, min(self.x, 600 - self.width))
        self.y = max(0, min(self.y, 900 - self.height))

    def shoot(self, current_time):
        if current_time - self.last_shot_time > self.shoot_delay:
            bullet = Bullet(self.x + self.width // 2, self.y)
            self.bullets.append(bullet)
            self.last_shot_time = current_time

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.bullet_speed = 1.7

    def move(self):
        self.y -= self.bullet_speed

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 900))
    clock = pygame.time.Clock()
    ship = Ship(300, 700)

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
            if bullet.y < 0:
                ship.bullets.remove(bullet)

        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), (ship.x, ship.y, ship.width, ship.height))
        for bullet in ship.bullets:
            pygame.draw.circle(screen, (255, 0, 0), (bullet.x, bullet.y), bullet.radius)

        pygame.display.flip()
        clock.tick(240)

    pygame.quit()

if __name__ == "__main__":
    main()