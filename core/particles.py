# ─────────────────────────────────────────────────────────────
#  EnergyQuest  –  core/particles.py
# ─────────────────────────────────────────────────────────────
import pygame
import random
import math


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "r", "g", "b",
                 "size", "lifetime", "max_lt", "gravity", "drag", "spin")

    def __init__(self, x, y, color, vx, vy,
                 size=4, lifetime=40, gravity=0.13, drag=0.94, spin=0.0):
        self.x      = float(x)
        self.y      = float(y)
        self.vx     = float(vx)
        self.vy     = float(vy)
        self.r, self.g, self.b = color
        self.size     = size
        self.lifetime = lifetime
        self.max_lt   = lifetime
        self.gravity  = gravity
        self.drag     = drag
        self.spin     = spin

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += self.gravity
        self.vx *= self.drag
        self.vy *= self.drag
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface):
        ratio = self.lifetime / self.max_lt
        sz    = max(1, int(self.size * ratio))
        alpha = int(230 * ratio)
        s = pygame.Surface((sz * 2 + 2, sz * 2 + 2), pygame.SRCALPHA)
        # Soft glow: draw two circles – outer at half alpha
        pygame.draw.circle(s, (self.r, self.g, self.b, alpha // 3),
                           (sz + 1, sz + 1), sz)
        pygame.draw.circle(s, (self.r, self.g, self.b, alpha),
                           (sz + 1, sz + 1), max(1, sz - 1))
        surface.blit(s, (int(self.x) - sz - 1, int(self.y) - sz - 1))


class SquareParticle:
    """Confetti square with rotation."""
    __slots__ = ("x", "y", "vx", "vy", "r", "g", "b",
                 "size", "lifetime", "max_lt", "gravity", "drag", "angle", "spin")

    def __init__(self, x, y, color, vx, vy, size=5, lifetime=80, spin=0.12):
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.r, self.g, self.b = color
        self.size     = size
        self.lifetime = lifetime
        self.max_lt   = lifetime
        self.gravity  = 0.20
        self.drag     = 0.975
        self.angle    = random.uniform(0, math.tau)
        self.spin     = spin

    def update(self):
        self.x     += self.vx
        self.y     += self.vy
        self.vy    += self.gravity
        self.vx    *= self.drag
        self.vy    *= self.drag
        self.angle += self.spin
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface):
        ratio = self.lifetime / self.max_lt
        sz    = max(1, self.size)
        alpha = int(245 * ratio)
        cos_a, sin_a = math.cos(self.angle) * sz, math.sin(self.angle) * sz
        pts = [
            (self.x - cos_a + sin_a, self.y - sin_a - cos_a),
            (self.x + cos_a + sin_a, self.y + sin_a - cos_a),
            (self.x + cos_a - sin_a, self.y + sin_a + cos_a),
            (self.x - cos_a - sin_a, self.y - sin_a + cos_a),
        ]
        # Draw onto alpha surface
        bounds = pygame.Rect(
            int(min(p[0] for p in pts)) - 2,
            int(min(p[1] for p in pts)) - 2,
            int(max(p[0] for p in pts) - min(p[0] for p in pts)) + 4,
            int(max(p[1] for p in pts) - min(p[1] for p in pts)) + 4,
        )
        if bounds.w < 2 or bounds.h < 2:
            return
        s = pygame.Surface((bounds.w, bounds.h), pygame.SRCALPHA)
        local = [(p[0] - bounds.x, p[1] - bounds.y) for p in pts]
        pygame.draw.polygon(s, (self.r, self.g, self.b, alpha), local)
        surface.blit(s, (bounds.x, bounds.y))


# ── Helpers ───────────────────────────────────────────────────
def _burst(x, y, palette, count, sz_range, lt_range,
           speed_range, gravity=0.13, drag=0.94):
    out = []
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(*speed_range)
        out.append(Particle(
            x, y, random.choice(palette),
            math.cos(angle) * speed, math.sin(angle) * speed,
            size=random.randint(*sz_range),
            lifetime=random.randint(*lt_range),
            gravity=gravity, drag=drag,
        ))
    return out


class ParticleSystem:
    def __init__(self):
        self._pool: list = []

    # ── Emitters ──────────────────────────────────────────────
    def emit_gem(self, x, y):
        self._pool += _burst(x, y,
            [(255, 225, 65), (255, 200, 40), (255, 252, 140),
             (205, 160, 18), (255, 175, 25)],
            count=28, sz_range=(2, 6), lt_range=(32, 60),
            speed_range=(1.8, 5.5), gravity=0.14)
        # Bright central flash
        for _ in range(6):
            a = random.uniform(0, math.tau)
            self._pool.append(Particle(
                x, y, (255, 255, 200),
                math.cos(a) * 0.8, math.sin(a) * 0.8,
                size=7, lifetime=12, gravity=0.0, drag=0.85,
            ))

    def emit_trap(self, x, y):
        self._pool += _burst(x, y,
            [(215, 42, 42), (255, 90, 90), (165, 18, 18),
             (255, 140, 55), (255, 55, 55)],
            count=22, sz_range=(2, 5), lt_range=(20, 42),
            speed_range=(1.5, 4.5), gravity=0.10)

    def emit_goal(self, x, y):
        self._pool += _burst(x, y,
            [(40, 215, 108), (98, 255, 162), (22, 165, 85),
             (185, 255, 205), (38, 235, 128)],
            count=45, sz_range=(3, 8), lt_range=(50, 90),
            speed_range=(2.2, 9.0), gravity=0.055)

    def emit_confetti(self, x, y, count=120):
        palette = [
            (255, 72,  72),  (255, 200, 48), (48,  200,  98),
            (72, 138, 255),  (200, 72, 255), (72,  220, 255),
            (255, 128,  48), (255, 215,  55),(38,  210, 108),
        ]
        for _ in range(count):
            angle = random.uniform(-math.pi * 0.95, -math.pi * 0.05)
            speed = random.uniform(4, 15)
            dx    = random.uniform(-5, 5)
            col   = random.choice(palette)
            sz    = random.randint(4, 8)
            lt    = random.randint(70, 120)
            spin  = random.uniform(-0.18, 0.18)
            self._pool.append(SquareParticle(
                x, y, col,
                math.cos(angle) * speed + dx,
                math.sin(angle) * speed,
                size=sz, lifetime=lt, spin=spin,
            ))

    def emit_trail(self, x, y, color, size=3, lifetime=16):
        r = random.uniform(-0.3, 0.3)
        self._pool.append(Particle(
            x + random.uniform(-2, 2),
            y + random.uniform(-2, 2),
            color, r, r,
            size=size, lifetime=lifetime, gravity=0.0, drag=1.0,
        ))

    def emit_wall_bump(self, x, y, color, count=5):
        self._pool += _burst(x, y,
            [color, tuple(min(255, v + 40) for v in color)],
            count=count, sz_range=(1, 3), lt_range=(8, 18),
            speed_range=(0.8, 2.5), gravity=0.06, drag=0.90)

    def emit_energy_spark(self, x, y, color, count=8):
        self._pool += _burst(x, y,
            [color, tuple(min(255, v + 60) for v in color)],
            count=count, sz_range=(1, 3), lt_range=(12, 24),
            speed_range=(0.6, 2.5), gravity=0.04, drag=0.92)

    # ── Core ──────────────────────────────────────────────────
    def update(self):
        self._pool = [p for p in self._pool if p.update()]

    def draw(self, surface):
        for p in self._pool:
            p.draw(surface)

    def clear(self):
        self._pool.clear()

    @property
    def count(self):
        return len(self._pool)
