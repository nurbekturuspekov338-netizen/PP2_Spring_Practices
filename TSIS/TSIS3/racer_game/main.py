import pygame
import sys
import random
import math

from racer import (
    Player, EnemyCar, OilSpill, Barrier, Pothole,
    Coin, PowerUp, MovingBarrier, NitroBoost, SpeedBump,
    SCREEN_W, SCREEN_H, ROAD_LEFT, ROAD_RIGHT, LANE_COUNT, LANES,
    CAR_COLORS, ENEMY_PALETTE,
)
from ui import (
    show_main_menu, show_username_entry,
    show_settings, show_game_over, show_leaderboard,
    _draw_bg, _label, _font,
)
from persistence import load_settings, add_leaderboard_entry

# ── Colours ───────────────────────────────────────────────────────────────────
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
DARK   = (20,  22,  30)
ACCENT = (255, 210, 0)
RED    = (220, 50,  50)
GREEN  = (50,  200, 80)
BLUE   = (50,  130, 230)
GRAY   = (150, 150, 150)
MUTED  = (120, 125, 145)
PANEL  = (35,  38,  52)
CYAN   = (0,   220, 220)
ORANGE = (255, 140, 0)

# ── Difficulty presets ────────────────────────────────────────────────────────
DIFFICULTY = {
    "easy":   {"base_speed": 3.5, "enemy_count": 3, "obstacle_interval": 4.0,
                "speed_inc": 0.15, "coin_bonus": 1},
    "medium": {"base_speed": 5.0, "enemy_count": 5, "obstacle_interval": 2.5,
                "speed_inc": 0.25, "coin_bonus": 2},
    "hard":   {"base_speed": 7.0, "enemy_count": 7, "obstacle_interval": 1.5,
                "speed_inc": 0.4,  "coin_bonus": 3},
}

FINISH_DISTANCE = 5000   # metres to finish line


# ── Road drawing ──────────────────────────────────────────────────────────────

class Road:
    def __init__(self):
        self.stripe_y = [i * 80 for i in range(10)]
        self.speed = 0

    def update(self, speed, dt):
        self.speed = speed
        for i in range(len(self.stripe_y)):
            self.stripe_y[i] += speed
            if self.stripe_y[i] > SCREEN_H + 80:
                self.stripe_y[i] -= (SCREEN_H + 160)

    def draw(self, surf):
        # Road surface
        road_rect = pygame.Rect(ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_H)
        pygame.draw.rect(surf, (45, 47, 55), road_rect)

        # Shoulders
        pygame.draw.rect(surf, (30, 32, 40), (ROAD_LEFT - 12, 0, 12, SCREEN_H))
        pygame.draw.rect(surf, (30, 32, 40), (ROAD_RIGHT, 0, 12, SCREEN_H))

        # Edge lines
        pygame.draw.line(surf, (200, 200, 60), (ROAD_LEFT, 0), (ROAD_LEFT, SCREEN_H), 3)
        pygame.draw.line(surf, (200, 200, 60), (ROAD_RIGHT, 0), (ROAD_RIGHT, SCREEN_H), 3)

        # Lane dashes
        for li in range(1, LANE_COUNT):
            lx = ROAD_LEFT + (ROAD_RIGHT - ROAD_LEFT) * li // LANE_COUNT
            for y in self.stripe_y:
                pygame.draw.rect(surf, (90, 95, 110), (lx - 2, y, 4, 40))


# ── HUD ───────────────────────────────────────────────────────────────────────

