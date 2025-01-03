import pygame

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('')
    size = width, height = 600, 900
    screen = pygame.display.set_mode(size)
    fps, clock, running = 50, pygame.time.Clock(), True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        rect = pygame.Rect(250, 800 - 50, 50, 50)
        pygame.draw.rect(screen, (255, 0, 0), rect)
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
