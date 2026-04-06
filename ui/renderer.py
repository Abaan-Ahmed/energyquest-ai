# ─────────────────────────────────────────────────────────────
#  EnergyQuest  –  ui/renderer.py
# ─────────────────────────────────────────────────────────────
import pygame
import math
from config.settings import *
from core.grid import EMPTY, WALL, GEM, TRAP, GOAL, GEM_A, GEM_BOTH

CS  = CELL_SIZE
CS2 = CELL_SIZE // 2


# ══════════════════════════════════════════════════════════════
#  Coordinate helpers
# ══════════════════════════════════════════════════════════════
def cell_center(r, c):
    return (GRID_OFFSET_X + c * CS + CS2,
            GRID_OFFSET_Y + r * CS + CS2)


def cell_rect(r, c):
    return pygame.Rect(GRID_OFFSET_X + c * CS,
                       GRID_OFFSET_Y + r * CS,
                       CS, CS)


# ══════════════════════════════════════════════════════════════
#  Alpha-blend helpers (cached circles)
# ══════════════════════════════════════════════════════════════
_circle_cache: dict = {}


def _acircle(surf, color, cx, cy, radius, alpha):
    key = (radius, color, alpha)
    if key not in _circle_cache:
        d = radius * 2 + 2
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, alpha), (radius + 1, radius + 1), radius)
        _circle_cache[key] = s
    surf.blit(_circle_cache[key], (cx - radius - 1, cy - radius - 1))


def _arect(surf, color, rect, alpha, radius=0):
    s = pygame.Surface((max(1, rect.w), max(1, rect.h)), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), s.get_rect(), border_radius=radius)
    surf.blit(s, (rect.x, rect.y))


