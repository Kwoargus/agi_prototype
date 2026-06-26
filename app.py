import pygame
import math
import sys
from bot import Bot

# ---------- Настройки ----------
WIDTH, HEIGHT = 1200, 800
FPS = 60

COLOR_BG = (30, 30, 30)
COLOR_GRID = (200, 200, 200)
COLOR_MARKER = (255, 100, 100)

WORLD_SIZE = 20
CELL_SIZE = 40

cam_x, cam_z = 0.0, 0.0
yaw = 45.0
pitch = 30.0
zoom = 1.0

MIN_PITCH = 10.0
MAX_PITCH = 85.0
MIN_ZOOM = 0.2
MAX_ZOOM = 3.0

# Красные ячейки (костры)
red_cells = [
    (-6, -6), (-4, -4), (-8, 0), (2, 4), (6, -2), (0, 8), (-8, -8)
]

# ---------- Pygame ----------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AGI Virtual World (Pygame)")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

# ---------- Функции преобразования и отрисовки ----------
def world_to_screen(wx, wz, wy=0):
    dx = wx - cam_x
    dz = wz - cam_z

    rad_yaw = math.radians(yaw)
    cos_y = math.cos(rad_yaw)
    sin_y = math.sin(rad_yaw)
    dx_rot = dx * cos_y + dz * sin_y
    dz_rot = -dx * sin_y + dz * cos_y

    rad_pitch = math.radians(pitch)
    sin_p = math.sin(rad_pitch)
    cos_p = math.cos(rad_pitch)

    x_proj = dx_rot
    y_proj = -dz_rot * sin_p - wy * cos_p

    scale = CELL_SIZE * zoom
    screen_x = WIDTH // 2 + x_proj * scale
    screen_y = HEIGHT // 2 + y_proj * scale
    return int(screen_x), int(screen_y)

def draw_red_cells(cells):
    half = 1
    for (cx, cz) in cells:
        corners = [
            (cx - half, cz - half),
            (cx + half, cz - half),
            (cx + half, cz + half),
            (cx - half, cz + half)
        ]
        screen_corners = [world_to_screen(x, z, 0) for (x, z) in corners]
        pygame.draw.polygon(screen, (255, 0, 0), screen_corners)

def draw_grid():
    half = WORLD_SIZE // 2
    for z in range(-half, half + 1, 2):
        x1, y1 = world_to_screen(-half, z, 0)
        x2, y2 = world_to_screen(half, z, 0)
        pygame.draw.line(screen, COLOR_GRID, (x1, y1), (x2, y2), 1)
    for x in range(-half, half + 1, 2):
        x1, y1 = world_to_screen(x, -half, 0)
        x2, y2 = world_to_screen(x, half, 0)
        pygame.draw.line(screen, COLOR_GRID, (x1, y1), (x2, y2), 1)

    for x in range(-half, half + 1, 2):
        for z in range(-half, half + 1, 2):
            if (x, z) == (0, 0):
                continue
            px, py = world_to_screen(x, z, 0)
            pygame.draw.circle(screen, COLOR_MARKER, (px, py), 4)
    cx, cy = world_to_screen(0, 0, 0)
    pygame.draw.circle(screen, (255, 255, 0), (cx, cy), 6)

def draw_ui():
    lines = [
        f"AGI Virtual World (Pygame)",
        f"Cam: ({cam_x:.1f}, {cam_z:.1f})  Yaw: {yaw:.1f}°  Pitch: {pitch:.1f}°  Zoom: {zoom:.2f}",
        f"Red cells: {len(red_cells)}",
        "Arrows: move camera | A/D: rotate | W/S: tilt | Scroll: zoom | Space: reset",
        "Bot control: I/K/J/L move | Q/E rotate | Esc: exit"
    ]
    y = 10
    for line in lines:
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (10, y))
        y += 25

# ---------- Создаём бота ----------
bot = Bot(x=0, z=0, angle=0)   # стоит в центре, смотрит вдоль +Z

