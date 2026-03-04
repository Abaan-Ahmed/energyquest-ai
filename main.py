import pygame
import sys

from core.game import Game
from config.settings import *

pygame.init()

# -----------------------------------------
# WINDOW SETUP
# -----------------------------------------
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Energy Quest – Intelligent Agent")

# Internal game surface (fixed resolution)
game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()

# -----------------------------------------
# GAME INSTANCE
# -----------------------------------------
game = Game(game_surface)

running = True

# -----------------------------------------
# MAIN LOOP
# -----------------------------------------
while running:

    clock.tick(FPS)

    window_width, window_height = window.get_size()

    # -------------------------------------
    # CALCULATE PROPER SCALE (keep ratio)
    # -------------------------------------
    scale = min(
        window_width / SCREEN_WIDTH,
        window_height / SCREEN_HEIGHT
    )

    scaled_width = int(SCREEN_WIDTH * scale)
    scaled_height = int(SCREEN_HEIGHT * scale)

    offset_x = (window_width - scaled_width) // 2
    offset_y = (window_height - scaled_height) // 2

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = event.pos

            # convert mouse coordinates to game coordinates
            game_x = (mouse_x - offset_x) / scale
            game_y = (mouse_y - offset_y) / scale

            if 0 <= game_x <= SCREEN_WIDTH and 0 <= game_y <= SCREEN_HEIGHT:
                game.handle_click((game_x, game_y))

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()

            game.handle_key(event.key)

    # -------------------------------------
    # UPDATE
    # -------------------------------------
    game.update()

    # -------------------------------------
    # DRAW TO GAME SURFACE
    # -------------------------------------
    game.draw()

    # -------------------------------------
    # SCALE GAME SURFACE
    # -------------------------------------
    scaled_surface = pygame.transform.smoothscale(
        game_surface,
        (scaled_width, scaled_height)
    )

    # clear background
    window.fill((15, 18, 28))

    # center the game
    window.blit(scaled_surface, (offset_x, offset_y))

    pygame.display.flip()

# -----------------------------------------
# CLEAN EXIT
# -----------------------------------------
pygame.quit()
sys.exit()