import pygame
from datetime import datetime
import sys
import math

pygame.init()
WIDTH=800
HEIGHT=800
screen=pygame.display.set_mode((WIDTH, HEIGHT))
done=True
pygame.display.set_caption("🕒 Mickey's Clock")
clock=pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FACE_COLOR = (255, 223, 128)
font = pygame.font.SysFont("consolas", 72, bold=True)

try:
    r_h_image=pygame.image.load("right_h.jpg")
    l_h_image=pygame.image.load("left_h.png")
except:
    print("Error")

center_x, center_y = WIDTH // 2, HEIGHT // 2

def create_clock():
    pygame.draw.circle(screen, BLACK, (center_x, center_y), 370, 30)
    pygame.draw.circle(screen, FACE_COLOR, (center_x, center_y), 340)
    pygame.draw.circle(screen, BLACK, (center_x, center_y), 310, 15)
    
    for i in range(60):
        angle = i * 6
        rad = math.radians(angle)
        x1 = center_x + 300 * math.cos(rad)
        y1 = center_y + 300 * math.sin(rad)
        x2 = center_x + 320 * math.cos(rad)
        y2 = center_y + 320 * math.sin(rad)
        pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 4 if i % 5 == 0 else 2)
        
    pygame.draw.circle(screen, BLACK, (center_x, center_y), 25)
    pygame.draw.circle(screen, (220, 0, 0), (center_x, center_y), 18)
    pygame.draw.circle(screen, BLACK, (center_x, center_y), 8)
    
    
def rotate_and_Blit(image, angle, position):
    rotated=pygame.transform.rotate(image, angle)
    rect=rotated.get_rect(center=position)
    screen.blit(rotated, rect.topleft)
    
while done:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            done=False
            
    cur=datetime.now()
    seconds=cur.second
    minutes=cur.minute
    
    minutes_angle=-((minutes*6)+(seconds*0.1))
    second_angle=-(seconds*6)
    
    screen.fill((30, 30, 40))
    
    create_clock()
    
    rotate_and_Blit(r_h_image, minutes_angle, (center_x, center_y))
    rotate_and_Blit(l_h_image, second_angle, (center_x, center_y))
    
    time_str = f"{minutes:02d}:{seconds:02d}"
    text_surf = font.render(time_str, True, BLACK)
    text_rect = text_surf.get_rect(center=(center_x, center_y + 420))
    screen.blit(text_surf, text_rect)
    title = pygame.font.SysFont("comicsansms", 42, bold=True).render("MICKEY'S CLOCK", True, (220, 0, 0))
    screen.blit(title, (center_x - title.get_width()//2, 30))
    
    pygame.display.flip()
    clock.tick(1)
    
pygame.quit()
sys.exit()
        
            