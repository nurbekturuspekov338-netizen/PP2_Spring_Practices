import pygame
import random
import sys

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)  # Color for high-weight food

pygame.init()

# Constants
WIDTH = 600
HEIGHT = 600
CELL = 30

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game: Weighted Food & Timers")

font_info = pygame.font.SysFont("Verdana", 20)
font_gameover = pygame.font.SysFont("Verdana", 60)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Snake:
    def __init__(self):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx = 1
        self.dy = 0
        self.dead = False

    def move(self):
        # Move body segments
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        self.body[0].x += self.dx
        self.body[0].y += self.dy

        # Check wall collision
        if (self.body[0].x >= WIDTH // CELL or self.body[0].x < 0 or
            self.body[0].y >= HEIGHT // CELL or self.body[0].y < 0):
            self.dead = True

        # Check self collision
        for segment in self.body[1:]:
            if self.body[0].x == segment.x and self.body[0].y == segment.y:
                self.dead = True

    def draw(self):
        for i, segment in enumerate(self.body):
            color = RED if i == 0 else (200, 200, 0)
            pygame.draw.rect(screen, color, (segment.x * CELL, segment.y * CELL, CELL, CELL))

class Food:
    def __init__(self, snake_body):
        self.pos = Point(0, 0)
        self.weight = 1
        self.color = GREEN
        self.timer = 0
        self.lifetime = 5000  # Food lasts 5 seconds (5000ms)
        self.generate_random_pos(snake_body)

    def generate_random_pos(self, snake_body):
        # Randomly assign weight: 20% chance for "Super Food"
        if random.randint(1, 5) == 5:
            self.weight = 3
            self.color = GOLD
            self.lifetime = 3000 # Gold food disappears faster (3s)
        else:
            self.weight = 1
            self.color = GREEN
            self.lifetime = 7000 # Normal food lasts longer (7s)
        
        self.timer = pygame.time.get_ticks() # Record creation time

        while True:
            self.pos.x = random.randint(0, WIDTH // CELL - 1)
            self.pos.y = random.randint(0, HEIGHT // CELL - 1)
            
            on_snake = any(s.x == self.pos.x and s.y == self.pos.y for s in snake_body)
            if not on_snake:
                break

    def update(self, snake_body):
        # Check if food has expired
        current_time = pygame.time.get_ticks()
        if current_time - self.timer > self.lifetime:
            self.generate_random_pos(snake_body)

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.pos.x * CELL, self.pos.y * CELL, CELL, CELL))

# Game setup
snake = Snake()
food = Food(snake.body)
score = 0
level = 1
base_fps = 7
clock = pygame.time.Clock()

running = True
while running:
    current_fps = base_fps + (level - 1) * 2 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and snake.dx != -1:
                snake.dx, snake.dy = 1, 0
            elif event.key == pygame.K_LEFT and snake.dx != 1:
                snake.dx, snake.dy = -1, 0
            elif event.key == pygame.K_DOWN and snake.dy != -1:
                snake.dx, snake.dy = 0, 1
            elif event.key == pygame.K_UP and snake.dy != 1:
                snake.dx, snake.dy = 0, -1

    # Logic update
    food.update(snake.body)
    snake.move()

    if snake.dead:
        screen.fill(RED)
        msg = font_gameover.render("GAME OVER", True, WHITE)
        screen.blit(msg, (WIDTH//2 - 180, HEIGHT//2 - 50))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    # Check collision with food
    if snake.body[0].x == food.pos.x and snake.body[0].y == food.pos.y:
        score += food.weight
        # Grow snake based on food weight
        for _ in range(food.weight):
            snake.body.append(Point(snake.body[-1].x, snake.body[-1].y))
        
        food.generate_random_pos(snake.body)
        
        # Level up every 5 points
        level = (score // 5) + 1

    # Rendering
    screen.fill(BLACK)
    
    # Draw Grid
    for i in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRAY, (i, 0), (i, HEIGHT))
        pygame.draw.line(screen, GRAY, (0, i), (WIDTH, i))

    snake.draw()
    food.draw()

    # UI
    score_text = font_info.render(f"Score: {score}", True, WHITE)
    level_text = font_info.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 35))

    pygame.display.flip()
    clock.tick(current_fps)

pygame.quit()