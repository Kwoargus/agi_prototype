from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from __future__ import annotations


@dataclass
class Perception:
    """Сырые или предобработанные сенсорные данные"""
    vision: Optional[bytes] = None  # изображение
    hearing: Optional[bytes] = None  # аудио
    touch: Optional[float] = None  # сила/температура
    smell: Optional[Dict[str, float]] = None  # концентрации веществ
    taste: Optional[Dict[str, float]] = None
    timestamp: float = 0.0


@dataclass
class ActionSuggestion:
    """Предложение действия от модуля"""
    action_id: str
    priority: float  # 0..1 уверенность/важность
    params: Dict[str, Any] = None


class ReactionModule(ABC):
    """Абстрактный модуль реакции (рефлексы, инстинкты, эмоции, интеллект)"""

    def __init__(self, memory: 'MemoryStore'):
        self.memory = memory
        self.name = self.__class__.__name__

    @abstractmethod
    def process(self, perception: Perception, context: Dict) -> List[ActionSuggestion]:
        """
        Обрабатывает восприятие и возвращает список предложений действий.
        context содержит историю, состояние группы, мета-информацию.
        """
        pass

    @abstractmethod
    def update(self, reward: float, action_taken: ActionSuggestion) -> None:
        """Обновляет внутренние параметры на основе полученной награды (для обучения)"""
        pass
