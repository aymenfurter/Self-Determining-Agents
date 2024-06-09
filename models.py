from dataclasses import dataclass
from typing import List

@dataclass
class Goal:
    goal: str

@dataclass
class Action:
    move: str

@dataclass
class Surrounding:
    direction: str
    object: str

@dataclass
class GameState:
    strategy: str
    completed_goals: List[Goal]
    terminal_goals: List[Goal]
    instrumental_goals: List[Goal]
    next_actions: List[Action]