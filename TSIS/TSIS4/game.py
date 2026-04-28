# game.py — Core game entities and logic

import random
import pygame
from config import *


# ─────────────────────────────────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────────────────────────────────

class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def copy(self):
        return Point(self.x, self.y)


def random_free_pos(occupied: list[Point]) -> Point:
    """Return a grid cell not in *occupied*."""
    occ_set = {(p.x, p.y) for p in occupied}
    candidates = [
        (x, y)
        for x in range(COLS)
        for y in range(ROWS)
        if (x, y) not in occ_set
    ]
    if not candidates:
        return Point(0, 0)
    x, y = random.choice(candidates)
    return Point(x, y)


# ─────────────────────────────────────────────────────────────────────────────
# Snake
# ─────────────────────────────────────────────────────────────────────────────

class Snake:
    def __init__(self, color=(200, 200, 0)):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx = 1
        self.dy = 0
        self.dead = False
        self.color = color
        self.shield = False          # shield power-up active
        self._pending_dir = None     # next direction (buffered once per frame)

    # ── Direction input ────────────────────────────────────────────────────

    def set_direction(self, dx: int, dy: int):
        # Prevent 180° reversal
        if (dx != -self.dx or dy != -self.dy):
            self._pending_dir = (dx, dy)

    # ── Movement ───────────────────────────────────────────────────────────

    def move(self, obstacles: list[Point]):
        if self._pending_dir:
            self.dx, self.dy = self._pending_dir
            self._pending_dir = None

        # Shift body
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        head = self.body[0]
        head.x += self.dx
        head.y += self.dy

        # Wall collision
        wall_hit = (
            head.x < 0 or head.x >= COLS or
            head.y < 0 or head.y >= ROWS
        )
        # Self collision
        self_hit = any(head.x == s.x and head.y == s.y for s in self.body[1:])
        # Obstacle collision
        obs_hit = any(head.x == o.x and head.y == o.y for o in obstacles)

        if wall_hit or self_hit or obs_hit:
            if self.shield:
                # Shield absorbs one hit — teleport head to safe spot
                self.shield = False
                safe = random_free_pos(self.body + obstacles)
                head.x, head.y = safe.x, safe.y
            else:
                self.dead = True

    # ── Growth / shrink ────────────────────────────────────────────────────

    def grow(self, segments: int = 1):
        tail = self.body[-1]
        for _ in range(segments):
            self.body.append(tail.copy())

    def shrink(self, segments: int = 2):
        """Shrink snake; returns True if snake becomes too short (game over)."""
        for _ in range(segments):
            if len(self.body) > 1:
                self.body.pop()
        return len(self.body) <= 1

    # ── Rendering ──────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        for i, seg in enumerate(self.body):
            if i == 0:
                color = RED
            else:
                color = self.color
            rect = pygame.Rect(seg.x * CELL, seg.y * CELL, CELL, CELL)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

        # Draw shield indicator on head
        if self.shield:
            cx = self.body[0].x * CELL + CELL // 2
            cy = self.body[0].y * CELL + CELL // 2
            pygame.draw.circle(surface, CYAN, (cx, cy), CELL // 2 - 2, 2)


# ─────────────────────────────────────────────────────────────────────────────
# Food
# ─────────────────────────────────────────────────────────────────────────────

class FoodItem:
    """Base food item."""

    def __init__(self, pos: Point, weight: int, color: tuple, lifetime_ms: int):
        self.pos = pos
        self.weight = weight
        self.color = color
        self.lifetime = lifetime_ms
        self.created = pygame.time.get_ticks()
        self.is_poison = False

    def is_expired(self) -> bool:
        return (pygame.time.get_ticks() - self.created) > self.lifetime

    def draw(self, surface: pygame.Surface):
        rect = pygame.Rect(self.pos.x * CELL + 2, self.pos.y * CELL + 2, CELL - 4, CELL - 4)
        pygame.draw.rect(surface, self.color, rect)
        # Pulsing border for gold food
        if self.color == GOLD:
            pygame.draw.rect(surface, WHITE, rect, 1)


def make_normal_food(occupied: list[Point]) -> FoodItem:
    pos = random_free_pos(occupied)
    if random.randint(1, 5) == 5:
        return FoodItem(pos, 3, GOLD, GOLD_FOOD_LIFETIME)
    return FoodItem(pos, 1, GREEN, NORMAL_FOOD_LIFETIME)


def make_poison_food(occupied: list[Point]) -> FoodItem:
    pos = random_free_pos(occupied)
    item = FoodItem(pos, 0, DARK_RED, POISON_FOOD_LIFETIME)
    item.is_poison = True
    return item


# ─────────────────────────────────────────────────────────────────────────────
# Power-ups
# ─────────────────────────────────────────────────────────────────────────────

POWERUP_SPEED_BOOST = "speed_boost"
POWERUP_SLOW_MOTION = "slow_motion"
POWERUP_SHIELD      = "shield"

POWERUP_META = {
    POWERUP_SPEED_BOOST: {"color": ORANGE, "label": "FAST!"},
    POWERUP_SLOW_MOTION: {"color": BLUE,   "label": "SLOW"},
    POWERUP_SHIELD:      {"color": PURPLE,  "label": "SHIELD"},
}


class PowerUp:
    """A collectible power-up item on the field."""

    def __init__(self, kind: str, occupied: list[Point]):
        self.kind = kind
        self.pos = random_free_pos(occupied)
        self.color = POWERUP_META[kind]["color"]
        self.label = POWERUP_META[kind]["label"]
        self.created = pygame.time.get_ticks()

    def is_expired(self) -> bool:
        return (pygame.time.get_ticks() - self.created) > POWERUP_FIELD_LIFETIME

    def draw(self, surface: pygame.Surface):
        rect = pygame.Rect(self.pos.x * CELL, self.pos.y * CELL, CELL, CELL)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, WHITE, rect, 1)


