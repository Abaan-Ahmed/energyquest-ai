from config.settings import *

def draw_hud(screen, game, font):
    x = GRID_COLS * CELL_SIZE + 20
    y = 40

    lines = [
        f"AI Energy: {game.ai_agent.energy}",
        f"Human Energy: {game.human_agent.energy}",
        f"Nodes Expanded: {getattr(game, 'nodes_expanded', 0)}",
        f"Status: {game.status}",
    ]

    for line in lines:
        label = font.render(line, True, BLACK)
        screen.blit(label, (x, y))
        y += 25
