import pygame
import math

class Bot:
    def __init__(self, x, z, angle=0):
        self.x = x
        self.z = z
        self.angle = angle          # градусы, 0 – смотрит вдоль +Z
        self.body_w = 0.8
        self.body_d = 0.5
        self.body_h = 1.2
        self.head_r = 0.3

    def draw(self, screen, world_to_screen_func, scale):
        """
        Отрисовка бота.
        scale = CELL_SIZE * zoom (пикселей на мировую единицу)
        """
        cx, cz = self.x, self.z
        ang_rad = math.radians(self.angle)

        def rotate_point(lx, lz):
            rx = lx * math.cos(ang_rad) - lz * math.sin(ang_rad)
            rz = lx * math.sin(ang_rad) + lz * math.cos(ang_rad)
            return cx + rx, cz + rz

        # ---- Тело ----
        corners_local = [
            (-self.body_w/2, -self.body_d/2),
            (self.body_w/2, -self.body_d/2),
            (self.body_w/2, self.body_d/2),
            (-self.body_w/2, self.body_d/2)
        ]
        corners_world = [rotate_point(lx, lz) for (lx, lz) in corners_local]
        base_points = [world_to_screen_func(wx, wz, 0) for (wx, wz) in corners_world]
        top_points = [world_to_screen_func(wx, wz, self.body_h) for (wx, wz) in corners_world]

        # Верхняя грань
        pygame.draw.polygon(screen, (0, 150, 200), top_points)
        # Боковые грани
        for i in range(4):
            j = (i+1) % 4
            pts = [base_points[i], base_points[j], top_points[j], top_points[i]]
            pygame.draw.polygon(screen, (0, 100, 150), pts)
        # Нижняя грань (необязательно)
        pygame.draw.polygon(screen, (0, 80, 120), base_points)

        # ---- Голова ----
        head_offset_z = 0.2
        head_x, head_z = rotate_point(0, head_offset_z)
        head_y = self.body_h + self.head_r * 0.8
        head_screen = world_to_screen_func(head_x, head_z, head_y)

        # Радиус в пикселях — фиксированный через масштаб
        rad_px = int(self.head_r * scale)
        if rad_px > 1:
            pygame.draw.circle(screen, (255, 200, 150), head_screen, rad_px)



# import pygame
# import math
#
# class Bot:
#     def __init__(self, x, z, angle=0):
#         self.x = x
#         self.z = z
#         self.angle = angle          # градусы, 0 – смотрит вдоль +Z
#         self.body_w = 0.8           # ширина (X)
#         self.body_d = 0.5           # глубина (Z)
#         self.body_h = 1.2           # высота (Y)
#         self.head_r = 0.3           # радиус головы
#
#     def draw(self, screen, world_to_screen_func):
#         """Отрисовка бота (тело + голова) поверх сетки."""
#         cx, cz = self.x, self.z
#         ang_rad = math.radians(self.angle)
#
#         # Вспомогательная функция поворота локальных координат
#         def rotate_point(lx, lz):
#             rx = lx * math.cos(ang_rad) - lz * math.sin(ang_rad)
#             rz = lx * math.sin(ang_rad) + lz * math.cos(ang_rad)
#             return cx + rx, cz + rz
#
#         # ---- Тело (параллелепипед) ----
#         # Углы основания в локальных координатах
#         corners_local = [
#             (-self.body_w/2, -self.body_d/2),
#             (self.body_w/2, -self.body_d/2),
#             (self.body_w/2, self.body_d/2),
#             (-self.body_w/2, self.body_d/2)
#         ]
#         # Преобразуем в мировые с поворотом
#         corners_world = [rotate_point(lx, lz) for (lx, lz) in corners_local]
#         # Получаем экранные координаты для основания и верха
#         base_points = [world_to_screen_func(wx, wz, 0) for (wx, wz) in corners_world]
#         top_points = [world_to_screen_func(wx, wz, self.body_h) for (wx, wz) in corners_world]
#
#         # Заливка верхней грани (цвет тела – голубой)
#         pygame.draw.polygon(screen, (0, 150, 200), top_points)
#         # Боковые грани (более тёмный голубой)
#         for i in range(4):
#             j = (i+1) % 4
#             pts = [base_points[i], base_points[j], top_points[j], top_points[i]]
#             pygame.draw.polygon(screen, (0, 100, 150), pts)
#         # Нижняя грань (для полноты, но она обычно не видна)
#         pygame.draw.polygon(screen, (0, 80, 120), base_points)
#
#         # ---- Голова (сфера) ----
#         # Смещена немного вперёд (по направлению взгляда)
#         head_offset_z = 0.0
#         head_x, head_z = rotate_point(0, head_offset_z)
#         head_y = self.body_h + self.head_r * 0.8   # центр головы
#         head_screen = world_to_screen_func(head_x, head_z, head_y)
#
#         # Вычисляем радиус в пикселях (по точке на радиусе вдоль оси X)
#         p_rad = world_to_screen_func(head_x + self.head_r, head_z, head_y)
#         rad_px = abs(p_rad[0] - head_screen[0])
#         if rad_px > 1:
#             pygame.draw.circle(screen, (255, 200, 150), head_screen, int(rad_px))





