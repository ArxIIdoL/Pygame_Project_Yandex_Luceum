import pygame

class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 90

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.x = max(0, min(self.x, 600 - self.width))
        self.y = max(0, min(self.y, 900 - self.height))

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 900))
    clock = pygame.time.Clock()
    ship = Ship(300, 800)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            ship.move(-5, 0)
        if keys[pygame.K_d]:
            ship.move(5, 0)
        if keys[pygame.K_w]:
            ship.move(0, -5)
        if keys[pygame.K_s]:
            ship.move(0, 5)

        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), (ship.x, ship.y, ship.width, ship.height))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()