def draw_hud(surf, score, coins, distance, speed, active_pu, pu_timer, player):
    # Left panel
    _label(surf, f"Score: {score}", 65, 10, 18, ACCENT)
    _label(surf, f"Coins: {coins}", 65, 32, 16, (255, 220, 100))
    _label(surf, f"Speed: {speed:.0f}", 65, 54, 16, MUTED)

    # Distance bar (right side)
    prog = min(1.0, distance / FINISH_DISTANCE)
    bar_x, bar_y, bar_w, bar_h = SCREEN_W - 28, 60, 14, SCREEN_H - 120
    pygame.draw.rect(surf, PANEL, (bar_x, bar_y, bar_w, bar_h), border_radius=7)
    filled = int(bar_h * prog)
    pygame.draw.rect(surf, GREEN, (bar_x, bar_y + bar_h - filled, bar_w, filled), border_radius=7)
    pygame.draw.rect(surf, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=7)
    _label(surf, f"{int(distance)}m", SCREEN_W - 21, bar_y - 20, 13, MUTED)
    _label(surf, f"{FINISH_DISTANCE}m", SCREEN_W - 21, bar_y + bar_h + 2, 12, MUTED)

    # Active power-up
    if active_pu:
        pu_colors = {"nitro": ACCENT, "shield": CYAN, "repair": GREEN}
        pu_col = pu_colors.get(active_pu, WHITE)
        label = f"⚡{active_pu.upper()}" if active_pu == "nitro" else \
                f"🛡{active_pu.upper()}" if active_pu == "shield" else f"✚{active_pu.upper()}"
        box = pygame.Rect(SCREEN_W // 2 - 70, 8, 140, 32)
        pygame.draw.rect(surf, PANEL, box, border_radius=8)
        pygame.draw.rect(surf, pu_col, box, 2, border_radius=8)
        fnt = _font(16, bold=True)
        txt = fnt.render(f"{active_pu.upper()} {pu_timer:.1f}s", True, pu_col)
        surf.blit(txt, txt.get_rect(center=box.center))

    # Shield indicator on player
    if player.shield:
        pygame.draw.ellipse(surf, (*CYAN, 160),
                            player.rect.inflate(10, 10), 3)


def draw_finish_banner(surf):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 80))
    surf.blit(overlay, (0, 0))
    fnt = _font(64, bold=True)
    txt = fnt.render("FINISH!", True, ACCENT)
    surf.blit(txt, txt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))


# ── Main game session ─────────────────────────────────────────────────────────

