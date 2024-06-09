import asyncio
from typing import List, Callable
import requests
from config import GAME_INPUT_URL
from models import Goal, GameState, Action

class ActionOrchestrator:
    def __init__(self):
        self.input_url = GAME_INPUT_URL
        self.pressed_keys: List[str] = []
        self.observers: List[Callable[[List[str]], None]] = []

    def register_observer(self, observer: Callable[[List[str]], None]):
        self.observers.append(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer(self.pressed_keys)

    async def send_command(self, command: Action):
        move = command.move

        self.pressed_keys.append(move)
        self.notify_observers()
        requests.get(f"{self.input_url}?{move}=1")
        await asyncio.sleep(0.2)
        self.pressed_keys.remove(move)
        self.notify_observers()
        requests.get(f"{self.input_url}?{move}=0")
        await asyncio.sleep(1)

    async def execute_moves(self, moves: List[Action]):
        for move in moves:
            await self.send_command(move)

    def get_pressed_keys(self) -> List[str]:
        return self.pressed_keys

    def update_pressed_keys(self, keys: List[str]):
        self.pressed_keys = keys
        self.notify_observers()