# ---------- Основной цикл ----------
running = True
while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                cam_x, cam_z = 0.0, 0.0
                yaw = 45.0
                pitch = 30.0
                zoom = 1.0
            # Управление ботом: перемещение и поворот
            if event.key == pygame.K_q:    # поворот влево
                bot.angle -= 10
            if event.key == pygame.K_e:    # поворот вправо
                bot.angle += 10
            # Перемещение бота (пошагово, по 0.5)
            if event.key == pygame.K_i:    # вперёд (по направлению взгляда)
                bot.x += 0.5 * math.sin(math.radians(bot.angle))
                bot.z += 0.5 * math.cos(math.radians(bot.angle))
            if event.key == pygame.K_k:    # назад
                bot.x -= 0.5 * math.sin(math.radians(bot.angle))
                bot.z -= 0.5 * math.cos(math.radians(bot.angle))
            if event.key == pygame.K_j:    # влево (перпендикулярно)
                bot.x -= 0.5 * math.cos(math.radians(bot.angle))
                bot.z += 0.5 * math.sin(math.radians(bot.angle))
            if event.key == pygame.K_l:    # вправо
                bot.x += 0.5 * math.cos(math.radians(bot.angle))
                bot.z -= 0.5 * math.sin(math.radians(bot.angle))

    # Непрерывное управление камерой
    keys = pygame.key.get_pressed()
    speed = 0.3 / zoom

    if keys[pygame.K_UP]:
        cam_x += math.sin(math.radians(yaw)) * speed
        cam_z += math.cos(math.radians(yaw)) * speed
    if keys[pygame.K_DOWN]:
        cam_x -= math.sin(math.radians(yaw)) * speed
        cam_z -= math.cos(math.radians(yaw)) * speed
    if keys[pygame.K_LEFT]:
        cam_x -= math.cos(math.radians(yaw)) * speed
        cam_z += math.sin(math.radians(yaw)) * speed
    if keys[pygame.K_RIGHT]:
        cam_x += math.cos(math.radians(yaw)) * speed
        cam_z -= math.sin(math.radians(yaw)) * speed

    if keys[pygame.K_a]:
        yaw -= 2.0
    if keys[pygame.K_d]:
        yaw += 2.0
    if keys[pygame.K_w]:
        pitch += 1.0
    if keys[pygame.K_s]:
        pitch -= 1.0
    pitch = max(MIN_PITCH, min(MAX_PITCH, pitch))

    # Обработка колёсика мыши
    # (обрабатывается в событиях, но для непрерывного зума можно добавить)
    # Обрабатываем в событиях выше

    # ---------- Отрисовка ----------
    screen.fill(COLOR_BG)

    # 1. Красные ячейки
    draw_red_cells(red_cells)

    # 2. Сетка
    draw_grid()

    # 3. Бот поверх сетки
    scale = CELL_SIZE * zoom
    bot.draw(screen, world_to_screen, scale)

    # 4. UI
    draw_ui()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()



