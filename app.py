import pygame

from WorldModel import WorldModel
from Bot import Bot

if __name__ == "__main__":
    world = WorldModel()
    # bot = Bot(x=0, z=0, angle=0)
    bot = Bot(x=0, z=0, angle=0, move_delay=10)  # медленно

    # Запускаем мир с ботом (в run уже есть цикл и обновление бота)
    world.run(bot)

