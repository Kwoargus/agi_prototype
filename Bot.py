import pygame
import math

class Bot:
    def __init__(self, x, z, angle=0, move_delay=5, reflex_rules=None):
        self.x = x
        self.z = z
        self.angle = angle
        self.body_w = 0.8
        self.body_d = 0.5
        self.body_h = 1.2
        self.head_r = 0.3

        self.step_size = 2.0
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.dir_index = 0
        self.segment_length = 1
        self.step_count = 0
        self.turns = 0
        self.moving = True
        self.max_steps = 500

        self.move_delay = move_delay
        self.frame_counter = 0

        self.visited_nodes = [(self.x, self.z)]
        self.visited_edges = []

        self.reflex_rules = reflex_rules if reflex_rules else []
        self.nearby_object = None
        self.nearby_params = {}

    def is_edge_visited(self, x1, z1, x2, z2):
        """Проверяет, было ли ребро между двумя точками уже пройдено."""
        for (a, b), (c, d) in self.visited_edges:
            if (a == x1 and b == z1 and c == x2 and d == z2) or (a == x2 and b == z2 and c == x1 and d == z1):
                return True
        return False

    def setInform(self, obj):
        self.nearby_object = obj
        self.nearby_params = obj.get(['type', 'temperature', 'smell', 'sound', 'name'])
        print(f"Bot обнаружил объект: {self.nearby_params}")

    def get_object_params(self, params):
        if self.nearby_object:
            return self.nearby_object.get(params)
        return {}

    def apply_reflexes(self, obj_params):
        if not self.reflex_rules or not obj_params:
            return None
        for rule in self.reflex_rules:
            sense_type = rule.get('sense_type')
            signal_type = rule.get('signal_type')
            threshold = rule.get('signal_threshold')
            action = rule.get('action')
            if signal_type in obj_params:
                value = obj_params[signal_type]
                # если сигнал - температура, то сравниваем
                if value > threshold:
                    if not sense_type or sense_type == obj_params.get('type', ''):
                        print(f"Рефлекс сработал: {action} (threshold={threshold}, value={value})")
                        return action
        return None

    def handle_predator(self, world, obj_params):
        smell = obj_params.get('smell')
        sound = obj_params.get('sound')
        action = None
        for rule in self.reflex_rules:
            signal_type = rule.get('signal_type')
            if signal_type == smell or signal_type == sound:
                action = rule.get('action')
                break
        if action == 'move_on':
            print("Рефлекс predator: move_on! Разворот и уход на 2 клетки.")
            self.dir_index = (self.dir_index + 2) % 4
            for _ in range(2):
                if not self._move_one_step(world):
                    break

    def handle_food(self, world, obj):
        """Обработка встречи с едой."""
        if self.nearby_object is None:
            return
        # Проверим правило: ищем по signal_type = 'smell' или 'type'
        action = None
        for rule in self.reflex_rules:
            signal_type = rule.get('signal_type')
            if signal_type == 'smell_food' and self.nearby_params.get('smell') == 'food_smell':
                action = rule.get('action')
                break
            elif signal_type == 'food_smell' and self.nearby_params.get('type') == 'food':
                action = rule.get('action')
                break
        if action == 'grab':
            print("Рефлекс food: grab! Захват еды.")
            self._grab_object(world)

    def _grab_object(self, world):
        if self.nearby_object is None:
            return False
        target_x = self.nearby_object.x
        target_z = self.nearby_object.z
        # Проверяем, что объект в соседней клетке
        dx = target_x - self.x
        dz = target_z - self.z
        if abs(dx) > self.step_size or abs(dz) > self.step_size:
            print("Объект не в соседней клетке")
            return False
        # Удаляем объект из мира
        world.remove_object(self.nearby_object)
        # Перемещаем бота в клетку объекта
        self.x, self.z = target_x, target_z
        self.visited_nodes.append((self.x, self.z))
        self.visited_edges.append(((self.x, self.z), (target_x, target_z)))  # сохраняем ребро
        print(f"Bot схватил {self.nearby_object.name if hasattr(self.nearby_object, 'name') else 'еду'} и переместился в ({self.x}, {self.z})")
        self.nearby_object = None
        self.nearby_params = {}
        return True

    def _choose_step(self, world):
        # Сначала проверяем текущее направление, если ребро не посещено и клетка свободна
        dx, dz = self.directions[self.dir_index]
        next_x = self.x + dx * self.step_size
        next_z = self.z + dz * self.step_size
        if (world.is_within_world(next_x, next_z) and
            world.get_object_at(next_x, next_z) is None and
            not self.is_edge_visited(self.x, self.z, next_x, next_z)):
            return dx, dz

        # Иначе пробуем другие направления в порядке: право, лево, назад
        for i in [1, 3, 2]:  # 1=право, 3=лево, 2=назад (относительно текущего)
            idx = (self.dir_index + i) % 4
            dx, dz = self.directions[idx]
            next_x = self.x + dx * self.step_size
            next_z = self.z + dz * self.step_size
            if (world.is_within_world(next_x, next_z) and
                world.get_object_at(next_x, next_z) is None and
                not self.is_edge_visited(self.x, self.z, next_x, next_z)):
                return dx, dz

        # Если ни одно непосещённое ребро не доступно, пробуем любое свободное направление (даже посещённое)
        for i in [0, 1, 3, 2]:
            idx = (self.dir_index + i) % 4
            dx, dz = self.directions[idx]
            next_x = self.x + dx * self.step_size
            next_z = self.z + dz * self.step_size
            if world.is_within_world(next_x, next_z) and world.get_object_at(next_x, next_z) is None:
                return dx, dz

        return None, None


    def _move_one_step(self, world):
        dx, dz = self.directions[self.dir_index]
        next_x = self.x + dx * self.step_size
        next_z = self.z + dz * self.step_size
        if world.is_within_world(next_x, next_z) and world.get_object_at(next_x, next_z) is None:
            self.visited_edges.append(((self.x, self.z), (next_x, next_z)))
            self.x, self.z = next_x, next_z
            self.visited_nodes.append((self.x, self.z))
            return True
        return False

    def update(self, world):
        if not self.moving:
            return

        self.frame_counter += 1
        if self.frame_counter < self.move_delay:
            return
        self.frame_counter = 0

        # Проверяем соседние клетки на объекты
        for (dx_check, dz_check) in self.directions:
            check_x = self.x + dx_check * self.step_size
            check_z = self.z + dz_check * self.step_size
            obj = world.get_object_at(check_x, check_z)
            if obj:
                self.setInform(obj)
                params = self.nearby_params
                if params.get('type') == 'predator':
                    self.handle_predator(world, params)
                    return
                elif params.get('type') == 'food':
                    self.handle_food(world, obj)
                    return
                else:
                    self.apply_reflexes(params)
                break
            # Выбор направления шага
            dx, dz = self._choose_step(world)
            if dx is None:
                # Если нет свободного направления, поворачиваем и выходим
                self._turn_right()
                return

            # Выполняем шаг
            next_x = self.x + dx * self.step_size
            next_z = self.z + dz * self.step_size
            self.visited_edges.append(((self.x, self.z), (next_x, next_z)))
            self.x, self.z = next_x, next_z
            self.visited_nodes.append((self.x, self.z))
            self.step_count += 1
            if self.step_count == self.segment_length:
                self._turn_right()

        # Обычный шаг
        if self._move_one_step(world):
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

