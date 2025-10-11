#!/usr/bin/env python3

import os
# Força X11 no Wayland, se estiver usando Linux
os.environ["SDL_VIDEODRIVER"] = "x11"

import threading
import time
import webbrowser

import requests
import arcade
import uvicorn

from config import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from views.login_view import LoginView
from api.app import app as fastapi_app
from api.db.mongo import mongo
import seed


class RPGGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.set_fullscreen(False)
        # Começa com a tela de login
        self.show_view(LoginView())

    def on_key_press(self, key, modifiers):
        # Atalho de fullscreen global
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
        # Encaminha evento para a view atual, se existir
        elif hasattr(self.view, "on_key_press"):
            self.view.on_key_press(key, modifiers)


def start_fastapi():
    """Inicia a API FastAPI em background (daemon)."""
    uvicorn.run(
        fastapi_app,
        host="127.0.0.1",
        port=8000,
        log_level="error",
        access_log=False,
    )


def silent_health_check() -> bool:
    """Verifica silenciosamente se a API está no ar."""
    try:
        requests.get("http://127.0.0.1:8000/health", timeout=2)
        return True
    except:
        return False


def main():
    # 1) Conecta no MongoDB
    if not mongo.connect():
        print("❌ Falha ao conectar no MongoDB")
        return

    # 2) Popula perguntas (seed)
    seed.run()

    # 3) Inicia a API em thread background
    api_thread = threading.Thread(target=start_fastapi, daemon=True)
    api_thread.start()

    # 4) Health check rápido
    time.sleep(1.5)
    if not silent_health_check():
        print("⚠️  API não respondeu, mas continuando...")

    # 5) Abre o jogo
    print("🎮 Iniciando Dungeons of Questions...")
    game = RPGGame()

    # 6) (Opcional) Abre docs do FastAPI depois de 3s
    threading.Timer(3.0, lambda: webbrowser.open("http://127.0.0.1:8000/docs")).start()

    arcade.run()

    # 7) Ao fechar o jogo, desconecta do MongoDB
    mongo.disconnect()


if __name__ == "__main__":
    main()
