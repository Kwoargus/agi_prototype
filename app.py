from WorldModel import WorldModel
from Bot import Bot

if __name__ == "__main__":
    # Создаём мир и бота
    world = WorldModel()
    bot = Bot(x=0, z=0, angle=0)   # бот стоит в центре, смотрит вдоль +Z

    # Запускаем мир с ботом
    world.run(bot)



