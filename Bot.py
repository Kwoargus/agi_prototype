import pygame
import math

class Bot:
    def __init__(self, x, z, angle=0, move_delay=5):
        self.x = x
        self.z = z
        self.angle = angle
        self.body_w = 0.8
        self.body_d = 0.5
        self.body_h = 1.2
        self.head_r = 0.3

        # ---- Параметры движения по спирали ----
        self.step_size = 2.0
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.dir_index = 0
        self.segment_length = 1
        self.step_count = 0
        self.turns = 0
        self.moving = True
        self.max_steps = 500

        # ---- Задержка между шагами ----
        self.move_delay = move_delay
        self.frame_counter = 0

        # ---- Пройденный путь ----
        self.visited_nodes = [(self.x, self.z)]
        self.visited_edges = []

        # ---- Инстинкт избегания огня (отключен) ----
        self.fire_avoidance_enabled = False

    def update(self, world):
        if not self.moving:
            return

        self.frame_counter += 1
        if self.frame_counter < self.move_delay:
            return
        self.frame_counter = 0

        dx, dz = self.directions[self.dir_index]
        next_x = self.x + dx * self.step_size
        next_z = self.z + dz * self.step_size

        can_step = (
            world.is_within_world(next_x, next_z) and
            not world.is_cell_red(next_x, next_z)
        )

        if can_step:
            self.visited_edges.append(((self.x, self.z), (next_x, next_z)))
            self.x, self.z = next_x, next_z
            self.visited_nodes.append((self.x, self.z))
            self.step_count += 1
            if self.step_count == self.segment_length:
                self._turn_right()
        else:
            self._turn_right()

        if len(self.visited_nodes) > self.max_steps:
            self.moving = False

    def _turn_right(self):
        self.dir_index = (self.dir_index + 1) % 4
        self.step_count = 0
        self.turns += 1
        if self.turns % 2 == 0:
            self.segment_length += 1

    def draw_path(self, screen, world_to_screen_func):
        if not self.visited_edges:
            return
        for (x1, z1), (x2, z2) in self.visited_edges:
            p1 = world_to_screen_func(x1, z1, 0.1)
            p2 = world_to_screen_func(x2, z2, 0.1)
            pygame.draw.line(screen, (0, 255, 0), p1, p2, 3)

    def draw(self, screen, world_to_screen_func, scale):
        self.draw_path(screen, world_to_screen_func)

        cx, cz = self.x, self.z
        ang_rad = math.radians(self.angle)

        def rotate_point(lx, lz):
            rx = lx * math.cos(ang_rad) - lz * math.sin(ang_rad)
            rz = lx * math.sin(ang_rad) + lz * math.cos(ang_rad)
            return cx + rx, cz + rz

        corners_local = [
            (-self.body_w/2, -self.body_d/2),
            (self.body_w/2, -self.body_d/2),
            (self.body_w/2, self.body_d/2),
            (-self.body_w/2, self.body_d/2)
        ]
        corners_world = [rotate_point(lx, lz) for (lx, lz) in corners_local]
        base_points = [world_to_screen_func(wx, wz, 0) for (wx, wz) in corners_world]
        top_points = [world_to_screen_func(wx, wz, self.body_h) for (wx, wz) in corners_world]

        pygame.draw.polygon(screen, (0, 150, 200), top_points)
        for i in range(4):
            j = (i+1) % 4
            pts = [base_points[i], base_points[j], top_points[j], top_points[i]]
            pygame.draw.polygon(screen, (0, 100, 150), pts)
        pygame.draw.polygon(screen, (0, 80, 120), base_points)

        head_offset_z = 0.2
        head_x, head_z = rotate_point(0, head_offset_z)
        head_y = self.body_h + self.head_r * 0.8
        head_screen = world_to_screen_func(head_x, head_z, head_y)
        rad_px = int(self.head_r * scale)
        if rad_px > 1:
            pygame.draw.circle(screen, (255, 200, 150), head_screen, rad_px)


