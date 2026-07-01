from __future__ import annotations
from typing import List, Dict, Optional, Any
from base_strategy import Perception, ActionSuggestion

class InstinctModule:
    def __init__(self, patterns: List[Dict]):
        """
        patterns: список словарей вида {'pattern': {'signals': {...}}, 'action': {'action': '...'}}
        """
        self.patterns = patterns

    def process(self, perception: Perception, context: Optional[Dict] = None) -> List[ActionSuggestion]:
        print(f"InstinctModule.process: perception={perception}")
        for entry in self.patterns:
            pattern = entry.get('pattern', {})
            signals = pattern.get('signals', {})
            print(f"Checking pattern signals: {signals}")

        suggestions = []
        for entry in self.patterns:
            pattern = entry.get('pattern', {})
            signals = pattern.get('signals', {})
            # Проверяем, что все сигналы из паттерна присутствуют в восприятии с соответствующими значениями
            match = True
            for key, expected_value in signals.items():
                if key not in perception or perception[key] != expected_value:
                    match = False
                    break
            if match:
                action = entry.get('action', {})
                action_id = action.get('action', 'run_away')
                suggestions.append(ActionSuggestion(action_id=action_id, priority=1.0))
        return suggestions

    def get_best_action(self, perception: Perception) -> Optional[ActionSuggestion]:
        suggestions = self.process(perception)
        if suggestions:
            return max(suggestions, key=lambda s: s.priority)
        return None

    def update(self, reward: float, action_taken: ActionSuggestion) -> None:
        # Пока не реализовано обучение
        pass