# import pygame
# import math
#
# class Bot:
#     def __init__(self, x, z, angle=0):
#         self.x = x
#         self.z = z
#         self.angle = angle  # градусы, 0 – смотрит вдоль +Z
#         # Размеры частей
#         self.body_w = 0.8
#         self.body_d = 0.5
#         self.body_h = 1.2
#         self.head_r = 0.0#0.3
#         self.leg_w = 0.0#0.2
#         self.leg_d = 0.0#0.2
#         self.leg_h = 0.0#0.6
#         self.arm_w = 0.0#0.15
#         self.arm_d = 0.0#0.15
#         self.arm_len = 0.0#0.7
#
#     def draw(self, screen, world_to_screen_func):
#         """Отрисовка бота с использованием функции world_to_screen (wx, wz, wy)."""
#         cx, cz = self.x, self.z
#         ang_rad = math.radians(self.angle)
#
#         def rotate_point(lx, lz):
#             rx = lx * math.cos(ang_rad) - lz * math.sin(ang_rad)
#             rz = lx * math.sin(ang_rad) + lz * math.cos(ang_rad)
#             return cx + rx, cz + rz
#
#         # ---- Ноги ----
#         leg_offset = 0.3
#         for side in [-1, 1]:
#             lx = side * leg_offset
#             lz = 0
#             # Углы ноги (в локальных координатах)
#             corners_local = [
#                 (lx - self.leg_w/2, lz - self.leg_d/2),
#                 (lx + self.leg_w/2, lz - self.leg_d/2),
#                 (lx + self.leg_w/2, lz + self.leg_d/2),
#                 (lx - self.leg_w/2, lz + self.leg_d/2)
#             ]
#             # Преобразуем углы в мировые с поворотом
#             corners_world = [rotate_point(lx, lz) for (lx, lz) in corners_local]
#             # Нижние и верхние точки
#             base_points = [world_to_screen_func(wx, wz, 0) for (wx, wz) in corners_world]
#             top_points = [world_to_screen_func(wx, wz, self.leg_h) for (wx, wz) in corners_world]
#             # Рисуем верхнюю грань
#             pygame.draw.polygon(screen, (120, 120, 120), top_points)
#             # Боковые грани
#             for i in range(4):
#                 j = (i+1) % 4
#                 pts = [base_points[i], base_points[j], top_points[j], top_points[i]]
#                 pygame.draw.polygon(screen, (80, 80, 80), pts)
#
#         # ---- Тело ----
#         corners_local = [
#             (-self.body_w/2, -self.body_d/2),
#             (self.body_w/2, -self.body_d/2),
#             (self.body_w/2, self.body_d/2),
#             (-self.body_w/2, self.body_d/2)
#         ]
#         corners_world = [rotate_point(lx, lz) for (lx, lz) in corners_local]
#         base_points = [world_to_screen_func(wx, wz, 0) for (wx, wz) in corners_world]
#         top_points = [world_to_screen_func(wx, wz, self.body_h) for (wx, wz) in corners_world]
#         # Верх
#         pygame.draw.polygon(screen, (0, 150, 200), top_points)
#         # Бока
#         for i in range(4):
#             j = (i+1) % 4
#             pts = [base_points[i], base_points[j], top_points[j], top_points[i]]
#             pygame.draw.polygon(screen, (0, 100, 150), pts)
#
#         # ---- Голова ----
#         head_offset_z = 0.2
#         head_x, head_z = rotate_point(0, head_offset_z)
#         head_y = self.body_h + self.head_r * 0.8
#         head_screen = world_to_screen_func(head_x, head_z, head_y)
#         # Радиус в пикселях
#         p_rad = world_to_screen_func(head_x + self.head_r, head_z, head_y)
#         rad_px = abs(p_rad[0] - head_screen[0])
#         pygame.draw.circle(screen, (255, 200, 150), head_screen, int(rad_px))
#
#         # ---- Руки ----
#         arm_offset_x = self.body_w/2 + 0.1
#         shoulder_y = self.body_h * 0.7
#         for side in [-1, 1]:
#             shoulder_x, shoulder_z = rotate_point(side * arm_offset_x, 0)
#             # Конец руки (опущена вниз и в сторону)
#             arm_end_x, arm_end_z = rotate_point(side * (arm_offset_x + 0.2), 0.2 * side)
#             arm_end_y = shoulder_y - self.arm_len
#             # Точки плеча и кисти в экранных координатах
#             p_shoulder = world_to_screen_func(shoulder_x, shoulder_z, shoulder_y)
#             p_elbow = world_to_screen_func(arm_end_x, arm_end_z, arm_end_y)
#             # Ширина руки в пикселях
#             arm_width_px = 8
#             dx_line = p_elbow[0] - p_shoulder[0]
#             dy_line = p_elbow[1] - p_shoulder[1]
#             length = math.hypot(dx_line, dy_line)
#             if length > 0:
#                 nx = -dy_line / length * arm_width_px / 2
#                 ny = dx_line / length * arm_width_px / 2
#                 pts = [
#                     (p_shoulder[0] + nx, p_shoulder[1] + ny),
#                     (p_shoulder[0] - nx, p_shoulder[1] - ny),
#                     (p_elbow[0] - nx, p_elbow[1] - ny),
#                     (p_elbow[0] + nx, p_elbow[1] + ny)
#                 ]
#                 pygame.draw.polygon(screen, (200, 150, 100), pts)
#