# import pygame
# import math
# import sys
# from bot import Bot
#
# # ---------- Настройки ----------
# WIDTH, HEIGHT = 1200, 800
# FPS = 60
#
# COLOR_BG = (30, 30, 30)
# COLOR_GRID = (200, 200, 200)
# COLOR_MARKER = (255, 100, 100)
#
# WORLD_SIZE = 20
# CELL_SIZE = 40
#
# # Начальные параметры камеры
# cam_x, cam_z = 0.0, 0.0
# yaw = 45.0
# pitch = 30.0
# zoom = 1.0
#
# MIN_PITCH = 10.0
# MAX_PITCH = 85.0
# MIN_ZOOM = 0.2
# MAX_ZOOM = 3.0
#
# # ---------- Красные ячейки ----------
# red_cells = [
#     (-6, -6),
#     (-4, -4),
#     (-8, 0),
#     (2, 4),
#     (6, -2),
#     (0, 8),
#     (-8, -8)
# ]
#
# # ---------- Pygame init ----------
# pygame.init()
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("AGI Virtual World (Pygame)")
# clock = pygame.time.Clock()
# font = pygame.font.Font(None, 24)
#
# # ---------- Вспомогательные функции ----------
# def world_to_screen(wx, wz, wy=0):
#     dx = wx - cam_x
#     dz = wz - cam_z
#
#     rad_yaw = math.radians(yaw)
#     cos_y = math.cos(rad_yaw)
#     sin_y = math.sin(rad_yaw)
#     dx_rot = dx * cos_y + dz * sin_y
#     dz_rot = -dx * sin_y + dz * cos_y
#
#     rad_pitch = math.radians(pitch)
#     sin_p = math.sin(rad_pitch)
#     cos_p = math.cos(rad_pitch)
#
#     x_proj = dx_rot
#     y_proj = -dz_rot * sin_p - wy * cos_p
#
#     scale = CELL_SIZE * zoom
#     screen_x = WIDTH // 2 + x_proj * scale
#     screen_y = HEIGHT // 2 + y_proj * scale
#     return int(screen_x), int(screen_y)
#
# def draw_red_cells(cells):
#     half = 1
#     for (cx, cz) in cells:
#         corners = [
#             (cx - half, cz - half),
#             (cx + half, cz - half),
#             (cx + half, cz + half),
#             (cx - half, cz + half)
#         ]
#         screen_corners = [world_to_screen(x, z, 0) for (x, z) in corners]
#         pygame.draw.polygon(screen, (255, 0, 0), screen_corners)
#
# def draw_grid():
#     half = WORLD_SIZE // 2
#     for z in range(-half, half + 1, 2):
#         x1, y1 = world_to_screen(-half, z, 0)
#         x2, y2 = world_to_screen(half, z, 0)
#         pygame.draw.line(screen, COLOR_GRID, (x1, y1), (x2, y2), 1)
#     for x in range(-half, half + 1, 2):
#         x1, y1 = world_to_screen(x, -half, 0)
#         x2, y2 = world_to_screen(x, half, 0)
#         pygame.draw.line(screen, COLOR_GRID, (x1, y1), (x2, y2), 1)
#
#     for x in range(-half, half + 1, 2):
#         for z in range(-half, half + 1, 2):
#             if (x, z) == (0, 0):
#                 continue
#             px, py = world_to_screen(x, z, 0)
#             pygame.draw.circle(screen, COLOR_MARKER, (px, py), 4)
#     cx, cy = world_to_screen(0, 0, 0)
#     pygame.draw.circle(screen, (255, 255, 0), (cx, cy), 6)
#
# def draw_ui():
#     lines = [
#         f"AGI Virtual World (Pygame)",
#         f"Cam: ({cam_x:.1f}, {cam_z:.1f})  Yaw: {yaw:.1f}°  Pitch: {pitch:.1f}°  Zoom: {zoom:.2f}",
#         f"Red cells: {len(red_cells)}",
#         "Arrows: move | A/D: rotate | W/S: tilt | Scroll: zoom | Space: reset | Esc: exit"
#     ]
#     y = 10
#     for line in lines:
#         text = font.render(line, True, (255, 255, 255))
#         screen.blit(text, (10, y))
#         y += 25
#
# # ---------- Создаём бота ----------
# bot = Bot(x=0, z=0, angle=0)  # стоит в координатах (2,2) смотрит вдоль +Z
#
# # ---------- Main loop ----------
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_ESCAPE:
#                 running = False
#             if event.key == pygame.K_SPACE:
#                 cam_x, cam_z = 0.0, 0.0
#                 yaw = 45.0
#                 pitch = 30.0
#                 zoom = 1.0
#             # Дополнительное управление ботом: клавиши WASD (без shift) для перемещения
#             # Можно добавить перемещение бота стрелками, но они заняты камерой.
#             # Предложим управление ботом с помощью цифр или других клавиш.
#             # Пока оставим статику.
#
#         if event.type == pygame.MOUSEWHEEL:
#             zoom += event.y * 0.1
#             zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))
#
#     keys = pygame.key.get_pressed()
#     speed = 0.3 / zoom
#
#     # Движение камеры стрелками
#     if keys[pygame.K_UP]:
#         cam_x += math.sin(math.radians(yaw)) * speed
#         cam_z += math.cos(math.radians(yaw)) * speed
#     if keys[pygame.K_DOWN]:
#         cam_x -= math.sin(math.radians(yaw)) * speed
#         cam_z -= math.cos(math.radians(yaw)) * speed
#     if keys[pygame.K_LEFT]:
#         cam_x -= math.cos(math.radians(yaw)) * speed
#         cam_z += math.sin(math.radians(yaw)) * speed
#     if keys[pygame.K_RIGHT]:
#         cam_x += math.cos(math.radians(yaw)) * speed
#         cam_z -= math.sin(math.radians(yaw)) * speed
#
#     # Поворот камеры A/D
#     rot_speed = 2.0
#     if keys[pygame.K_a]:
#         yaw -= rot_speed
#     if keys[pygame.K_d]:
#         yaw += rot_speed
#
#     # Наклон W/S
#     pitch_speed = 1.0
#     if keys[pygame.K_w]:
#         pitch += pitch_speed
#     if keys[pygame.K_s]:
#         pitch -= pitch_speed
#     pitch = max(MIN_PITCH, min(MAX_PITCH, pitch))
#
#     # Отрисовка
#     screen.fill(COLOR_BG)
#     draw_red_cells(red_cells)
#     bot.draw(screen, world_to_screen)   # рисуем бота поверх красных ячеек, но под сеткой? Можно менять порядок.
#     draw_grid()
#     draw_ui()
#
#     pygame.display.flip()
#     clock.tick(FPS)
#
# pygame.quit()
# sys.exit()



