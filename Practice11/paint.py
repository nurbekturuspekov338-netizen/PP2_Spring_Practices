import pygame
import math

# Константы
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)

def draw_geometry(surface, shape, is_preview=False):
    """Отрисовка геометрических фигур (прямоугольник, круг, треугольники, ромб)."""
    color = shape['color']
    start = shape['start']
    end = shape['end']
    width = 1 if is_preview else 2 # Тонкая линия для предпросмотра

    x1, y1 = start
    x2, y2 = end
    
    if shape['type'] == 'rect':
        rect_x, rect_y = min(x1, x2), min(y1, y2)
        pygame.draw.rect(surface, color, (rect_x, rect_y, abs(x2-x1), abs(y2-y1)), width)

    elif shape['type'] == 'square':
        side = max(abs(x2-x1), abs(y2-y1))
        rect_x = x1 if x2 > x1 else x1 - side
        rect_y = y1 if y2 > y1 else y1 - side
        pygame.draw.rect(surface, color, (rect_x, rect_y, side, side), width)

    elif shape['type'] == 'circle':
        rad = int(math.hypot(x2-x1, y2-y1))
        pygame.draw.circle(surface, color, start, rad, width)

    elif shape['type'] == 'right triangle':
        points = [start, (x1, y2), end]
        pygame.draw.polygon(surface, color, points, width)

    elif shape['type'] == 'equilateral triangle':
        w = abs(x2 - x1)
        h = int((math.sqrt(3) / 2) * w)
        direction = 1 if y2 > y1 else -1
        p1 = (x1, y1)
        p2 = (x1 - w // 2, y1 + h * direction)
        p3 = (x1 + w // 2, y1 + h * direction)
        pygame.draw.polygon(surface, color, [p1, p2, p3], width)

    elif shape['type'] == 'rhombus':
        dx, dy = (x2 - x1), (y2 - y1)
        points = [
            (x1 + dx // 2, y1),      # Верх
            (x2, y1 + dy // 2),      # Право
            (x1 + dx // 2, y2),      # Низ
            (x1, y1 + dy // 2)       # Лево
        ]
        pygame.draw.polygon(surface, color, points, width)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    radius = 15
    curr_color = BLUE
    curr_tool = 'brush' 
    
    shapes = [] # История всех нарисованных объектов
    drawing = False
    start_pos = (0, 0)

    while True:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            # Клавиши управления
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: curr_color = RED
                if event.key == pygame.K_2: curr_color = GREEN
                if event.key == pygame.K_3: curr_color = BLUE
                
                if event.key == pygame.K_b: curr_tool = 'brush'
                if event.key == pygame.K_r: curr_tool = 'rect'
                if event.key == pygame.K_c: curr_tool = 'circle'
                if event.key == pygame.K_e: curr_tool = 'eraser'
                if event.key == pygame.K_t: curr_tool = 'right triangle'
                if event.key == pygame.K_s: curr_tool = 'square'
                if event.key == pygame.K_h: curr_tool = 'rhombus'
                if event.key == pygame.K_w: curr_tool = 'equilateral triangle'
                if event.key == pygame.K_ESCAPE: return

            # Нажатие мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True 
                start_pos = event.pos
                if curr_tool in ['brush', 'eraser']:
                    color = BLACK if curr_tool == 'eraser' else curr_color
                    shapes.append({'type': 'brush_line', 'color': color, 'pos': event.pos, 'radius': radius})

            # Движение мыши
            if event.type == pygame.MOUSEMOTION:
                if drawing and curr_tool in ['brush', 'eraser']:
                    color = BLACK if curr_tool == 'eraser' else curr_color
                    shapes.append({'type': 'brush_line', 'color': color, 'pos': event.pos, 'radius': radius})

            # Отпускание мыши
            if event.type == pygame.MOUSEBUTTONUP:
                if drawing and curr_tool not in ['brush', 'eraser']:
                    # Сохраняем геометрию только после отпускания кнопки
                    shapes.append({
                        'type': curr_tool, 
                        'color': curr_color, 
                        'start': start_pos, 
                        'end': event.pos
                    })
                drawing = False

        # --- Рендеринг всех объектов из памяти ---
        for s in shapes:
            if s['type'] == 'brush_line':
                pygame.draw.circle(screen, s['color'], s['pos'], s['radius'])
            else:
                draw_geometry(screen, s)

        # --- Отрисовка "призрака" (предпросмотра) во время зажатой мыши ---
        if drawing and curr_tool not in ['brush', 'eraser']:
            preview = {'type': curr_tool, 'color': curr_color, 'start': start_pos, 'end': mouse_pos}
            draw_geometry(screen, preview, is_preview=True)

        pygame.display.set_caption(f"Tool: {curr_tool} | Color: {curr_color} | Radius: {radius}")
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()