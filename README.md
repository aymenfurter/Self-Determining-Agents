<div id="top"></div>

<br />
<div align="center">
    <img src="assets/demo.gif?raw=true">
  <h1 align="center">Self-Determining Agents with GPT-4o</h1>
  <p align="center">
    AI agents that can define and edit their own goals to interact with game environments. Powered by GPT-4o.
    <br />
    <br />
    <a href="#running-the-project">Get Started</a>
    ·
    <a href="#limitations">View Limitations</a>
  </p>
</div>
<br />

## Disclaimers
1. The AI needed minor assistance with positioning on the first floor (one move to the left).
2. Assistance was also required during a conversation with Oak before the Pokemon selection due to a looping issue. These could be resolved with better examples, but running the application is expensive.

## Overview
This repository introduces a self-determining agent powered by GPT-4o, capable of defining and editing its own terminal and instrumental goals. The agent interacts with the game environment, processes visual input, and makes decisions based on its cognitive capabilities. With the recent release of GPT-4o, the enhanced multimodal capabilities and increased context size allow for more images as samples in in-context learning, improving the agent's speed and efficiency.

## Key Features
- **Few-Shot Learning:** Uses CLIP embeddings to match current game screenshots with relevant examples from the "examples" directory for context.
- **Environment Description:** AI describes surroundings (up, down, left, right) to understand the environment better.
- **Structured Output:** Utilizes function calling to provide environment descriptions and actions, converting them into JSON for game control.
- **SkyEmu:** Interacts with the game emulator using a REST API for key presses and screen retrieval.
- **Reasoning Loop:** [`GameBridge`](./game_bridge.py) manages the reasoning loop, providing the last 3 game states for planning the next action.

## Running the Project

### Prerequisites
1. Ensure Python 3.7+ is installed.

### Installation
1. Clone the repository and navigate to the project directory:
   ```sh
   git clone https://github.com/yourusername/self-determining-agent.git
   cd self-determining-agent
   ```
2. Install the required packages using pip:
   ```sh
   pip install -r requirements.txt
   ```

### Configuration
Configure the following environment variables in your environment or in a `.env` file:

```sh
# OpenAI API configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_ENGINE="gpt-4o"

# Azure OpenAI configuration
OPENAI_USE_AZURE=False
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint

# Game configuration
GAME_SCREEN_URL="http://localhost:8080/screen"
GAME_INPUT_URL="http://localhost:8080/input"
```

The sample runs on both Azure OpenAI and OpenAI directly. To use Azure OpenAI, set `OPENAI_USE_AZURE` to `True` and provide the necessary Azure OpenAI configurations.

### Running the Application
1. Run the application:
   ```sh
   python app.py
   ```

## Limitations
- AI assistance was needed for some tasks.
- Inference costs can be high due to the use of GPT-4o.

## Classes and Functionality
- **[KnowledgeRepository](./knowledge_repository.py):** Finds relevant examples based on the current game screen.
- **[ActionOrchestrator](./action_orchestrator.py):** Handles HTTP requests to SkyEmu for game control.
- **[GameBridge](./game_bridge.py):** Main reasoning loop, using previous game states for the next action.
- **[EnvironmentPerceptions](./environment_perceptions.py):** Retrieves the current game screen and will handle environment perception in future updates.

## Frontend
A web-based frontend visualizes the current game state, actions, and overlays showing the model's plans and observations. Users can browse through few-shot learning samples and view associated text data.

<br />

<p align="right">(<a href="#top">back to top</a>)</p>