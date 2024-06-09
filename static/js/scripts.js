document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const screenImage = document.getElementById('screen-image');
    const keys = document.querySelectorAll('.key');
    const completedGoalsList = document.getElementById('completed-goals-list');
    const terminalGoalsList = document.getElementById('terminal-goals-list');
    const instrumentalGoalsList = document.getElementById('instrumental-goals-list');
    const strategyContent = document.getElementById('strategy-content');
    const goalsLoading = document.getElementById('goals-loading');
    const closestExamplesLoading = document.getElementById('closest-examples-loading');

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
        if (examples.length === 0) {
            closestExamplesLoading.classList.add('hidden');
            return;
        }
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

        closestExamplesLoading.remove();
        closestExamplesContainer.classList.remove('hidden');
        document.getElementById('closest-examples-header').classList.remove('hidden');
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
        if (data.completed_goals.length === 0 && data.terminal_goals.length === 0 && data.instrumental_goals.length === 0) {
            return;
        }
        completedGoalsList.innerHTML = '';
        data.completed_goals.forEach(goal => {
            const li = document.createElement('li');
            li.className = 'completed';
            li.textContent = goal;
            completedGoalsList.appendChild(li);
        });

        terminalGoalsList.innerHTML = '';
        data.terminal_goals.forEach(goal => {
            const li = document.createElement('li');
            li.textContent = goal;
            terminalGoalsList.appendChild(li);
        });

        instrumentalGoalsList.innerHTML = '';
        data.instrumental_goals.forEach(goal => {
            const li = document.createElement('li');
            li.textContent = goal;
            instrumentalGoalsList.appendChild(li);
        });

        goalsLoading.remove();
        document.querySelectorAll('#goals > div').forEach(div => div.classList.remove('hidden'));
        
        if (data.completed_goals.length === 0) {
            document.getElementById('completed-goals').style.display = 'none';
        } else {
            document.getElementById('completed-goals').style.display = 'block';
        }
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
