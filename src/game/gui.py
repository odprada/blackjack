import pygame

pygame.init()
screen = pygame.display.set_mode((720, 1280))
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("green")

    pygame.display.flip()

    clock.tick(60)

pygame.quit()