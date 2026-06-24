from __future__ import annotations
from base_strategy import ReactionModule
from base_strategy import Perception
from base_strategy import ActionSuggestion
from typing import List, Dict, Optional, Any

class Orchestrator:
    def __init__(self):
        self.modules: List[ReactionModule] = []
        self.context = {}  # общий контекст для всех модулей

    def register_module(self, module: ReactionModule):
        self.modules.append(module)

    def decide(self, perception: Perception) -> ActionSuggestion:
        all_suggestions = []
        # Последовательно запускаем модули (можно параллельно)
        for mod in self.modules:
            suggestions = mod.process(perception, self.context)
            all_suggestions.extend(suggestions)
        # Агрегация: выбираем действие с наивысшим приоритетом
        # или комбинируем (например, если несколько модулей предлагают одно и то же)
        best = max(all_suggestions, key=lambda s: s.priority, default=None)
        if best is None:
            # Действие по умолчанию (бездействие)
            return ActionSuggestion(action_id='IDLE', priority=0.0)
        return best

    def learn(self, reward: float, action_taken: ActionSuggestion):
        for mod in self.modules:
            mod.update(reward, action_taken)

