import asyncio
import base64

from datetime import datetime

import json
from io import BytesIO
import requests
from PIL import Image
from openai import OpenAI
client = OpenAI()

async def send_a():
    print("Sending A")
    requests.get("http://localhost:8080/input?A=1")
    await asyncio.sleep(0.2)
    requests.get("http://localhost:8080/input?A=0")
    await asyncio.sleep(0.2)

async def send_up():
    print("Sending Up")
    requests.get("http://localhost:8080/input?Up=1")
    await asyncio.sleep(0.2)
    requests.get("http://localhost:8080/input?Up=0")

async def send_down():
    print("Sending Down")
    requests.get("http://localhost:8080/input?Down=1")
    await asyncio.sleep(0.2)
    requests.get("http://localhost:8080/input?Down=0")

async def send_left():
    print("Sending Left")
    requests.get("http://localhost:8080/input?Left=1")
    await asyncio.sleep(0.2)
    requests.get("http://localhost:8080/input?Left=0")

async def send_right():
    print("Sending Right")
    requests.get("http://localhost:8080/input?Right=1")
    await asyncio.sleep(0.2)
    requests.get("http://localhost:8080/input?Right=0")

async def send_b():
    print("Sending B")
    requests.get("http://localhost:8080/input?B=1")
    await asyncio.sleep(0.2)
    requests.get("http://localhost:8080/input?B=0")

def get_image_as_base64():
    image_url = "http://localhost:8080/screen"
    response = requests.get(image_url)
    response.raise_for_status()
    return base64.b64encode(response.content).decode('utf-8')

def get_local_image_as_base64(filename):
    with open("examples/" + filename, "rb") as image:
        return base64.b64encode(image.read()).decode('utf-8')

async def send_start():
    print("Sending Start")
    requests.get("http://localhost:8080/input?Start=1")
    await asyncio.sleep(0.5)
    requests.get("http://localhost:8080/input?Start=0")

async def execute_moves(moves):
    for moveObj in moves:
        move = moveObj["move"]
        if move == "a":
            await send_a()
        elif move == "up":
            await send_up()
        elif move == "down":
            await send_down()
        elif move == "left":
            await send_left()
        elif move == "right":
            await send_right()
        elif move == "b":
            await send_b()
        elif move == "start":
            await send_start()

# TODO: implement method that caulcates the difference integer between (0 and 100) between two images (encoded as base64) - Additional metric for the LLM to use
def calculate_image_difference(image1, image2):
    return 0

