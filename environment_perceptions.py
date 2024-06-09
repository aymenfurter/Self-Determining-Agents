import base64
import requests
from config import GAME_SCREEN_URL, EXAMPLES_DIRECTORY
from utils import get_image_from_base64, get_image_as_base64

class EnvironmentPerceptions:
    def __init__(self):
        self.screen_url = GAME_SCREEN_URL

    def get_current_screen(self):
        response = requests.get(self.screen_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')

    def calculate_image_similarity(self, image1, image2):
        return 0.5
