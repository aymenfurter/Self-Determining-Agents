# game_bridge.py
import asyncio
import json
from flask_socketio import emit
from environment_perceptions import EnvironmentPerceptions
from action_orchestrator import ActionOrchestrator
from cognitive_engine import CognitiveEngine
from knowledge_repository import KnowledgeRepository
from typing import List
from openai import OpenAI
from openai import AzureOpenAI
from datetime import datetime
from config import OPENAI_API_KEY, OPENAI_ENGINE, SYSTEM_PROMPT, TOOLS, OPENAI_USE_AZURE, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT

class GameBridge:
    def __init__(self, socketio):
        self.socketio = socketio
        self.environment_perceptions = EnvironmentPerceptions()
        self.action_orchestrator = ActionOrchestrator()
        self.action_orchestrator.register_observer(self.on_keys_update)  # Register as observer
        self.cognitive_engine = CognitiveEngine()
        self.knowledge_repository = KnowledgeRepository()
        if OPENAI_USE_AZURE:
            self.openai_client = AzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                api_version="2024-02-01",
                azure_endpoint=AZURE_OPENAI_ENDPOINT
            )
        else:
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY)

        self.past_states = []

    async def game_logic(self):
        while True:
            current_time_minutes = datetime.now().minute
            base64_image = self.environment_perceptions.get_current_screen()
            relevant_examples = self.knowledge_repository.get_relevant_examples(base64_image)

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            for example in relevant_examples:
                 messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "# This is a similar situation previously recorded by expert players.\nHere is the output:\n" +  example['example_prompt']
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{example['base64_image']}",
                                },
                            },
                        ],
                    }
                )

            self.socketio.emit('closest_examples_update', {"closest_examples": relevant_examples})

            for state in self.past_states:
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
                            #{
                            #    "type": "image_url",
                            #    "image_url": {
                            #        "url": f"data:image/png;base64,{image_base64_data}"
                            #    },
                            #},
                        ],
                    }
                )

            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "# Current screenshot of YOUR game that YOU are currently playing\n## Time\n**NOW**"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        },
                    },
                ],
            })

            if OPENAI_USE_AZURE:
                response = self.openai_client.chat.completions.create(
                    model=OPENAI_ENGINE,
                    messages=messages,
                    max_tokens=1500,
                    tools=TOOLS,
                )
            else:
                response = self.openai_client.chat.completions.create(
                    model=OPENAI_ENGINE,
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

            if OPENAI_USE_AZURE:
                response_function_call = self.openai_client.chat.completions.create(
                    model=OPENAI_ENGINE,
                    messages=messages_function_call,
                    max_tokens=500,
                    tools=TOOLS,
                )
            else:
                response_function_call = self.openai_client.chat.completions.create(
                    model=OPENAI_ENGINE,
                    messages=messages_function_call,
                    max_tokens=500,
                    tools=TOOLS,
                )

            tool_calls = response_function_call.choices[0].message.tool_calls

            function_args = None
            updated_tool_call = None

            if tool_calls:
                for tool_call in tool_calls:
                    self.past_states.append({"image": base64_image, "function": json.loads(tool_call.function.arguments), "time": datetime.now(), "minutes_played": current_time_minutes})
                    function_args = json.loads(tool_call.function.arguments)

            if not function_args:
                return

            if len(self.past_states) > 3:
                self.past_states.pop(0)

            if function_args:
                game_state = self.cognitive_engine.process_game_state_json(function_args)
                self.send_goals_update()
                self.send_keys_update()
                self.send_surroundings_update()
                if "NextActions" in function_args:
                    await self.action_orchestrator.execute_moves(game_state.next_actions)



    def send_screen_update(self):
        current_screen = self.environment_perceptions.get_current_screen()
        self.socketio.emit('screen_update', {"image": current_screen})

    def send_surroundings_update(self):
        surroundings = self.cognitive_engine.get_surroundings()
        self.socketio.emit('surroundings_update', {"surroundings": surroundings})

    def send_goals_update(self):
        completed_goals = self.cognitive_engine.get_completed_goals()
        terminal_goals = self.cognitive_engine.get_terminal_goals()
        instrumental_goals = self.cognitive_engine.get_instrumental_goals()
        goals_update = {
            "completed_goals": completed_goals,
            "terminal_goals": terminal_goals,
            "instrumental_goals": instrumental_goals,
        }
        self.socketio.emit('goals_update', goals_update)

    def send_keys_update(self):
        pressed_keys = self.action_orchestrator.get_pressed_keys()
        self.socketio.emit('keys_update', {"keys": pressed_keys})

    def on_keys_update(self, keys: List[str]):
        self.send_keys_update()

    def handle_connect(self):
        self.socketio.emit('initial_data', {
            "completed_goals": self.cognitive_engine.get_completed_goals(),
            "terminal_goals": self.cognitive_engine.get_terminal_goals(),
            "instrumental_goals": self.cognitive_engine.get_instrumental_goals(),
            "keys": self.action_orchestrator.get_pressed_keys(),
        })
        self.send_screen_update()

    def handle_update_keys(self, data):
        keys = data.get('keys', [])
        self.action_orchestrator.update_pressed_keys(keys)
        self.send_keys_update()

    def handle_execute(self, data):
        moves = data.get('moves', [])
        asyncio.run(self.action_orchestrator.execute_moves(moves))
        self.socketio.emit('execute_status', {"status": "success"})