class ActiveEffect:
    """Tracks a currently-running power-up effect."""

    def __init__(self, kind: str):
        self.kind = kind
        self.started = pygame.time.get_ticks()

    def is_done(self) -> bool:
        return (pygame.time.get_ticks() - self.started) > POWERUP_EFFECT_DURATION

    def remaining_ms(self) -> int:
        elapsed = pygame.time.get_ticks() - self.started
        return max(0, POWERUP_EFFECT_DURATION - elapsed)


# ─────────────────────────────────────────────────────────────────────────────
# Obstacles
# ─────────────────────────────────────────────────────────────────────────────

def generate_obstacles(level: int, snake_body: list[Point]) -> list[Point]:
    """Randomly place obstacle blocks for the given level (level >= 3)."""
    if level < OBSTACLE_START_LEVEL:
        return []

    count = OBSTACLES_PER_LEVEL * (level - OBSTACLE_START_LEVEL + 1)
    obstacles: list[Point] = []

    # Keep a safe zone around the snake head (3-cell radius)
    head = snake_body[0]
    safe = {(x, y) for x in range(head.x - 3, head.x + 4)
                   for y in range(head.y - 3, head.y + 4)}

    occupied_pts = snake_body + obstacles
    for _ in range(count):
        attempts = 0
        while attempts < 200:
            pos = random_free_pos(occupied_pts)
            if (pos.x, pos.y) not in safe:
                obstacles.append(pos)
                occupied_pts.append(pos)
                break
            attempts += 1

    return obstacles


# ─────────────────────────────────────────────────────────────────────────────
# GameState — orchestrates everything except rendering screens
# ─────────────────────────────────────────────────────────────────────────────

