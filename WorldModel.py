import pygame
import math
import sys

class WorldModel:
    def __init__(self, red_cells=None, world_size=20, cell_size=40):
        """
        Инициализация виртуального мира.
        :param red_cells: список кортежей (x, z) центров красных ячеек.
        :param world_size: размер мира в единицах (от -world_size/2 до +world_size/2).
        :param cell_size: базовый размер ячейки в пикселях (масштаб).
        """
        # Параметры мира
        self.world_size = world_size
        self.cell_size = cell_size

        # Красные ячейки
        self.red_cells = red_cells if red_cells is not None else []

        # Настройки Pygame
        self.width, self.height = 1200, 800
        self.fps = 60

        # Цвета
        self.color_bg = (30, 30, 30)
        self.color_grid = (200, 200, 200)
        self.color_marker = (255, 100, 100)

        # Параметры камеры
        self.cam_x, self.cam_z = 0.0, 0.0
        self.yaw = 45.0
        self.pitch = 30.0
        self.zoom = 1.0

        self.min_pitch = 10.0
        self.max_pitch = 85.0
        self.min_zoom = 0.2
        self.max_zoom = 3.0

        # Инициализация Pygame (будет выполнена в run)
        self.screen = None
        self.clock = None
        self.font = None

    def _world_to_screen(self, wx, wz):
        """Преобразование мировых координат в экранные с учётом камеры."""
        dx = wx - self.cam_x
        dz = wz - self.cam_z

        rad_yaw = math.radians(self.yaw)
        cos_y = math.cos(rad_yaw)
        sin_y = math.sin(rad_yaw)
        dx_rot = dx * cos_y + dz * sin_y
        dz_rot = -dx * sin_y + dz * cos_y

        rad_pitch = math.radians(self.pitch)
        sin_p = math.sin(rad_pitch)
        x_proj = dx_rot
        y_proj = -dz_rot * sin_p

        scale = self.cell_size * self.zoom
        screen_x = self.width // 2 + x_proj * scale
        screen_y = self.height // 2 + y_proj * scale
        return int(screen_x), int(screen_y)

    def _draw_red_cells(self):
        """Рисует красные ячейки."""
        half = 1  # половина размера ячейки (т.к. шаг сетки 2)
        for (cx, cz) in self.red_cells:
            corners = [
                (cx - half, cz - half),
                (cx + half, cz - half),
                (cx + half, cz + half),
                (cx - half, cz + half)
            ]
            screen_corners = [self._world_to_screen(x, z) for (x, z) in corners]
            pygame.draw.polygon(self.screen, (255, 0, 0), screen_corners)

    def _draw_grid(self):
        """Рисует координатную сетку и маркеры."""
        half = self.world_size // 2
        # Горизонтальные линии (по Z)
        for z in range(-half, half + 1, 2):
            x1, y1 = self._world_to_screen(-half, z)
            x2, y2 = self._world_to_screen(half, z)
            pygame.draw.line(self.screen, self.color_grid, (x1, y1), (x2, y2), 1)
        # Вертикальные линии (по X)
        for x in range(-half, half + 1, 2):
            x1, y1 = self._world_to_screen(x, -half)
            x2, y2 = self._world_to_screen(x, half)
            pygame.draw.line(self.screen, self.color_grid, (x1, y1), (x2, y2), 1)
        # Маркеры
        for x in range(-half, half + 1, 2):
            for z in range(-half, half + 1, 2):
                if (x, z) == (0, 0):
                    continue
                px, py = self._world_to_screen(x, z)
                pygame.draw.circle(self.screen, self.color_marker, (px, py), 4)
        # Центр
        cx, cy = self._world_to_screen(0, 0)
        pygame.draw.circle(self.screen, (255, 255, 0), (cx, cy), 6)

    def _draw_ui(self):
        """Отображает информацию об управлении и параметрах камеры."""
        lines = [
            f"AGI Virtual World (Pygame)",
            f"Cam: ({self.cam_x:.1f}, {self.cam_z:.1f})  Yaw: {self.yaw:.1f}°  Pitch: {self.pitch:.1f}°  Zoom: {self.zoom:.2f}",
            f"Red cells: {len(self.red_cells)}",
            "Arrows: move | A/D: rotate | W/S: tilt | Scroll: zoom | Space: reset | Esc: exit"
        ]
        y = 10
        for line in lines:
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (10, y))
            y += 25

    def run(self):
        """Запускает основной цикл отображения мира."""
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("AGI Virtual World (Pygame)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE:
                        self.cam_x, self.cam_z = 0.0, 0.0
                        self.yaw = 45.0
                        self.pitch = 30.0
                        self.zoom = 1.0
                if event.type == pygame.MOUSEWHEEL:
                    self.zoom += event.y * 0.1
                    self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

            keys = pygame.key.get_pressed()
            speed = 0.3 / self.zoom

            # Движение стрелками
            if keys[pygame.K_LEFT]:
                self.cam_x += math.sin(math.radians(self.yaw)) * speed
                self.cam_z += math.cos(math.radians(self.yaw)) * speed
            if keys[pygame.K_RIGHT]:
                self.cam_x -= math.sin(math.radians(self.yaw)) * speed
                self.cam_z -= math.cos(math.radians(self.yaw)) * speed
            if keys[pygame.K_UP]:
                self.cam_x -= math.cos(math.radians(self.yaw)) * speed
                self.cam_z += math.sin(math.radians(self.yaw)) * speed
            if keys[pygame.K_DOWN]:
                self.cam_x += math.cos(math.radians(self.yaw)) * speed
                self.cam_z -= math.sin(math.radians(self.yaw)) * speed

            # Поворот A/D
            rot_speed = 2.0
            if keys[pygame.K_a]:
                self.yaw -= rot_speed
            if keys[pygame.K_d]:
                self.yaw += rot_speed

            # Наклон W/S
            pitch_speed = 1.0
            if keys[pygame.K_w]:
                self.pitch += pitch_speed
            if keys[pygame.K_s]:
                self.pitch -= pitch_speed
            self.pitch = max(self.min_pitch, min(self.max_pitch, self.pitch))

            # Отрисовка
            self.screen.fill(self.color_bg)
            self._draw_red_cells()
            self._draw_grid()
            self._draw_ui()

            pygame.display.flip()
            self.clock.tick(self.fps)

        pygame.quit()
        sys.exit()



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