# from WorldModel import WorldModel
#
# if __name__ == "__main__":
#     # Задаём список красных ячеек (костры)
#     red_cells = [
#         (-6, -6),
#         (-4, -4),
#         (-8, 0),
#         (2, 4),
#         (6, -2),
#         (0, 8),
#         (-8, -8)
#     ]
#
#     # Создаём мир и запускаем
#     world = WorldModel(red_cells=red_cells, world_size=20, cell_size=40)
#     world.run()

# import pygame
# import math
# import sys
#
# # ---------- Настройки ----------
# WIDTH, HEIGHT = 1200, 800
# FPS = 60
#
# COLOR_BG = (30, 30, 30)
# COLOR_GRID = (200, 200, 200)
# COLOR_MARKER = (255, 100, 100)
#
# WORLD_SIZE = 20
# CELL_SIZE = 40
#
# # Начальные параметры камеры
# cam_x, cam_z = 0.0, 0.0
# yaw = 45.0
# pitch = 30.0
# zoom = 1.0
#
# MIN_PITCH = 10.0
# MAX_PITCH = 85.0
# MIN_ZOOM = 0.2
# MAX_ZOOM = 3.0
#
# # ---------- Красные ячейки ----------
# red_cells = [
#     (-6, -6),
#     (-4, -4),
#     (-8, 0),
#     (2, 4),
#     (6, -2),
#     (0, 8),
#     (-8, -8)
# ]
#
# # ---------- Pygame init ----------
# pygame.init()
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("AGI Virtual World (Pygame)")
# clock = pygame.time.Clock()
# font = pygame.font.Font(None, 24)
#
# # ---------- Вспомогательные функции ----------
# def world_to_screen(wx, wz):
#     dx = wx - cam_x
#     dz = wz - cam_z
#
#     rad_yaw = math.radians(yaw)
#     cos_y = math.cos(rad_yaw)
#     sin_y = math.sin(rad_yaw)
#     dx_rot = dx * cos_y + dz * sin_y
#     dz_rot = -dx * sin_y + dz * cos_y
#
#     rad_pitch = math.radians(pitch)
#     sin_p = math.sin(rad_pitch)
#     x_proj = dx_rot
#     y_proj = -dz_rot * sin_p
#
#     scale = CELL_SIZE * zoom
#     screen_x = WIDTH // 2 + x_proj * scale
#     screen_y = HEIGHT // 2 + y_proj * scale
#     return int(screen_x), int(screen_y)
#
# def draw_red_cells(cells):
#     half = 1
#     for (cx, cz) in cells:
#         corners = [
#             (cx - half, cz - half),
#             (cx + half, cz - half),
#             (cx + half, cz + half),
#             (cx - half, cz + half)
#         ]
#         screen_corners = [world_to_screen(x, z) for (x, z) in corners]
#         pygame.draw.polygon(screen, (255, 0, 0), screen_corners)
#
# def draw_grid():
#     half = WORLD_SIZE // 2
#     for z in range(-half, half + 1, 2):
#         x1, y1 = world_to_screen(-half, z)
#         x2, y2 = world_to_screen(half, z)
#         pygame.draw.line(screen, COLOR_GRID, (x1, y1), (x2, y2), 1)
#     for x in range(-half, half + 1, 2):
#         x1, y1 = world_to_screen(x, -half)
#         x2, y2 = world_to_screen(x, half)
#         pygame.draw.line(screen, COLOR_GRID, (x1, y1), (x2, y2), 1)
#
#     for x in range(-half, half + 1, 2):
#         for z in range(-half, half + 1, 2):
#             if (x, z) == (0, 0):
#                 continue
#             px, py = world_to_screen(x, z)
#             pygame.draw.circle(screen, COLOR_MARKER, (px, py), 4)
#     cx, cy = world_to_screen(0, 0)
#     pygame.draw.circle(screen, (255, 255, 0), (cx, cy), 6)
#
# def draw_ui():
#     lines = [
#         f"AGI Virtual World (Pygame)",
#         f"Cam: ({cam_x:.1f}, {cam_z:.1f})  Yaw: {yaw:.1f}°  Pitch: {pitch:.1f}°  Zoom: {zoom:.2f}",
#         f"Red cells: {len(red_cells)}",
#         "Arrows: move | A/D: rotate | W/S: tilt | Scroll: zoom | Space: reset | Esc: exit"
#     ]
#     y = 10
#     for line in lines:
#         text = font.render(line, True, (255, 255, 255))
#         screen.blit(text, (10, y))
#         y += 25
#
# # ---------- Main loop ----------
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_ESCAPE:
#                 running = False
#             if event.key == pygame.K_SPACE:
#                 cam_x, cam_z = 0.0, 0.0
#                 yaw = 45.0
#                 pitch = 30.0
#                 zoom = 1.0
#         if event.type == pygame.MOUSEWHEEL:
#             zoom += event.y * 0.1
#             zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))
#
#     keys = pygame.key.get_pressed()
#     speed = 0.2 / zoom
#
#     # Движение стрелками (с учётом поворота)
#     if keys[pygame.K_LEFT]:
#         cam_x += math.sin(math.radians(yaw)) * speed
#         cam_z += math.cos(math.radians(yaw)) * speed
#     if keys[pygame.K_RIGHT]:
#         cam_x -= math.sin(math.radians(yaw)) * speed
#         cam_z -= math.cos(math.radians(yaw)) * speed
#     if keys[pygame.K_UP]:
#         cam_x -= math.cos(math.radians(yaw)) * speed
#         cam_z += math.sin(math.radians(yaw)) * speed
#     if keys[pygame.K_DOWN]:
#         cam_x += math.cos(math.radians(yaw)) * speed
#         cam_z -= math.sin(math.radians(yaw)) * speed
#
#     # Поворот A/D
#     rot_speed = 2.0
#     if keys[pygame.K_a]:
#         yaw -= rot_speed
#     if keys[pygame.K_d]:
#         yaw += rot_speed
#
#     # Наклон W/S
#     pitch_speed = 1.0
#     if keys[pygame.K_w]:
#         pitch += pitch_speed
#     if keys[pygame.K_s]:
#         pitch -= pitch_speed
#     pitch = max(MIN_PITCH, min(MAX_PITCH, pitch))
#
#     # Отрисовка
#     screen.fill(COLOR_BG)
#     draw_red_cells(red_cells)
#     draw_grid()
#     draw_ui()
#
#     pygame.display.flip()
#     clock.tick(FPS)
#
# pygame.quit()
# sys.exit()