def run_game(surf, clock, settings, username):
    diff = DIFFICULTY[settings.get("difficulty", "medium")]
    base_speed = diff["base_speed"]
    speed = base_speed
    coin_bonus = diff["coin_bonus"]
    sound_on = settings.get("sound", True)

    # Simple beep sounds (generated via pygame)
    def beep(freq=440, dur=80, vol=0.3):
        if not sound_on:
            return
        try:
            sample_rate = 44100
            n = int(sample_rate * dur / 1000)
            buf = bytearray(n * 2)
            for i in range(n):
                v = int(32767 * vol * math.sin(2 * math.pi * freq * i / sample_rate))
                buf[2*i]   = v & 0xFF
                buf[2*i+1] = (v >> 8) & 0xFF
            sound = pygame.mixer.Sound(buffer=bytes(buf))
            sound.play()
        except Exception:
            pass

    road = Road()
    player = Player(settings.get("car_color", "blue"))

    enemies   = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()   # oil, barriers, potholes, speed bumps, moving barriers
    coins_grp = pygame.sprite.Group()
    powerups  = pygame.sprite.Group()

    all_sprites = pygame.sprite.Group(player)

    def spawn_enemies(count):
        for _ in range(count):
            e = EnemyCar(speed, player.rect)
            enemies.add(e)
            all_sprites.add(e)

    spawn_enemies(diff["enemy_count"])

    # Initial coins
    for _ in range(5):
        c = Coin(speed)
        coins_grp.add(c)
        all_sprites.add(c)

    score    = 0
    coins    = 0
    distance = 0.0

    active_pu    = None    # "nitro" | "shield" | "repair"
    active_timer = 0.0

    obs_timer = 0.0
    obs_interval = diff["obstacle_interval"]

    pu_timer   = 0.0
    pu_interval = 6.0

    enemy_timer = 0.0
    enemy_interval = 3.0

    event_timer = 0.0
    event_interval = 12.0

    speed_timer = 0.0
    speed_interval = 5.0

    coin_timer = 0.0
    coin_interval = 2.0

    finished = False
    finish_timer = 0.0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)   # cap in case of lag

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # ── Timers & speed scaling ──────────────────────────────────────────
        speed_timer += dt
        if speed_timer >= speed_interval:
            speed_timer = 0
            speed += diff["speed_inc"]
            # Also make existing sprites faster is not practical;
            # new spawns will use updated speed

        enemy_timer += dt
        if enemy_timer >= enemy_interval:
            enemy_timer = 0
            e = EnemyCar(speed, player.rect)
            enemies.add(e)
            all_sprites.add(e)
            # Cull oldest enemies if too many
            enemy_list = list(enemies)
            max_enemies = diff["enemy_count"] + int(distance / 500)
            if len(enemy_list) > max_enemies + 2:
                enemy_list[0].kill()

        obs_timer += dt
        if obs_timer >= obs_interval:
            obs_timer = 0
            kind = random.choices(
                [OilSpill, Barrier, Pothole, SpeedBump],
                weights=[3, 2, 2, 1]
            )[0]
            obs = kind(speed)
            obstacles.add(obs)
            all_sprites.add(obs)

        pu_timer += dt
        if pu_timer >= pu_interval:
            pu_timer = 0
            kind = random.choice([PowerUp.KIND_NITRO, PowerUp.KIND_SHIELD, PowerUp.KIND_REPAIR])
            pu = PowerUp(kind, speed)
            powerups.add(pu)
            all_sprites.add(pu)

        event_timer += dt
        if event_timer >= event_interval:
            event_timer = 0
            # Randomly pick a dynamic event
            ev_kind = random.choice(["moving_barrier", "nitro_boost", "coin_burst"])
            if ev_kind == "moving_barrier":
                mb = MovingBarrier(speed)
                obstacles.add(mb)
                all_sprites.add(mb)
            elif ev_kind == "nitro_boost":
                nb = NitroBoost(speed)
                powerups.add(nb)
                all_sprites.add(nb)
            else:
                # Coin burst – spawn 5 coins in a line
                lane = random.choice(LANES)
                for j in range(5):
                    c = Coin(speed)
                    c.rect.centerx = lane
                    c.rect.top = -40 - j * 40
                    coins_grp.add(c)
                    all_sprites.add(c)

        coin_timer += dt
        if coin_timer >= coin_interval:
            coin_timer = 0
            c = Coin(speed)
            coins_grp.add(c)
            all_sprites.add(c)

        # ── Player update ───────────────────────────────────────────────────
        keys = pygame.key.get_pressed()
        player.move(keys, dt)
        player.update_timers(dt)

        if active_pu in ("nitro", "shield"):
            active_timer -= dt
            if active_timer <= 0:
                active_pu = None

        # ── Sprite updates ──────────────────────────────────────────────────
        for s in list(enemies) + list(obstacles) + list(coins_grp) + list(powerups):
            s.update(dt)

        distance += speed * dt * 2.5  # arbitrary scaling to metres

        # ── Collision: coins ────────────────────────────────────────────────
        hit_coins = pygame.sprite.spritecollide(player, coins_grp, True,
                                                pygame.sprite.collide_rect)
        for _ in hit_coins:
            coins += 1
            score += 10 * coin_bonus
            beep(880, 60, 0.2)

        # ── Collision: power-ups ────────────────────────────────────────────
        hit_pus = pygame.sprite.spritecollide(player, powerups, True,
                                              pygame.sprite.collide_rect)
        for pu in hit_pus:
            kind = pu.kind if hasattr(pu, "kind") else PowerUp.KIND_NITRO
            beep(1200, 100, 0.3)
            if kind == PowerUp.KIND_NITRO or isinstance(pu, NitroBoost):
                player.activate_nitro(4.0)
                active_pu = "nitro"
                active_timer = 4.0
            elif kind == PowerUp.KIND_SHIELD:
                player.activate_shield()
                active_pu = "shield"
                active_timer = 9999
            elif kind == PowerUp.KIND_REPAIR:
                # Repair: clear all obstacles from screen
                for obs in list(obstacles):
                    obs.kill()
                active_pu = "repair"
                active_timer = 0   # instant
                score += 50

        # ── Collision: obstacles (oil/speedbump = slow; barrier/pothole = crash) ──
        mask_player = pygame.mask.from_surface(player.image)

        def mask_collide(spr):
            offset = (spr.rect.left - player.rect.left,
                      spr.rect.top  - player.rect.top)
            m = pygame.mask.from_surface(spr.image)
            return mask_player.overlap(m, offset)

        for obs in list(obstacles):
            if not player.rect.colliderect(obs.rect):
                continue
            if isinstance(obs, (OilSpill, SpeedBump)):
                speed = max(base_speed * 0.6, speed - 0.5)
                obs.kill()
            elif isinstance(obs, (Barrier, Pothole, MovingBarrier)):
                if mask_collide(obs):
                    if player.shield:
                        player.use_shield()
                        active_pu = None
                        obs.kill()
                        beep(400, 150, 0.4)
                    else:
                        beep(200, 200, 0.6)
                        return "crash", score, distance, coins

        # ── Collision: enemy cars ───────────────────────────────────────────
        for en in list(enemies):
            if not player.rect.colliderect(en.rect):
                continue
            if mask_collide(en):
                if player.shield:
                    player.use_shield()
                    active_pu = None
                    en.kill()
                    beep(400, 150, 0.4)
                    score += 25
                else:
                    beep(200, 250, 0.6)
                    return "crash", score, distance, coins

        # ── Score from distance ─────────────────────────────────────────────
        score = int(coins * 10 * coin_bonus + distance * 0.5)

        # ── Finish line ─────────────────────────────────────────────────────
        if distance >= FINISH_DISTANCE:
            finished = True
            finish_timer += dt
            if finish_timer >= 2.5:
                return "finish", score, distance, coins

        # ── Draw ────────────────────────────────────────────────────────────
        surf.fill(DARK)
        road.update(speed, dt)
        road.draw(surf)

        # Grass sides
        pygame.draw.rect(surf, (30, 60, 30), (0, 0, ROAD_LEFT - 12, SCREEN_H))
        pygame.draw.rect(surf, (30, 60, 30), (ROAD_RIGHT + 12, 0, SCREEN_W - ROAD_RIGHT - 12, SCREEN_H))

        for s in all_sprites:
            surf.blit(s.image, s.rect)

        draw_hud(surf, score, coins, distance, speed * 20, active_pu, active_timer, player)

        if finished:
            draw_finish_banner(surf)

        # Username in top right
        fnt = _font(15)
        nm_txt = fnt.render(username, True, MUTED)
        surf.blit(nm_txt, (SCREEN_W - nm_txt.get_width() - 8, 10))

        pygame.display.flip()

    return "quit", score, distance, coins


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mixer.init()

    surf  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Speed Rush")
    clock = pygame.time.Clock()

    settings = load_settings()
    username = ""

    while True:
        choice = show_main_menu(surf, clock)

        if choice == "quit":
            pygame.quit(); sys.exit()

        elif choice == "leaderboard":
            show_leaderboard(surf, clock)

        elif choice == "settings":
            settings = show_settings(surf, clock)

        elif choice == "play":
            if not username:
                username = show_username_entry(surf, clock)

            while True:
                result, score, distance, coins = run_game(surf, clock, settings, username)

                if result in ("crash", "finish"):
                    add_leaderboard_entry(username, score, distance, coins)
                    action = show_game_over(surf, clock, score, distance, coins)
                    if action == "retry":
                        continue   # play again
                    else:
                        break      # back to menu
                else:
                    # ESC pressed
                    break


if __name__ == "__main__":
    main()
