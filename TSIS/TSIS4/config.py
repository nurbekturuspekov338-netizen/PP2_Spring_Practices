# config.py — Game constants and configuration

WIDTH = 600
HEIGHT = 600
CELL = 30

COLS = WIDTH // CELL  # 20
ROWS = HEIGHT // CELL  # 20

# FPS
BASE_FPS = 7
FPS_PER_LEVEL = 2

# Food lifetimes (ms)
NORMAL_FOOD_LIFETIME = 7000
GOLD_FOOD_LIFETIME   = 3000
POISON_FOOD_LIFETIME = 5000

# Power-up field lifetime (ms)
POWERUP_FIELD_LIFETIME = 8000
# Power-up effect duration (ms)
POWERUP_EFFECT_DURATION = 5000

# Score thresholds
SCORE_PER_LEVEL = 5

# Obstacle settings
OBSTACLE_START_LEVEL = 3
OBSTACLES_PER_LEVEL  = 5   # extra blocks per level beyond level 3

# Colors (r, g, b)
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (40,  40,  40)
DARK_GRAY  = (20,  20,  20)
RED        = (220, 50,  50)
GREEN      = (80,  200, 80)
GOLD       = (255, 200, 0)
DARK_RED   = (120, 0,   0)
CYAN       = (0,   220, 220)
ORANGE     = (255, 140, 0)
PURPLE     = (160, 32,  240)
BLUE       = (50,  100, 220)
LIGHT_GRAY = (180, 180, 180)

# DB connection string — update with your credentials
DB_DSN = "host=localhost dbname=SNAKE user=postgres password=MyPass@2026"
