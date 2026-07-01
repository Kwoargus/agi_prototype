import pygame
import math
from ReflexModule import ReflexModule
from InstinctModule import InstinctModule
from base_strategy import Perception, ActionSuggestion
import random

class Bot:
    def __init__(self, x, z, angle=0, move_delay=5, reflex_rules=None, instinct_patterns=None):
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

        # Модули рефлексов и инстинктов
        self.reflex_module = ReflexModule(reflex_rules if reflex_rules else [])
        self.instinct_module = InstinctModule(instinct_patterns if instinct_patterns else [])

        self.nearby_object = None
        self.nearby_params = {}

        # Состояние убегания
        self.runaway_target = None       # направление (dx, dz)
        self.awaiting_steps = 0          # сколько шагов осталось ждать после достижения границы

        self.runaway_dir_index = None

        self.visited_edges_set = set()  # для быстрой проверки


    def _add_edge(self, node1, node2):
        # сортируем, чтобы (a,b) и (b,a) считались одинаковыми
        if node1 > node2:
            node1, node2 = node2, node1
        self.visited_edges_set.add((node1, node2))

    # ---------- Взаимодействие с объектами ----------
    def setInform(self, obj):
        self.nearby_object = obj
        self.nearby_params = obj.get(['type', 'temperature', 'smell', 'sound', 'name'])
        print(f"Bot обнаружил объект: {self.nearby_params}")

    def get_object_params(self, params):
        if self.nearby_object:
            return self.nearby_object.get(params)
        return {}

    # ---------- Выполнение действий от рефлексов ----------
    def execute_action(self, action, world):
        if action == 'move_on':
            print("Рефлекс: move_on! Разворот и уход на 2 клетки.")
            self.dir_index = (self.dir_index + 2) % 4
            for _ in range(2):
                if not self._move_one_step(world):
                    break
        elif action == 'grab':
            print("Рефлекс: grab! Захват еды.")
            self._grab_object(world)
        elif action == 'avoid':
            print("Рефлекс: avoid! Отворачиваем.")
            self._turn_right()
        else:
            print(f"Неизвестное действие: {action}")

    def _grab_object(self, world):
        if self.nearby_object is None:
            return False
        target_x = self.nearby_object.x
        target_z = self.nearby_object.z
        dx = target_x - self.x
        dz = target_z - self.z
        if abs(dx) > self.step_size or abs(dz) > self.step_size:
            print("Объект не в соседней клетке")
            return False
        world.remove_object(self.nearby_object)
        self.visited_edges.append(((self.x, self.z), (target_x, target_z)))
        self._add_edge((self.x, self.z), (target_x, target_z))
        self.x, self.z = target_x, target_z
        self.visited_nodes.append((self.x, self.z))
        print(
            f"Bot схватил {self.nearby_object.name if hasattr(self.nearby_object, 'name') else 'еду'} и переместился в ({self.x}, {self.z})")
        self.nearby_object = None
        self.nearby_params = {}
        return True


    def _move_one_step(self, world):
        dx, dz = self.directions[self.dir_index]
        next_x = self.x + dx * self.step_size
        next_z = self.z + dz * self.step_size
        if world.is_within_world(next_x, next_z) and world.get_object_at(next_x, next_z) is None:
            self.visited_edges.append(((self.x, self.z), (next_x, next_z)))
            self._add_edge((self.x, self.z), (next_x, next_z))
            self.x, self.z = next_x, next_z
            self.visited_nodes.append((self.x, self.z))
            return True
        return False


    def _turn_right(self):
        self.dir_index = (self.dir_index + 1) % 4


    # ---------- Уведомление о глобальном событии (взрыв) ----------
    def notify(self, event_type, data):
        if event_type == 'explosion':
            # Формируем восприятие из сигналов
            perception = Perception({
                'sound': data.get('sound'),
                'vision': data.get('vision'),
                'position': data.get('position')
            })
            print(f"Perception for instinct: {perception}")
            suggestion = self.instinct_module.get_best_action(perception)
            print(f"Instinct suggestion: {suggestion}")
            if suggestion:
                self.execute_instinct(suggestion.action_id, data.get('position'))

    def execute_instinct(self, action_id, target_pos):
        if action_id == 'run_away':
            dx = self.x - target_pos[0]
            dz = self.z - target_pos[1]
            # Выбираем доминирующую ось (ближайшее направление из 4)
            if abs(dx) >= abs(dz):
                if dx >= 0:
                    dir_vec = (1, 0)  # вправо
                else:
                    dir_vec = (-1, 0)  # влево
            else:
                if dz >= 0:
                    dir_vec = (0, 1)  # вниз (по Z+)
                else:
                    dir_vec = (0, -1)  # вверх (по Z-)
            self.runaway_target = dir_vec
            self.awaiting_steps = 0
            self.moving = False
            print(f"Убегаем в направлении {dir_vec}")



    def _move_in_direction(self, dir_index, world):
        dx, dz = self.directions[dir_index]
        next_x = self.x + dx * self.step_size
        next_z = self.z + dz * self.step_size
        if world.is_within_world(next_x, next_z) and world.get_object_at(next_x, next_z) is None:
            self.visited_edges.append(((self.x, self.z), (next_x, next_z)))
            self.x, self.z = next_x, next_z
            self.visited_nodes.append((self.x, self.z))
            return True
        return False


    def update(self, world):
        if self.runaway_target:
            self._update_runaway(world)
            return

        if not self.moving:
            return

        self.frame_counter += 1
        if self.frame_counter < self.move_delay:
            return
        self.frame_counter = 0

        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        candidates = []  # непройденные ребра
        fallback = []  # доступные, но уже пройденные

        for (dx, dz) in dirs:
            next_x = self.x + dx * self.step_size
            next_z = self.z + dz * self.step_size

            if not world.is_within_world(next_x, next_z):
                continue
            if world.get_object_at(next_x, next_z) is not None:
                continue

            node1 = (self.x, self.z)
            node2 = (next_x, next_z)
            if node1 > node2:
                node1, node2 = node2, node1

            if (node1, node2) not in self.visited_edges_set:
                candidates.append((dx, dz))
            else:
                fallback.append((dx, dz))

        if candidates:
            dx, dz = random.choice(candidates)  # случайный выбор для разнообразия
        elif fallback:
            dx, dz = random.choice(fallback)  # идём по пройденному ребру, чтобы выйти из тупика
        else:
            # Нет доступных направлений – останавливаемся
            self.moving = False
            print("Обход завершён: нет доступных направлений")
            return

        # Делаем шаг
        next_x = self.x + dx * self.step_size
        next_z = self.z + dz * self.step_size
        self.visited_edges.append(((self.x, self.z), (next_x, next_z)))
        self._add_edge((self.x, self.z), (next_x, next_z))
        self.x, self.z = next_x, next_z
        self.visited_nodes.append((self.x, self.z))

        # Проверяем объекты в соседних клетках (рефлексы)
        for (dx_check, dz_check) in dirs:
            check_x = self.x + dx_check * self.step_size
            check_z = self.z + dz_check * self.step_size
            obj = world.get_object_at(check_x, check_z)
            if obj:
                self.setInform(obj)
                print(f"Object found: {obj}, params: {self.nearby_params}")
                perception = Perception(self.nearby_params.copy())
                suggestion = self.reflex_module.get_best_action(perception)
                print(f"Reflex suggestion: {suggestion}")
                if suggestion:
                    self.execute_action(suggestion.action_id, world)
                break

        if len(self.visited_nodes) > self.max_steps:
            self.moving = False
            print("Достигнут лимит шагов")





    def _update_runaway(self, world):
        dx, dz = self.runaway_target
        next_x = self.x + dx * self.step_size
        next_z = self.z + dz * self.step_size

        if world.is_within_world(next_x, next_z) and world.get_object_at(next_x, next_z) is None:
            self.visited_edges.append(((self.x, self.z), (next_x, next_z)))
            self._add_edge((self.x, self.z), (next_x, next_z))
            self.x, self.z = next_x, next_z
            self.visited_nodes.append((self.x, self.z))
            self.awaiting_steps = 0
        else:
            if self.awaiting_steps == 0:
                self.awaiting_steps = 50
            else:
                self.awaiting_steps -= 1
                if self.awaiting_steps <= 0:
                    self.runaway_target = None
                    self.moving = True
                    self.frame_counter = 0
                    print("Возврат к спирали")

    # ---------- Отрисовка ----------
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

