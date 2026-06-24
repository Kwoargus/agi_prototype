from __future__ import annotations
from base_strategy import ReactionModule
from base_strategy import Perception
from base_strategy import ActionSuggestion
from typing import List, Dict, Optional, Any

class ReflexModule(ReactionModule):
    def process(self, perception: Perception, context: Dict) -> List[ActionSuggestion]:
        suggestions = []
        # Ищем в памяти таблицу рефлексов: channel, threshold, action_id
        for channel, value in perception.items():
            if channel in ['touch', 'temperature']:  # пример
                threshold = self.memory.get_reflex_threshold(channel)
                if value > threshold:
                    action = self.memory.get_reflex_action(channel)
                    suggestions.append(ActionSuggestion(action_id=action, priority=1.0))
        return suggestions

    def update(self, reward: float, action_taken: ActionSuggestion) -> None:
        # Рефлексы обычно не обучаются, можно лишь корректировать пороги
        pass