# import pygame
# import math
# import sys
#
# # ---------- Настройки ----------
# WIDTH, HEIGHT = 1200, 800
# FPS = 60
#
# # Цвета
# COLOR_BG = (30, 30, 30)          # тёмно-серый фон
# COLOR_GROUND = (100, 100, 100)   # не используется, но оставлено
# COLOR_GRID = (200, 200, 200)     # белая сетка
# COLOR_MARKER = (255, 100, 100)   # красные маркеры
#
# # Размеры ландшафта (в единицах)
# WORLD_SIZE = 20                  # от -10 до +10 по X и Z
# CELL_SIZE = 40                   # пикселей на единицу (базовый масштаб)
#
# # Начальные параметры камеры
# cam_x, cam_z = 0.0, 0.0          # позиция камеры в мировых координатах (точка, на которую смотрит)
# yaw = 45.0                       # угол поворота вокруг вертикали (градусы)
# pitch = 30.0                     # угол наклона (градусы от вертикали, 90° – вид сверху, 10° – почти горизонтально)
# zoom = 1.0
#
# # Ограничения
# MIN_PITCH = 10.0
# MAX_PITCH = 85.0
# MIN_ZOOM = 0.2
# MAX_ZOOM = 3.0
#
# # ---------- Инициализация Pygame ----------
# pygame.init()
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("AGI Virtual World (Pygame)")
# clock = pygame.time.Clock()
# font = pygame.font.Font(None, 24)
#
# # ---------- Вспомогательные функции ----------
# def world_to_screen(wx, wz):
#     """
#     Преобразует мировые координаты (wx, wz) в экранные с учётом:
#     - позиции камеры (cam_x, cam_z)
#     - поворота камеры (yaw)
#     - наклона (pitch) – угол от вертикали (90° – сверху, меньше – наклон)
#     - масштаба (zoom)
#     """
#     # 1. Смещение относительно точки, на которую смотрит камера
#     dx = wx - cam_x
#     dz = wz - cam_z
#
#     # 2. Поворот системы координат на yaw (чтобы камера смотрела вдоль оси Z)
#     rad_yaw = math.radians(yaw)
#     cos_y = math.cos(rad_yaw)
#     sin_y = math.sin(rad_yaw)
#     dx_rot = dx * cos_y + dz * sin_y
#     dz_rot = -dx * sin_y + dz * cos_y
#
#     # 3. Наклон (pitch) – ортографическая проекция с наклоном
#     # При pitch = 90° (sin=1, cos=0): x_proj = dx_rot, y_proj = -dz_rot (вид сверху)
#     # При pitch < 90°: y_proj = -dz_rot * sin(pitch), что сжимает вертикаль, создавая наклон
#     rad_pitch = math.radians(pitch)
#     sin_p = math.sin(rad_pitch)
#     # cos_p не используется, так как мы центрируем по центру экрана
#     x_proj = dx_rot
#     y_proj = -dz_rot * sin_p
#
#     # 4. Масштабирование и центрирование
#     scale = CELL_SIZE * zoom
#     screen_x = WIDTH // 2 + x_proj * scale
#     screen_y = HEIGHT // 2 + y_proj * scale
#     return int(screen_x), int(screen_y)
#
# def draw_grid():
#     """Рисует координатную сетку и маркеры."""
#     half = WORLD_SIZE // 2
#     # Горизонтальные линии (по Z)
#     for z in range(-half, half + 1, 2):
#         x1, y1 = world_to_screen(-half, z)
#         x2, y2 = world_to_screen(half, z)
#         pygame.draw.line(screen, COLOR_GRID, (x1, y1), (x2, y2), 1)
#
#     # Вертикальные линии (по X)
#     for x in range(-half, half + 1, 2):
#         x1, y1 = world_to_screen(x, -half)
#         x2, y2 = world_to_screen(x, half)
#         pygame.draw.line(screen, COLOR_GRID, (x1, y1), (x2, y2), 1)
#
#     # Маркеры в узлах (шаг 2)
#     for x in range(-half, half + 1, 2):
#         for z in range(-half, half + 1, 2):
#             if (x, z) == (0, 0):
#                 continue
#             px, py = world_to_screen(x, z)
#             pygame.draw.circle(screen, COLOR_MARKER, (px, py), 4)
#
#     # Центр (0,0) выделим жёлтым
#     cx, cy = world_to_screen(0, 0)
#     pygame.draw.circle(screen, (255, 255, 0), (cx, cy), 6)
#
# def draw_ui():
#     """Отображает информацию об управлении и параметрах камеры."""
#     lines = [
#         f"AGI Virtual World (Pygame)",
#         f"Cam: ({cam_x:.1f}, {cam_z:.1f})  Yaw: {yaw:.1f}°  Pitch: {pitch:.1f}°  Zoom: {zoom:.2f}",
#         "Arrows: move | A/D: rotate | W/S: tilt (pitch) | Scroll: zoom | Space: reset | Esc: exit"
#     ]
#     y = 10
#     for line in lines:
#         text = font.render(line, True, (255, 255, 255))
#         screen.blit(text, (10, y))
#         y += 25
#
# # ---------- Основной цикл ----------
# running = True
# while running:
#     # Обработка событий
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_ESCAPE:
#                 running = False
#             if event.key == pygame.K_SPACE:
#                 cam_x, cam_z = 0.0, 0.0
#                 yaw = 45.0
#                 pitch = 30.0
#                 zoom = 1.0
#         if event.type == pygame.MOUSEWHEEL:
#             zoom += event.y * 0.1
#             zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))
#
#     # Управление с клавиатуры
#     keys = pygame.key.get_pressed()
#     speed = 0.3 / zoom   # скорость движения, чтобы не улетать при зуме
#
#     # Движение вперёд/назад (стрелки вверх/вниз)
#     if keys[pygame.K_LEFT]:
#         cam_x += math.sin(math.radians(yaw)) * speed
#         cam_z += math.cos(math.radians(yaw)) * speed
#     if keys[pygame.K_RIGHT]:
#         cam_x -= math.sin(math.radians(yaw)) * speed
#         cam_z -= math.cos(math.radians(yaw)) * speed
#
#     # Движение влево/вправо (стрелки влево/вправо)
#     if keys[pygame.K_UP]:
#         cam_x -= math.cos(math.radians(yaw)) * speed
#         cam_z += math.sin(math.radians(yaw)) * speed
#     if keys[pygame.K_DOWN]:
#         cam_x += math.cos(math.radians(yaw)) * speed
#         cam_z -= math.sin(math.radians(yaw)) * speed
#
#     # Поворот вокруг вертикали (A/D)
#     rot_speed = 2.0  # градусов за кадр
#     if keys[pygame.K_a]:
#         yaw -= rot_speed
#     if keys[pygame.K_d]:
#         yaw += rot_speed
#
#     # Наклон (изменение pitch) – W/S
#     pitch_speed = 1.0
#     if keys[pygame.K_w]:
#         pitch += pitch_speed
#     if keys[pygame.K_s]:
#         pitch -= pitch_speed
#     pitch = max(MIN_PITCH, min(MAX_PITCH, pitch))
#
#     # Отрисовка
#     screen.fill(COLOR_BG)
#     draw_grid()
#     draw_ui()
#
#     pygame.display.flip()
#     clock.tick(FPS)
#
# pygame.quit()
# sys.exit()
#