def _lerp_col(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ══════════════════════════════════════════════════════════════
#  Cell renderers
# ══════════════════════════════════════════════════════════════

def _draw_empty(surf, r, c):
    bg = GRID_CELL_ALT if (r + c) % 2 else GRID_CELL_BG
    pygame.draw.rect(surf, bg, cell_rect(r, c))


def _draw_wall(surf, r, c):
    rc = cell_rect(r, c)
    x, y, w, h = rc.x, rc.y, rc.w, rc.h
    pygame.draw.rect(surf, WALL_FACE, rc)
    bevel = 5
    pygame.draw.rect(surf, WALL_HI,    pygame.Rect(x, y, w, bevel))
    pygame.draw.rect(surf, WALL_HI,    pygame.Rect(x, y, bevel, h))
    pygame.draw.rect(surf, WALL_SHADE, pygame.Rect(x, y + h - bevel, w, bevel))
    pygame.draw.rect(surf, WALL_SHADE, pygame.Rect(x + w - bevel, y, bevel, h))
    pygame.draw.rect(surf, WALL_TOP,   pygame.Rect(x, y, 3, 3))
    pygame.draw.rect(surf, WALL_BASE,  pygame.Rect(x + w - 3, y + h - 3, 3, 3))
    for i in range(2):
        iy = y + 14 + i * 14
        if iy < y + h - 4:
            pygame.draw.line(surf, WALL_CRACK, (x + 8, iy), (x + w - 8, iy), 1)


def _draw_start(surf, r, c, font):
    rc     = cell_rect(r, c)
    cx, cy = rc.centerx, rc.centery
    pygame.draw.rect(surf, START_BG, rc)
    sz, lw = 9, 2
    for ox2, oy2, sx, sy in [(rc.x, rc.y, 1, 1), (rc.right, rc.y, -1, 1),
                              (rc.x, rc.bottom, 1, -1), (rc.right, rc.bottom, -1, -1)]:
        pygame.draw.line(surf, START_DIM, (ox2, oy2), (ox2 + sx * sz, oy2), lw)
        pygame.draw.line(surf, START_DIM, (ox2, oy2), (ox2, oy2 + sy * sz), lw)
    lbl = font.render("S", True, START_CORE)
    surf.blit(lbl, lbl.get_rect(center=(cx, cy)))


def _draw_gem_shape(surf, r, c, t,
                    core, bright, glow, deep, edge, label_char, label_col, font,
                    cx_off=0, scale=1.0):
    """Shared gem drawing for both human (gold) and AI (purple) gems."""
    rc     = cell_rect(r, c)
    cx     = rc.centerx + cx_off
    cy     = rc.centery
    pygame.draw.rect(surf, GRID_CELL_BG, rc)

    pulse = 1.0 + 0.10 * math.sin(t * 0.065 + r * 0.8 + c * 0.5)
    size  = CS * 0.28 * pulse * scale
    angle = t * 0.042 + (r + c) * 0.4

    # Glow layers
    _acircle(surf, glow, int(cx), cy, int(size) + 14, 18)
    _acircle(surf, glow, int(cx), cy, int(size) +  8, 38)
    _acircle(surf, glow, int(cx), cy, int(size) +  3, 68)

    # 8-point faceted gem body
    pts_outer, pts_inner = [], []
    for i in range(8):
        a = angle + i * math.pi / 4
        pts_outer.append((cx + math.cos(a) * size,
                          cy + math.sin(a) * size * 1.18))
    for i in range(8):
        a = angle + i * math.pi / 4 + math.pi / 8
        pts_inner.append((cx + math.cos(a) * size * 0.52,
                          cy + math.sin(a) * size * 0.52 * 1.18))
    pts = []
    for i in range(8):
        pts.append(pts_outer[i])
        pts.append(pts_inner[i])

    pygame.draw.polygon(surf, deep, [(p[0] + 2, p[1] + 3) for p in pts])
    pygame.draw.polygon(surf, core, pts)
    pygame.draw.polygon(surf, edge, pts, 1)

    _arect(surf, bright,
           pygame.Rect(int(cx - size), int(cy - size * 1.3),
                       int(size * 2), int(size)), 60, radius=2)

    # Sparkle
    sp_angle = angle * 1.3
    sp_r     = size * 0.40
    sp_cx    = int(cx - size * 0.22)
    sp_cy    = int(cy - size * 0.32)
    for i in range(4):
        a  = sp_angle + i * math.pi / 2
        a2 = sp_angle + i * math.pi / 2 + math.pi / 4
        p1 = (sp_cx + math.cos(a)  * sp_r,       sp_cy + math.sin(a)  * sp_r)
        p2 = (sp_cx + math.cos(a2) * sp_r * 0.3, sp_cy + math.sin(a2) * sp_r * 0.3)
        p3 = (sp_cx + math.cos(a  + math.pi / 2) * sp_r,
              sp_cy + math.sin(a  + math.pi / 2) * sp_r)
        pygame.draw.polygon(surf, (255, 255, 228), [p1, p2, p3])

    # Small owner label (H or A) at bottom of cell
    lbl = font.render(label_char, True, label_col)
    lbl_small = pygame.transform.scale(lbl, (max(8, lbl.get_width() * 8 // 10),
                                              max(8, lbl.get_height() * 8 // 10)))
    surf.blit(lbl_small, lbl_small.get_rect(
        center=(int(cx), rc.y + rc.h - lbl_small.get_height() // 2 - 5)
    ))


def _draw_gem(surf, r, c, t, font):
    """Gold gem — human only."""
    _draw_gem_shape(surf, r, c, t,
                    GEM_CORE, GEM_BRIGHT, GEM_GLOW, GEM_DEEP, GEM_EDGE,
                    "H", H_BRIGHT, font)


def _draw_gem_ai(surf, r, c, t, font):
    """Purple gem — AI only."""
    _draw_gem_shape(surf, r, c, t,
                    GEM_A_CORE, GEM_A_BRIGHT, GEM_A_GLOW, GEM_A_DEEP, GEM_A_EDGE,
                    "A", A_BRIGHT, font)


def _draw_gem_both(surf, r, c, t, font):
    """
    Paired tile — gold (human) gem on the left, purple (AI) gem on the right.
    Both gems are drawn smaller (0.58 scale) so they fit side-by-side.
    """
    rc     = cell_rect(r, c)
    cx, cy = rc.centerx, rc.centery
    # Draw shared cell background once
    pygame.draw.rect(surf, GRID_CELL_BG, rc)

    offset = int(CS * 0.20)
    scale  = 0.58

    # Gold gem – left
    _draw_gem_shape_raw(surf, rc, cx - offset, cy, t, r, c,
                        GEM_CORE, GEM_BRIGHT, GEM_GLOW, GEM_DEEP, GEM_EDGE,
                        "H", H_BRIGHT, font, scale)
    # Purple gem – right
    _draw_gem_shape_raw(surf, rc, cx + offset, cy, t, r, c,
                        GEM_A_CORE, GEM_A_BRIGHT, GEM_A_GLOW, GEM_A_DEEP, GEM_A_EDGE,
                        "A", A_BRIGHT, font, scale)


def _draw_gem_shape_raw(surf, rc, cx, cy, t, r, c,
                        core, bright, glow, deep, edge,
                        label_char, label_col, font, scale):
    """
    Internal helper – draws a single gem body at an arbitrary (cx, cy)
    without overwriting the cell background.
    """
    pulse = 1.0 + 0.10 * math.sin(t * 0.065 + r * 0.8 + c * 0.5)
    size  = CS * 0.28 * pulse * scale
    angle = t * 0.042 + (r + c) * 0.4

    _acircle(surf, glow, int(cx), int(cy), int(size) + 9,  15)
    _acircle(surf, glow, int(cx), int(cy), int(size) + 5,  30)
    _acircle(surf, glow, int(cx), int(cy), int(size) + 2,  55)

    pts_outer, pts_inner = [], []
    for i in range(8):
        a = angle + i * math.pi / 4
        pts_outer.append((cx + math.cos(a) * size,
                          cy + math.sin(a) * size * 1.18))
    for i in range(8):
        a = angle + i * math.pi / 4 + math.pi / 8
        pts_inner.append((cx + math.cos(a) * size * 0.52,
                          cy + math.sin(a) * size * 0.52 * 1.18))
    pts = []
    for i in range(8):
        pts.append(pts_outer[i])
        pts.append(pts_inner[i])

    pygame.draw.polygon(surf, deep, [(p[0] + 1, p[1] + 2) for p in pts])
    pygame.draw.polygon(surf, core, pts)
    pygame.draw.polygon(surf, edge, pts, 1)

    _arect(surf, bright,
           pygame.Rect(int(cx - size), int(cy - size * 1.3),
                       int(size * 2), int(size)), 55, radius=2)

    # Tiny sparkle
    sp_angle = angle * 1.3
    sp_r     = size * 0.35
    sp_cx    = int(cx - size * 0.20)
    sp_cy    = int(cy - size * 0.28)
    for i in range(4):
        a  = sp_angle + i * math.pi / 2
        a2 = sp_angle + i * math.pi / 2 + math.pi / 4
        p1 = (sp_cx + math.cos(a)  * sp_r,       sp_cy + math.sin(a)  * sp_r)
        p2 = (sp_cx + math.cos(a2) * sp_r * 0.3, sp_cy + math.sin(a2) * sp_r * 0.3)
        p3 = (sp_cx + math.cos(a  + math.pi / 2) * sp_r,
              sp_cy + math.sin(a  + math.pi / 2) * sp_r)
        pygame.draw.polygon(surf, (255, 255, 228), [p1, p2, p3])

    # Owner label — placed at the bottom of each gem's half
    lbl = font.render(label_char, True, label_col)
    lbl_s = pygame.transform.scale(lbl,
                                    (max(6, lbl.get_width()  * 7 // 10),
                                     max(6, lbl.get_height() * 7 // 10)))
    surf.blit(lbl_s, lbl_s.get_rect(
        center=(int(cx), rc.y + rc.h - lbl_s.get_height() // 2 - 4)
    ))


def _draw_trap(surf, r, c, t):
    rc     = cell_rect(r, c)
    cx, cy = rc.centerx, rc.centery
    pygame.draw.rect(surf, TRAP_BG, rc)

    phase  = t * 0.085 + r * 0.7 + c * 0.6
    pulse  = 1.0 + 0.18 * math.sin(phase)
    size   = CS * 0.30 * pulse
    glow_a = int(38 + 22 * math.sin(phase))

    _acircle(surf, TRAP_GLOW, cx, cy, int(size) + 14, glow_a // 2)
    _acircle(surf, TRAP_GLOW, cx, cy, int(size) +  7, glow_a)
    _acircle(surf, TRAP_GLOW, cx, cy, int(size) +  2, glow_a + 30)

    d = int(size * 1.4)
    _arect(surf, TRAP_GLOW, pygame.Rect(cx - d, cy - d, d * 2, d * 2), 55)

    s  = size * 0.65
    lw = max(3, int(size * 0.32))
    pygame.draw.line(surf, TRAP_GLOW,
        (int(cx - s), int(cy - s)), (int(cx + s), int(cy + s)), lw + 4)
    pygame.draw.line(surf, TRAP_GLOW,
        (int(cx - s), int(cy + s)), (int(cx + s), int(cy - s)), lw + 4)
    pygame.draw.line(surf, TRAP_BRIGHT,
        (int(cx - s), int(cy - s)), (int(cx + s), int(cy + s)), lw)
    pygame.draw.line(surf, TRAP_BRIGHT,
        (int(cx - s), int(cy + s)), (int(cx + s), int(cy - s)), lw)

    tick_col = TRAP_TICK if math.sin(phase * 1.6) > 0 else TRAP_CORE
    for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        px2 = int(cx + dc * (CS2 - 7))
        py2 = int(cy + dr * (CS2 - 7))
        pygame.draw.circle(surf, tick_col, (px2, py2), 3)


def _draw_goal(surf, r, c, t):
    rc     = cell_rect(r, c)
    cx, cy = rc.centerx, rc.centery
    pygame.draw.rect(surf, GOAL_BG, rc)

    phase = t * 0.050 + r + c
    pulse = 1.0 + 0.22 * math.sin(phase)
    size  = CS * 0.30 * pulse

    for rad, alpha in [(int(size) + 22, 12), (int(size) + 14, 24),
                       (int(size) + 8,  42), (int(size) + 3,  68)]:
        _acircle(surf, GOAL_GLOW, cx, cy, rad, alpha)

    ring_r = int(CS2 * 0.88)
    ring_a = t * 0.018
    for i in range(8):
        a = ring_a + i * math.pi / 4
        pygame.draw.circle(surf, GOAL_RING,
                           (int(cx + math.cos(a) * ring_r),
                            int(cy + math.sin(a) * ring_r)), 2)

    angle = t * 0.028
    pts6  = []
    for i in range(12):
        a  = angle + i * math.pi / 6 - math.pi / 2
        rr = size if i % 2 == 0 else size * 0.44
        pts6.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))

    pygame.draw.polygon(surf, GOAL_GLOW, [(x + 2, y + 2) for x, y in pts6])
    pygame.draw.polygon(surf, GOAL_CORE,   pts6)
    pygame.draw.polygon(surf, GOAL_BRIGHT, pts6, 1)
    pygame.draw.circle(surf, GOAL_BRIGHT, (cx, cy), max(3, int(size * 0.22)))
    pygame.draw.circle(surf, (220, 255, 235), (cx, cy), max(1, int(size * 0.10)))


# ══════════════════════════════════════════════════════════════
#  Agent renderer
# ══════════════════════════════════════════════════════════════
def _draw_agent(surf, draw_pos, core, bright, deep, label_surf, t, offset=0):
    c_f = draw_pos[1]
    r_f = draw_pos[0]
    cx  = int(GRID_OFFSET_X + c_f * CS + CS2)
    cy  = int(GRID_OFFSET_Y + r_f * CS + CS2)

    breathe = 1.0 + 0.045 * math.sin(t * 0.110 + offset)
    radius  = int((CS2 - 5) * breathe)

    _acircle(surf, core, cx, cy, radius + 20, 8)
    _acircle(surf, core, cx, cy, radius + 13, 18)
    _acircle(surf, core, cx, cy, radius +  7, 32)
    _acircle(surf, core, cx, cy, radius +  2, 55)

    pygame.draw.circle(surf, deep,   (cx, cy), radius)
    pygame.draw.circle(surf, core,   (cx, cy), radius - 2)

    rim_angle = t * 0.08 + offset
    rim_cx    = int(cx + math.cos(rim_angle - 0.8) * (radius - 4))
    rim_cy    = int(cy + math.sin(rim_angle - 0.8) * (radius - 4))
    _acircle(surf, bright, rim_cx, rim_cy, max(2, radius // 3), 200)

    pygame.draw.circle(surf, bright, (cx, cy), radius, 1)
    surf.blit(label_surf, label_surf.get_rect(center=(cx, cy)))


# ══════════════════════════════════════════════════════════════
#  Ambient star field
# ══════════════════════════════════════════════════════════════
_star_field: list = []
_stars_built = False


def _build_stars():
    global _star_field, _stars_built
    import random
    _star_field = [
        (random.randint(GRID_OFFSET_X + 2, GRID_OFFSET_X + GRID_COLS * CS - 2),
         random.randint(GRID_OFFSET_Y + 2, GRID_OFFSET_Y + GRID_ROWS * CS - 2),
         random.uniform(0.3, 1.0),
         random.uniform(0, math.tau))
        for _ in range(35)
    ]
    _stars_built = True


def _draw_ambient(surf, t):
    if not _stars_built:
        _build_stars()
    for sx, sy, brt, ph in _star_field:
        pygame.draw.circle(surf, (140, 160, 220), (sx, sy), 1)


# ══════════════════════════════════════════════════════════════
#  Main draw entry
# ══════════════════════════════════════════════════════════════
def draw_grid(screen, game, font_small):
    t  = game.tick
    gw = GRID_COLS * CS
    gh = GRID_ROWS * CS

    _draw_ambient(screen, t)

    from core.game import STATE_MENU, STATE_FINISHED
    show_start = game.state in (STATE_MENU, STATE_FINISHED)

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            cell = game.grid.grid[r][c]
            if   cell == WALL:     _draw_wall(screen, r, c)
            elif cell == GEM:      _draw_gem(screen, r, c, t, font_small)
            elif cell == GEM_A:    _draw_gem_ai(screen, r, c, t, font_small)
            elif cell == GEM_BOTH: _draw_gem_both(screen, r, c, t, font_small)
            elif cell == TRAP:     _draw_trap(screen, r, c, t)
            elif cell == GOAL:     _draw_goal(screen, r, c, t)
            else:
                _draw_empty(screen, r, c)
                if show_start and (r, c) == (0, 0):
                    _draw_start(screen, r, c, font_small)

    # Grid lines
    for row in range(GRID_ROWS + 1):
        y = GRID_OFFSET_Y + row * CS
        pygame.draw.line(screen, GRID_LINE,
                         (GRID_OFFSET_X, y), (GRID_OFFSET_X + gw, y))
    for col in range(GRID_COLS + 1):
        x = GRID_OFFSET_X + col * CS
        pygame.draw.line(screen, GRID_LINE,
                         (x, GRID_OFFSET_Y), (x, GRID_OFFSET_Y + gh))

    # Outer border
    br = pygame.Rect(GRID_OFFSET_X - 3, GRID_OFFSET_Y - 3, gw + 6, gh + 6)
    pygame.draw.rect(screen, GRID_BORDER, br, 2, border_radius=3)
    pygame.draw.rect(screen, (60, 75, 125), br.inflate(2, 2), 1, border_radius=4)

    # AI path preview
    from core.game import STATE_COMPETING
    if game.state == STATE_COMPETING and game.ai_path:
        for i, (pr, pc) in enumerate(game.ai_path[:40]):
            fade = max(8, 72 - i * 2)
            sz   = 3 if i % 3 != 0 else 4
            _acircle(screen, PATH_DOT, *cell_center(pr, pc), sz, fade)

    # Trails
    for trail, col in [(game.human_trail, TRAIL_H), (game.ai_trail, TRAIL_A)]:
        for i, (tr, tc) in enumerate(reversed(trail[-10:])):
            a  = (i + 1) * 15
            sz = max(2, 9 - i)
            _acircle(screen, col, *cell_center(tr, tc), sz, a)

    # Particles
    game.particles.draw(screen)

    # Agents
    h_lbl = font_small.render("H", True, C_WHITE)
    a_lbl = font_small.render("A", True, C_WHITE)

    if game.human_agent.energy > 0:
        _draw_agent(screen, game.human_draw_pos,
                    H_CORE, H_BRIGHT, H_DEEP, h_lbl, t, offset=0.0)
    if game.ai_agent.energy > 0:
        _draw_agent(screen, game.ai_draw_pos,
                    A_CORE, A_BRIGHT, A_DEEP, a_lbl, t, offset=1.4)