import asyncio
import base64
from rich.console import Console
from rich.markdown import Markdown
import markdown2

import torch
from transformers import CLIPProcessor, CLIPModel

from datetime import datetime

import json
from io import BytesIO
import requests
from PIL import Image
from openai import OpenAI
import os

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

def get_current_screen():
    image_url = "http://localhost:8080/screen"
    response = requests.get(image_url)
    response.raise_for_status()
    return base64.b64encode(response.content).decode('utf-8')

def get_local_image_as_base64(filename):
    with open(f"examples/{filename}", "rb") as image:
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

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def calculate_image_difference(image1, image2):
    return 0

def print_markdown(markdown_text: str):
    console = Console()
    md = Markdown(markdown2.markdown(markdown_text))
    console.print(md)

def get_example_prompt(filename):
    text_filename = filename.replace(".png", ".txt")
    with open(f"examples/{text_filename}", "r") as file:
        return file.read()

def get_image_as_base64(image_path=None):
    if image_path:
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                return base64.b64encode(image_data).decode('utf-8')
        except FileNotFoundError:
            print(f"Error: Image file '{image_path}' not found.")
        except Exception as e:
            print(f"Error while reading image file '{image_path}': {e}")
    else:
        print("Error: Image path is not provided.")
    return None

def get_clip_embedding(image_base64):
    image_data = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_data)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    outputs = model.get_image_features(**inputs)
    return outputs

def find_closest_images(base64_image, example_images, top_k=30):
    base_image_embedding = get_clip_embedding(base64_image)
    similarities = []
    for example_image in example_images:
        example_image_base64 = get_image_as_base64(f"examples/{example_image}")
        example_image_embedding = get_clip_embedding(example_image_base64)
        similarity = torch.cosine_similarity(base_image_embedding, example_image_embedding).item()
        similarities.append((similarity, example_image))
    
    similarities.sort(reverse=True, key=lambda x: x[0])
    return [image for _, image in similarities[:top_k]]

async def main():
    current_time_minutes = datetime.now().minute
    past_states = []

    is_first_run = True

    while True:
        base64_image = get_current_screen()

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
                                "description": "Up to 4 next moves",
                                "maxItems": 4
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

Analyze the screenshot, plan the next moves. If are moving on map, visualize each move step by step. Consider past game states and screenshots to determine if you are moving in the right direction.

To help you with the game you will be given two types of additional information:
- **Past game plans & screenshots**: You will be given the game plan and screenshot of the previous 5 game states. Some examples are just for instructing path finding.
- **Example Moves**: You will be given three expert moves from various situations in the game.

IMPORTANT: Compare the current and previous game screenshots to determine if you are making progress. You are sometimes mixing up the directions. Try out different directions and check if the environment changes.


While you are on maps:
IMPORTANT: 
IN YOUR STRATEGY (Additional Chapter called: ## Orientation above Terminal Goals): ORIENT YOURSELF: WRITE FIRST WHAT I CAN FIND UP, DOWN, LEFT, RIGHT OF THE MAP. LIST ALL OBJECTS AND LOCATIONS. Example: I am currently in a room. On the rigth side there is a wall. On the left side there is a wall. On the bottom as well. Top right I can see a staircase. (this is not shown in the example but you MUST do it).
Example
- Top: Wall / Black Space (Obsticle)
- Right: Wall / Black Space (Obsticle)
- Bottom: Warp (Rug) leading outside (Bottom left), Wall / Black Space (Obsticle) (Bottom)
- Left: Table, chairs, a character, Wall / Black Space (Obsticle)
- Warps: Bottom left warp leads to a room with a chest.

IMPORTANT: On Maps: Never plan ahead of the current map. Never plan ahead of warps.


"""

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        example_files = sorted([f for f in os.listdir("examples") if f.endswith(".png")])

        closest_examples = find_closest_images(base64_image, example_files)

        for example_file in closest_examples:
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{get_image_as_base64(f'examples/{example_file}')}"
                            }
                        },
                        {
                            "type": "text",
                            "text": get_example_prompt(example_file)
                        }
                    ]
                }
            )

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

        if is_first_run:
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "{\"strategy\": \"This is the first game round. I have no completed goals yet. I need to think about defining my terminal goals given the current situation.\", \"CompletedGoals\": [], \"TerminalGoals\": [], \"InstrumentalGoals\": [], \"NextActions\": []}"
                    }
                ],
            })
            is_first_run = False

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
            max_tokens=1500,
        )

        messages_function_call = [
            {
                "role": "system",
                "content": "You will be given a Markdown document that describes the current game state object. Call the function as per the values in the provided in the Markdown. Don't change any of the values in the object."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": response.choices[0].message.content
                    }
                ]
            }
        ]

        print(response.choices[0].message.content)

        response_function_call = client.chat.completions.create(
            model="gpt-4o",
            messages=messages_function_call,
            max_tokens=500,
            tools=tools,
        )

        tool_calls = response_function_call.choices[0].message.tool_calls

        function_args = None

        if tool_calls:
            for tool_call in tool_calls:
                past_states.append({"image": base64_image, "function": json.loads(tool_call.function.arguments),
                                    "time": datetime.now(), "minutes_played": current_time_minutes})
                function_args = json.loads(tool_call.function.arguments)

        if len(past_states) > 5:
            past_states.pop(0)

        print(function_args)
        if function_args and "NextActions" in function_args:
            await execute_moves(function_args["NextActions"])

if __name__ == "__main__":
   asyncio.run(main())