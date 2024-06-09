import json
from models import Goal, GameState, Action

class CognitiveEngine:
    def __init__(self):
        self.completed_goals = []
        self.terminal_goals = []
        self.instrumental_goals = []

    def update_game_plan(self, game_state: GameState):
        self.update_completed_goals(game_state.completed_goals)
        self.update_terminal_goals(game_state.terminal_goals)
        self.update_instrumental_goals(game_state.instrumental_goals)
        return GameState(
            strategy=game_state.strategy,
            completed_goals=self.completed_goals,
            terminal_goals=self.terminal_goals,
            instrumental_goals=self.instrumental_goals,
            next_actions=game_state.next_actions
        )

    def update_completed_goals(self, completed_goals):
        for goal in completed_goals:
            if goal not in self.completed_goals:
                self.completed_goals.append(goal)
        if len(self.completed_goals) > 15:
            self.completed_goals = self.completed_goals[-5:]

    def update_terminal_goals(self, terminal_goals):
        self.terminal_goals = terminal_goals[:2]

    def update_instrumental_goals(self, instrumental_goals):
        self.instrumental_goals = instrumental_goals[:3]

    def get_completed_goals(self):
        return [goal.goal for goal in self.completed_goals]

    def get_terminal_goals(self):
        return [goal.goal for goal in self.terminal_goals]

    def get_instrumental_goals(self):
        return [goal.goal for goal in self.instrumental_goals]

    def process_game_state(self, game_state: GameState):
        updated_game_plan = self.update_game_plan(game_state)
        return updated_game_plan

    def process_game_state_json(self, game_state_json):
        if not game_state_json:
            raise ValueError("Received empty game state JSON.")
        
        if isinstance(game_state_json, dict):
            game_state_dict = game_state_json
        else:
            game_state_dict = json.loads(game_state_json)   

        strategy = game_state_dict.get("strategy")
        completed_goals = [Goal(goal=goal["goal"]) for goal in game_state_dict.get("CompletedGoals", [])]
        terminal_goals = [Goal(goal=goal["goal"]) for goal in game_state_dict.get("TerminalGoals", [])]
        instrumental_goals = [Goal(goal=goal["goal"]) for goal in game_state_dict.get("InstrumentalGoals", [])]
        next_actions = [Action(move=action["move"]) for action in game_state_dict.get("NextActions", [])]

        game_state = GameState(
            strategy=strategy,
            completed_goals=completed_goals,
            terminal_goals=terminal_goals,
            instrumental_goals=instrumental_goals,
            next_actions=next_actions
        )
        return self.process_game_state(game_state)
