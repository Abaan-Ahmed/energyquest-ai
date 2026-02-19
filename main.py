import pygame
from core.game import Game
from config.settings import *

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Energy Quest – Intelligent Agent")

clock = pygame.time.Clock()
game = Game(screen)

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            game.handle_click(event.pos)
        if event.type == pygame.KEYDOWN:
            game.handle_key(event.key)

    game.update()
    game.draw()
    pygame.display.flip()

pygame.quit()
