import pygame
from config.settings import *

TEXT_COLOR = (240, 240, 250)

BTN_NORMAL = (60, 70, 100)
BTN_HOVER = (85, 105, 150)

BTN_BORDER = (100, 120, 170)
BTN_SHADOW = (20, 25, 40)

BTN_SELECTED = (120, 150, 220)

BTN_START = (70, 150, 95)
BTN_START_HOVER = (90, 180, 110)

BTN_RESET = (150, 80, 80)
BTN_RESET_HOVER = (180, 100, 100)


class Button:

    def __init__(self, x, y, w, h, text, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action

    def draw(self, screen, font, selected=False):

        mouse = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse)

        # --------------------------------
        # COLOR LOGIC
        # --------------------------------
        color = BTN_NORMAL

        if self.action == "START_GAME":
            color = BTN_START_HOVER if hovered else BTN_START

        elif self.action == "RESET":
            color = BTN_RESET_HOVER if hovered else BTN_RESET

        else:
            if selected:
                color = BTN_SELECTED
            elif hovered:
                color = BTN_HOVER

        # --------------------------------
        # SHADOW
        # --------------------------------
        shadow_rect = self.rect.move(0, 4)

        pygame.draw.rect(
            screen,
            BTN_SHADOW,
            shadow_rect,
            border_radius=10
        )

        # --------------------------------
        # BUTTON BODY
        # --------------------------------
        pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=10
        )

        # --------------------------------
        # BORDER
        # --------------------------------
        pygame.draw.rect(
            screen,
            BTN_BORDER,
            self.rect,
            1,
            border_radius=10
        )

        # --------------------------------
        # TEXT
        # --------------------------------
        label = font.render(self.text, True, TEXT_COLOR)

        screen.blit(
            label,
            label.get_rect(center=self.rect.center)
        )

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)