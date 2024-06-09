import asyncio
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO
from game_bridge import GameBridge
from colorama import Fore, Style

app = Flask(__name__)
socketio = SocketIO(app)
game_bridge = GameBridge(socketio)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    game_bridge.handle_connect()

@socketio.on('update_keys')
def handle_update_keys(data):
    game_bridge.handle_update_keys(data)

@socketio.on('execute')
def handle_execute(data):
    game_bridge.handle_execute(data)

def run_game_logic():
    asyncio.run(game_bridge.game_logic())

def screen_update_thread():
    while True:
        game_bridge.send_screen_update()
        socketio.sleep(0.05) 

if __name__ == "__main__":
    print(Fore.GREEN + Style.BRIGHT + "🎮 Welcome! 🎮" + Style.RESET_ALL)
    print(Fore.YELLOW + "✨ Get ready for an exciting adventure! ✨" + Style.RESET_ALL)
    print(Fore.CYAN + "🚀 Starting up ... 🚀" + Style.RESET_ALL)

    threading.Thread(target=run_game_logic).start()
    threading.Thread(target=screen_update_thread).start()
    socketio.run(app, debug=True)
