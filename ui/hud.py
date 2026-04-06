# ─────────────────────────────────────────────────────────────
#  EnergyQuest  –  ui/hud.py
# ─────────────────────────────────────────────────────────────
import pygame
import math
from config.settings import *

PANEL_X = GRID_OFFSET_X + GRID_COLS * CELL_SIZE + 22
PANEL_W = SCREEN_WIDTH - PANEL_X - 12


# ══════════════════════════════════════════════════════════════
#  Low-level helpers
# ══════════════════════════════════════════════════════════════
def _alpha(surf, color, rect, alpha, radius=0):
    s = pygame.Surface((max(1, rect.w), max(1, rect.h)), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), s.get_rect(), border_radius=radius)
    surf.blit(s, (rect.x, rect.y))


def _card(surf, rect, radius=10, tint=None):
    pygame.draw.rect(surf, tint or HUD_CARD_BG, rect, border_radius=radius)
    pygame.draw.rect(surf, HUD_BORDER, rect, 1, border_radius=radius)
    _alpha(surf, (255, 255, 255),
           pygame.Rect(rect.x + 1, rect.y + 1, rect.w - 2, max(1, rect.h // 3)),
           7, radius=radius)


def _lerp_col(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _energy_col(ratio):
    # ratio MUST be clamped to [0, 1] before calling this function.
    # If not clamped, _lerp_col can produce values outside [0, 255]
    # which Pygame rejects as an invalid color argument.
    ratio = max(0.0, min(1.0, ratio))
    if ratio >= 0.5:
        return _lerp_col(E_MID, E_HIGH, (ratio - 0.5) * 2)
    return _lerp_col(E_LOW, E_MID, ratio * 2)


def _label(surf, font, text, x, y, color=None):
    lbl = font.render(text, True, color or HUD_TEXT)
    surf.blit(lbl, (x, y))
    return lbl.get_width()


def _label_r(surf, font, text, rx, y, color=None):
    lbl = font.render(text, True, color or HUD_TEXT)
    surf.blit(lbl, (rx - lbl.get_width(), y))


def _label_c(surf, font, text, cx, y, color=None):
    lbl = font.render(text, True, color or HUD_TEXT)
    surf.blit(lbl, (cx - lbl.get_width() // 2, y))


# ══════════════════════════════════════════════════════════════
#  Segmented energy bar
# ══════════════════════════════════════════════════════════════
def _energy_bar(surf, rect, value, max_val, tick=0, segments=20):
    # Clamp ratio here as well to be safe
    ratio = max(0.0, min(1.0, value / max_val)) if max_val else 0.0
    color = _energy_col(ratio)

    pygame.draw.rect(surf, E_BAR_BG, rect, border_radius=5)
    pygame.draw.rect(surf, E_BAR_BORD, rect, 1, border_radius=5)

    if ratio <= 0:
        return

    if ratio < 0.25:
        pulse = abs(math.sin(tick * 0.18))
        color = _lerp_col(color, (255, 255, 255), pulse * 0.40)

    seg_w  = (rect.w - segments + 1) / segments
    filled = int(ratio * segments)
    for i in range(filled):
        sx  = rect.x + int(i * (seg_w + 1))
        seg = pygame.Rect(sx, rect.y + 1, max(1, int(seg_w)), rect.h - 2)
        shade = _lerp_col(color, tuple(min(255, v + 40) for v in color),
                          i / max(1, segments - 1))
        pygame.draw.rect(surf, shade, seg, border_radius=3)

    fill_w = int(ratio * rect.w)
    sheen  = pygame.Rect(rect.x, rect.y + 1, fill_w, rect.h // 2 - 1)
    _alpha(surf, tuple(min(255, v + 70) for v in color), sheen, 55, radius=4)


# ══════════════════════════════════════════════════════════════
#  Mini radar map
# ══════════════════════════════════════════════════════════════
def _mini_map(surf, game, x, y, w, h, fonts):
    from core.grid import WALL, GEM, TRAP, GOAL, GEM_A

    map_rect = pygame.Rect(x, y, w, h)
    _card(surf, map_rect, radius=8, tint=(12, 15, 28))

    pw  = w - 8
    ph  = h - 8
    ox  = x + 4
    oy  = y + 4
    cw  = pw / GRID_COLS
    ch  = ph / GRID_ROWS

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            cell = game.grid.grid[r][c]
            cx2  = int(ox + c * cw)
            cy2  = int(oy + r * ch)
            rc   = pygame.Rect(cx2, cy2, max(1, int(cw) - 1), max(1, int(ch) - 1))
            if   cell == WALL:  pygame.draw.rect(surf, WALL_FACE, rc)
            elif cell == GEM:   pygame.draw.rect(surf, GEM_CORE,   rc)
            elif cell == GEM_A: pygame.draw.rect(surf, GEM_A_CORE, rc)
            elif cell == TRAP:  pygame.draw.rect(surf, TRAP_CORE,  rc)
            elif cell == GOAL:  pygame.draw.rect(surf, GOAL_CORE,  rc)

    for agent, col in [(game.human_agent, H_CORE), (game.ai_agent, A_CORE)]:
        ar, ac = agent.position
        ax = int(ox + ac * cw + cw / 2)
        ay = int(oy + ar * ch + ch / 2)
        pygame.draw.circle(surf, col, (ax, ay), max(2, int(min(cw, ch) * 0.6)))
        pygame.draw.circle(surf, (255, 255, 255), (ax, ay), max(1, int(min(cw, ch) * 0.3)))


# ══════════════════════════════════════════════════════════════
#  Agent stat card
# ══════════════════════════════════════════════════════════════
def _agent_card(surf, rect, fonts, agent, color, label, extra_rows, tick):
    f_h, f_n, f_s = fonts
    _card(surf, rect, radius=10)

    x, y, w = rect.x, rect.y, rect.w

    pygame.draw.rect(surf, color,
                     pygame.Rect(x, y + 8, 3, rect.h - 16), border_radius=1)

    y += 10
    lbl = f_h.render(label, True, color)
    surf.blit(lbl, (x + 12, y))
    y += lbl.get_height() + 7

    bar = pygame.Rect(x + 12, y, w - 60, 14)
    _energy_bar(surf, bar, agent.energy, START_ENERGY, tick)

    # FIX: clamp ratio to [0, 1] before computing color
    # Without this, gems can push energy above START_ENERGY, making
    # ratio > 1.0, which causes _lerp_col to return negative RGB values
    # and Pygame raises ValueError: invalid color argument.
    ratio  = max(0.0, min(1.0, agent.energy / START_ENERGY))
    ecol   = _energy_col(ratio)
    ev_txt = f"{max(0, agent.energy)}"
    ev_lbl = f_n.render(ev_txt, True, ecol)
    surf.blit(ev_lbl, (x + w - 46, y - 1))
    y += 20

    pygame.draw.line(surf, HUD_BORDER, (x + 10, y), (x + w - 10, y))
    y += 6

    for left, right in extra_rows:
        ll = f_s.render(left,  True, HUD_MUTED)
        rl = f_s.render(right, True, HUD_TEXT)
        surf.blit(ll, (x + 12, y))
        surf.blit(rl, (x + w - 12 - rl.get_width(), y))
        y += ll.get_height() + 5


# ══════════════════════════════════════════════════════════════
#  Scrolling ticker
# ══════════════════════════════════════════════════════════════
_ticker_x = float(SCREEN_WIDTH)


def _draw_ticker(surf, font, tick, state_txt):
    global _ticker_x
    txt = (f"  ·  {state_txt}  ·  Arrow Keys to move  ·  "
           "Gold gems = yours, Purple gems = AI  ·  ESC = menu  ·  F11 = fullscreen  ")
    lbl = font.render(txt, True, HUD_DIM)
    _ticker_x -= 1.2
    if _ticker_x < -lbl.get_width():
        _ticker_x = float(SCREEN_WIDTH)
    surf.blit(lbl, (int(_ticker_x), SCREEN_HEIGHT - 22))


# ══════════════════════════════════════════════════════════════
#  Main HUD draw
# ══════════════════════════════════════════════════════════════
def draw_hud(screen, game, fonts):
    from core.game import (STATE_MENU, STATE_COMPETING, STATE_FINISHED,
                           STATE_COUNTDOWN, STATE_CREDITS)
    f_title, f_h, f_n, f_s = fonts

    px = PANEL_X
    pw = PANEL_W
    py = GRID_OFFSET_Y - 4

    # Top bar
    pygame.draw.rect(screen, HUD_BG,
                     pygame.Rect(0, 0, SCREEN_WIDTH, GRID_OFFSET_Y - 4))
    pygame.draw.line(screen, HUD_BORDER,
                     (0, GRID_OFFSET_Y - 5), (SCREEN_WIDTH, GRID_OFFSET_Y - 5))

    t_lbl = f_title.render("ENERGY QUEST", True, HUD_TEXT)
    screen.blit(t_lbl, (GRID_OFFSET_X + 2, 12))

    algo_col = {"BFS": H_CORE, "A*": GOAL_CORE, "GA": A_BRIGHT}
    ac = algo_col.get(game.algorithm, HUD_ACCENT)
    bdg_txt  = f"  {game.algorithm}  "
    bdg_lbl  = f_n.render(bdg_txt, True, ac)
    bdg_rect = pygame.Rect(px, 14, bdg_lbl.get_width() + 8, bdg_lbl.get_height() + 6)
    _alpha(screen, ac, bdg_rect, 28, radius=6)
    pygame.draw.rect(screen, ac, bdg_rect, 1, border_radius=6)
    screen.blit(bdg_lbl, (px + 4, 17))

    state_tags = {
        STATE_MENU:      "Select algorithm & start",
        STATE_COUNTDOWN: "Get ready!",
        STATE_COMPETING: "Race in progress",
        STATE_FINISHED:  "Race finished",
    }
    tag_txt = state_tags.get(game.state, "")
    screen.blit(f_s.render(tag_txt, True, HUD_MUTED),
                (px + bdg_rect.w + 14, 22))

    # Right panel background
    panel_bg = pygame.Rect(px - 10, py, pw + 12, GRID_ROWS * CELL_SIZE + 8)
    pygame.draw.rect(screen, HUD_BG, panel_bg)
    pygame.draw.line(screen, HUD_BORDER,
                     (px - 10, py), (px - 10, py + panel_bg.h))

    # Bottom ticker strip
    bot_y = GRID_OFFSET_Y + GRID_ROWS * CELL_SIZE + 4
    bot_h = SCREEN_HEIGHT - bot_y
    pygame.draw.rect(screen, HUD_BG, pygame.Rect(0, bot_y, SCREEN_WIDTH, bot_h))
    pygame.draw.line(screen, HUD_BORDER, (0, bot_y), (SCREEN_WIDTH, bot_y))
    _draw_ticker(screen, f_s, game.tick, tag_txt)

    if game.state in (STATE_MENU, STATE_COUNTDOWN):
        _panel_menu(screen, game, fonts, px, py, pw)
    elif game.state == STATE_COMPETING:
        _panel_live(screen, game, fonts, px, py, pw)
    elif game.state == STATE_FINISHED:
        _panel_results(screen, game, fonts, px, py, pw)


# ══════════════════════════════════════════════════════════════
#  Menu panel
# ══════════════════════════════════════════════════════════════
def _panel_menu(screen, game, fonts, px, py, pw):
    f_title, f_h, f_n, f_s = fonts

    for btn in game.buttons:
        if btn.action in ("BFS", "A*", "GA"):
            btn.update_hover(pygame.mouse.get_pos())
            btn.draw(screen, f_n, selected=(btn.action == game.algorithm))

    y = py + 60

    descs = {
        "BFS": ("Breadth-First Search",
                "Uninformed baseline, finds shortest path.",
                "Counts fewest steps; ignores energy."),
        "A*":  ("A* Search",
                "Heuristic-guided, f(n) = g(n) + h(n).",
                "Maximises remaining energy on arrival."),
        "GA":  ("Genetic Algorithm",
                "Evolutionary search, 80 gen x 100 chromosomes.",
                "Energy-optimised stochastic pathfinding."),
    }
    title, d1, d2 = descs.get(game.algorithm, ("", "", ""))
    ic = pygame.Rect(px, y, pw - 10, 82)
    _card(screen, ic)
    screen.blit(f_n.render(title, True, HUD_TEXT),  (px + 12, y + 10))
    screen.blit(f_s.render(d1,    True, HUD_MUTED), (px + 12, y + 34))
    screen.blit(f_s.render(d2,    True, HUD_MUTED), (px + 12, y + 52))
    y += 92

    # Updated legend — shows both gem types
    legend = [
        (GEM_CORE,    "Gold gem  — yours only (+energy)"),
        (GEM_A_CORE,  "Purple gem — AI only  (+energy)"),
        (TRAP_BRIGHT, "Trap   — penalises anyone"),
        (GOAL_CORE,   "Goal   — reach to finish"),
    ]
    lc = pygame.Rect(px, y, pw - 10, len(legend) * 26 + 22)
    _card(screen, lc)
    screen.blit(f_s.render("MAP LEGEND", True, HUD_DIM), (px + 12, y + 8))
    for i, (col, txt) in enumerate(legend):
        ly = y + 28 + i * 26
        pygame.draw.circle(screen, col, (px + 20, ly + 8), 7)
        screen.blit(f_s.render(txt, True, HUD_TEXT), (px + 36, ly))
    y += lc.h + 10

    ec = pygame.Rect(px, y, pw - 10, 76)
    _card(screen, ec)
    screen.blit(f_h.render("ENERGY RULES", True, HUD_DIM),  (px + 12, y + 8))
    screen.blit(f_s.render(f"Start:          {START_ENERGY}", True, HUD_TEXT), (px + 12, y + 30))
    screen.blit(f_s.render(f"Per move:    -{MOVE_COST}",     True, HUD_MUTED), (px + 12, y + 48))
    screen.blit(f_s.render(f"Trap hit:     -{TRAP_COST}",   True, (210, 65, 65)), (px + 150, y + 48))
    y += 86

    map_h = min(180, GRID_ROWS * CELL_SIZE - (y - py) - 100)
    if map_h > 80:
        _mini_map(screen, game, px, y, pw - 10, map_h, fonts)
        y += map_h + 10

    for btn in game.buttons:
        if btn.action not in ("BFS", "A*", "GA"):
            btn.update_hover(pygame.mouse.get_pos())
            btn.draw(screen, f_n)


# ══════════════════════════════════════════════════════════════
#  Live race panel
# ══════════════════════════════════════════════════════════════
def _panel_live(screen, game, fonts, px, py, pw):
    f_title, f_h, f_n, f_s = fonts
    y = py + 8

    elapsed = (pygame.time.get_ticks() - game.race_start_ms) / 1000
    t_lbl   = f_n.render(f"{elapsed:.1f}s", True, HUD_MUTED)
    screen.blit(t_lbl, (px + pw - 12 - t_lbl.get_width(), y))
    y += t_lbl.get_height() + 4

    h = game.human_agent
    a = game.ai_agent
    algo_col = {"BFS": H_CORE, "A*": GOAL_CORE, "GA": A_BRIGHT}
    ac = algo_col.get(game.algorithm, A_CORE)

    h_rows = [("Steps",  str(h.steps)),
              ("Gems",   str(len(h.collected_gems))),
              ("Energy", f"{max(0, h.energy)} / {START_ENERGY}")]
    hc = pygame.Rect(px, y, pw - 10, 118)
    _agent_card(screen, hc, (f_h, f_n, f_s), h, H_CORE, "  YOU  (Human)", h_rows, game.tick)
    y += 126

    a_rows = [("Algorithm", game.algorithm),
              ("Steps",     str(a.steps)),
              ("Gems",      str(len(a.collected_gems))),
              ("Energy",    f"{max(0, a.energy)} / {START_ENERGY}")]
    acard = pygame.Rect(px, y, pw - 10, 130)
    _agent_card(screen, acard, (f_h, f_n, f_s), a, ac, f"  AI  ({game.algorithm})", a_rows, game.tick)
    y += 138

    map_h = 165
    _mini_map(screen, game, px, y, pw - 10, map_h, fonts)
    y += map_h + 10

    ci = pygame.Rect(px, y, pw - 10, 52)
    _card(screen, ci)
    screen.blit(f_s.render("AI SEARCH STATS", True, HUD_DIM),   (px + 12, y + 7))
    screen.blit(f_s.render(f"{game.nodes_expanded:,} nodes expanded", True, HUD_TEXT),
                (px + 12, y + 26))
    screen.blit(f_s.render(f"Plan time:  {game.ai_time:.4f}s",  True, HUD_MUTED),
                (px + 168, y + 26))


# ══════════════════════════════════════════════════════════════
#  Results panel
# ══════════════════════════════════════════════════════════════
def _panel_results(screen, game, fonts, px, py, pw):
    f_title, f_h, f_n, f_s = fonts
    y = py + 12

    h  = game.human_agent
    a  = game.ai_agent
    cx = px + (pw - 10) // 2

    wmap = {
        "HUMAN WINS": ((255, 210, 80),  "YOU WIN!"),
        "AI WINS":    ((190, 110, 255), "AI WINS"),
        "DRAW":       ((175, 188, 215), "DRAW"),
    }
    wcolor, wtxt = wmap.get(game.winner, ((200, 200, 200), "?"))
    wlbl = f_h.render(wtxt, True, wcolor)
    glow_r = pygame.Rect(cx - wlbl.get_width() // 2 - 14, y - 4,
                         wlbl.get_width() + 28, wlbl.get_height() + 8)
    _alpha(screen, wcolor, glow_r, 22, radius=8)
    pygame.draw.rect(screen, wcolor, glow_r, 1, border_radius=8)
    screen.blit(wlbl, (cx - wlbl.get_width() // 2, y))
    y += wlbl.get_height() + 14

    algo_col = {"BFS": H_CORE, "A*": GOAL_CORE, "GA": A_BRIGHT}
    ac   = algo_col.get(game.algorithm, A_CORE)
    col_w = (pw - 10) // 3

    headers = [("",        HUD_DIM),
               ("You",     H_CORE),
               (game.algorithm, ac)]
    rows = [
        ("Energy", str(max(0, h.energy)), str(max(0, a.energy))),
        ("Steps",  str(h.steps),          str(a.steps)),
        ("Gems",   str(len(h.collected_gems)), str(len(a.collected_gems))),
    ]

    hr = pygame.Rect(px, y, pw - 10, 26)
    pygame.draw.rect(screen, HUD_CARD_HI, hr, border_radius=6)
    pygame.draw.rect(screen, HUD_BORDER,  hr, 1, border_radius=6)
    for ci, (txt, col) in enumerate(headers):
        lbl = f_s.render(txt, True, col)
        screen.blit(lbl, (px + ci * col_w + col_w // 2 - lbl.get_width() // 2, y + 5))
    y += 28

    for ri, (lbl, hv, av) in enumerate(rows):
        row_r = pygame.Rect(px, y, pw - 10, 24)
        if ri % 2 == 0:
            _card(screen, row_r, radius=4)
        else:
            pygame.draw.rect(screen, HUD_CARD_BG, row_r, border_radius=4)

        if hv != av:
            try:
                win_ci = 1 if int(hv) > int(av) else 2
                win_r  = pygame.Rect(px + win_ci * col_w, y, col_w, 24)
                _alpha(screen, GOAL_GLOW, win_r, 38, radius=4)
            except ValueError:
                pass

        for ci, txt in enumerate([lbl, hv, av]):
            col = HUD_MUTED if ci == 0 else HUD_TEXT
            ll  = f_s.render(txt, True, col)
            screen.blit(ll, (px + ci * col_w + col_w // 2 - ll.get_width() // 2, y + 4))
        y += 26

    y += 8

    sc = pygame.Rect(px, y, pw - 10, 52)
    _card(screen, sc)
    screen.blit(f_s.render("AI SEARCH STATS", True, HUD_DIM), (px + 12, y + 7))
    screen.blit(f_s.render(
        f"{game.nodes_expanded:,} nodes  |  {game.ai_time:.4f}s plan time",
        True, HUD_TEXT), (px + 12, y + 26))
    y += 60

    map_h = 145
    _mini_map(screen, game, px, y, pw - 10, map_h, fonts)
    y += map_h + 10

    for btn in game.buttons:
        if btn.action not in ("BFS", "A*", "GA"):
            btn.update_hover(pygame.mouse.get_pos())
            btn.draw(screen, f_n)
