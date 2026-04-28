# main.py — Screen manager and game loop

import sys
import pygame
import settings as cfg_settings
import db
from game import GameState, POWERUP_SPEED_BOOST, POWERUP_SLOW_MOTION, POWERUP_SHIELD
from config import *

# ─── Init ──────────────────────────────────────────────────────────────────────

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake — TSIS 4")
clock = pygame.time.Clock()

# Try to connect to DB; game works offline if it fails
_db_ok = False
try:
    db.init_db()
    _db_ok = True
except Exception as e:
    print(f"[DB] Connection failed — leaderboard disabled. ({e})")

# Fonts
F_TITLE  = pygame.font.SysFont("Verdana", 52, bold=True)
F_LARGE  = pygame.font.SysFont("Verdana", 36, bold=True)
F_MED    = pygame.font.SysFont("Verdana", 22)
F_SMALL  = pygame.font.SysFont("Verdana", 16)
F_TINY   = pygame.font.SysFont("Verdana", 13)
F_INPUT  = pygame.font.SysFont("Consolas", 28)

# ─── Helpers ───────────────────────────────────────────────────────────────────

def draw_text(surf, text, font, color, cx, cy, anchor="center"):
    img = font.render(text, True, color)
    r = img.get_rect()
    if anchor == "center":
        r.center = (cx, cy)
    elif anchor == "topleft":
        r.topleft = (cx, cy)
    elif anchor == "midleft":
        r.midleft = (cx, cy)
    surf.blit(img, r)


def draw_button(surf, text, rect, hover=False):
    color = (70, 70, 70) if hover else (40, 40, 40)
    border = WHITE if hover else LIGHT_GRAY
    pygame.draw.rect(surf, color, rect, border_radius=6)
    pygame.draw.rect(surf, border, rect, 2, border_radius=6)
    draw_text(surf, text, F_MED, WHITE, rect.centerx, rect.centery)


def mouse_over(rect):
    return rect.collidepoint(pygame.mouse.get_pos())


# ─── Username input screen ─────────────────────────────────────────────────────

