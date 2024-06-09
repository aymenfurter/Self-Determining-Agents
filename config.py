import os

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENGINE = "gpt-4o"

# Azure OpenAI configuration
OPENAI_USE_AZURE = True
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# Game configuration
GAME_SCREEN_URL = "http://localhost:8080/screen"
GAME_INPUT_URL = "http://localhost:8080/input"

EXAMPLES_DIRECTORY = "examples"

SYSTEM_PROMPT = """# Role
You are an expert Pokemon speedrunner.

# Instructions        
You are speedrunning Pokemon game. You must rush through the game as quickly as possible. 

You are playing the game by analyzing the **current screenshot**  updating a so called **game plan**.

Analyze the screenshot, plan the next moves. If are moving on map, visualize each move step by step. Consider past game states and screenshots to determine if you are moving in the right direction.

To help you with the game you will be given two types of additional information:
- **Past game plans & screenshots**: You will be given the game plan and screenshot of the previous 5 game states. Some examples are just for instructing path finding.
- **Example Moves**: You will be given expert moves from various situations in the game.

IMPORTANT: Compare the current and previous game screenshots to determine if you are making progress. You are sometimes mixing up the directions. Try out different directions and check if the environment changes.

While you are on maps:
IMPORTANT: Always start with orientation. During orientation you describe the screen in detail and list possible actions or move to take. Then you can plan the next moves.
Example:
```
## Orientation
- Top: Wall / Black Space (Obsticle) - I can' t move up
- Right: Wall / Black Space (Obsticle) - I can't move right
- Bottom: Warp (Rug) leading outside (Bottom left), Wall / Black Space (Obsticle) (Bottom) - I can move down
- Left: Table, chairs, a character, Wall / Black Space (Obsticle) - I can move left
- Warps: Bottom left warp leads to a room with a chest.
```

IMPORTANT: On Maps: Never plan ahead of the current map. Never plan ahead of warps.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "updateGamePlan",
            "parameters": {
                "type": "object",
                "properties": {
                    "strategy": {"type": "string", "description": "Reflect on previous moves and suggest a strategy for the next 4 moves."},
                    "CompletedGoals": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "goal": {"type": "string", "description": "Completed terminal goal."}
                            },
                            "required": ["goal"]
                        },
                        "description": "keep track of the last 5 completed terminal goals.",
                        "maxItems": 5
                    },
                    "TerminalGoals": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "goal": {"type": "string", "description": "Terminal goal."}
                            },
                            "required": ["goal"]
                        },
                        "description": "up to 2 terminal goals.",
                        "maxItems": 2
                    },
                    "Surroundings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "direction": {"type": "string", "enum": ["Up", "Down", "Left", "Right"], "description": "Direction."},
                                "object": {"type": "string", "description": "Object in the direction."}
                            },
                            "required": ["direction", "object"]
                        },
                        "description": "Objects in the surroundings.",
                        "maxItems": 4
                    },
                    "InstrumentalGoals": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "goal": {"type": "string", "description": "Instrumental goal."}
                            },
                            "required": ["goal"]
                        },
                        "description": "up to 3 instrumental goals incl rationales for each.",
                        "maxItems": 3
                    },
                    "NextActions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "move": {"type": "string", "enum": ["Up", "Down", "Left", "Right", "A", "B", "Start"], "description": "Suggested move."}
                            }
                        },
                        "description": "Up to 4 next moves",
                        "maxItems": 4
                    }
                },
                "required": ["strategy", "ScreenDescription", "TerminalGoals", "InstrumentalGoals", "NextActions"]
            }
        }
    }
]
