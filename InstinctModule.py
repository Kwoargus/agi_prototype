from __future__ import annotations
from base_strategy import ReactionModule
from base_strategy import Perception
from base_strategy import ActionSuggestion
from typing import List, Dict, Optional, Any

class InstinctModule(ReactionModule):
    def process(self, perception: Perception, context: Dict) -> List[ActionSuggestion]:
        # Преобразуем восприятие в вектор признаков
        feature_vector = self._extract_features(perception)
        # Ищем в таблице инстинктов ближайшие паттерны (можно через ANN)
        patterns = self.memory.find_instinct_patterns(feature_vector, top_k=3)
        suggestions = []
        for pattern in patterns:
            action_seq = pattern.action_sequence  # список action_id
            # Создаём предложение на первое действие последовательности
            suggestions.append(ActionSuggestion(
                action_id=action_seq[0],
                priority=pattern.confidence,
                params={'remaining_sequence': action_seq[1:]}
            ))
        return suggestions

    def update(self, reward: float, action_taken: ActionSuggestion) -> None:
        # Если последовательность привела к успеху, усиливаем паттерн
        if reward > 0:
            self.memory.reinforce_instinct_pattern(action_taken)