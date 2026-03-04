import pygame
from config.settings import *

# UI colors
PANEL_BG = (35, 38, 50)
SECTION_BG = (45, 50, 65)

TEXT_COLOR = (230, 230, 240)
SUBTEXT = (180, 185, 200)

HUMAN_BAR = (80, 160, 255)
AI_BAR = (180, 90, 255)

BAR_BG = (70, 75, 90)


def draw_hud(screen, game, font):

    panel_x = GRID_COLS * CELL_SIZE
    panel_width = SCREEN_WIDTH - panel_x

    # -----------------------------
    # SIDE PANEL
    # -----------------------------
    panel = pygame.Rect(panel_x, 0, panel_width, SCREEN_HEIGHT)
    pygame.draw.rect(screen, PANEL_BG, panel)

    # Title
    title_font = pygame.font.SysFont(None, 42)
    title = title_font.render("ENERGY QUEST", True, TEXT_COLOR)
    screen.blit(title, (panel_x + 20, 30))

    y = 110

    # -----------------------------
    # AI TYPE
    # -----------------------------
    label = font.render("AI Opponent", True, SUBTEXT)
    screen.blit(label, (panel_x + 20, y))

    y += 25

    ai_type = font.render(game.algorithm, True, TEXT_COLOR)
    screen.blit(ai_type, (panel_x + 20, y))

    y += 50

    # -----------------------------
    # ENERGY SECTION
    # -----------------------------
    section = pygame.Rect(panel_x + 10, y, panel_width - 20, 120)
    pygame.draw.rect(screen, SECTION_BG, section, border_radius=8)

    y += 15

    energy_title = font.render("ENERGY", True, TEXT_COLOR)
    screen.blit(energy_title, (panel_x + 20, y - 10))

    y += 30

    # HUMAN ENERGY BAR
    draw_energy_bar(
        screen,
        panel_x + 20,
        y,
        panel_width - 40,
        game.human_agent.energy,
        HUMAN_BAR,
        "Human",
        font
    )

    y += 40

    # AI ENERGY BAR
    draw_energy_bar(
        screen,
        panel_x + 20,
        y,
        panel_width - 40,
        game.ai_agent.energy,
        AI_BAR,
        "AI",
        font
    )

    y += 60

    # -----------------------------
    # METRICS SECTION
    # -----------------------------
    section = pygame.Rect(panel_x + 10, y, panel_width - 20, 140)
    pygame.draw.rect(screen, SECTION_BG, section, border_radius=8)

    y += 15

    stats_title = font.render("METRICS", True, TEXT_COLOR)
    screen.blit(stats_title, (panel_x + 20, y))

    y += 30

    stats = [
        ("Nodes Expanded", getattr(game, "nodes_expanded", 0)),
        ("Game Status", game.status),
    ]

    for label, value in stats:
        left = font.render(label, True, SUBTEXT)
        right = font.render(str(value), True, TEXT_COLOR)

        screen.blit(left, (panel_x + 20, y))
        screen.blit(right, (panel_x + 160, y))

        y += 28


# --------------------------------------------------
# ENERGY BAR
# --------------------------------------------------
def draw_energy_bar(screen, x, y, width, energy, color, label, font):

    max_energy = 60  # visual cap

    pygame.draw.rect(screen, BAR_BG, (x, y, width, 18), border_radius=6)

    filled = max(0, min(width, int((energy / max_energy) * width)))

    pygame.draw.rect(screen, color, (x, y, filled, 18), border_radius=6)

    label_text = font.render(f"{label}: {energy}", True, TEXT_COLOR)
    screen.blit(label_text, (x, y - 18))