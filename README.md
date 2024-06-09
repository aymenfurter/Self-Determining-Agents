<div id="top"></div>

<br />
<div align="center">
    <img src="assets/demo.gif?raw=true">
    <h1 align="center">Self-Determining Agents with GPT-4o</h1>
    <p align="center">
        AI agents that define their own goals to interact with a game environment. Powered by GPT-4o.
        <br />
        <br />
        <a href="#running-the-project">Get Started</a>
        ·
        <a href="#limitations">View Limitations</a>
    </p>
</div>


<sub>Disclaimer: During the demo, the AI needed minor help with positioning on the first floor and a looping issue during a chat with Oak. Both could be fixed with more samples</sub>
<br />
## Overview
This repository introduces a self-determining agent powered by GPT-4o, capable of defining and editing its own terminal and instrumental goals. The agent interacts with the game environment, processes visual input, and makes decisions based on its cognitive capabilities. This is made possible by the recent release of GPT-4o, which features enhanced multimodal capabilities and a larger context size for image data. This allows for more images as samples in in-context learning, improving the agent's speed and efficiency.

## Key Features
- **Few-Shot Learning:** Uses CLIP embeddings to match current game screenshots with relevant examples from the "examples" directory for context.
- **Environment Description:** AI describes surroundings (up, down, left, right) to understand the environment better.
- **Structured Output:** Utilizes function calling to provide environment descriptions and actions, converting them into JSON for game control.
- **Game Interaction:** Interacts with the game using a REST API for key presses and screen retrieval.
- **Reasoning Loop:** [`GameBridge`](./game_bridge.py) manages the reasoning loop, providing the last 3 game states for planning the next action.

## Running the Project

### Prerequisites
1. Ensure Python 3.7+ is installed.

### Installation
1. Clone the repository and navigate to the project directory:
   ```sh
   git clone https://github.com/aymenfurter/Self-Determining-Agent-GPT4o.git
   cd Self-Determining-Agent-GPT4o
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
- The AI's performance relies greatly on high-quality examples that demonstrate the game in different situations.
- Inference costs can be high due to the use of GPT-4o.

## Classes and Functionality
- **[KnowledgeRepository](./knowledge_repository.py):** Finds relevant examples based on the current game screen.
- **[ActionOrchestrator](./action_orchestrator.py):** Handles HTTP requests for game control. An HTTP Endpoint to retrieve the screen and perform key actions on Port 8080 is expected.
- **[GameBridge](./game_bridge.py):** Main reasoning loop, using previous game states for the next action.
- **[EnvironmentPerceptions](./environment_perceptions.py):** Retrieves the current game screen and will handle environment perception in future updates.

## Frontend
A web-based frontend visualizes the current game state, actions, and overlays showing the model's plans and observations. Users can browse through few-shot learning samples and view associated text data.

<br />

<p align="right">(<a href="#top">back to top</a>)</p>
