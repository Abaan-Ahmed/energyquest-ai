import pygame
from config.settings import *

def draw_grid(screen, game, font):
    grid = game.grid

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            rect = pygame.Rect(
                c * CELL_SIZE,
                r * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            # Grid outline
            pygame.draw.rect(screen, GRAY, rect, 1)

            cell = grid.grid[r][c]

            # WALLS
            if cell == 1:
                pygame.draw.rect(screen, (70, 70, 70), rect)

            # GOAL
            elif cell == 4:
                pygame.draw.rect(screen, GREEN, rect)

            # TRAPS
            elif (r, c) in grid.traps:
                pygame.draw.rect(screen, RED, rect, 2)
                pygame.draw.line(screen, RED, rect.topleft, rect.bottomright, 2)
                pygame.draw.line(screen, RED, rect.topright, rect.bottomleft, 2)

            # GEMS
            elif (r, c) in grid.gems:
                pygame.draw.circle(screen, YELLOW, rect.center, 10)
                val = font.render(
                    str(grid.gems[(r, c)]),
                    True,
                    BLACK
                )
                screen.blit(val, val.get_rect(center=rect.center))

    # -----------------------------------
    # DRAW HUMAN (BLUE)
    # -----------------------------------
    hr, hc = game.human_agent.position
    pygame.draw.rect(
        screen,
        BLUE,
        pygame.Rect(
            hc * CELL_SIZE,
            hr * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
    )

    # -----------------------------------
    # DRAW AI (PURPLE)
    # -----------------------------------
    ar, ac = game.ai_agent.position
    pygame.draw.rect(
        screen,
        (150, 0, 200),
        pygame.Rect(
            ac * CELL_SIZE,
            ar * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
    )
