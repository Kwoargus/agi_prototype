from WorldModel import WorldModel
from Bot import Bot
from GameObject import GameObject, Predator, Food
from db_connector import load_reflex_rules, load_instinct_patterns

if __name__ == "__main__":
    reflex_rules = load_reflex_rules()
    instinct_patterns = load_instinct_patterns()
    print(f"Загружено {len(reflex_rules)} правил рефлексов")
    print(f"Загружено {len(instinct_patterns)} паттернов инстинктов")

    world = WorldModel()
    bot = Bot(x=0, z=0, angle=0, move_delay=10,
              reflex_rules=reflex_rules,
              instinct_patterns=instinct_patterns)

    # Костры
    fire_positions = [(-4, -4), (6, -2), (0, 8), (-8, -8)]
    for (x, z) in fire_positions:
        fire = GameObject(x, z, obj_type="fire", temperature=800, size=1.0)
        world.add_object(fire)

    # Волк
    wolf = Predator(x=8, z=6, name="wolf", obj_type="predator", smell="predator_smell", sound="predator_roar")
    world.add_object(wolf)

    # Яблоки
    apple1 = Food(x=-6, z=4, name="apple", obj_type="food", smell="food_smell")
    apple2 = Food(x=8, z=-6, name="apple", obj_type="food", smell="food_smell")
    world.add_object(apple1)
    world.add_object(apple2)

    world.run(bot)

