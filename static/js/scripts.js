document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const screenImage = document.getElementById('screen-image');
    const keys = document.querySelectorAll('.key');
    const completedGoalsList = document.getElementById('completed-goals-list');
    const terminalGoalsList = document.getElementById('terminal-goals-list');
    const instrumentalGoalsList = document.getElementById('instrumental-goals-list');
    const strategyContent = document.getElementById('strategy-content');

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('initial_data', (data) => {
        updateGoals(data);
        updateKeys(data.keys);
    });

    socket.on('screen_update', (data) => {
        screenImage.src = `data:image/png;base64,${data.image}`;
    });

    socket.on('closest_examples_update', (data) => {
        updateClosestExamples(data.closest_examples);
    });

    socket.on('goals_update', (data) => {
        updateGoals(data);
    });

    socket.on('keys_update', (data) => {
        updateKeys(data.keys);
    });

    socket.on('strategy_update', (data) => {
        strategyContent.textContent = data.strategy;
    });

    function updateClosestExamples(examples) {
        console.log('Updating closest examples:', examples);
        const closestExamplesContainer = document.getElementById('closest-examples-grid');
        closestExamplesContainer.innerHTML = '';
    
        examples.forEach(example => {
            const img = document.createElement('img');
            img.src = `data:image/png;base64,${example.base64_image}`;
            img.alt = example.filename;
            img.addEventListener('click', () => {
                showExampleDetails(example);
            });
            closestExamplesContainer.appendChild(img);
        });
    }

    function showExampleDetails(example) {
        const modal = document.getElementById('example-modal');
        const modalImage = document.getElementById('modal-image');
        const modalPrompt = document.getElementById('modal-prompt');
        const closeButton = document.querySelector('.close-button');
    
        modalImage.src = `data:image/png;base64,${example.base64_image}`;
        modalPrompt.textContent = example.example_prompt;
    
        modal.style.display = 'flex';
    
        closeButton.onclick = function() {
            modal.style.display = 'none';
        }
    
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    }


    function updateGoals(data) {
        completedGoalsList.innerHTML = '';
        data.completed_goals.forEach(goal => {
            const li = document.createElement('li');
            li.className = 'completed';
            li.textContent = goal.goal;
            completedGoalsList.appendChild(li);
        });

        terminalGoalsList.innerHTML = '';
        data.terminal_goals.forEach(goal => {
            const li = document.createElement('li');
            li.textContent = goal.goal;
            terminalGoalsList.appendChild(li);
        });

        instrumentalGoalsList.innerHTML = '';
        data.instrumental_goals.forEach(goal => {
            const li = document.createElement('li');
            li.textContent = goal.goal;
            instrumentalGoalsList.appendChild(li);
        });
    }

    function updateKeys(keysPressed) {
        keys.forEach(key => {
            key.classList.remove('pressed');
        });

        keysPressed.forEach(key => {
            const keyElement = document.getElementById(`key-${key.toLowerCase()}`);
            if (keyElement) {
                keyElement.classList.add('pressed');
            }
        });
    }
});
