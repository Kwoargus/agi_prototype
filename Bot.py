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
        rad_px = int(self.head_r * scale)
        if rad_px > 1:
            pygame.draw.circle(screen, (255, 200, 150), head_screen, rad_px)


