import pygame
import sys

pygame.init()

size = (400, 400)
screen = pygame.display.set_mode(size)

player = pygame.Surface((50, 50))
player.fill((255, 0, 0))

player_pos = [175, 175]

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            player_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            pass
        elif event.type == pygame.FINGERDOWN:
            print(event)
            player_pos = [event.x*400, event.y*400]
        elif event.type == pygame.FINGERUP:
            pass

    screen.fill((0,0,0))

    screen.blit(player, player_pos)

    pygame.display.update()

pygame.quit()
sys.exit()
