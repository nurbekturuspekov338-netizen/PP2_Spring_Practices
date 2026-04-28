import pygame
import sys
from datetime import datetime

from tools import (
    draw_geometry, flood_fill,
    PALETTE, BRUSH_SIZES,
    BLACK, WHITE, RED, GREEN, BLUE,
    YELLOW, CYAN, MAGENTA, ORANGE, PURPLE, GREY,
)

# ── Layout constants ──────────────────────────────────────────────────────────
TOOLBAR_W   = 170        # left panel width
CANVAS_W    = 900
CANVAS_H    = 660
WIN_W       = TOOLBAR_W + CANVAS_W
WIN_H       = CANVAS_H

# Toolbar geometry
PAD         = 10
SWATCH_SIZE = 30
BTN_H       = 32
BTN_W       = TOOLBAR_W - 2 * PAD

# ── Colour constants ──────────────────────────────────────────────────────────
BG_DARK   = (18,  18,  22)
BG_PANEL  = (28,  28,  36)
ACCENT    = (90, 150, 255)
TEXT_COL  = (210, 210, 220)
SEL_RING  = (255, 255, 100)


# ═══════════════════════════════════════════════════════════════════════════════
#  Toolbar
# ═══════════════════════════════════════════════════════════════════════════════
class Toolbar:
    TOOLS = [
        ('pencil',              'Pencil',        'P'),
        ('brush',               'Brush',         'B'),
        ('line',                'Line',          'L'),
        ('rect',                'Rectangle',     'R'),
        ('square',              'Square',        'Q'),
        ('circle',              'Circle',        'C'),
        ('right triangle',      'Rt-Triangle',   'T'),
        ('equilateral triangle','Eq-Triangle',   'E'),
        ('rhombus',             'Rhombus',       'H'),
        ('fill',                'Fill',          'F'),
        ('text',                'Text',          'X'),
        ('eraser',              'Eraser',        'Z'),
    ]

    SIZE_LABELS = ['S (1)', 'M (2)', 'L (3)']

    def __init__(self, font_sm, font_xs):
        self.font_sm = font_sm
        self.font_xs = font_xs
        self._build_layout()

    def _build_layout(self):
        """Pre-compute bounding rects for every clickable element."""
        y = PAD

        # ── Section: Tools ──
        self.tool_label_y = y
        y += 20

        self.tool_rects = {}   # tool_id → pygame.Rect
        for tid, label, key in self.TOOLS:
            r = pygame.Rect(PAD, y, BTN_W, BTN_H)
            self.tool_rects[tid] = r
            y += BTN_H + 4

        y += 8

        # ── Section: Brush size ──
        self.size_label_y = y
        y += 20

        self.size_rects = {}
        sw = (BTN_W - 8) // 3
        for i in range(3):
            r = pygame.Rect(PAD + i * (sw + 4), y, sw, BTN_H)
            self.size_rects[i] = r
        y += BTN_H + 8

        # ── Section: Colour palette ──
        self.palette_label_y = y
        y += 20

        self.swatch_rects = {}
        cols_per_row = 4
        for idx, col in enumerate(PALETTE):
            cx = PAD + (idx % cols_per_row) * (SWATCH_SIZE + 4)
            cy = y + (idx // cols_per_row) * (SWATCH_SIZE + 4)
            self.swatch_rects[idx] = pygame.Rect(cx, cy, SWATCH_SIZE, SWATCH_SIZE)

        # ── Hint strip at the bottom ──
        self.hint_y = WIN_H - 20

    # ─── Draw ─────────────────────────────────────────────────────────────────
    def draw(self, surface, curr_tool, curr_size_idx, curr_color):
        # Panel background
        pygame.draw.rect(surface, BG_PANEL, (0, 0, TOOLBAR_W, WIN_H))
        pygame.draw.line(surface, ACCENT, (TOOLBAR_W-1, 0), (TOOLBAR_W-1, WIN_H), 1)

        def label(text, y, color=TEXT_COL):
            s = self.font_xs.render(text, True, color)
            surface.blit(s, (PAD, y))

        # ── Tools ──
        label('TOOLS', self.tool_label_y, ACCENT)
        for tid, lbl, key in self.TOOLS:
            r    = self.tool_rects[tid]
            sel  = (tid == curr_tool)
            bcol = ACCENT if sel else (45, 45, 58)
            tcol = BLACK  if sel else TEXT_COL
            pygame.draw.rect(surface, bcol, r, border_radius=4)
            if sel:
                pygame.draw.rect(surface, SEL_RING, r, 2, border_radius=4)
            txt = self.font_sm.render(f'{key}  {lbl}', True, tcol)
            surface.blit(txt, (r.x + 6, r.y + (BTN_H - txt.get_height()) // 2))

        # ── Brush size ──
        label('SIZE', self.size_label_y, ACCENT)
        for i, lbl in enumerate(self.SIZE_LABELS):
            r   = self.size_rects[i]
            sel = (i == curr_size_idx)
            pygame.draw.rect(surface, ACCENT if sel else (45, 45, 58), r, border_radius=4)
            if sel:
                pygame.draw.rect(surface, SEL_RING, r, 2, border_radius=4)
            s = self.font_xs.render(lbl, True, BLACK if sel else TEXT_COL)
            surface.blit(s, (r.x + (r.width - s.get_width()) // 2,
                              r.y + (BTN_H - s.get_height()) // 2))

        # ── Palette ──
        label('COLOR', self.palette_label_y, ACCENT)
        for idx, col in enumerate(PALETTE):
            r = self.swatch_rects[idx]
            pygame.draw.rect(surface, col, r, border_radius=3)
            if col == curr_color:
                pygame.draw.rect(surface, SEL_RING, r, 3, border_radius=3)
            else:
                pygame.draw.rect(surface, (80, 80, 100), r, 1, border_radius=3)

        # ── Hint ──
        hint = self.font_xs.render('Ctrl+S  save  |  Esc quit', True, (100, 100, 120))
        surface.blit(hint, (PAD, self.hint_y))

    # ─── Hit-test ─────────────────────────────────────────────────────────────
    def handle_click(self, pos, curr_tool, curr_size_idx, curr_color):
        """Return updated (tool, size_idx, color) after a toolbar click."""
        for tid, r in self.tool_rects.items():
            if r.collidepoint(pos):
                return tid, curr_size_idx, curr_color
        for i, r in self.size_rects.items():
            if r.collidepoint(pos):
                return curr_tool, i, curr_color
        for idx, r in self.swatch_rects.items():
            if r.collidepoint(pos):
                return curr_tool, curr_size_idx, PALETTE[idx]
        return curr_tool, curr_size_idx, curr_color


# ═══════════════════════════════════════════════════════════════════════════════
#  Main application
# ═══════════════════════════════════════════════════════════════════════════════
def canvas_pos(mouse_pos):
    """Convert absolute mouse position to canvas-relative position."""
    return (mouse_pos[0] - TOOLBAR_W, mouse_pos[1])


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption('Paint — Practice 12')
    clock  = pygame.time.Clock()

    # Fonts
    font_sm = pygame.font.SysFont('consolas,monospace', 13, bold=True)
    font_xs = pygame.font.SysFont('consolas,monospace', 11)
    font_text = pygame.font.SysFont('arial,sans-serif', 22)   # text tool

    toolbar = Toolbar(font_sm, font_xs)

    # Canvas — separate surface (white background)
    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(WHITE)

    # State
    curr_tool     = 'pencil'
    curr_size_idx = 0          # index into BRUSH_SIZES
    curr_color    = BLACK

    shapes   = []              # list of committed shape dicts
    drawing  = False
    start_pos = (0, 0)
    last_pos  = (0, 0)        # for pencil continuity

    # Text tool state
    text_active  = False
    text_pos     = (0, 0)
    text_buffer  = ''

    def brush_size():
        return BRUSH_SIZES[curr_size_idx]

    def redraw_canvas():
        """Re-render all committed shapes onto canvas."""
        canvas.fill(WHITE)
        for s in shapes:
            if s['type'] in ('brush_line', 'pencil_line'):
                pygame.draw.line(canvas, s['color'],
                                 s['pos'], s['end'], s['radius'])
            elif s['type'] == 'fill_result':
                pass  # already baked into canvas pixels — handled separately
            elif s['type'] == 'text_commit':
                surf = font_text.render(s['text'], True, s['color'])
                canvas.blit(surf, s['pos'])
            else:
                draw_geometry(canvas, s)

    # ── Main loop ──────────────────────────────────────────────────────────────
    running = True
    while running:
        mouse_abs = pygame.mouse.get_pos()
        mouse_rel = canvas_pos(mouse_abs)   # canvas-relative
        on_canvas = mouse_abs[0] >= TOOLBAR_W

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ── Keyboard ────────────────────────────────────────────────────
            elif event.type == pygame.KEYDOWN:

                # Text tool captures all keystrokes when active
                if text_active:
                    if event.key == pygame.K_RETURN:
                        if text_buffer:
                            shapes.append({
                                'type':  'text_commit',
                                'text':  text_buffer,
                                'color': curr_color,
                                'pos':   text_pos,
                            })
                        text_active = False
                        text_buffer = ''
                        redraw_canvas()
                    elif event.key == pygame.K_ESCAPE:
                        text_active = False
                        text_buffer = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode:
                            text_buffer += event.unicode
                    continue  # swallow all keys while typing

                # Global shortcuts (when text tool is not active)
                mods = pygame.key.get_mods()
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    # Save canvas
                    fname = datetime.now().strftime('canvas_%Y%m%d_%H%M%S.png')
                    pygame.image.save(canvas, fname)
                    pygame.display.set_caption(f'Saved → {fname}')
                    continue

                if event.key == pygame.K_ESCAPE:
                    running = False

                # Tool shortcuts
                key_tool_map = {
                    pygame.K_p: 'pencil',
                    pygame.K_b: 'brush',
                    pygame.K_l: 'line',
                    pygame.K_r: 'rect',
                    pygame.K_q: 'square',
                    pygame.K_c: 'circle',
                    pygame.K_t: 'right triangle',
                    pygame.K_e: 'equilateral triangle',
                    pygame.K_h: 'rhombus',
                    pygame.K_f: 'fill',
                    pygame.K_x: 'text',
                    pygame.K_z: 'eraser',
                }
                if event.key in key_tool_map:
                    curr_tool = key_tool_map[event.key]

                # Brush size shortcuts (numrow 1/2/3)
                if event.key == pygame.K_1: curr_size_idx = 0
                if event.key == pygame.K_2: curr_size_idx = 1
                if event.key == pygame.K_3: curr_size_idx = 2

            # ── Mouse down ──────────────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_abs = event.pos
                click_rel = canvas_pos(click_abs)

                # Toolbar click
                if not on_canvas:
                    curr_tool, curr_size_idx, curr_color = toolbar.handle_click(
                        click_abs, curr_tool, curr_size_idx, curr_color)
                    continue

                # Canvas click
                if curr_tool == 'fill':
                    # Bake fill directly into canvas pixels
                    flood_fill(canvas, click_rel, curr_color)
                    # Save a snapshot token so Ctrl+Z could work in future
                    # (for now we just commit the pixel state)
                    continue

                if curr_tool == 'text':
                    text_active = True
                    text_pos    = click_rel
                    text_buffer = ''
                    continue

                drawing   = True
                start_pos = click_rel
                last_pos  = click_rel

                if curr_tool in ('brush', 'eraser', 'pencil'):
                    color  = BLACK if curr_tool == 'eraser' else curr_color
                    radius = brush_size() if curr_tool != 'eraser' else 20
                    shapes.append({'type': 'pencil_line', 'color': color,
                                   'pos': start_pos, 'end': click_rel,
                                   'radius': radius})

            # ── Mouse motion ────────────────────────────────────────────────
            elif event.type == pygame.MOUSEMOTION:
                if not drawing:
                    continue
                cur_rel = canvas_pos(event.pos)

                if curr_tool in ('brush', 'eraser', 'pencil'):
                    color  = BLACK if curr_tool == 'eraser' else curr_color
                    radius = brush_size() if curr_tool != 'eraser' else 20
                    shapes.append({'type': 'pencil_line', 'color': color,
                                   'pos': last_pos, 'end': cur_rel,
                                   'radius': radius})
                    last_pos = cur_rel

            # ── Mouse up ────────────────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if not drawing:
                    continue
                end_rel = canvas_pos(event.pos)

                if curr_tool not in ('brush', 'eraser', 'pencil'):
                    shapes.append({
                        'type':       curr_tool,
                        'color':      curr_color,
                        'start':      start_pos,
                        'end':        end_rel,
                        'brush_size': brush_size(),
                    })

                drawing = False
                redraw_canvas()   # bake everything into canvas surface

        # ── Render ────────────────────────────────────────────────────────────
        # 1) Draw toolbar panel
        toolbar.draw(screen, curr_tool, curr_size_idx, curr_color)

        # 2) Blit canvas
        #    We copy the committed canvas and draw live layers on top
        live = canvas.copy()

        # Live pencil strokes (while mouse still down)
        if drawing and curr_tool in ('brush', 'eraser', 'pencil'):
            # already appended to shapes each MOUSEMOTION; just redraw them
            for s in shapes:
                if s['type'] in ('brush_line', 'pencil_line'):
                    pygame.draw.line(live, s['color'],
                                     s['pos'], s['end'], s['radius'])

        # Live geometry preview
        if drawing and curr_tool not in ('brush', 'eraser', 'pencil', 'fill', 'text'):
            cur_rel = canvas_pos(pygame.mouse.get_pos())
            preview = {
                'type':       curr_tool,
                'color':      curr_color,
                'start':      start_pos,
                'end':        cur_rel,
                'brush_size': 1,
            }
            draw_geometry(live, preview, is_preview=True)

        # Text cursor & live text
        if text_active:
            disp = text_buffer + ('|' if (pygame.time.get_ticks() // 500) % 2 == 0 else '')
            t_surf = font_text.render(disp, True, curr_color)
            live.blit(t_surf, text_pos)

        screen.blit(live, (TOOLBAR_W, 0))

        # Status caption
        tool_disp = curr_tool.replace('equilateral triangle', 'eq-tri').replace('right triangle', 'rt-tri')
        sz_label  = ['Small', 'Medium', 'Large'][curr_size_idx]
        pygame.display.set_caption(
            f'Paint  |  Tool: {tool_disp}  |  Size: {sz_label} ({brush_size()}px)'
            + ('  |  TYPING — Enter to confirm' if text_active else ''))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()