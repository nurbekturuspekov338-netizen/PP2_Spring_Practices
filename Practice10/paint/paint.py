import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    radius = 15
    curr_color = BLUE
    curr_tool = 'brush' 
    
    
    shapes = [] 
    
    drawing = False
    start_pos = (0, 0)

    while True:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
               
                if event.key == pygame.K_1: curr_color = RED
                if event.key == pygame.K_2: curr_color = GREEN
                if event.key == pygame.K_3: curr_color = BLUE
                
               
                if event.key == pygame.K_b: curr_tool = 'brush'
                if event.key == pygame.K_r: curr_tool = 'rect'
                if event.key == pygame.K_c: curr_tool = 'circle'
                if event.key == pygame.K_e: curr_tool = 'eraser'
                
                if event.key == pygame.K_ESCAPE: return

            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                start_pos = event.pos
                if curr_tool == 'brush' or curr_tool == 'eraser':
                    color = BLACK if curr_tool == 'eraser' else curr_color
                    shapes.append({'type': 'brush', 'color': color, 'pos': event.pos, 'radius': radius})

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    if curr_tool == 'brush' or curr_tool == 'eraser':
                        color = BLACK if curr_tool == 'eraser' else curr_color
                        shapes.append({'type': 'brush', 'color': color, 'pos': event.pos, 'radius': radius})

            if event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    if curr_tool == 'rect':
                        shapes.append({'type': 'rect', 'color': curr_color, 'start': start_pos, 'end': event.pos})
                    elif curr_tool == 'circle':
                        shapes.append({'type': 'circle', 'color': curr_color, 'start': start_pos, 'end': event.pos})
                drawing = False

        
        for shape in shapes:
            if shape['type'] == 'brush':
                pygame.draw.circle(screen, shape['color'], shape['pos'], shape['radius'])
            
            elif shape['type'] == 'rect':
                x = min(shape['start'][0], shape['end'][0])
                y = min(shape['start'][1], shape['end'][1])
                w = abs(shape['start'][0] - shape['end'][0])
                h = abs(shape['start'][1] - shape['end'][1])
                pygame.draw.rect(screen, shape['color'], (x, y, w, h), 2)
                
            elif shape['type'] == 'circle':
                x_c = shape['start'][0]
                y_c = shape['start'][1]
                rad = int(((x_c - shape['end'][0])**2 + (y_c - shape['end'][1])**2)**0.5)
                pygame.draw.circle(screen, shape['color'], (x_c, y_c), rad, 2)

        
        if drawing:
            if curr_tool == 'rect':
                x = min(start_pos[0], mouse_pos[0])
                y = min(start_pos[1], mouse_pos[1])
                w = abs(start_pos[0] - mouse_pos[0])
                h = abs(start_pos[1] - mouse_pos[1])
                pygame.draw.rect(screen, curr_color, (x, y, w, h), 1)
            elif curr_tool == 'circle':
                rad = int(((start_pos[0] - mouse_pos[0])**2 + (start_pos[1] - mouse_pos[1])**2)**0.5)
                pygame.draw.circle(screen, curr_color, start_pos, rad, 1)

        # Info panel
        info = f"Tool: {curr_tool} | Color: {curr_color} | Radius: {radius}"
        pygame.display.set_caption(info)
        
        pygame.display.flip()
        clock.tick(60)

main()