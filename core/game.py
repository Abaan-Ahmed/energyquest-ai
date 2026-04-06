# ─────────────────────────────────────────────────────────────
#  EnergyQuest  –  core/game.py
# ─────────────────────────────────────────────────────────────
import pygame
import time
import math

from core.grid      import GridWorld
from core.agent     import Agent
from core.particles import ParticleSystem
from ai.search      import bfs, astar
from ai.genetic     import genetic_algorithm
from ui.buttons     import Button
from ui.hud         import draw_hud, PANEL_X, PANEL_W
from ui.renderer    import draw_grid, cell_center
from config.settings import *

STATE_MENU      = "MENU"
STATE_COUNTDOWN = "COUNTDOWN"
STATE_COMPETING = "COMPETING"
STATE_FINISHED  = "FINISHED"
STATE_CREDITS   = "CREDITS"

MOVE_DELAY = {"BFS": 460, "A*": 320, "GA": 220}
TRAIL_LEN  = 10


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.fonts  = self._load_fonts()

        self.original_grid = GridWorld()
        self.grid          = self.original_grid.clone()
        self.human_agent   = Agent()
        self.ai_agent      = Agent()

        self.human_draw_pos = [0.0, 0.0]
        self.ai_draw_pos    = [0.0, 0.0]
        self.move_lerp      = 0.18

        self.human_trail: list = []
        self.ai_trail:    list = []

        self.particles = ParticleSystem()

        self.ai_path        = []
        self.nodes_expanded = 0
        self.ai_time        = 0.0

        self.algorithm     = "A*"
        self.state         = STATE_MENU
        self.ai_finished   = False
        self.human_finished = False
        self.winner        = None
        self.confetti_done = False

        self.last_ai_move  = 0
        self.move_delay    = MOVE_DELAY["A*"]
        self.countdown_val = 3
        self.countdown_ms  = 0
        self.race_start_ms = 0
        self.tick          = 0

        self._build_buttons()

    # ── Fonts ─────────────────────────────────────────────────
    def _load_fonts(self):
        def sf(name, size, bold=False):
            for n in [name, "Segoe UI", "Helvetica Neue", "Ubuntu", "Arial", None]:
                try:
                    f = pygame.font.SysFont(n, size, bold=bold)
                    if f:
                        return f
                except Exception:
                    pass
            return pygame.font.Font(None, size)

        return (
            sf("Segoe UI", 30, bold=True),   # title
            sf("Segoe UI", 20, bold=True),   # heading
            sf("Segoe UI", 17),              # normal
            sf("Segoe UI", 14),              # small
        )

    # ── Buttons ───────────────────────────────────────────────
    def _build_buttons(self):
        px = PANEL_X
        pw = PANEL_W
        bw = (pw - 16) // 3 - 2

        # Algo toggle row – positioned near top of panel
        by = GRID_OFFSET_Y + 32
        self.buttons = [
            Button(px,              by, bw, 34, "BFS", "BFS"),
            Button(px + bw + 3,     by, bw, 34, "A*",  "A*"),
            Button(px + 2*(bw + 3), by, bw, 34, "GA",  "GA"),
        ]

        # Action buttons near bottom of panel
        bot = GRID_OFFSET_Y + GRID_ROWS * CELL_SIZE - 142
        half = (pw - 16) // 2
        self.buttons += [
            Button(px,          bot,      pw - 10, 44, "START GAME", "START_GAME",
                   variant="action"),
            Button(px,          bot + 52, half, 34, "New Map", "NEW_MAP"),
            Button(px + half + 6, bot + 52, pw - 16 - half, 34, "Reset",  "RESET"),
            Button(px,          bot + 94, pw - 10, 30, "Credits", "CREDITS"),
        ]

    # ── Reset ─────────────────────────────────────────────────
    def reset(self, algo=None):
        if algo:
            self.algorithm = algo
        self.grid          = self.original_grid.clone()
        self.human_agent   = Agent()
        self.ai_agent      = Agent()
        self.human_draw_pos = [0.0, 0.0]
        self.ai_draw_pos    = [0.0, 0.0]
        self.human_trail.clear()
        self.ai_trail.clear()
        self.particles.clear()
        self.ai_path        = []
        self.nodes_expanded = 0
        self.ai_time        = 0.0
        self.ai_finished    = False
        self.human_finished = False
        self.winner         = None
        self.confetti_done  = False
        self.state          = STATE_MENU
        self.last_ai_move   = 0
        self.move_delay     = MOVE_DELAY.get(self.algorithm, 350)

    # ── Planning ──────────────────────────────────────────────
    def plan(self):
        fn = {"BFS": bfs, "A*": astar}.get(self.algorithm, genetic_algorithm)
        result = fn(self.ai_agent.position, self.grid.goal, self.grid)
        if result:
            self.ai_path        = result.get("path", [])
            self.nodes_expanded = result.get("expanded", 0)
            self.ai_time        = result.get("time", 0.0)

    # ── Input ─────────────────────────────────────────────────
    def handle_click(self, pos):
        for btn in self.buttons:
            if not btn.is_clicked(pos):
                continue
            act = btn.action
            if act == "START_GAME":
                self.reset(self.algorithm)
                self.plan()
                self.state         = STATE_COUNTDOWN
                self.countdown_val = 3
                self.countdown_ms  = pygame.time.get_ticks()
            elif act == "RESET":
                self.reset(self.algorithm)
            elif act == "NEW_MAP":
                self.original_grid = GridWorld()
                self.reset(self.algorithm)
            elif act == "CREDITS":
                self.state = STATE_CREDITS
            elif act in ("BFS", "A*", "GA"):
                self.reset(act)
                self._build_buttons()
            return

    def handle_key(self, key):
        if self.state == STATE_CREDITS:
            if key == pygame.K_ESCAPE:
                self.state = STATE_MENU
            return
        if key == pygame.K_ESCAPE and self.state in (STATE_COMPETING, STATE_FINISHED):
            self.reset(self.algorithm)
            return
        if self.state != STATE_COMPETING:
            return
        if self.human_finished or self.human_agent.energy <= 0:
            return

        delta = {pygame.K_UP: (-1, 0), pygame.K_DOWN: (1, 0),
                 pygame.K_LEFT: (0, -1), pygame.K_RIGHT: (0, 1)}.get(key)
        if delta is None:
            return

        r, c = self.human_agent.position
        new_pos = (r + delta[0], c + delta[1])

        if not self.grid.in_bounds(new_pos):
            return
        if not self.grid.is_walkable(new_pos):
            ccx, ccy = cell_center(r, c)
            self.particles.emit_wall_bump(ccx, ccy, H_CORE, 5)
            return

        old_pos = (r, c)
        event   = self.human_agent.move(new_pos, self.grid, self.grid.human_gems)
        self._append_trail(self.human_trail, old_pos)
        self.human_draw_pos = [float(r), float(c)]

        ccx, ccy = cell_center(*new_pos)
        if event == "gem":
            self.particles.emit_gem(ccx, ccy)
        elif event == "trap":
            self.particles.emit_trap(ccx, ccy)

        if self.human_agent.energy <= 0:
            self.human_finished = True
        elif new_pos == self.grid.goal:
            self.particles.emit_goal(ccx, ccy)
            self.human_finished = True

    # ── Update ────────────────────────────────────────────────
    def update(self):
        self.tick += 1
        self.particles.update()

        if self.state == STATE_CREDITS:
            return

        if self.state == STATE_COUNTDOWN:
            now = pygame.time.get_ticks()
            if now - self.countdown_ms >= 1000:
                self.countdown_val -= 1
                self.countdown_ms   = now
            if self.countdown_val <= 0:
                self.state         = STATE_COMPETING
                self.last_ai_move  = pygame.time.get_ticks()
                self.race_start_ms = pygame.time.get_ticks()
            return

        if self.state != STATE_COMPETING:
            return

        # Smooth lerp
        hr, hc = self.human_agent.position
        ar, ac = self.ai_agent.position
        α = self.move_lerp
        self.human_draw_pos[0] += (hr - self.human_draw_pos[0]) * α
        self.human_draw_pos[1] += (hc - self.human_draw_pos[1]) * α
        self.ai_draw_pos[0]    += (ar - self.ai_draw_pos[0]) * α
        self.ai_draw_pos[1]    += (ac - self.ai_draw_pos[1]) * α

        # AI step
        now = pygame.time.get_ticks()
        if (not self.ai_finished and self.ai_path
                and now - self.last_ai_move >= self.move_delay):
            self.last_ai_move = now
            old_pos  = self.ai_agent.position
            next_pos = self.ai_path.pop(0)
            event    = self.ai_agent.move(next_pos, self.grid, self.grid.ai_gems)
            self._append_trail(self.ai_trail, old_pos)

            ccx, ccy = cell_center(*next_pos)
            if event == "gem":
                self.particles.emit_gem(ccx, ccy)
            elif event == "trap":
                self.particles.emit_trap(ccx, ccy)
            if self.ai_agent.energy <= 0 or next_pos == self.grid.goal:
                if next_pos == self.grid.goal:
                    self.particles.emit_goal(ccx, ccy)
                self.ai_finished = True

        # Trail particles
        if self.tick % 3 == 0:
            hcx, hcy = cell_center(*self.human_agent.position)
            acx, acy = cell_center(*self.ai_agent.position)
            self.particles.emit_trail(hcx, hcy, H_GLOW, size=3, lifetime=20)
            self.particles.emit_trail(acx, acy, A_GLOW, size=3, lifetime=20)

        # End check
        ai_done    = self.ai_finished or not self.ai_path
        human_done = self.human_finished or self.human_agent.energy <= 0
        if ai_done and human_done:
            self._decide_winner()

    def _decide_winner(self):
        hs = max(0, self.human_agent.energy)
        ai = max(0, self.ai_agent.energy)
        if hs > ai:
            self.winner = "HUMAN WINS"
        elif ai > hs:
            self.winner = "AI WINS"
        else:
            self.winner = "DRAW"
        self.state = STATE_FINISHED

    def _append_trail(self, trail, pos):
        trail.append(pos)
        if len(trail) > TRAIL_LEN:
            trail.pop(0)

    # ── Draw ──────────────────────────────────────────────────
    def draw(self):
        # Rich background: vertical gradient
        for iy in range(0, SCREEN_HEIGHT, 2):
            t   = iy / SCREEN_HEIGHT
            r   = int(BG_BASE[0] + (BG_ELEVATED[0] - BG_BASE[0]) * t)
            g   = int(BG_BASE[1] + (BG_ELEVATED[1] - BG_BASE[1]) * t)
            b   = int(BG_BASE[2] + (BG_ELEVATED[2] - BG_BASE[2]) * t)
            pygame.draw.line(self.screen, (r, g, b),
                             (0, iy), (SCREEN_WIDTH, iy))
            pygame.draw.line(self.screen, (r, g, b),
                             (0, iy + 1), (SCREEN_WIDTH, iy + 1))

        if self.state == STATE_CREDITS:
            self._draw_credits()
            return

        draw_grid(self.screen, self, self.fonts[3])
        draw_hud(self.screen, self, self.fonts)

        if self.state == STATE_COUNTDOWN:
            self._draw_countdown()
        if self.state == STATE_FINISHED:
            self._draw_winner_overlay()

    # ── Countdown ─────────────────────────────────────────────
    def _draw_countdown(self):
        num = str(max(1, self.countdown_val))
        f   = pygame.font.Font(None, 200)
        shadow = f.render(num, True, (15, 20, 40))
        glow   = f.render(num, True, H_BRIGHT)
        text   = f.render(num, True, (245, 248, 255))
        cx = GRID_OFFSET_X + GRID_COLS * CELL_SIZE // 2
        cy = GRID_OFFSET_Y + GRID_ROWS * CELL_SIZE // 2
        self.screen.blit(shadow, shadow.get_rect(center=(cx + 5, cy + 5)))
        # Soft glow: render slightly larger
        s = pygame.Surface((glow.get_width() + 20, glow.get_height() + 20),
                            pygame.SRCALPHA)
        s.blit(glow, (10, 10))
        self.screen.blit(text, text.get_rect(center=(cx, cy)))

    # ── Winner overlay ────────────────────────────────────────
    def _draw_winner_overlay(self):
        if not self.confetti_done:
            cx = GRID_OFFSET_X + GRID_COLS * CELL_SIZE // 2
            cy = GRID_OFFSET_Y + GRID_ROWS * CELL_SIZE // 3
            self.particles.emit_confetti(cx, cy, count=130)
            self.confetti_done = True

        self.particles.draw(self.screen)

        t     = self.tick
        pulse = 1.0 + 0.05 * math.sin(t * 0.14)

        wmap = {
            "HUMAN WINS": ((255, 210, 75),  (55, 48, 18, 215)),
            "AI WINS":    ((190, 108, 255), (44, 30, 66, 215)),
            "DRAW":       ((175, 185, 215), (46, 50, 66, 215)),
        }
        wcolor, panel_rgba = wmap.get(game_winner := self.winner,
                                      ((200, 200, 200), (50, 50, 60, 210)))

        f   = pygame.font.Font(None, int(88 * pulse))
        lbl = f.render(game_winner, True, wcolor)
        cx  = GRID_OFFSET_X + GRID_COLS * CELL_SIZE // 2
        cy  = GRID_OFFSET_Y + 55

        banner = pygame.Rect(cx - lbl.get_width() // 2 - 28,
                             cy - lbl.get_height() // 2 - 14,
                             lbl.get_width() + 56,
                             lbl.get_height() + 28)
        s = pygame.Surface((banner.w, banner.h), pygame.SRCALPHA)
        pygame.draw.rect(s, panel_rgba, s.get_rect(), border_radius=18)
        pygame.draw.rect(s, (*wcolor, 210), s.get_rect(), 2, border_radius=18)
        self.screen.blit(s, (banner.x, banner.y))
        self.screen.blit(lbl, lbl.get_rect(center=banner.center))

    # ── Credits ───────────────────────────────────────────────
    def _draw_credits(self):
        f_t, f_h, f_n, f_s = self.fonts
        cx  = SCREEN_WIDTH // 2
        pw, ph = 680, 530
        px  = cx - pw // 2
        py  = SCREEN_HEIGHT // 2 - ph // 2

        s = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(s, (20, 26, 50, 240), s.get_rect(), border_radius=20)
        pygame.draw.rect(s, (65, 82, 135, 200), s.get_rect(), 1, border_radius=20)
        self.screen.blit(s, (px, py))

        y = py + 48
        t_lbl = f_t.render("ENERGY QUEST", True, HUD_TEXT)
        self.screen.blit(t_lbl, (cx - t_lbl.get_width() // 2, y))
        y += t_lbl.get_height() + 6

        sub = f_n.render("Artificial Intelligence  –  EECE453", True, HUD_MUTED)
        self.screen.blit(sub, (cx - sub.get_width() // 2, y))
        y += sub.get_height() + 16

        pygame.draw.line(self.screen, HUD_BORDER, (px + 55, y), (px + pw - 55, y))
        y += 18

        for label, value in [
            ("Instructor",  "Dr. Nejib Ben Hadj-Alouane"),
            ("Course",      "EECE453 – Spring 2026"),
            ("University",  "American University in Dubai"),
        ]:
            ll = f_s.render(label + ":", True, HUD_MUTED)
            vl = f_n.render(value,       True, HUD_TEXT)
            self.screen.blit(ll, (cx - 235, y))
            self.screen.blit(vl, (cx - 60,  y))
            y += vl.get_height() + 8

        y += 10
        pygame.draw.line(self.screen, HUD_BORDER, (px + 55, y), (px + pw - 55, y))
        y += 18

        dh = f_h.render("Developed By", True, HUD_MUTED)
        self.screen.blit(dh, (cx - dh.get_width() // 2, y))
        y += dh.get_height() + 10

        for name in ["Abaan Ahmed", "Mohammed Almheiri",
                     "Younis Almarzooqi", "Sultan Alsalman"]:
            nl = f_n.render(name, True, HUD_TEXT)
            self.screen.blit(nl, (cx - nl.get_width() // 2, y))
            y += nl.get_height() + 6

        footer = f_s.render("Press  ESC  to return", True, HUD_DIM)
        self.screen.blit(footer, (cx - footer.get_width() // 2,
                                  py + ph - footer.get_height() - 18))
