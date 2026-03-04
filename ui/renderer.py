import pygame
from config.settings import *

# visual theme
BOARD_BG = (32, 35, 45)
GRID_LINE = (60, 65, 80)

WALL_COLOR = (90, 95, 110)
GOAL_COLOR = (80, 200, 140)

TRAP_FILL = (110, 40, 40)
TRAP_COLOR = (230, 70, 70)

HUMAN_COLOR = (80, 160, 255)
AI_COLOR = (180, 90, 255)

HUMAN_GEM = (255, 210, 70)
AI_GEM = (200, 120, 255)


def draw_grid(screen, game, font):
    grid = game.grid

    # board background
    board_rect = pygame.Rect(0, 0, GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE)
    pygame.draw.rect(screen, BOARD_BG, board_rect)

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):

            rect = pygame.Rect(
                c * CELL_SIZE,
                r * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            # base tile
            pygame.draw.rect(screen, BOARD_BG, rect, border_radius=6)

            # grid lines
            pygame.draw.rect(screen, GRID_LINE, rect, 1, border_radius=6)

            cell = grid.grid[r][c]

            # -----------------------------
            # WALLS
            # -----------------------------
            if cell == 1:
                pygame.draw.rect(screen, WALL_COLOR, rect, border_radius=6)
                pygame.draw.rect(screen, (40, 40, 50), rect, 2, border_radius=6)

            # -----------------------------
            # GOAL
            # -----------------------------
            elif cell == 4:
                pygame.draw.rect(screen, GOAL_COLOR, rect, border_radius=6)

                # inner highlight
                inner = rect.inflate(-12, -12)
                pygame.draw.rect(screen, (255, 255, 255), inner, 2, border_radius=4)

            # -----------------------------
            # TRAPS
            # -----------------------------
            elif (r, c) in grid.traps:

                pygame.draw.rect(screen, TRAP_FILL, rect, border_radius=6)
                pygame.draw.rect(screen, TRAP_COLOR, rect, 2, border_radius=6)

                pygame.draw.line(screen, TRAP_COLOR, rect.topleft, rect.bottomright, 2)
                pygame.draw.line(screen, TRAP_COLOR, rect.topright, rect.bottomleft, 2)

            # -----------------------------
            # GEMS
            # -----------------------------
            elif (r, c) in grid.gems:

                center = rect.center

                # human gem (big)
                pygame.draw.circle(screen, HUMAN_GEM, center, 14)

                # ai gem (small inner)
                pygame.draw.circle(screen, AI_GEM, center, 6)

                # gem value
                val = font.render(str(grid.gems[(r, c)]), True, (30, 30, 30))
                screen.blit(val, val.get_rect(center=center))

    # -----------------------------------
    # DRAW HUMAN AGENT
    # -----------------------------------
    hr, hc = game.human_agent.position
    human_center = (
        hc * CELL_SIZE + CELL_SIZE // 2,
        hr * CELL_SIZE + CELL_SIZE // 2
    )

    pygame.draw.circle(screen, HUMAN_COLOR, human_center, CELL_SIZE // 2 - 6)
    pygame.draw.circle(screen, (255, 255, 255), human_center, CELL_SIZE // 2 - 6, 2)

    # -----------------------------------
    # DRAW AI AGENT
    # -----------------------------------
    ar, ac = game.ai_agent.position
    ai_center = (
        ac * CELL_SIZE + CELL_SIZE // 2,
        ar * CELL_SIZE + CELL_SIZE // 2
    )

    pygame.draw.circle(screen, AI_COLOR, ai_center, CELL_SIZE // 2 - 6)
    pygame.draw.circle(screen, (255, 255, 255), ai_center, CELL_SIZE // 2 - 6, 2)