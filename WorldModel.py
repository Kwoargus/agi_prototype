import pygame
import math

class WorldModel:
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.running = True

        self.COLOR_BG = (30, 30, 30)
        self.COLOR_GRID = (200, 200, 200)
        self.COLOR_MARKER = (255, 100, 100)
        self.WORLD_SIZE = 20
        self.CELL_SIZE = 40

        self.cam_x = 0.0
        self.cam_z = 0.0
        self.yaw = 45.0
        self.pitch = 30.0
        self.zoom = 1.0

        self.MIN_PITCH = 10.0
        self.MAX_PITCH = 85.0
        self.MIN_ZOOM = 0.2
        self.MAX_ZOOM = 3.0

        # Список объектов
        self.objects = []

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("AGI Virtual World (Pygame)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)
            print(f"Объект {obj} удалён")
        else:
            print(f"Объект {obj} не найден в списке")

    def get_object_at(self, x, z):
        for obj in self.objects:
            if hasattr(obj, 'size'):  # GameObject
                half = obj.size * 0.5
                if abs(x - obj.x) < half and abs(z - obj.z) < half:
                    return obj
            elif hasattr(obj, 'body_w') and hasattr(obj, 'body_d'):  # Predator
                half_w = obj.body_w / 2
                half_d = obj.body_d / 2
                if abs(x - obj.x) < half_w and abs(z - obj.z) < half_d:
                    return obj
            elif hasattr(obj, 'radius'):  # Food (яблоко)
                if abs(x - obj.x) < obj.radius and abs(z - obj.z) < obj.radius:
                    return obj
        return None

    def world_to_screen(self, wx, wz, wy=0):
        dx = wx - self.cam_x
        dz = wz - self.cam_z

        rad_yaw = math.radians(self.yaw)
        cos_y = math.cos(rad_yaw)
        sin_y = math.sin(rad_yaw)
        dx_rot = dx * cos_y + dz * sin_y
        dz_rot = -dx * sin_y + dz * cos_y

        rad_pitch = math.radians(self.pitch)
        sin_p = math.sin(rad_pitch)
        cos_p = math.cos(rad_pitch)

        x_proj = dx_rot
        y_proj = -dz_rot * sin_p - wy * cos_p

        scale = self.CELL_SIZE * self.zoom
        screen_x = self.width // 2 + x_proj * scale
        screen_y = self.height // 2 + y_proj * scale
        return int(screen_x), int(screen_y)

    def get_scale(self):
        return self.CELL_SIZE * self.zoom

    def is_within_world(self, x, z):
        half = self.WORLD_SIZE // 2
        return -half <= x <= half and -half <= z <= half

    # ---------- Методы для работы с объектами ----------
    def add_object(self, obj):
        self.objects.append(obj)

    # ---------- Отрисовка ----------
    def draw_grid(self):
        half = self.WORLD_SIZE // 2
        for z in range(-half, half + 1, 2):
            x1, y1 = self.world_to_screen(-half, z, 0)
            x2, y2 = self.world_to_screen(half, z, 0)
            pygame.draw.line(self.screen, self.COLOR_GRID, (x1, y1), (x2, y2), 1)
        for x in range(-half, half + 1, 2):
            x1, y1 = self.world_to_screen(x, -half, 0)
            x2, y2 = self.world_to_screen(x, half, 0)
            pygame.draw.line(self.screen, self.COLOR_GRID, (x1, y1), (x2, y2), 1)

        for x in range(-half, half + 1, 2):
            for z in range(-half, half + 1, 2):
                if (x, z) == (0, 0):
                    continue
                px, py = self.world_to_screen(x, z, 0)
                pygame.draw.circle(self.screen, self.COLOR_MARKER, (px, py), 4)
        cx, cy = self.world_to_screen(0, 0, 0)
        pygame.draw.circle(self.screen, (255, 255, 0), (cx, cy), 6)

    def draw_ui(self, bot=None):
        lines = [
            f"AGI Virtual World (Pygame)",
            f"Cam: ({self.cam_x:.1f}, {self.cam_z:.1f})  Yaw: {self.yaw:.1f}°  Pitch: {self.pitch:.1f}°  Zoom: {self.zoom:.2f}",
            f"Objects: {len(self.objects)}",
            "Arrows: move | A/D: rotate | W/S: tilt | Scroll: zoom | Space: reset | Esc: exit"
        ]
        if bot:
            lines.append(f"Bot pos: ({bot.x:.1f}, {bot.z:.1f})  Steps: {len(bot.visited_nodes)-1}  Seg: {bot.segment_length}")
            if bot.nearby_object:
                params = bot.get_object_params(['type', 'temperature'])
                lines.append(f"Nearby: {params.get('type', '')} temp={params.get('temperature', '')}")
        y = 10
        for line in lines:
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (10, y))
            y += 25

    def draw(self, bot=None):
        self.screen.fill(self.COLOR_BG)
        self.draw_grid()
        # Отрисовка объектов (поверх сетки)
        for obj in self.objects:
            obj.draw(self.screen, self.world_to_screen)
        if bot:
            bot.draw(self.screen, self.world_to_screen, self.get_scale())
        self.draw_ui(bot)
        pygame.display.flip()

    # ---------- Обработка событий и цикл ----------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_SPACE:
                    self.cam_x, self.cam_z = 0.0, 0.0
                    self.yaw = 45.0
                    self.pitch = 30.0
                    self.zoom = 1.0
            if event.type == pygame.MOUSEWHEEL:
                self.zoom += event.y * 0.1
                self.zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, self.zoom))

    def update_camera(self):
        keys = pygame.key.get_pressed()
        speed = 0.3 / self.zoom

        if keys[pygame.K_UP]:
            self.cam_x += math.sin(math.radians(self.yaw)) * speed
            self.cam_z += math.cos(math.radians(self.yaw)) * speed
        if keys[pygame.K_DOWN]:
            self.cam_x -= math.sin(math.radians(self.yaw)) * speed
            self.cam_z -= math.cos(math.radians(self.yaw)) * speed
        if keys[pygame.K_LEFT]:
            self.cam_x -= math.cos(math.radians(self.yaw)) * speed
            self.cam_z += math.sin(math.radians(self.yaw)) * speed
        if keys[pygame.K_RIGHT]:
            self.cam_x += math.cos(math.radians(self.yaw)) * speed
            self.cam_z -= math.sin(math.radians(self.yaw)) * speed

        if keys[pygame.K_a]:
            self.yaw -= 2.0
        if keys[pygame.K_d]:
            self.yaw += 2.0
        if keys[pygame.K_w]:
            self.pitch += 1.0
        if keys[pygame.K_s]:
            self.pitch -= 1.0
        self.pitch = max(self.MIN_PITCH, min(self.MAX_PITCH, self.pitch))

    def run(self, bot=None):
        while self.running:
            self.handle_events()
            self.update_camera()
            if bot:
                bot.update(self)
            self.draw(bot)
            self.clock.tick(60)
        pygame.quit()