def screen_username() -> str:
    """Show a text-input screen; return the entered username (stripped)."""
    username = ""
    error = ""

    while True:
        screen.fill(DARK_GRAY)
        draw_text(screen, "SNAKE", F_TITLE, GREEN, WIDTH // 2, 100)
        draw_text(screen, "Enter your username:", F_MED, WHITE, WIDTH // 2, 200)

        # Input box
        box = pygame.Rect(WIDTH // 2 - 150, 235, 300, 44)
        pygame.draw.rect(screen, BLACK, box, border_radius=6)
        pygame.draw.rect(screen, GREEN, box, 2, border_radius=6)
        draw_text(screen, username + "|", F_INPUT, GREEN, box.centerx, box.centery)

        if error:
            draw_text(screen, error, F_SMALL, RED, WIDTH // 2, 295)

        btn = pygame.Rect(WIDTH // 2 - 80, 330, 160, 44)
        draw_button(screen, "PLAY", btn, mouse_over(btn))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    name = username.strip()
                    if name:
                        return name
                    error = "Username cannot be empty."
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 20 and event.unicode.isprintable():
                    username += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn.collidepoint(event.pos):
                    name = username.strip()
                    if name:
                        return name
                    error = "Username cannot be empty."

        clock.tick(30)


# ─── Main Menu ─────────────────────────────────────────────────────────────────

def screen_main_menu() -> str:
    """Return one of: 'play', 'leaderboard', 'settings', 'quit'."""
    buttons = {
        "play":        pygame.Rect(WIDTH // 2 - 100, 200, 200, 48),
        "leaderboard": pygame.Rect(WIDTH // 2 - 100, 265, 200, 48),
        "settings":    pygame.Rect(WIDTH // 2 - 100, 330, 200, 48),
        "quit":        pygame.Rect(WIDTH // 2 - 100, 395, 200, 48),
    }
    labels = {
        "play": "▶  PLAY",
        "leaderboard": "🏆  LEADERBOARD",
        "settings": "⚙  SETTINGS",
        "quit": "✕  QUIT",
    }

    while True:
        screen.fill(DARK_GRAY)
        draw_text(screen, "SNAKE", F_TITLE, GREEN, WIDTH // 2, 110)
        draw_text(screen, "TSIS 4 Edition", F_SMALL, LIGHT_GRAY, WIDTH // 2, 162)

        for key, rect in buttons.items():
            draw_button(screen, labels[key], rect, mouse_over(rect))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for key, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        return key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "play"
                if event.key == pygame.K_ESCAPE:
                    return "quit"

        clock.tick(30)


# ─── Leaderboard screen ────────────────────────────────────────────────────────

def screen_leaderboard():
    rows = []
    if _db_ok:
        try:
            rows = db.get_top10()
        except Exception as e:
            rows = []
            print(f"[DB] Leaderboard fetch failed: {e}")

    back_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 60, 160, 44)

    while True:
        screen.fill(DARK_GRAY)
        draw_text(screen, "LEADERBOARD", F_LARGE, GOLD, WIDTH // 2, 40)

        # Header
        cols = [40, 120, 300, 400, 490]
        headers = ["#", "Player", "Score", "Level", "Date"]
        for i, h in enumerate(headers):
            draw_text(screen, h, F_SMALL, LIGHT_GRAY, cols[i], 85, anchor="midleft")

        pygame.draw.line(screen, GRAY, (30, 98), (WIDTH - 30, 98))

        if not rows and not _db_ok:
            draw_text(screen, "Database not connected.", F_MED, RED, WIDTH // 2, 250)
        elif not rows:
            draw_text(screen, "No records yet.", F_MED, LIGHT_GRAY, WIDTH // 2, 250)
        else:
            for idx, row in enumerate(rows):
                rank, username, score, level, date = row
                y = 115 + idx * 22
                color = GOLD if idx == 0 else (WHITE if idx < 3 else LIGHT_GRAY)
                vals = [str(rank), str(username), str(score), str(level), str(date)]
                for i, val in enumerate(vals):
                    draw_text(screen, val, F_TINY, color, cols[i], y, anchor="midleft")

        draw_button(screen, "← BACK", back_btn, mouse_over(back_btn))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    return

        clock.tick(30)


# ─── Settings screen ───────────────────────────────────────────────────────────

COLOR_CHOICES = [
    ("Yellow",  (200, 200, 0)),
    ("Cyan",    (0,   220, 220)),
    ("Orange",  (255, 140, 0)),
    ("White",   (240, 240, 240)),
    ("Purple",  (160, 32,  240)),
]


def screen_settings(user_settings: dict) -> dict:
    save_btn = pygame.Rect(WIDTH // 2 - 90, HEIGHT - 70, 180, 44)
    color_idx = next(
        (i for i, (_, c) in enumerate(COLOR_CHOICES)
         if list(c) == user_settings.get("snake_color")),
        0
    )
    temp = dict(user_settings)

    while True:
        screen.fill(DARK_GRAY)
        draw_text(screen, "SETTINGS", F_LARGE, WHITE, WIDTH // 2, 50)

        y = 130
        # Grid toggle
        grid_rect = pygame.Rect(WIDTH // 2 - 100, y, 200, 40)
        gv = "ON" if temp["grid"] else "OFF"
        draw_button(screen, f"Grid: {gv}", grid_rect, mouse_over(grid_rect))
        y += 65

        # Sound toggle
        sound_rect = pygame.Rect(WIDTH // 2 - 100, y, 200, 40)
        sv = "ON" if temp["sound"] else "OFF"
        draw_button(screen, f"Sound: {sv}", sound_rect, mouse_over(sound_rect))
        y += 65

        # Snake color
        draw_text(screen, "Snake Color:", F_MED, WHITE, WIDTH // 2, y)
        y += 35
        cname, cval = COLOR_CHOICES[color_idx]
        prev_btn = pygame.Rect(WIDTH // 2 - 140, y, 40, 36)
        next_btn = pygame.Rect(WIDTH // 2 + 100, y, 40, 36)
        swatch   = pygame.Rect(WIDTH // 2 - 95, y, 190, 36)
        draw_button(screen, "<", prev_btn, mouse_over(prev_btn))
        draw_button(screen, ">", next_btn, mouse_over(next_btn))
        pygame.draw.rect(screen, cval, swatch, border_radius=4)
        pygame.draw.rect(screen, WHITE, swatch, 1, border_radius=4)
        draw_text(screen, cname, F_MED, BLACK if sum(cval) > 380 else WHITE, swatch.centerx, swatch.centery)

        draw_button(screen, "✓ SAVE & BACK", save_btn, mouse_over(save_btn))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if grid_rect.collidepoint(event.pos):
                    temp["grid"] = not temp["grid"]
                elif sound_rect.collidepoint(event.pos):
                    temp["sound"] = not temp["sound"]
                elif prev_btn.collidepoint(event.pos):
                    color_idx = (color_idx - 1) % len(COLOR_CHOICES)
                elif next_btn.collidepoint(event.pos):
                    color_idx = (color_idx + 1) % len(COLOR_CHOICES)
                elif save_btn.collidepoint(event.pos):
                    temp["snake_color"] = list(COLOR_CHOICES[color_idx][1])
                    cfg_settings.save(temp)
                    return temp
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return user_settings  # discard changes

        clock.tick(30)


# ─── Game Over screen ──────────────────────────────────────────────────────────

def screen_game_over(score: int, level: int, personal_best: int) -> str:
    """Return 'retry' or 'menu'."""
    retry_btn = pygame.Rect(WIDTH // 2 - 110, 370, 200, 48)
    menu_btn  = pygame.Rect(WIDTH // 2 - 110, 435, 200, 48)

    while True:
        screen.fill(DARK_GRAY)
        draw_text(screen, "GAME OVER", F_TITLE, RED, WIDTH // 2, 120)
        draw_text(screen, f"Score:  {score}",  F_MED, WHITE, WIDTH // 2, 220)
        draw_text(screen, f"Level:  {level}",  F_MED, WHITE, WIDTH // 2, 255)
        draw_text(screen, f"Best:   {personal_best}", F_MED, GOLD, WIDTH // 2, 290)

        if score >= personal_best and score > 0:
            draw_text(screen, "★ NEW PERSONAL BEST ★", F_SMALL, GOLD, WIDTH // 2, 330)

        draw_button(screen, "↺  RETRY",    retry_btn, mouse_over(retry_btn))
        draw_button(screen, "⌂  MAIN MENU", menu_btn,  mouse_over(menu_btn))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    return "retry"
                if menu_btn.collidepoint(event.pos):
                    return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"
                if event.key == pygame.K_ESCAPE:
                    return "menu"

        clock.tick(30)


# ─── HUD helpers ───────────────────────────────────────────────────────────────

EFFECT_COLORS = {
    POWERUP_SPEED_BOOST: ORANGE,
    POWERUP_SLOW_MOTION: BLUE,
    POWERUP_SHIELD:      CYAN,
}
EFFECT_LABELS = {
    POWERUP_SPEED_BOOST: "FAST",
    POWERUP_SLOW_MOTION: "SLOW",
    POWERUP_SHIELD:      "SHIELD",
}


def draw_hud(gs: GameState, personal_best: int):
    """Draw score, level, personal best and active effect on top of the game."""
    # Semi-transparent HUD bar
    bar = pygame.Surface((WIDTH, 52), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 160))
    screen.blit(bar, (0, 0))

    draw_text(screen, f"Score: {gs.score}", F_MED, WHITE, 10, 14, anchor="midleft")
    draw_text(screen, f"Level: {gs.level}", F_MED, WHITE, 150, 14, anchor="midleft")
    draw_text(screen, f"Best: {personal_best}", F_MED, GOLD, 280, 14, anchor="midleft")

    # Active power-up timer
    if gs.active_effect:
        rem = gs.active_effect.remaining_ms() // 1000 + 1
        kind = gs.active_effect.kind
        col = EFFECT_COLORS.get(kind, WHITE)
        lbl = EFFECT_LABELS.get(kind, "")
        draw_text(screen, f"{lbl} {rem}s", F_MED, col, WIDTH - 10, 14, anchor="midright")
    elif gs.snake.shield:
        draw_text(screen, "SHIELD", F_MED, CYAN, WIDTH - 10, 14, anchor="midright")

    # Second row: tiny legend
    draw_text(screen, "● Normal  ● Gold×3  ● Poison  ■ Power-up", F_TINY, GRAY,
              WIDTH // 2, 40, anchor="center")


# ─── Main game play loop ────────────────────────────────────────────────────────

def play_game(username: str, player_id: int | None, user_settings: dict, personal_best: int) -> int:
    """Run one game; return final score."""
    snake_color = tuple(user_settings.get("snake_color", [200, 200, 0]))
    gs = GameState(snake_color=snake_color)
    show_grid = user_settings.get("grid", True)

    while not gs.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    gs.snake.set_direction(1, 0)
                elif event.key == pygame.K_LEFT:
                    gs.snake.set_direction(-1, 0)
                elif event.key == pygame.K_DOWN:
                    gs.snake.set_direction(0, 1)
                elif event.key == pygame.K_UP:
                    gs.snake.set_direction(0, -1)
                elif event.key == pygame.K_ESCAPE:
                    return gs.score  # treat as game over

        gs.update()

        gs.draw(screen, show_grid)
        draw_hud(gs, personal_best)
        pygame.display.flip()
        clock.tick(gs.current_fps())

    return gs.score


# ─── Entry point ───────────────────────────────────────────────────────────────

def main():
    user_settings = cfg_settings.load()

    # Username + DB player
    username = screen_username()
    player_id = None
    personal_best = 0
    if _db_ok:
        try:
            player_id = db.get_or_create_player(username)
            personal_best = db.get_personal_best(player_id)
        except Exception as e:
            print(f"[DB] Player lookup failed: {e}")

    while True:
        choice = screen_main_menu()

        if choice == "quit":
            break

        elif choice == "leaderboard":
            screen_leaderboard()

        elif choice == "settings":
            user_settings = screen_settings(user_settings)

        elif choice == "play":
            game_outcome = "retry"
            while game_outcome == "retry":
                score = play_game(username, player_id, user_settings, personal_best)

                # Save to DB
                if _db_ok and player_id is not None:
                    try:
                        level_reached = (score // SCORE_PER_LEVEL) + 1
                        db.save_session(player_id, score, level_reached)
                        personal_best = db.get_personal_best(player_id)
                    except Exception as e:
                        print(f"[DB] Save failed: {e}")

                level_reached = (score // SCORE_PER_LEVEL) + 1
                game_outcome = screen_game_over(score, level_reached, personal_best)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
