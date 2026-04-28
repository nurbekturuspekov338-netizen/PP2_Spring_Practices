import pygame
import random
import math

# ── Colours ──────────────────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (150, 150, 150)
DARK_GRAY = (60, 60, 60)
RED    = (220, 50,  50)
GREEN  = (50,  200, 80)
BLUE   = (50,  120, 220)
YELLOW = (255, 210, 0)
ORANGE = (255, 140, 0)
CYAN   = (0,   220, 220)
PURPLE = (170, 0,   255)
BROWN  = (120, 70,  20)

SCREEN_W = 800
SCREEN_H = 700

# Lane centres (6 lanes)
LANE_COUNT = 6
ROAD_LEFT  = 80
ROAD_RIGHT = 720
LANE_W = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT
LANES  = [ROAD_LEFT + LANE_W * i + LANE_W // 2 for i in range(LANE_COUNT)]

CAR_COLORS = {
    "blue":   (50,  120, 220),
    "red":    (220, 50,  50),
    "green":  (50,  200, 80),
    "yellow": (255, 210, 0),
}

# ── Drawing helpers ───────────────────────────────────────────────────────────

def draw_rounded_rect(surf, color, rect, radius=8):
    pygame.draw.rect(surf, color, rect, border_radius=radius)


def draw_car(surf, color, cx, cy, w=36, h=60):
    """Draw a simple top-down car."""
    body_rect = pygame.Rect(cx - w//2, cy - h//2, w, h)
    draw_rounded_rect(surf, color, body_rect, 8)

    # Windshields
    wf_rect = pygame.Rect(cx - w//2 + 4, cy - h//2 + 6, w - 8, 12)
    draw_rounded_rect(surf, (160, 220, 255), wf_rect, 4)
    wb_rect = pygame.Rect(cx - w//2 + 4, cy + h//2 - 18, w - 8, 10)
    draw_rounded_rect(surf, (160, 220, 255), wb_rect, 4)

    # Wheels
    whl_color = (30, 30, 30)
    for wx, wy in [(-w//2 - 3, -h//4), (w//2 - 9, -h//4),
                   (-w//2 - 3,  h//4 - 5), (w//2 - 9,  h//4 - 5)]:
        pygame.draw.rect(surf, whl_color, (cx + wx, cy + wy, 12, 10), border_radius=2)

    # Headlights / taillights
    pygame.draw.circle(surf, YELLOW, (cx - w//2 + 5, cy - h//2 + 3), 4)
    pygame.draw.circle(surf, YELLOW, (cx + w//2 - 5, cy - h//2 + 3), 4)
    pygame.draw.circle(surf, RED,    (cx - w//2 + 5, cy + h//2 - 3), 4)
    pygame.draw.circle(surf, RED,    (cx + w//2 - 5, cy + h//2 - 3), 4)


ENEMY_PALETTE = [
    (200, 60,  60),
    (60,  60,  200),
    (200, 150, 0),
    (80,  160, 80),
    (180, 60,  180),
    (0,   160, 160),
]


# ── Sprite base ───────────────────────────────────────────────────────────────

class RectSprite(pygame.sprite.Sprite):
    """Sprite backed by a surface we draw ourselves (no image files needed)."""
    def __init__(self, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.rect  = self.image.get_rect()
        self._w, self._h = w, h

    def _redraw(self):
        """Override to repaint self.image."""
        pass

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


# ── Player ────────────────────────────────────────────────────────────────────

class Player(RectSprite):
    W, H = 36, 60

    def __init__(self, car_color="blue"):
        super().__init__(self.W, self.H)
        self.color = CAR_COLORS.get(car_color, BLUE)
        self.rect.center = (SCREEN_W // 2, SCREEN_H - 100)
        self.speed = 6
        self.shield = False
        self.nitro  = False
        self.nitro_timer  = 0
        self.shield_timer = 0
        self._redraw()

    def _redraw(self):
        self.image.fill((0, 0, 0, 0))
        draw_car(self.image, self.color, self.W // 2, self.H // 2, self.W, self.H)
        if self.shield:
            pygame.draw.ellipse(self.image, (*CYAN, 80),
                                (0, 0, self.W, self.H), 3)

    def move(self, keys, dt):
        spd = self.speed * (1.8 if self.nitro else 1.0)
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.rect.x -= spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.rect.x += spd
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.rect.y -= spd
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.rect.y += spd
        # Clamp to road
        self.rect.clamp_ip(pygame.Rect(ROAD_LEFT - 10, 0, ROAD_RIGHT - ROAD_LEFT + 20, SCREEN_H))

    def update_timers(self, dt):
        if self.nitro:
            self.nitro_timer -= dt
            if self.nitro_timer <= 0:
                self.nitro = False
        if self.shield:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield = False
        self._redraw()

    def activate_nitro(self, duration=4.0):
        self.nitro = True
        self.nitro_timer = duration

    def activate_shield(self, duration=0):
        self.shield = True
        self.shield_timer = 9999  # until hit

    def use_shield(self):
        self.shield = False
        self.shield_timer = 0


# ── Enemy / Traffic ───────────────────────────────────────────────────────────

class EnemyCar(RectSprite):
    W, H = 36, 60

    def __init__(self, speed, player_rect):
        super().__init__(self.W, self.H)
        self.color = random.choice(ENEMY_PALETTE)
        self.speed = speed + random.uniform(-1, 1)
        self._place_safe(player_rect)
        self._redraw()

    def _place_safe(self, player_rect, tries=20):
        for _ in range(tries):
            lane = random.choice(LANES)
            y = random.randint(-200, -self.H)
            self.rect.centerx = lane
            self.rect.top = y
            if not self.rect.colliderect(player_rect.inflate(60, 120)):
                return
        self.rect.top = -200

    def _redraw(self):
        self.image.fill((0, 0, 0, 0))
        draw_car(self.image, self.color, self.W // 2, self.H // 2, self.W, self.H)

    def update(self, dt):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 20:
            self.kill()


# ── Road Obstacles ────────────────────────────────────────────────────────────

class OilSpill(RectSprite):
    """Slows the player, does not kill."""
    W, H = 50, 30

    def __init__(self, speed):
        super().__init__(self.W, self.H)
        self.speed = speed * 0.7
        self.rect.centerx = random.choice(LANES)
        self.rect.top = random.randint(-300, -40)
        self._redraw()

    def _redraw(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.ellipse(self.image, (30, 20, 60, 180), (0, 0, self.W, self.H))
        pygame.draw.ellipse(self.image, (80, 50, 120, 120),
                            (4, 4, self.W - 8, self.H - 8))

    def update(self, dt):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 20:
            self.kill()


class Barrier(RectSprite):
    """Kills on contact (unless shield)."""
    W, H = 44, 22

    def __init__(self, speed):
        super().__init__(self.W, self.H)
        self.speed = speed * 0.8
        self.rect.centerx = random.choice(LANES)
        self.rect.top = random.randint(-400, -60)
        self._redraw()

    def _redraw(self):
        self.image.fill((0, 0, 0, 0))
        draw_rounded_rect(self.image, ORANGE, (0, 6, self.W, self.H - 12), 4)
        # Stripes
        for i in range(4):
            x = i * 11 + 2
            pygame.draw.rect(self.image, BLACK, (x, 6, 5, self.H - 12))

    def update(self, dt):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 20:
            self.kill()


class Pothole(RectSprite):
    """Slows and damages (counts as a crash)."""
    W, H = 38, 28

    def __init__(self, speed):
        super().__init__(self.W, self.H)
        self.speed = speed * 0.6
        self.rect.centerx = random.choice(LANES)
        self.rect.top = random.randint(-400, -80)
        self._redraw()

    def _redraw(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.ellipse(self.image, (40, 30, 20), (0, 0, self.W, self.H))
        pygame.draw.ellipse(self.image, (25, 18, 8),
                            (5, 5, self.W - 10, self.H - 10))

    def update(self, dt):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 20:
            self.kill()


# ── Coins ─────────────────────────────────────────────────────────────────────

class Coin(RectSprite):
    W = H = 24

    def __init__(self, speed):
        super().__init__(self.W, self.H)
        self.speed = speed * 0.65
        self.rect.centerx = random.choice(LANES)
        self.rect.top = random.randint(-600, -40)
        self._redraw()

    def _redraw(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, YELLOW,   (self.W // 2, self.H // 2), self.W // 2)
        pygame.draw.circle(self.image, (200, 160, 0), (self.W // 2, self.H // 2), self.W // 2, 2)
        # "$" mark
        fnt = pygame.font.SysFont("Arial", 12, bold=True)
        txt = fnt.render("$", True, (120, 80, 0))
        self.image.blit(txt, txt.get_rect(center=(self.W // 2, self.H // 2)))

    def update(self, dt):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 20:
            self.kill()


# ── Power-ups ─────────────────────────────────────────────────────────────────

POWERUP_TIMEOUT = 8.0   # seconds before disappearing if not collected

class PowerUp(RectSprite):
    W = H = 32
    KIND_NITRO  = "nitro"
    KIND_SHIELD = "shield"
    KIND_REPAIR = "repair"

    ICONS = {
        KIND_NITRO:  ("⚡", (255, 220, 0),   (200, 80, 0)),
        KIND_SHIELD: ("🛡", (0,  200, 255),  (0,  80, 180)),
        KIND_REPAIR: ("✚",  (80, 220, 80),   (20, 120, 20)),
    }

    def __init__(self, kind, speed):
        super().__init__(self.W, self.H)
        self.kind  = kind
        self.speed = speed * 0.55
        self.age   = 0.0
        self.rect.centerx = random.choice(LANES)
        self.rect.top = random.randint(-500, -60)
        self._redraw()

    def _redraw(self):
        label, bg, border = self.ICONS[self.kind]
        self.image.fill((0, 0, 0, 0))
        draw_rounded_rect(self.image, bg, (0, 0, self.W, self.H), 8)
        pygame.draw.rect(self.image, border, (0, 0, self.W, self.H), 2, border_radius=8)
        try:
            fnt = pygame.font.SysFont("Segoe UI Emoji", 16)
            txt = fnt.render(label, True, WHITE)
        except Exception:
            fnt = pygame.font.SysFont("Arial", 14, bold=True)
            lbl_map = {self.KIND_NITRO: "N", self.KIND_SHIELD: "S", self.KIND_REPAIR: "R"}
            txt = fnt.render(lbl_map[self.kind], True, WHITE)
        self.image.blit(txt, txt.get_rect(center=(self.W // 2, self.H // 2)))

    def update(self, dt):
        self.rect.y += self.speed
        self.age += dt
        if self.rect.top > SCREEN_H + 20 or self.age > POWERUP_TIMEOUT:
            self.kill()


# ── Dynamic Road Events ───────────────────────────────────────────────────────

class MovingBarrier(RectSprite):
    """Horizontally sweeping barrier – a dynamic road event."""
    W, H = 60, 22

    def __init__(self, speed):
        super().__init__(self.W, self.H)
        self.fall_speed = speed * 0.7
        self.side_speed = random.choice([-2, 2]) * random.uniform(0.8, 1.4)
        self.rect.centerx = random.choice(LANES)
        self.rect.top = random.randint(-400, -60)
        self._redraw()

    def _redraw(self):
        self.image.fill((0, 0, 0, 0))
        draw_rounded_rect(self.image, RED, (0, 4, self.W, self.H - 8), 4)
        for i in range(5):
            x = i * 12 + 2
            pygame.draw.rect(self.image, WHITE, (x, 4, 6, self.H - 8))

    def update(self, dt):
        self.rect.y += self.fall_speed
        self.rect.x += self.side_speed
        if self.rect.left < ROAD_LEFT:
            self.rect.left = ROAD_LEFT
            self.side_speed = abs(self.side_speed)
        if self.rect.right > ROAD_RIGHT:
            self.rect.right = ROAD_RIGHT
            self.side_speed = -abs(self.side_speed)
        if self.rect.top > SCREEN_H + 20:
            self.kill()


class NitroBoost(RectSprite):
    """Rare pickup that gives a nitro burst."""
    W = H = 34

    def __init__(self, speed):
        super().__init__(self.W, self.H)
        self.speed = speed * 0.5
        self.rect.centerx = random.choice(LANES)
        self.rect.top = random.randint(-600, -100)
        self._redraw()

    def _redraw(self):
        self.image.fill((0, 0, 0, 0))
        draw_rounded_rect(self.image, (255, 180, 0), (0, 0, self.W, self.H), 10)
        fnt = pygame.font.SysFont("Arial", 11, bold=True)
        txt = fnt.render("NITRO", True, BLACK)
        self.image.blit(txt, txt.get_rect(center=(self.W // 2, self.H // 2)))

    def update(self, dt):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 20:
            self.kill()


# ── Speedbump ─────────────────────────────────────────────────────────────────

class SpeedBump(RectSprite):
    W, H = 80, 16

    def __init__(self, speed):
        super().__init__(self.W, self.H)
        self.speed = speed * 0.55
        # Place across 2 lanes
        lane_idx = random.randint(0, LANE_COUNT - 2)
        self.rect.centerx = (LANES[lane_idx] + LANES[lane_idx + 1]) // 2
        self.rect.top = random.randint(-400, -80)
        self._redraw()

    def _redraw(self):
        self.image.fill((0, 0, 0, 0))
        draw_rounded_rect(self.image, (200, 200, 0), (0, 0, self.W, self.H), 4)
        for i in range(6):
            x = i * 13 + 2
            pygame.draw.rect(self.image, BLACK, (x, 2, 7, self.H - 4))

    def update(self, dt):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 20:
            self.kill()
