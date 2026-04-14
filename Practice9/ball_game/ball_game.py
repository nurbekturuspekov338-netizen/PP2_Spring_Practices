import pygame
import sys

pygame.init()

WIDTH=800
HEIGHT=800
screen=pygame.display.set_mode((WIDTH, HEIGHT))
Done=True
clock=pygame.time.Clock()

WHITE=(255,255,255)
RED=(255, 0, 0)
ball_radius = 25
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
move_step = 20

while Done:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            Done=False
        if event.type == pygame.KEYDOWN:
            new_x = ball_x
            new_y = ball_y

            if event.key == pygame.K_LEFT:
                new_x -= move_step
            elif event.key == pygame.K_RIGHT:
                new_x += move_step
            elif event.key == pygame.K_UP:
                new_y -= move_step
            elif event.key == pygame.K_DOWN:
                new_y += move_step

            if (ball_radius <= new_x <= WIDTH - ball_radius and
                ball_radius <= new_y <= HEIGHT - ball_radius):
                ball_x = new_x
                ball_y = new_y
                
    screen.fill(WHITE)
    pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
sys.exit()