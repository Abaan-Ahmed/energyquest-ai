import pygame
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
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24)

        self.original_grid = GridWorld()
        self.grid = self.original_grid.clone()
        self.human_agent = Agent()
        self.ai_agent = Agent()

        self.ai_path = []
        self.ai_finished = False
        self.human_finished = False
        self.winner = None

        self.algorithm = "A*"
        self.status = "IDLE"
        self.state = STATE_MENU
        self.countdown_value = 3
        self.countdown_start = 0

        self.last_move_time = 0
        self.move_delay = 350

        self.buttons = [
            Button(650, 420, 200, 40, "BFS (Easy)", "BFS"),
            Button(650, 470, 200, 40, "A* (Hard)", "A*"),
            Button(650, 520, 200, 40, "GA (Very Hard)", "GA"),
            Button(650, 570, 200, 40, "START GAME", "START_GAME"),
            Button(650, 620, 200, 40, "CREDITS", "CREDITS"),
            Button(650, 670, 200, 40, "RESET", "RESET"),
        ]

    def reset(self, algo):
        # Fresh grid
        self.grid = self.original_grid.clone()

        # Recreate agents completely
        self.human_agent = Agent()
        self.ai_agent = Agent()

        # Reset AI planning
        self.ai_path = []
        self.ai_finished = False
        self.human_finished = False

        # Reset game state
        self.algorithm = algo
        self.status = "IDLE"
        self.state = STATE_MENU
        self.winner = None

        # Reset timing
        self.last_move_time = 0

    def plan(self):

        if self.algorithm == "BFS":
            result = bfs(self.ai_agent.position,
                        self.grid.goal,
                        self.grid)

        elif self.algorithm == "A*":
            result = astar(self.ai_agent.position,
                        self.grid.goal,
                        self.grid)

        elif self.algorithm == "GA":
            result = genetic_algorithm(self.ai_agent.position,
                                    self.grid.goal,
                                    self.grid)

        else:
            result = None

        if result:
            self.ai_path = result["path"]
            self.nodes_expanded = result["expanded"]
            self.ai_time = result["time"]

    def handle_click(self, pos):
        for btn in self.buttons:
            if not btn.is_clicked(pos):
                continue

            elif btn.action == "START_GAME":
                self.reset(self.algorithm)
                self.plan()

                self.state = STATE_COUNTDOWN
                self.countdown_value = 3
                self.countdown_start = pygame.time.get_ticks()

            elif btn.action == "RESET":
                self.reset(self.algorithm)

            elif btn.action == "NEW_MAP":
                self.original_grid = GridWorld()
                self.reset(self.algorithm)

            elif btn.action == "CREDITS":
                self.state = STATE_CREDITS

            elif btn.action in ["BFS", "A*", "GA"]:
                self.algorithm = btn.action
                self.reset(self.algorithm)


    def update(self):
        if self.state == STATE_CREDITS:
            return

        # ----------------------
        # COUNTDOWN STATE
        # ----------------------
        if self.state == STATE_COUNTDOWN:
            now = pygame.time.get_ticks()

            if now - self.countdown_start >= 1000:
                self.countdown_value -= 1
                self.countdown_start = now

            if self.countdown_value <= 0:
                self.state = STATE_COMPETING
                self.last_move_time = pygame.time.get_ticks()

            return


        # ----------------------
        # COMPETING STATE
        # ----------------------
        if self.state != STATE_COMPETING:
            return

        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_delay:
            return

        self.last_move_time = now

        # AI MOVE
        # If AI finished and human finished
        if self.ai_finished and self.human_finished:
            self.decide_winner()
            return

        # If AI finished and human has no energy
        if self.ai_finished and self.human_agent.energy <= 0:
            self.decide_winner()
            return

        # If human finished and AI has no path left
        if self.human_finished and not self.ai_path:
            self.decide_winner()
            return
        
        if not self.ai_finished and self.ai_path:
            self.ai_agent.move(self.ai_path.pop(0), self.grid)

            if self.ai_agent.energy <= 0:
                self.ai_finished = True

            if self.ai_agent.position == self.grid.goal:
                self.ai_finished = True

        # Determine end condition
        if (
            (self.ai_finished and self.human_finished) or
            (self.ai_finished and self.human_agent.energy <= 0) or
            (self.human_finished and not self.ai_path)
        ):
            self.decide_winner()
            self.state = STATE_FINISHED
            return



    def draw(self):
        self.screen.fill(WHITE)

        # -----------------------
        # CREDITS SCREEN
        # -----------------------
        if self.state == STATE_CREDITS:
            self.draw_credits()
            return

        draw_grid(self.screen, self, self.font)
        draw_hud(self.screen, self, self.font)

        if self.state in [STATE_MENU, STATE_FINISHED]:
            for btn in self.buttons:
                btn.draw(self.screen, self.font)

        # COUNTDOWN DISPLAY
        if self.state == STATE_COUNTDOWN:
            big_font = pygame.font.SysFont(None, 120)
            text = big_font.render(str(self.countdown_value), True, BLACK)
            self.screen.blit(
                text,
                text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            )

        # FINISHED DISPLAY
        if self.state == STATE_FINISHED:
            big_font = pygame.font.SysFont(None, 60)
            text = big_font.render(self.winner, True, RED)
            self.screen.blit(
                text,
                text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            )

        if self.state in [STATE_MENU, STATE_FINISHED]:
            selected = self.font.render(
                f"Selected AI: {self.algorithm}",
                True,
                BLACK
            )
            self.screen.blit(selected, (650, 380))

    def handle_key(self, key):

        # ESC should work in credits
        if self.state == STATE_CREDITS:
            if key == pygame.K_ESCAPE:
                self.state = STATE_MENU
            return

        # Only allow movement during competition
        if self.state != STATE_COMPETING:
            return

        # STOP input if game already finished
        if self.status in ["FAILED", "SUCCESS"]:
            return

        move_map = {
            pygame.K_UP:    (-1, 0),
            pygame.K_DOWN:  (1, 0),
            pygame.K_LEFT:  (0, -1),
            pygame.K_RIGHT: (0, 1),
        }

        if key not in move_map:
            return

        dx, dy = move_map[key]
        r, c = self.human_agent.position
        new_pos = (r + dx, c + dy)

        # Boundary check
        if not self.grid.in_bounds(new_pos):
            return

        # Wall check
        if not self.grid.is_walkable(new_pos):
            return

        # Perform move
        self.human_agent.move(new_pos, self.grid)

        # Check terminal conditions AFTER move
        if self.human_agent.energy <= 0:
            self.status = "FAILED"
            self.human_finished = True

        if new_pos == self.grid.goal:
            self.status = "SUCCESS"
            self.human_energy = self.human_agent.energy
            self.human_path_length = len(self.human_agent.path)

        if self.human_agent.position == self.grid.goal:
            self.human_finished = True

    def decide_winner(self):
        human_score = self.human_agent.energy
        ai_score = self.ai_agent.energy

        if human_score > ai_score:
            self.winner = "HUMAN WINS"
        elif ai_score > human_score:
            self.winner = "AI WINS"
        else:
            self.winner = "DRAW"

        self.status = self.winner
        self.state = STATE_FINISHED

    def draw_credits(self):

        big_font = pygame.font.SysFont(None, 50)
        medium_font = pygame.font.SysFont(None, 36)
        small_font = pygame.font.SysFont(None, 28)

        y = 100

        title = big_font.render("EnergyQuest", True, BLACK)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += 80

        lines = [
            "Artificial Intelligence EECE453",
            "",
            "Instructor:",
            "Dr. Nejib Ben Hadj-Alouane",
            "",
            "Developed By:",
            "Abaan Ahmed",
            "Mohammed Almheiri",
            "Younis Almarzooqi",
            "Sultan Alsalman",
            "",
            "American University in Dubai",
            "Spring 2026",
            "",
            "Press ESC to return"
        ]

        for line in lines:
            text = medium_font.render(line, True, BLACK)
            self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, y)))
            y += 40



