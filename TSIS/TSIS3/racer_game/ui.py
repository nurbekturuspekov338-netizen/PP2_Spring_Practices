import pygame
import sys
from persistence import load_leaderboard, load_settings, save_settings

# ── Palette ───────────────────────────────────────────────────────────────────
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GRAY    = (180, 180, 180)
DARK    = (20,  22,  30)
ACCENT  = (255, 210, 0)
RED     = (220, 50,  50)
GREEN   = (50,  200, 80)
BLUE    = (50,  130, 230)
PANEL   = (35,  38,  52)
MUTED   = (120, 125, 145)

SCREEN_W = 800
SCREEN_H = 700

# ── Fonts (loaded lazily after pygame.init) ───────────────────────────────────
_fonts = {}

def _font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("Verdana", size, bold=bold)
    return _fonts[key]


# ── Reusable button ───────────────────────────────────────────────────────────

class Button:
    def __init__(self, rect, text, color=ACCENT, text_color=BLACK, font_size=22):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(255, c + 40) for c in color)
        self.text_color = text_color
        self.font_size = font_size
        self._hovered = False

    def draw(self, surf):
        col = self.hover_color if self._hovered else self.color
        pygame.draw.rect(surf, col, self.rect, border_radius=10)
        pygame.draw.rect(surf, WHITE, self.rect, 2, border_radius=10)
        fnt = _font(self.font_size, bold=True)
        txt = fnt.render(self.text, True, self.text_color)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def check(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


def _draw_bg(surf):
    surf.fill(DARK)
    # Subtle road stripes in background
    for y in range(0, SCREEN_H, 60):
        pygame.draw.line(surf, (30, 33, 44), (0, y), (SCREEN_W, y), 1)


def _title(surf, text, y, size=56, color=ACCENT):
    fnt = _font(size, bold=True)
    t = fnt.render(text, True, color)
    surf.blit(t, t.get_rect(centerx=SCREEN_W // 2, y=y))


def _label(surf, text, cx, y, size=20, color=WHITE):
    fnt = _font(size)
    t = fnt.render(text, True, color)
    surf.blit(t, t.get_rect(centerx=cx, y=y))


# ── Main Menu ─────────────────────────────────────────────────────────────────

def show_main_menu(surf, clock):
    """Returns: 'play' | 'leaderboard' | 'settings' | 'quit'"""
    btn_w, btn_h = 260, 52
    cx = SCREEN_W // 2
    buttons = {
        "play":        Button((cx - btn_w // 2, 270, btn_w, btn_h), "▶  PLAY",        GREEN, BLACK),
        "leaderboard": Button((cx - btn_w // 2, 340, btn_w, btn_h), "🏆  LEADERBOARD", BLUE,  WHITE),
        "settings":    Button((cx - btn_w // 2, 410, btn_w, btn_h), "⚙  SETTINGS",    PANEL, WHITE),
        "quit":        Button((cx - btn_w // 2, 480, btn_w, btn_h), "✕  QUIT",         RED,  WHITE),
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            for key, btn in buttons.items():
                if btn.check(event):
                    return key

        _draw_bg(surf)

        # Decorative car silhouette
        pygame.draw.rect(surf, (50, 54, 70), (350, 140, 100, 16), border_radius=4)  # road stripe

        _title(surf, "SPEED RUSH", 80)
        _label(surf, "Dodge traffic. Collect coins. Survive.", SCREEN_W // 2, 155, 18, MUTED)

        # Divider
        pygame.draw.line(surf, ACCENT, (cx - 130, 240), (cx + 130, 240), 2)

        for btn in buttons.values():
            btn.draw(surf)

        _label(surf, "Arrow keys / WASD to drive", SCREEN_W // 2, 548, 16, MUTED)

        pygame.display.flip()
        clock.tick(60)


# ── Username Entry ────────────────────────────────────────────────────────────

def show_username_entry(surf, clock):
    """Returns the entered username string (trimmed, max 18 chars)."""
    name = ""
    cursor_visible = True
    cursor_timer = 0

    while True:
        dt = clock.tick(60) / 1000.0
        cursor_timer += dt
        if cursor_timer >= 0.5:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()[:18]
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 18 and event.unicode.isprintable():
                    name += event.unicode

        _draw_bg(surf)
        _title(surf, "ENTER YOUR NAME", 160, 44)
        _label(surf, "Type your racing name, then press Enter", SCREEN_W // 2, 225, 17, MUTED)

        # Input box
        box = pygame.Rect(SCREEN_W // 2 - 180, 280, 360, 54)
        pygame.draw.rect(surf, PANEL, box, border_radius=10)
        pygame.draw.rect(surf, ACCENT, box, 2, border_radius=10)

        display_text = name + ("|" if cursor_visible else " ")
        fnt = _font(26, bold=True)
        txt = fnt.render(display_text, True, WHITE)
        surf.blit(txt, txt.get_rect(center=box.center))

        _label(surf, "Press Enter to start", SCREEN_W // 2, 356, 16, MUTED)
        pygame.display.flip()


# ── Settings Screen ───────────────────────────────────────────────────────────

def show_settings(surf, clock):
    """Shows settings screen, returns updated settings dict."""
    settings = load_settings()

    COLORS  = ["blue", "red", "green", "yellow"]
    DIFFS   = ["easy", "medium", "hard"]
    COLOR_DISPLAY = {"blue": BLUE, "red": RED, "green": GREEN, "yellow": ACCENT}

    back_btn = Button((SCREEN_W // 2 - 100, 590, 200, 48), "← BACK", PANEL, WHITE)

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if back_btn.check(event):
                save_settings(settings)
                return settings
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_settings(settings)
                return settings
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Sound toggle (row y=270)
                toggle_rect = pygame.Rect(SCREEN_W // 2 + 40, 265, 80, 36)
                if toggle_rect.collidepoint(mx, my):
                    settings["sound"] = not settings["sound"]

                # Car color buttons (row y=340)
                for i, c in enumerate(COLORS):
                    r = pygame.Rect(SCREEN_W // 2 - 130 + i * 70, 335, 58, 36)
                    if r.collidepoint(mx, my):
                        settings["car_color"] = c

                # Difficulty buttons (row y=420)
                for i, d in enumerate(DIFFS):
                    r = pygame.Rect(SCREEN_W // 2 - 150 + i * 110, 415, 96, 36)
                    if r.collidepoint(mx, my):
                        settings["difficulty"] = d

        _draw_bg(surf)
        _title(surf, "SETTINGS", 80, 44)

        # ── Sound toggle ──
        _label(surf, "Sound", SCREEN_W // 2 - 110, 273, 20)
        tgl = pygame.Rect(SCREEN_W // 2 + 40, 265, 80, 36)
        on_color = GREEN if settings["sound"] else (80, 80, 80)
        pygame.draw.rect(surf, on_color, tgl, border_radius=8)
        pygame.draw.rect(surf, WHITE, tgl, 2, border_radius=8)
        fnt = _font(17, bold=True)
        txt = fnt.render("ON" if settings["sound"] else "OFF", True, WHITE)
        surf.blit(txt, txt.get_rect(center=tgl.center))

        # ── Car colour ──
        _label(surf, "Car Colour", SCREEN_W // 2 - 110, 343, 20)
        for i, c in enumerate(COLORS):
            r = pygame.Rect(SCREEN_W // 2 - 130 + i * 70, 335, 58, 36)
            border = ACCENT if settings["car_color"] == c else WHITE
            pygame.draw.rect(surf, COLOR_DISPLAY[c], r, border_radius=8)
            pygame.draw.rect(surf, border, r, 3 if settings["car_color"] == c else 1, border_radius=8)
            lbl = _font(13, bold=True).render(c[:3].upper(), True, BLACK)
            surf.blit(lbl, lbl.get_rect(center=r.center))

        # ── Difficulty ──
        _label(surf, "Difficulty", SCREEN_W // 2 - 110, 423, 20)
        diff_colors = {"easy": GREEN, "medium": ACCENT, "hard": RED}
        for i, d in enumerate(DIFFS):
            r = pygame.Rect(SCREEN_W // 2 - 150 + i * 110, 415, 96, 36)
            active = settings["difficulty"] == d
            bg = diff_colors[d] if active else PANEL
            pygame.draw.rect(surf, bg, r, border_radius=8)
            pygame.draw.rect(surf, WHITE, r, 2 if active else 1, border_radius=8)
            lbl = _font(16, bold=True).render(d.upper(), True, WHITE if active else MUTED)
            surf.blit(lbl, lbl.get_rect(center=r.center))

        # Dividers
        for y_div in [300, 380, 460]:
            pygame.draw.line(surf, (50, 54, 70), (SCREEN_W // 2 - 200, y_div),
                             (SCREEN_W // 2 + 200, y_div))

        back_btn.draw(surf)
        pygame.display.flip()


# ── Game Over Screen ──────────────────────────────────────────────────────────

def show_game_over(surf, clock, score, distance, coins):
    """Returns: 'retry' | 'menu'"""
    retry_btn = Button((SCREEN_W // 2 - 220, 480, 190, 52), "↺  RETRY", GREEN, BLACK)
    menu_btn  = Button((SCREEN_W // 2 + 30,  480, 190, 52), "⌂  MENU",  BLUE,  WHITE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if retry_btn.check(event): return "retry"
            if menu_btn.check(event):  return "menu"

        _draw_bg(surf)

        # Red flash overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((200, 0, 0, 40))
        surf.blit(overlay, (0, 0))

        _title(surf, "GAME OVER", 110, 54, RED)

        # Stats panel
        panel = pygame.Rect(SCREEN_W // 2 - 200, 210, 400, 230)
        pygame.draw.rect(surf, PANEL, panel, border_radius=14)
        pygame.draw.rect(surf, RED, panel, 2, border_radius=14)

        rows = [
            ("Score",    str(score)),
            ("Distance", f"{int(distance)} m"),
            ("Coins",    str(coins)),
        ]
        for i, (label, val) in enumerate(rows):
            y = 240 + i * 58
            _label(surf, label, SCREEN_W // 2 - 60, y, 20, MUTED)
            fnt = _font(28, bold=True)
            txt = fnt.render(val, True, ACCENT)
            surf.blit(txt, txt.get_rect(centerx=SCREEN_W // 2 + 80, y=y - 4))

        retry_btn.draw(surf)
        menu_btn.draw(surf)

        pygame.display.flip()
        clock.tick(60)


# ── Leaderboard Screen ────────────────────────────────────────────────────────

def show_leaderboard(surf, clock):
    """Shows top 10 leaderboard."""
    back_btn = Button((SCREEN_W // 2 - 100, 610, 200, 48), "← BACK", PANEL, WHITE)
    entries  = load_leaderboard()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if back_btn.check(event): return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return

        _draw_bg(surf)
        _title(surf, "LEADERBOARD", 55, 40)

        # Header
        hdr_y = 120
        for label, cx in [("Rank", 80), ("Name", 240), ("Score", 450), ("Dist.", 590), ("Coins", 710)]:
            _label(surf, label, cx, hdr_y, 16, MUTED)
        pygame.draw.line(surf, ACCENT, (30, 145), (SCREEN_W - 30, 145), 1)

        row_medals = {0: (255, 215, 0), 1: (192, 192, 192), 2: (205, 127, 50)}
        for i, e in enumerate(entries[:10]):
            y = 158 + i * 44
            bg_alpha = max(0, 60 - i * 5)
            row_surf = pygame.Surface((SCREEN_W - 60, 38), pygame.SRCALPHA)
            row_surf.fill((255, 255, 255, bg_alpha))
            surf.blit(row_surf, (30, y))

            rank_color = row_medals.get(i, WHITE)
            fnt_b = _font(18, bold=True)
            fnt_n = _font(18)

            # Rank
            rk = fnt_b.render(f"#{i+1}", True, rank_color)
            surf.blit(rk, rk.get_rect(centerx=80, y=y + 8))
            # Name
            nm = fnt_b.render(e.get("name", "???")[:14], True, WHITE)
            surf.blit(nm, nm.get_rect(x=160, y=y + 8))
            # Score
            sc = fnt_b.render(str(e.get("score", 0)), True, ACCENT)
            surf.blit(sc, sc.get_rect(centerx=450, y=y + 8))
            # Distance
            ds = fnt_n.render(f"{e.get('distance', 0)} m", True, GRAY)
            surf.blit(ds, ds.get_rect(centerx=590, y=y + 8))
            # Coins
            cn = fnt_n.render(str(e.get("coins", 0)), True, ACCENT)
            surf.blit(cn, cn.get_rect(centerx=710, y=y + 8))

        if not entries:
            _label(surf, "No scores yet – start racing!", SCREEN_W // 2, 280, 20, MUTED)

        back_btn.draw(surf)
        pygame.display.flip()
        clock.tick(60)
