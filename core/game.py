import pygame
import random
from core.grid import GridWorld
from core.agent import Agent
from ai.search import bfs, astar
from ui.buttons import Button
from ui.hud import draw_hud
from ui.renderer import draw_grid
from config.settings import *
from ai.genetic import genetic_algorithm

STATE_MENU = "MENU"
STATE_COUNTDOWN = "COUNTDOWN"
STATE_COMPETING = "COMPETING"
STATE_FINISHED = "FINISHED"
STATE_CREDITS = "CREDITS"


class Game:
    def __init__(self, screen):

        # ---------------------------
        # BASIC SETUP
        # ---------------------------
        self.screen = screen

        # fonts
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 42)
        self.big_font = pygame.font.SysFont(None, 120)

        # ---------------------------
        # GRID + AGENTS
        # ---------------------------
        self.original_grid = GridWorld()
        self.grid = self.original_grid.clone()

        self.human_agent = Agent()
        self.ai_agent = Agent()

        # drawing positions (for smooth animation later)
        self.human_draw_pos = list(self.human_agent.position)
        self.ai_draw_pos = list(self.ai_agent.position)

        # animation speed
        self.move_speed = 0.18

        # ---------------------------
        # AI PLANNING
        # ---------------------------
        self.ai_path = []
        self.nodes_expanded = 0
        self.ai_time = 0

        # ---------------------------
        # GAME STATUS
        # ---------------------------
        self.ai_finished = False
        self.human_finished = False
        self.winner = None

        self.algorithm = "A*"
        self.status = "IDLE"
        self.state = STATE_MENU

        # ---------------------------
        # COUNTDOWN TIMER
        # ---------------------------
        self.countdown_value = 3
        self.countdown_start = 0

        # ---------------------------
        # AI MOVE TIMING
        # ---------------------------
        self.last_move_time = 0
        self.move_delay = 350

        # difficulty speed map
        self.difficulty_speed = {"BFS": 500, "A*": 350, "GA": 250}

        # ---------------------------
        # UI BUTTONS
        # ---------------------------
        self.buttons = [

            # -------------------------
            # AI DIFFICULTY
            # -------------------------
            Button(650, 480, 95, 36, "BFS", "BFS"),
            Button(755, 480, 95, 36, "A*", "A*"),
            Button(702.5, 525, 95, 36, "Genetic AI", "GA"),

            # -------------------------
            # MAIN ACTION
            # -------------------------
            Button(625, 580, 250, 50, "START GAME", "START_GAME"),

            # -------------------------
            # SECONDARY ACTIONS
            # -------------------------
            Button(603, 650, 95, 36, "Credits", "CREDITS"),
            Button(703, 650, 95, 36, "Reset", "RESET"),
            Button(803, 650, 95, 36, "Map", "NEW_MAP"),
        ]

    def reset(self, algo):

        # ---------------------------
        # RESET GRID
        # ---------------------------
        self.grid = self.original_grid.clone()

        # ---------------------------
        # RESET AGENTS
        # ---------------------------
        self.human_agent = Agent()
        self.ai_agent = Agent()

        # reset drawing positions (for smooth animation)
        self.human_draw_pos = list(self.human_agent.position)
        self.ai_draw_pos = list(self.ai_agent.position)

        # ---------------------------
        # RESET AI PATH / SEARCH
        # ---------------------------
        self.ai_path = []
        self.nodes_expanded = 0
        self.ai_time = 0

        # ---------------------------
        # RESET GAME STATUS
        # ---------------------------
        self.ai_finished = False
        self.human_finished = False
        self.winner = None

        self.algorithm = algo
        self.status = "IDLE"
        self.state = STATE_MENU

        # ---------------------------
        # RESET TIMERS
        # ---------------------------
        self.last_move_time = 0

        # adjust AI speed based on difficulty
        if algo in self.difficulty_speed:
            self.move_delay = self.difficulty_speed[algo]

    def plan(self):

        import time

        # ---------------------------
        # START TIMER
        # ---------------------------
        start_time = time.perf_counter()

        result = None

        # ---------------------------
        # SELECT ALGORITHM
        # ---------------------------
        if self.algorithm == "BFS":
            result = bfs(self.ai_agent.position, self.grid.goal, self.grid)

        elif self.algorithm == "A*":
            result = astar(self.ai_agent.position, self.grid.goal, self.grid)

        elif self.algorithm == "GA":
            result = genetic_algorithm(
                self.ai_agent.position, self.grid.goal, self.grid
            )

        # ---------------------------
        # END TIMER
        # ---------------------------
        end_time = time.perf_counter()

        # ---------------------------
        # STORE RESULTS
        # ---------------------------
        if result:

            self.ai_path = result.get("path", [])
            self.nodes_expanded = result.get("expanded", 0)

            # measured planning time
            self.ai_time = round(end_time - start_time, 4)

        else:
            # fallback safety
            self.ai_path = []
            self.nodes_expanded = 0
            self.ai_time = 0

    def handle_click(self, pos):

        for btn in self.buttons:

            if not btn.is_clicked(pos):
                continue

            action = btn.action

            # ---------------------------
            # START GAME
            # ---------------------------
            if action == "START_GAME":

                self.reset(self.algorithm)

                # plan AI path
                self.plan()

                # start countdown
                self.state = STATE_COUNTDOWN
                self.countdown_value = 3
                self.countdown_start = pygame.time.get_ticks()

                return

            # ---------------------------
            # RESET GAME
            # ---------------------------
            if action == "RESET":

                self.reset(self.algorithm)
                return

            # ---------------------------
            # NEW MAP
            # ---------------------------
            if action == "NEW_MAP":

                self.original_grid = GridWorld()
                self.reset(self.algorithm)
                return

            # ---------------------------
            # SHOW CREDITS
            # ---------------------------
            if action == "CREDITS":

                self.state = STATE_CREDITS
                return

            # ---------------------------
            # SELECT AI ALGORITHM
            # ---------------------------
            if action in ["BFS", "A*", "GA"]:

                self.algorithm = action

                # update AI move speed
                if action in self.difficulty_speed:
                    self.move_delay = self.difficulty_speed[action]

                self.reset(self.algorithm)
                return

    def update(self):

        # ---------------------------------
        # CREDITS SCREEN (no updates)
        # ---------------------------------
        if self.state == STATE_CREDITS:
            return

        # ---------------------------------
        # COUNTDOWN STATE
        # ---------------------------------
        if self.state == STATE_COUNTDOWN:

            now = pygame.time.get_ticks()

            if now - self.countdown_start >= 1000:
                self.countdown_value -= 1
                self.countdown_start = now

            if self.countdown_value <= 0:
                self.state = STATE_COMPETING
                self.last_move_time = pygame.time.get_ticks()

            return

        # ---------------------------------
        # ONLY UPDATE DURING GAMEPLAY
        # ---------------------------------
        if self.state != STATE_COMPETING:
            return

        now = pygame.time.get_ticks()

        if now - self.last_move_time < self.move_delay:
            return

        self.last_move_time = now

        # ---------------------------------
        # AI MOVE
        # ---------------------------------
        if not self.ai_finished and self.ai_path:

            next_move = self.ai_path.pop(0)
            self.ai_agent.move(next_move, self.grid)

            if self.ai_agent.energy <= 0:
                self.ai_finished = True

            if self.ai_agent.position == self.grid.goal:
                self.ai_finished = True

        # ---------------------------------
        # CHECK END CONDITIONS
        # ---------------------------------
        if (
            (self.ai_finished and self.human_finished)
            or (self.ai_finished and self.human_agent.energy <= 0)
            or (self.human_finished and not self.ai_path)
        ):
            self.decide_winner()
            self.state = STATE_FINISHED
            return

        # ---------------------------------
        # SMOOTH AGENT ANIMATION
        # ---------------------------------
        self.ai_draw_pos[0] += (
            self.ai_agent.position[0] - self.ai_draw_pos[0]
        ) * self.move_speed
        self.ai_draw_pos[1] += (
            self.ai_agent.position[1] - self.ai_draw_pos[1]
        ) * self.move_speed

        self.human_draw_pos[0] += (
            self.human_agent.position[0] - self.human_draw_pos[0]
        ) * self.move_speed
        self.human_draw_pos[1] += (
            self.human_agent.position[1] - self.human_draw_pos[1]
        ) * self.move_speed

    def draw(self):

        # ---------------------------------
        # BACKGROUND GRADIENT
        # ---------------------------------
        for y in range(SCREEN_HEIGHT):
            shade = 18 + int(12 * (y / SCREEN_HEIGHT))
            pygame.draw.line(
                self.screen,
                (shade, shade + 2, shade + 10),
                (0, y),
                (SCREEN_WIDTH, y),
            )

        # ---------------------------------
        # CREDITS SCREEN
        # ---------------------------------
        if self.state == STATE_CREDITS:
            self.draw_credits()
            return

        # ---------------------------------
        # DRAW GAME WORLD
        # ---------------------------------
        draw_grid(self.screen, self, self.font)
        draw_hud(self.screen, self, self.font)

        # ---------------------------------
        # DRAW MENU BUTTONS
        # ---------------------------------
        if self.state in [STATE_MENU, STATE_FINISHED]:
            for btn in self.buttons:

                selected = False

                if btn.action in ["BFS", "A*", "GA"]:
                    selected = btn.action == self.algorithm

                btn.draw(self.screen, self.font, selected)

        # ---------------------------------
        # COUNTDOWN DISPLAY
        # ---------------------------------
        if self.state == STATE_COUNTDOWN:

            number = str(self.countdown_value)

            shadow = self.big_font.render(number, True, (40, 40, 40))
            text = self.big_font.render(number, True, (240, 240, 255))

            center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

            self.screen.blit(
                shadow,
                shadow.get_rect(center=(center[0] + 5, center[1] + 5)),
            )

            self.screen.blit(
                text,
                text.get_rect(center=center),
            )

        # ---------------------------------
        # WINNER BANNER
        # ---------------------------------
        if self.state == STATE_FINISHED:

            import math

            t = pygame.time.get_ticks() / 300

            pulse = 1 + 0.05 * math.sin(t)

            # --------------------------------
            # COLOR THEMES
            # --------------------------------
            if self.winner == "HUMAN WINS":
                glow_color = (255, 210, 100)
                panel_color = (70, 60, 30)

            elif self.winner == "AI WINS":
                glow_color = (170, 120, 255)
                panel_color = (50, 40, 80)

            else:
                glow_color = (200, 200, 200)
                panel_color = (60, 60, 60)

            # --------------------------------
            # BANNER PANEL
            # --------------------------------
            banner = pygame.Rect(SCREEN_WIDTH // 2 - 260, 70, 520, 110)

            pygame.draw.rect(self.screen, panel_color, banner, border_radius=18)

            pygame.draw.rect(self.screen, glow_color, banner, 3, border_radius=18)

            # --------------------------------
            # PULSING TEXT
            # --------------------------------
            base_size = 70
            size = int(base_size * pulse)

            win_font = pygame.font.SysFont(None, size)

            text = win_font.render(self.winner, True, glow_color)

            self.screen.blit(text, text.get_rect(center=banner.center))

    def handle_key(self, key):

        # ---------------------------------
        # ESC FROM CREDITS
        # ---------------------------------
        if self.state == STATE_CREDITS:
            if key == pygame.K_ESCAPE:
                self.state = STATE_MENU
            return

        # ---------------------------------
        # ONLY MOVE DURING GAMEPLAY
        # ---------------------------------
        if self.state != STATE_COMPETING:
            return

        # ---------------------------------
        # STOP MOVEMENT IF HUMAN FINISHED
        # ---------------------------------
        if self.human_finished:
            return

        # ---------------------------------
        # STOP IF NO ENERGY
        # ---------------------------------
        if self.human_agent.energy <= 0:
            self.human_finished = True
            return

        # ---------------------------------
        # STOP IF GOAL ALREADY REACHED
        # ---------------------------------
        if self.human_agent.position == self.grid.goal:
            self.human_finished = True
            return

        # ---------------------------------
        # HUMAN MOVEMENT KEYS
        # ---------------------------------
        move_map = {
            pygame.K_UP: (-1, 0),
            pygame.K_DOWN: (1, 0),
            pygame.K_LEFT: (0, -1),
            pygame.K_RIGHT: (0, 1),
        }

        if key not in move_map:
            return

        dx, dy = move_map[key]

        r, c = self.human_agent.position
        new_pos = (r + dx, c + dy)

        # ---------------------------------
        # VALIDATE MOVE
        # ---------------------------------
        if not self.grid.in_bounds(new_pos):
            return

        if not self.grid.is_walkable(new_pos):
            return

        # ---------------------------------
        # EXECUTE MOVE
        # ---------------------------------
        self.human_agent.move(new_pos, self.grid)

        # ---------------------------------
        # CHECK HUMAN STATUS
        # ---------------------------------
        if self.human_agent.energy <= 0:
            self.status = "FAILED"
            self.human_finished = True
            return

        if new_pos == self.grid.goal:
            self.status = "SUCCESS"
            self.human_finished = True

    def decide_winner(self):

        human_score = max(0, self.human_agent.energy)
        ai_score = max(0, self.ai_agent.energy)

        if human_score > ai_score:
            self.winner = "HUMAN WINS"

        elif ai_score > human_score:
            self.winner = "AI WINS"

        else:
            self.winner = "DRAW"

        self.status = self.winner
        self.state = STATE_FINISHED

    def draw_credits(self):

        # ---------------------------------
        # BACKGROUND GRADIENT
        # ---------------------------------
        for y in range(SCREEN_HEIGHT):
            shade = 18 + int(12 * (y / SCREEN_HEIGHT))
            pygame.draw.line(
                self.screen,
                (shade, shade + 2, shade + 10),
                (0, y),
                (SCREEN_WIDTH, y),
            )

        # ---------------------------------
        # FONTS
        # ---------------------------------
        title_font = pygame.font.SysFont(None, 64)
        section_font = pygame.font.SysFont(None, 42)
        text_font = pygame.font.SysFont(None, 32)
        small_font = pygame.font.SysFont(None, 26)

        # ---------------------------------
        # PANEL
        # ---------------------------------
        panel_width = 700
        panel_height = 520

        panel = pygame.Rect(
            (SCREEN_WIDTH - panel_width) // 2,
            (SCREEN_HEIGHT - panel_height) // 2,
            panel_width,
            panel_height,
        )

        pygame.draw.rect(self.screen, (40, 45, 60), panel, border_radius=18)

        pygame.draw.rect(self.screen, (90, 100, 130), panel, 2, border_radius=18)

        center_x = SCREEN_WIDTH // 2
        y = panel.top + 50

        # ---------------------------------
        # TITLE
        # ---------------------------------
        title = title_font.render("ENERGY QUEST", True, (240, 240, 255))
        self.screen.blit(title, title.get_rect(center=(center_x, y)))

        y += 60

        # ---------------------------------
        # COURSE NAME
        # ---------------------------------
        course = section_font.render(
            "Artificial Intelligence – EECE453",
            True,
            (210, 210, 230),
        )

        self.screen.blit(course, course.get_rect(center=(center_x, y)))

        y += 40

        pygame.draw.line(
            self.screen, (80, 90, 120), (panel.left + 60, y), (panel.right - 60, y), 1
        )

        y += 40

        # ---------------------------------
        # INSTRUCTOR
        # ---------------------------------
        instructor_title = small_font.render("Instructor", True, (200, 200, 220))

        self.screen.blit(
            instructor_title, instructor_title.get_rect(center=(center_x, y))
        )

        y += 35

        instructor = text_font.render(
            "Dr. Nejib Ben Hadj-Alouane",
            True,
            (240, 240, 255),
        )

        self.screen.blit(instructor, instructor.get_rect(center=(center_x, y)))

        y += 55

        # ---------------------------------
        # DEVELOPERS
        # ---------------------------------
        dev_title = section_font.render("Developed By", True, (210, 210, 230))

        self.screen.blit(dev_title, dev_title.get_rect(center=(center_x, y)))

        y += 45

        developers = [
            "Abaan Ahmed",
            "Mohammed Almheiri",
            "Younis Almarzooqi",
            "Sultan Alsalman",
        ]

        for name in developers:

            text = text_font.render(name, True, (240, 240, 255))

            self.screen.blit(text, text.get_rect(center=(center_x, y)))

            y += 32

        y += 30

        pygame.draw.line(
            self.screen, (80, 90, 120), (panel.left + 60, y), (panel.right - 60, y), 1
        )

        y += 35

        # ---------------------------------
        # UNIVERSITY
        # ---------------------------------
        university = text_font.render(
            "American University in Dubai",
            True,
            (220, 220, 240),
        )

        self.screen.blit(university, university.get_rect(center=(center_x, y + 30)))

        y += 32

        semester = text_font.render("Spring 2026", True, (220, 220, 240))

        self.screen.blit(semester, semester.get_rect(center=(center_x, y + 30)))

        # ---------------------------------
        # FOOTER
        # ---------------------------------
        footer = small_font.render("Press ESC to return", True, (190, 190, 210))

        self.screen.blit(footer, footer.get_rect(center=(center_x, panel.bottom - 20)))
