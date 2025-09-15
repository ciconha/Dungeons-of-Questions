import os

os.environ["SDL_VIDEODRIVER"] = "x11"

import threading
import time
import webbrowser
import requests
import arcade
import uvicorn

from config import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from views.menu_view import MenuView
from api.app import app as fastapi_app


class RPGGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.set_fullscreen(True)
        self.show_view(MenuView())

    def on_key_press(self, key, modifiers):
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

def start_fastapi():
    uvicorn.run(
        fastapi_app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )

def main():
    
    server_thread = threading.Thread(target=start_fastapi, daemon=True)
    server_thread.start()

    
    time.sleep(1)
    try:
        resp = requests.get("http://127.0.0.1:8000/health")
        print("Health check:", resp.json())
    except Exception as e:
        print("Health check falhou:", e)

   
    webbrowser.open("http://127.0.0.1:8000/")

  
    print("Abrindo o jogo...")
    game = RPGGame()
    arcade.run()

if __name__ == "__main__":
    main()
