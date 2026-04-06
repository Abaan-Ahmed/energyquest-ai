# ─────────────────────────────────────────────────────────────
#  EnergyQuest  –  ui/buttons.py
# ─────────────────────────────────────────────────────────────
import pygame
from config.settings import *


class Button:
    def __init__(self, x, y, w, h, label, action, variant="default"):
        self.rect     = pygame.Rect(x, y, w, h)
        self.label    = label
        self.action   = action
        self.variant  = variant
        self._hovered = False

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update_hover(self, mouse_pos):
        self._hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface, font, selected=False):
        r = self.rect

        if selected:
            bg, border, tc = BTN_SEL_BG, BTN_SEL_BOR, BTN_SEL_TEXT
        elif self.variant == "action":
            bg     = BTN_ACTION_H if self._hovered else BTN_ACTION
            border = BTN_SEL_BOR  if self._hovered else (55, 100, 200)
            tc     = C_WHITE
        elif self.variant == "danger":
            bg     = BTN_DANGER_H if self._hovered else BTN_DANGER
            border = (235, 85, 85) if self._hovered else BTN_BORDER
            tc     = C_WHITE
        elif self.variant == "success":
            bg     = BTN_SUCCESS_H if self._hovered else BTN_SUCCESS
            border = (75, 205, 115) if self._hovered else BTN_BORDER
            tc     = C_WHITE
        else:
            bg     = BTN_HOVER_BG if self._hovered else BTN_BG
            border = HUD_BORDER_B if self._hovered else BTN_BORDER
            tc     = BTN_TEXT

        # Shadow
        s_rect = r.move(0, 3)
        _fill_alpha(surface, (0, 0, 0, 55), s_rect, radius=8)

        # Body
        pygame.draw.rect(surface, bg, r, border_radius=8)

        # Selected glow
        if selected:
            glow = r.inflate(4, 4)
            _fill_alpha(surface, (*BTN_SEL_BOR, 45), glow, radius=11)

        # Border
        pygame.draw.rect(surface, border, r, 1, border_radius=8)

        # Top sheen (glass effect)
        sheen = pygame.Rect(r.x + 2, r.y + 2, r.w - 4, r.h // 2 - 1)
        _fill_alpha(surface, (255, 255, 255, 14), sheen, radius=6)

        # Label
        lbl = font.render(self.label, True, tc)
        surface.blit(lbl, lbl.get_rect(center=r.center))

        # Hover underline accent
        if self._hovered and not selected:
            accent_col = {
                "action":  BTN_ACTION_H,
                "danger":  BTN_DANGER_H,
                "success": BTN_SUCCESS_H,
            }.get(self.variant, HUD_ACCENT)
            pygame.draw.rect(surface, accent_col,
                             pygame.Rect(r.x + 6, r.bottom - 3, r.w - 12, 2),
                             border_radius=1)


def _fill_alpha(surface, color_rgba, rect, radius=0):
    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(s, color_rgba, s.get_rect(), border_radius=radius)
    surface.blit(s, (rect.x, rect.y))
