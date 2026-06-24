class Environment:
    """Внешняя среда, с которой взаимодействует агент"""
    def step(self, action: ActionSuggestion) -> (Perception, float, bool):
        # Выполнить действие, вернуть новое восприятие, награду, признак окончания
        pass

class ActionExecutor:
    def execute(self, action: ActionSuggestion, env: Environment):
        # Преобразует действие в команду для среды
        env.step(action)