class GameState:
    def __init__(self, snake_color=(200, 200, 0)):
        self.snake = Snake(color=snake_color)
        self.score = 0
        self.level = 1
        self.game_over = False

        self.obstacles: list[Point] = []

        # Foods
        self.normal_food  = make_normal_food(self._all_blocked())
        self.poison_food  = make_poison_food(self._all_blocked())

        # Power-ups
        self.field_powerup: PowerUp | None = None
        self._next_powerup_spawn = pygame.time.get_ticks() + random.randint(5000, 12000)
        self.active_effect: ActiveEffect | None = None

        self._prev_level = 1

    # ── Helpers ────────────────────────────────────────────────────────────

    def _all_blocked(self) -> list[Point]:
        """All occupied cells: snake + obstacles + existing foods."""
        blocked = list(self.snake.body) + self.obstacles
        if hasattr(self, "normal_food") and self.normal_food:
            blocked.append(self.normal_food.pos)
        if hasattr(self, "poison_food") and self.poison_food:
            blocked.append(self.poison_food.pos)
        if hasattr(self, "field_powerup") and self.field_powerup:
            blocked.append(self.field_powerup.pos)
        return blocked

    def current_fps(self) -> int:
        fps = BASE_FPS + (self.level - 1) * FPS_PER_LEVEL
        if self.active_effect:
            if self.active_effect.kind == POWERUP_SPEED_BOOST:
                fps += 4
            elif self.active_effect.kind == POWERUP_SLOW_MOTION:
                fps = max(2, fps - 4)
        return fps

    # ── Update ─────────────────────────────────────────────────────────────

    def update(self):
        if self.game_over:
            return

        now = pygame.time.get_ticks()

        # Expire active effect
        if self.active_effect and self.active_effect.is_done():
            self.active_effect = None

        # Respawn expired foods
        if self.normal_food.is_expired():
            self.normal_food = make_normal_food(self._all_blocked())
        if self.poison_food.is_expired():
            self.poison_food = make_poison_food(self._all_blocked())

        # Spawn / expire field power-up
        if self.field_powerup and self.field_powerup.is_expired():
            self.field_powerup = None
        if self.field_powerup is None and now >= self._next_powerup_spawn:
            kind = random.choice([POWERUP_SPEED_BOOST, POWERUP_SLOW_MOTION, POWERUP_SHIELD])
            self.field_powerup = PowerUp(kind, self._all_blocked())
            self._next_powerup_spawn = now + random.randint(8000, 18000)

        # Move snake
        self.snake.move(self.obstacles)
        if self.snake.dead:
            self.game_over = True
            return

        head = self.snake.body[0]

        # Eat normal food
        if head.x == self.normal_food.pos.x and head.y == self.normal_food.pos.y:
            self.score += self.normal_food.weight
            self.snake.grow(self.normal_food.weight)
            self.normal_food = make_normal_food(self._all_blocked())

        # Eat poison food
        elif head.x == self.poison_food.pos.x and head.y == self.poison_food.pos.y:
            too_short = self.snake.shrink(2)
            if too_short:
                self.game_over = True
                return
            self.poison_food = make_poison_food(self._all_blocked())

        # Collect power-up
        if self.field_powerup and head.x == self.field_powerup.pos.x and head.y == self.field_powerup.pos.y:
            kind = self.field_powerup.kind
            if kind == POWERUP_SHIELD:
                self.snake.shield = True
            else:
                self.active_effect = ActiveEffect(kind)
            self.field_powerup = None

        # Level up
        new_level = (self.score // SCORE_PER_LEVEL) + 1
        if new_level != self._prev_level:
            self._prev_level = new_level
            self.level = new_level
            if new_level >= OBSTACLE_START_LEVEL:
                self.obstacles = generate_obstacles(new_level, self.snake.body)

    # ── Render ─────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, show_grid: bool):
        surface.fill(BLACK)

        if show_grid:
            for i in range(0, WIDTH, CELL):
                pygame.draw.line(surface, GRAY, (i, 0), (i, HEIGHT))
                pygame.draw.line(surface, GRAY, (0, i), (WIDTH, i))

        # Obstacles
        for obs in self.obstacles:
            rect = pygame.Rect(obs.x * CELL, obs.y * CELL, CELL, CELL)
            pygame.draw.rect(surface, LIGHT_GRAY, rect)
            pygame.draw.rect(surface, WHITE, rect, 1)

        self.normal_food.draw(surface)
        self.poison_food.draw(surface)
        if self.field_powerup:
            self.field_powerup.draw(surface)
        self.snake.draw(surface)
