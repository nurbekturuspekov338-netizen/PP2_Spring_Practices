import pygame
import math
from collections import deque

# ── Colour palette ──────────────────────────────────────────────────────────
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
RED     = (255,  50,  50)
GREEN   = ( 50, 200,  50)
BLUE    = ( 50, 130, 255)
YELLOW  = (255, 220,   0)
CYAN    = (  0, 220, 220)
MAGENTA = (220,   0, 220)
ORANGE  = (255, 140,   0)
PURPLE  = (150,  50, 220)
GREY    = (160, 160, 160)

PALETTE = [BLACK, WHITE, RED, GREEN, BLUE, YELLOW,
           CYAN, MAGENTA, ORANGE, PURPLE, GREY]

# ── Brush sizes ──────────────────────────────────────────────────────────────
BRUSH_SIZES = [2, 5, 10]          # small / medium / large


# ── Geometry drawing ─────────────────────────────────────────────────────────
def draw_geometry(surface, shape, is_preview=False):
    """Draw all supported geometric shapes onto *surface*."""
    color  = shape['color']
    start  = shape['start']
    end    = shape['end']
    bsize  = shape.get('brush_size', 2)
    width  = 1 if is_preview else bsize

    x1, y1 = start
    x2, y2 = end

    stype = shape['type']

    if stype == 'rect':
        rx, ry = min(x1, x2), min(y1, y2)
        pygame.draw.rect(surface, color,
                         (rx, ry, abs(x2 - x1), abs(y2 - y1)), width)

    elif stype == 'square':
        side = max(abs(x2 - x1), abs(y2 - y1))
        rx = x1 if x2 > x1 else x1 - side
        ry = y1 if y2 > y1 else y1 - side
        pygame.draw.rect(surface, color, (rx, ry, side, side), width)

    elif stype == 'circle':
        rad = int(math.hypot(x2 - x1, y2 - y1))
        pygame.draw.circle(surface, color, start, rad, width)

    elif stype == 'line':
        pygame.draw.line(surface, color, start, end, width)

    elif stype == 'right triangle':
        pygame.draw.polygon(surface, color, [start, (x1, y2), end], width)

    elif stype == 'equilateral triangle':
        w = abs(x2 - x1)
        h = int((math.sqrt(3) / 2) * w)
        direction = 1 if y2 > y1 else -1
        p1 = (x1, y1)
        p2 = (x1 - w // 2, y1 + h * direction)
        p3 = (x1 + w // 2, y1 + h * direction)
        pygame.draw.polygon(surface, color, [p1, p2, p3], width)

    elif stype == 'rhombus':
        dx, dy = x2 - x1, y2 - y1
        points = [
            (x1 + dx // 2, y1),
            (x2,           y1 + dy // 2),
            (x1 + dx // 2, y2),
            (x1,           y1 + dy // 2),
        ]
        pygame.draw.polygon(surface, color, points, width)


# ── Flood fill ───────────────────────────────────────────────────────────────
def flood_fill(surface, pos, fill_color):
    """BFS flood-fill on *surface* starting at *pos* with *fill_color*."""
    sx, sy = int(pos[0]), int(pos[1])
    w, h   = surface.get_size()

    if not (0 <= sx < w and 0 <= sy < h):
        return

    target_color = surface.get_at((sx, sy))[:3]   # ignore alpha
    fill_rgb      = fill_color[:3]

    if target_color == fill_rgb:
        return                                      # nothing to do

    # Lock surface for pixel-level access
    surface.lock()
    queue = deque()
    queue.append((sx, sy))
    visited = set()
    visited.add((sx, sy))

    while queue:
        cx, cy = queue.popleft()
        if surface.get_at((cx, cy))[:3] != target_color:
            continue
        surface.set_at((cx, cy), fill_rgb)

        for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
            if (0 <= nx < w and 0 <= ny < h
                    and (nx, ny) not in visited
                    and surface.get_at((nx, ny))[:3] == target_color):
                visited.add((nx, ny))
                queue.append((nx, ny))

    surface.unlock()