async def main():
    current_time_minutes = datetime.now().minute
    past_states = []

    while True:
        base64_image = get_image_as_base64()

        tools = [
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
                                        "move": {"type": "string", "enum": ["up", "down", "left", "right", "a", "b", "start"], "description": "Suggested move."}
                                    }
                                },
                                "description": "Up to 5 next moves",
                                "maxItems": 5
                            }
                        },
                        "required": ["strategy", "ScreenDescription", "TerminalGoals", "InstrumentalGoals", "NextActions"]
                    }
                }
            }
        ]

        system_prompt = """# Role
You are an expert Pokemon speedrunner.

# Instructions        
You are speedrunning Pokemon game. You must rush through the game as quickly as possible. 

You are playing the game by analyzing the **current screenshot**  updating a so called **game plan**.

To help you with the game you will be given two types of additional information:
- **Past game plans & screenshots**: You will be given the game plan and screenshot of the previous 10 game states.
- **Example Moves**: You will be given three expert moves from various situations in the game.

IMPORTANT: ALWAYS call updateGamePlan function to update the game plan with the next 5 moves. No other output is allowed.
IMPORTANT: Compare the current and previous game screenshots to determine if you are making progress. You are sometimes mixing up the directions. Try out different directions and check if the environment changes.
IMPORTANT: If the game screenshot don't change after a few moves, you might be stuck. You are seeing a bit blurry, so there might be a obstacle in the way. Try to move 1-2 steps in different directions to see if the environment changes.
"""

        example_1_prompt = """## Example Game State 1

## Previous Game State
{
  "strategy": "Given the number of minutes played we are in the beginning of the game. We should focus on finding Doctor Oak to get our first Pokemon.",
  "TerminalGoals": [
    {
      "goal": "Find Doctor Oak"
    }
  ],
  "InstrumentalGoals": [
    {
      "goal": "Leave the house and go to the north to find Doctor Oak."
    }
  ],
  "CompletedGoals": [],
  "NextActions": [
    {
      "move": left"
    }, 
    {
      "move": "left"
    },
    {
      "move": "left"
    }
]
}
        
## Expected Game Plan (calling updateGamePlan)
{
  "strategy": "Given the number of minutes played we are in the beginning of the game. We should focus on finding Doctor Oak to get our first Pokemon.",
  "TerminalGoals": [
    {
      "goal": "Find Doctor Oak"
    }
  ],
  "InstrumentalGoals": [
    {
      "goal": "Leave the house and go to the north to find Doctor Oak."
    }
  ],
  "CompletedGoals": [],
  "NextActions": [
    {
      "move": left"
    }, 
    {
      "move": "down"
    } 
]
}
"""

        example_2_prompt = """## Example Game State 2

## Previous Game State
{
  "strategy": "We need to win the battle against the rival.",
  "TerminalGoals": [
    {
      "goal": "Beat rival in pokemon battle."
    }
  ],
  "InstrumentalGoals": [
    {
      "goal": "Attack with Shiggy using Tackle to win the battle."
    }
  ],
  "CompletedGoals": [
    {
      "goal": "Find Doctor Oak."
    },
    {
      "goal": "Get the first Pokemon."
    },
  ],
  "NextActions": [
    {
      "move": a"
    }, 
    {
      "move": "a"
    },
    {
      "move": "a"
    }
]
}
        
## Expected Game Plan (calling updateGamePlan)
{
  "strategy": "We won the battle against the rival. Now we need to complete the text dialog to progress in the game",
  "TerminalGoals": [
    {
        "goal": "Travel to the next city in the north, Viridian City."
    }
  ],
  "InstrumentalGoals": [
    {
      "goal": "Complete the text dialog to progress in the game."
    },
    {
      "goal": "Leave the building by going down."
    }
  ],
  "CompletedGoals": [
    {
      "goal": "Beat rival in pokemon battle."
    },
    {
      "goal": "Find Doctor Oak."
    },
    {
      "goal": "Get the first Pokemon."
    },
  ],
  "NextActions": [
    {
      "move": a"
    }, 
    {
      "move": "a"
    },
    {
      "move": "a"
    },
    {
      "move": "a"
    }
  ]
}
"""

        example_3_prompt = """## Example Game State 3

## Previous Game State
{
  "strategy": "We are currently in a battle against Bisasam with our Schiggy. Schiggy has 11/20 HP. The move set includes Tackle (Tackle) and Rutenschlag (Tail Whip). Proceed with the most effective strategy to win the battle.",
  "TerminalGoals": [
    {
      "goal": "Beat rival in pokemon battle."
    }
  ],
  "InstrumentalGoals": [
    {
      "goal": "Use high-damage moves to defeat Bisasam quickly to minimize damage taken by Schiggy."
    }
  ],  
  "CompletedGoals": [
    {
      "goal": "Find Doctor Oak."
    },
    {
      "goal": "Get the first Pokemon."
    },
  ],
  "NextActions": [
    {
      "move": "a"
    }
  ]
}
        
## Expected Game Plan (calling updateGamePlan)
{
  "strategy": "We are currently in a battle against Bisasam with our Schiggy. Let's proceed with using Tackle to reduce the HP of the enemy Bisasam.",
  "TerminalGoals": [
    {
      "goal": "Beat rival in pokemon battle."
    }
  ],
  "InstrumentalGoals": [
    {
      "goal": "Use high-damage moves to defeat Bisasam quickly to minimize damage taken by Schiggy."
    }
  ],
  "CompletedGoals": [
    {
      "goal": "Find Doctor Oak."
    },
    {
      "goal": "Get the first Pokemon."
    },
  ],
  "NextActions": [
    {
      "move": "a"
    },
    {
      "move": "a"
    },
    {
      "move": "a"
    },
    {
      "move": "a"
    }
  ]
}
"""
        example_4_prompt = """## Example Game State 4

## Previous Game State
{
  "strategy": "We are currently on our way to the next city, Viridian City. We need to go up to go north to reach the city.",
  "TerminalGoals": [
    {
        "goal": "Travel to the next city in the north, Viridian City."
    }
  ],
  "InstrumentalGoals": [
    {
      "goal": "Navigate to the north of the city."
    }
  ],
  "CompletedGoals": [
    {
      "goal": "Find Doctor Oak."
    },
    {
      "goal": "Get the first Pokemon."
    },
    {
      "goal": "Beat rival in pokemon battle."
    }
  ],
  "NextActions": [
    {
      "move": "left"
    },
    {
      "move": "left"
    },
    {
      "move": "up"
    },
    {
      "move": "up"
    }
  ]
}
        
## Expected Game Plan (calling updateGamePlan)
{
  "strategy": "We are currently on our way to the next city, Viridian City. We need to go up to go north to reach the city.",
  "TerminalGoals": [
    {
        "goal": "Navigate to the north of the city."
    }
  ],
  "InstrumentalGoals": [
    {
      "goal": "Use high-damage moves to defeat Bisasam quickly to minimize damage taken by Schiggy."
    }
  ],
  "CompletedGoals": [
    {
      "goal": "Find Doctor Oak."
    },
    {
      "goal": "Get the first Pokemon."
    },
    {
      "goal": "Beat rival in pokemon battle."
    }
  ],
  "NextActions": [
    {
      "move": "a"
    },
    {
      "move": "a"
    },
    {
      "move": "a"
    },
    {
      "move": "a"
    }
  ]
}
"""


        example_5_prompt = """## Example Game State 5

## Previous Game State
{
  "strategy": "Given the number of minutes played we are in the beginning of the game. We should focus on finding Doctor Oak to get our first Pokemon.",
  "TerminalGoals": [
    {
      "goal": "Find Doctor Oak"
    }
  ],
  "InstrumentalGoals": [
    {
      "goal": "Go to the first floor of the house."
    }
  ],
  "CompletedGoals": [],
  "NextActions": [
    {
      "move": right"
    }, 
    {
      "move": "top"
    },
    {
      "move": "top"
    }
]
}
        
## Expected Game Plan (calling updateGamePlan)
{
  "strategy": "Given the number of minutes played we are in the beginning of the game. I should try to reach the stairs at the top right corner of the room to go to the first floor of the house.",
  "TerminalGoals": [
    {
      "goal": "Find Doctor Oak"
    }
  ],
  "InstrumentalGoals": [
    {
      "goal": "Go to the first floor of the house."
    }
  ],
  "CompletedGoals": [],
  "NextActions": [
    {
      "move": "top"
    }, 
    {
      "move": "top"
    },
    {
      "move": "top"
    },
    {
      "move": "right"
    }
]
}
"""

        messages=[
                {   
                    "role": "system", 
                    "content": system_prompt  
                },
                {   
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{get_local_image_as_base64('screen-0.png')}"
                            }
                        },
                        {
                            "type": "text",
                            "text": example_1_prompt
                        }
                    ]
                }, 
                {   
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{get_local_image_as_base64('screen-8.png')}"
                            }
                        },
                        {
                            "type": "text",
                            "text": example_2_prompt
                        }
                    ]
                },
                {   
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{get_local_image_as_base64('screen-4.png')}"
                            }
                        },
                        {
                            "type": "text",
                            "text": example_3_prompt
                        }
                    ]
                },
                {   
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{get_local_image_as_base64('screen-10.png')}"
                            }
                        },
                        {
                            "type": "text",
                            "text": example_4_prompt
                        }
                    ]
                },
                {   
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{get_local_image_as_base64('screen-13.png')}"
                            }
                        },
                        {
                            "type": "text",
                            "text": example_5_prompt
                        }
                    ]
                }
        ]

        for state in past_states:
            print("Adding past state")
            image_base64_data = state["image"]
            function_data = state["function"]
            time = state["time"]
            minutes_played = state["minutes_played"]

            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": f"# Previous Game State\n## Time\n{time}\n## Minutes played\n{minutes_played}\n## Game State\n```json\n{json.dumps(function_data, indent=2)}\n```"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64_data}"
                            },
                        },
                    ],
                }
            )
        
        messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "# Current game screenshot\n## Time\n**NOW**"
                            },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                    ],
                })


        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages, 
            max_tokens=500,
            tools=tools,
        )
        print (response)
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        function_args = None

        if tool_calls:
            for tool_call in tool_calls:
                past_states.append({ "image": base64_image, "function": json.loads(tool_call.function.arguments), "time": datetime.now(), "minutes_played": current_time_minutes})
                function_args = json.loads(tool_call.function.arguments)

        
        if len(past_states) > 50:
            past_states.pop(0)

        print(function_args)
        if function_args and "NextActions" in function_args:
            await execute_moves(function_args["NextActions"])

if __name__ == "__main__":
    asyncio.run(main())