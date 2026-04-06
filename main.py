# ─────────────────────────────────────────────────────────────
#  EnergyQuest  –  main.py
# ─────────────────────────────────────────────────────────────
import sys
import pygame
from core.game       import Game
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

pygame.init()
pygame.display.set_caption("EnergyQuest – AI vs Human")

window       = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
clock        = pygame.time.Clock()
game         = Game(game_surface)

_fullscreen = False   # manage fullscreen manually — toggle_fullscreen is buggy on Windows

running = True
while running:
    clock.tick(FPS)
    win_w, win_h = window.get_size()
    scale = min(win_w / SCREEN_WIDTH, win_h / SCREEN_HEIGHT)
    sw, sh = int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)
    ox, oy = (win_w - sw) // 2, (win_h - sh) // 2

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            if not _fullscreen:
                window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            gx = (mx - ox) / scale
            gy = (my - oy) / scale
            if 0 <= gx <= SCREEN_WIDTH and 0 <= gy <= SCREEN_HEIGHT:
                game.handle_click((gx, gy))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                _fullscreen = not _fullscreen
                if _fullscreen:
                    window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    window = pygame.display.set_mode(
                        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE
                    )
            else:
                game.handle_key(event.key)

    game.update()
    game.draw()

    scaled = pygame.transform.smoothscale(game_surface, (sw, sh))
    window.fill((6, 8, 16))
    window.blit(scaled, (ox, oy))
    pygame.display.flip()

pygame.quit()
sys.exit()
