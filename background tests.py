# import pygame
#
# # Определение цветов
# BLACK = (0, 0, 0)
# WHITE = (255, 255, 255)
# RED = (255, 0, 0)
#
# # Начальная установка
# pygame.init()
# screen = pygame.display.set_mode((600, 900))
# clock = pygame.time.Clock()
#
#
# class EnergyCharge(object):
#     def __init__(self, x, y, width, height):
#         self.x = x
#         self.y = y
#         self.width = width
#         self.height = height
#         self.color = RED
#
#     def draw(self, surface):
#         rect = pygame.Rect(self.x, self.y, self.width, self.height)
#         pygame.draw.rect(surface, self.color, rect)
#
#
# # # Создание спрайта энергетического заряда
# # energy_charge = EnergyCharge(100, 100, 8, 35)
#
#
# # Основной цикл игры
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#
#     screen.fill(BLACK)
#     rect = pygame.Rect(600 - 180, 50, 180, 50)
#     pygame.draw.rect(screen, 'Red', rect)
#     rect = pygame.Rect(300, 700, 50, 90)
#     pygame.draw.rect(screen, 'white', rect)
#
#     pygame.display.flip()
#     clock.tick(60)
def change_health(take_damage=True):
    global hp_bar
    try:
        if take_damage:
            hp_bar[hp_bar.index(True)] = False
        else:
            hp_bar[hp_bar.index(False)] = True
    except ValueError:
        print('Xn')


hp_bar = [True] * 3
change_health(take_damage=False)
change_health(take_damage=False)
change_health()
print(hp_bar)
