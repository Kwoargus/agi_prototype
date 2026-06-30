import pygame
from WorldModel import WorldModel
from Bot import Bot
from GameObject import GameObject, Predator, Food
from db_connector import load_reflex_rules

if __name__ == "__main__":
    rules = load_reflex_rules()
    print(f"Загружено {len(rules)} правил рефлексов")

    world = WorldModel()
    bot = Bot(x=0, z=0, angle=0, move_delay=20, reflex_rules=rules)

    # Костры
    fire_positions = [
        # (-6, -6), (-4, -4), (-8, 0), (2, 4), (6, -2), (0, 8), (-8, -8)
        (-4, -4), (6, -2), (0, 8), (-8, -8)
    ]
    for (x, z) in fire_positions:
        fire = GameObject(x, z, obj_type="fire", temperature=800, size=1.0)
        world.add_object(fire)

    # Волк
    wolf = Predator(x=8, z=6, name="wolf", obj_type="predator", smell="predator_smell", sound="predator_roar")
    world.add_object(wolf)

    # Яблоки (еда)
    apple1 = Food(x=-6, z=4, name="apple", obj_type="food", smell="food_smell")
    apple2 = Food(x=8, z=-6, name="apple", obj_type="food", smell="food_smell")
    world.add_object(apple1)
    world.add_object(apple2)

    world.run(bot)
