import pygame
import random
import sys

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

pygame.init()

WIDTH = 600
HEIGHT = 600
CELL = 30

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game: Levels & Scores")


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
        # move of body
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        self.body[0].x += self.dx
        self.body[0].y += self.dy

        # 1. Checking confrantation with walls
        if (self.body[0].x >= WIDTH // CELL or self.body[0].x < 0 or
            self.body[0].y >= HEIGHT // CELL or self.body[0].y < 0):
            self.dead = True

        # Checking confrantation with oneself
        for segment in self.body[1:]:
            if self.body[0].x == segment.x and self.body[0].y == segment.y:
                self.dead = True

    def draw(self):
        for i, segment in enumerate(self.body):
            color = RED if i == 0 else YELLOW
            pygame.draw.rect(screen, color, (segment.x * CELL, segment.y * CELL, CELL, CELL))

class Food:
    def __init__(self, snake_body):
        self.pos = Point(0, 0)
        self.generate_random_pos(snake_body)

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.pos.x * CELL, self.pos.y * CELL, CELL, CELL))

    # 2. Smart generation of food
    def generate_random_pos(self, snake_body):
        while True:
            self.pos.x = random.randint(0, WIDTH // CELL - 1)
            self.pos.y = random.randint(0, HEIGHT // CELL - 1)
            
            # Проверяем, не попала ли еда на сегмент змеи
            on_snake = False
            for segment in snake_body:
                if segment.x == self.pos.x and segment.y == self.pos.y:
                    on_snake = True
                    break
            
            if not on_snake:
                break

# options of the game
snake = Snake()
food = Food(snake.body)
score = 0
level = 1
base_fps = 5  # initial speed
clock = pygame.time.Clock()

running = True
while running:
    # 4. Increasing speed with levels
    current_fps = base_fps + (level - 1) * 2 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Запрет разворота в обратную сторону
            if event.key == pygame.K_RIGHT and snake.dx != -1:
                snake.dx, snake.dy = 1, 0
            elif event.key == pygame.K_LEFT and snake.dx != 1:
                snake.dx, snake.dy = -1, 0
            elif event.key == pygame.K_DOWN and snake.dy != -1:
                snake.dx, snake.dy = 0, 1
            elif event.key == pygame.K_UP and snake.dy != 1:
                snake.dx, snake.dy = 0, -1

    screen.fill(BLACK)
    
    # Draw of the net
    for i in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRAY, (i, 0), (i, HEIGHT))
        pygame.draw.line(screen, GRAY, (0, i), (WIDTH, i))

    snake.move()

    # If snake die
    if snake.dead:
        screen.fill(RED)
        msg = font_gameover.render("GAME OVER", True, WHITE)
        screen.blit(msg, (WIDTH//2 - 180, HEIGHT//2 - 50))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    #Checking eating 
    if snake.body[0].x == food.pos.x and snake.body[0].y == food.pos.y:
        score += 1
        snake.body.append(Point(snake.body[-1].x, snake.body[-1].y))
        food.generate_random_pos(snake.body)
        
        # 3. ЛОГИКА УРОВНЕЙ (каждые 3 очка)
        if score % 3 == 0:
            level += 1

    snake.draw()
    food.draw()

    # 5. Score and counter
    score_text = font_info.render(f"Score: {score}", True, WHITE)
    level_text = font_info.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 35))

    pygame.display.flip()
    clock.tick(current_fps)

pygame.quit()