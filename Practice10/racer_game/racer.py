import pygame
import sys
from pygame.locals import *
import random
import time

# Initializing 
pygame.init()

# Setting up FPS 
FPS = 60
FramePerSec = pygame.time.Clock()

# Creating colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Other Variables for use in the program
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1000
SPEED = 5
SCORE = 0
COIN_SCORE = 0 # Variable to track collected coins

# Setting up Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

background = pygame.image.load("as.png")

# Create a white screen 
DISPLAYSURF = pygame.display.set_mode((800, 800))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("e1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-30, -30)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0) 

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if (self.rect.top > 600):
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("p1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-30, -30)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (160, 520)
       
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)       
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)

# Extra Task: Coin Class
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("images.png").convert_alpha()
        # Scale coin if necessary
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        # Randomly spawn at the top
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)

    def move(self):
        self.rect.move_ip(0, SPEED)
        # If coin goes off screen, reset position
        if (self.rect.top > 600):
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def reset(self):
        """Used when a coin is collected to reappear at the top"""
        self.rect.top = 0
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

# Setting up Sprites        
P1 = Player()
E1 = Enemy()
C1 = Coin() # Creating one coin instance

# Creating Sprites Groups
enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)

# Adding a new User event 
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Game Loop
while True:
      
    # Cycles through all events occurring  
    for event in pygame.event.get():
        if event.type == INC_SPEED:
              SPEED += 0.5     
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.blit(background, (0,0))
    
    # Render Scores
    scores = font_small.render(f"Score: {SCORE}", True, GREEN)
    DISPLAYSURF.blit(scores, (10,10))
    
    # Extra Task: Showing number of collected coins in top right
    coin_counter = font_small.render(f"Coins: {COIN_SCORE}", True, RED)
    # Positioning in top right (Width - text width - padding)
    DISPLAYSURF.blit(coin_counter, (SCREEN_WIDTH - 100, 10))

    # Moves and Re-draws all Sprites
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # Extra Task: Coin Collection logic
    if pygame.sprite.spritecollideany(P1, coins):
        COIN_SCORE += 1
        pygame.mixer.Sound("kolco.mp3").play()
        C1.reset() # Reset coin position once collected

    # To be run if collision occurs between Player and Enemy
    if pygame.sprite.spritecollideany(P1, enemies, pygame.sprite.collide_mask):
          pygame.mixer.Sound('crash.mp3').play()
          time.sleep(0.5)
                   
          DISPLAYSURF.fill(RED)
          DISPLAYSURF.blit(game_over, (30,250))
          
          pygame.display.update()
          for entity in all_sprites:
                entity.kill() 
          time.sleep(2)
          pygame.quit()
          sys.exit()        
        
    pygame.display.update()
    FramePerSec.tick(FPS)