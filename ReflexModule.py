from __future__ import annotations
from typing import List, Dict, Optional
from base_strategy import Perception, ActionSuggestion

class ReflexModule:
    def __init__(self, rules: List[Dict]):
        self.rules = rules

    def process(self, perception: Perception, context: Optional[Dict] = None) -> List[ActionSuggestion]:
        suggestions = []
        for rule in self.rules:
            sense_type = rule.get('sense_type')      # канал: smell, sound, vision, touch...
            signal_type = rule.get('signal_type')    # конкретное значение сигнала: food_smell, predator_smell...
            threshold = rule.get('signal_threshold')
            action = rule.get('action')

            # Если это числовой сигнал (например, temperature_sense)
            if signal_type in ('temperature_sense', 'cutting_edge_sence'):
                if signal_type in perception:
                    value = perception[signal_type]
                    try:
                        if float(value) > float(threshold if threshold is not None else 0.0):
                            suggestions.append(ActionSuggestion(action_id=action, priority=1.0))
                    except (ValueError, TypeError):
                        pass
            else:
                # Строковый сигнал – ищем по каналу sense_type (если он указан)
                if sense_type and sense_type in perception:
                    if perception[sense_type] == signal_type:
                        suggestions.append(ActionSuggestion(action_id=action, priority=1.0))
                else:
                    # Если sense_type не задан, проверяем все значения в perception
                    for value in perception.values():
                        if value == signal_type:
                            suggestions.append(ActionSuggestion(action_id=action, priority=1.0))
                            break
        return suggestions

    def get_best_action(self, perception: Perception) -> Optional[ActionSuggestion]:
        suggestions = self.process(perception)
        if suggestions:
            return max(suggestions, key=lambda s: s.priority)
        return None

    def update(self, reward: float, action_taken: ActionSuggestion) -> None:
        pass
