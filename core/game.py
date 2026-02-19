import pygame
from core.grid import GridWorld
from core.agent import Agent
from ai.search import bfs, astar
from ui.buttons import Button
from ui.hud import draw_hud
from ui.renderer import draw_grid
from config.settings import *

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
        self.phase = "IDLE"

        self.last_move_time = 0
        self.move_delay = 350

        self.buttons = [
            Button(650, 420, 200, 40, "START GAME", "START_GAME"),
            Button(650, 520, 200, 40, "BFS", "BFS"),
            Button(650, 570, 200, 40, "A*", "A*"),
            Button(650, 620, 200, 40, "RESET", "RESET"),
            Button(650, 670, 200, 40, "NEW MAP", "NEW_MAP"),
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
        self.phase = "IDLE"
        self.winner = None

        # Reset timing
        self.last_move_time = 0


    def plan(self):
        result = None

        if self.algorithm == "BFS":
            result = bfs(self.ai_agent.position, self.grid.goal, self.grid)
        else:
            result = astar(self.ai_agent.position, self.grid.goal, self.grid)

        if result:
            self.ai_path = result["path"]
            self.nodes_expanded = result["expanded"]
            self.ai_time = result["time"]
        else:
            self.ai_path = []


    def handle_click(self, pos):
        for btn in self.buttons:
            if not btn.is_clicked(pos):
                continue

            if btn.action == "START_GAME":
                self.reset(self.algorithm)
                self.plan()
                self.phase = "COMPETING"
                self.status = "RUNNING"

            elif btn.action == "RESET":
                self.reset(self.algorithm)

            elif btn.action == "NEW_MAP":
                self.original_grid = GridWorld()
                self.reset(self.algorithm)

            elif btn.action in ["BFS", "A*"]:
                self.algorithm = btn.action
                self.reset(self.algorithm)


    def update(self):
        if self.phase != "COMPETING":
            return

        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_delay:
            return

        self.last_move_time = now

        # -------------------------
        # AI MOVE
        # -------------------------
        if not self.ai_finished and self.ai_path:
            self.ai_agent.move(self.ai_path.pop(0), self.grid)

            if self.ai_agent.energy <= 0:
                self.ai_finished = True

            if self.ai_agent.position == self.grid.goal:
                self.ai_finished = True

        # -------------------------
        # CHECK END CONDITION
        # -------------------------
        if self.ai_finished and self.human_finished:
            self.decide_winner()


    def draw(self):
        self.screen.fill(WHITE)
        draw_grid(self.screen, self, self.font)
        draw_hud(self.screen, self, self.font)
        for btn in self.buttons:
            btn.draw(self.screen, self.font)

    def handle_key(self, key):

        if self.phase != "COMPETING":
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
            self.human_energy = 0

        if new_pos == self.grid.goal:
            self.status = "SUCCESS"
            self.human_energy = self.human_agent.energy
            self.human_path_length = len(self.human_agent.path)
        
        if self.human_agent.energy <= 0:
            self.human_finished = True

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
        self.phase = "FINISHED"




