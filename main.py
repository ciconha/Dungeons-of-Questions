#!/usr/bin/env python3
import os
# Força X11 no Wayland
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
        # F11 alterna fullscreen
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
        else:
            if hasattr(self.view, "on_key_press"):
                self.view.on_key_press(key, modifiers)

def start_fastapi():
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")

def main():
    # 1) Inicializa API em thread daemon
    threading.Thread(target=start_fastapi, daemon=True).start()

    # 2) Pequeno delay e health check
    time.sleep(1)
    try:
        print("Health check:", requests.get("http://127.0.0.1:8000/health").json())
    except Exception as e:
        print("Health check falhou:", e)

    # 3) Abre o Swagger UI e um endpoint de teste
    webbrowser.open("http://127.0.0.1:8000/docs")
    webbrowser.open("http://127.0.0.1:8000/api/launch")

    # 4) Inicia o jogo
    print("Abrindo o jogo...")
    game = RPGGame()
    arcade.run()

if __name__ == "__main__":
    main()
