#!/usr/bin/env python3

import os
import sys
import threading
import time
import webbrowser
import signal

import requests
import arcade
import uvicorn

from config import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from views.login_view import LoginView
from api.app import app as fastapi_app
from api.db.mongo import mongo
import seed


def check_arcade_version() -> bool:
    """Verifica se a versão do Arcade é compatível (retorna True para versão moderna)."""
    try:
        arcade_version = getattr(arcade, "__version__", "unknown")
        print(f"🎯 Arcade Version: {arcade_version}")
        if arcade_version.startswith("1.") or arcade_version.startswith("2."):
            print("⚠️ Versão antiga do Arcade detectada - Usando modo compatível")
            return False
        print("✅ Versão moderna do Arcade - Recursos completos disponíveis")
        return True
    except Exception:
        print("⚠️ Não foi possível detectar versão do Arcade - Usando modo compatível")
        return False


class RPGGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.set_fullscreen(False)
        self.modern_arcade = check_arcade_version()
        self.show_view(LoginView())

    def on_key_press(self, key, modifiers):
        # Atalho global para fullscreen
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

        # Encaminha evento para a view atual
        current_view = getattr(self, "view", None)
        if current_view and hasattr(current_view, "on_key_press"):
            try:
                current_view.on_key_press(key, modifiers)
            except Exception:
                pass

    def on_resize(self, width, height):
        super().on_resize(width, height)
        current_view = getattr(self, "view", None)
        if current_view and hasattr(current_view, "on_resize"):
            try:
                current_view.on_resize(width, height)
            except Exception:
                pass


def start_fastapi():
    """Inicia o FastAPI via uvicorn (bloqueante) — esta função deve rodar em thread."""
    try:
        uvicorn.run(
            fastapi_app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=False,
            # reload=False  # não usar reload em produção; se quiser debug, ative
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar FastAPI (uvicorn): {e}")


def silent_health_check(url: str = "http://127.0.0.1:8000/docs", timeout: float = 2.0) -> bool:
    """Checa se a API respondeu (tenta a URL indicada)."""
    try:
        r = requests.get(url, timeout=timeout)
        return 200 <= r.status_code < 400
    except Exception:
        return False


def setup_environment():
    """Configura variáveis do ambiente e otimizações de runtime."""
    # Força X11 no Wayland (Linux)
    if sys.platform.startswith("linux"):
        os.environ.setdefault("SDL_VIDEODRIVER", "x11")

    # Otimizações/flags do Arcade
    os.environ.setdefault("ARCADE_HEADLESS", "0")

    print("🔧 Ambiente configurado")


def open_docs_delayed(delay: float = 3.0):
    """Abre docs no navegador após delay (tentativa silenciosa)."""
    time.sleep(delay)
    try:
        webbrowser.open("http://127.0.0.1:8000/docs")
        print("📚 Docs do FastAPI abertos no navegador")
    except Exception:
        print("⚠️ Não foi possível abrir docs automaticamente")


def register_signal_handlers(termination_callback):
    """Registra sinais para shutdown limpo (Linux/macOS/Windows)."""
    def handler(signum, frame):
        print(f"🛑 Sinal recebido {signum} — encerrando...")
        termination_callback()

    for sig in ("SIGINT", "SIGTERM"):
        if hasattr(signal, sig):
            signal.signal(getattr(signal, sig), handler)


def main():
    setup_environment()

    # Conecta ao MongoDB (necessário para seed e operações)
    print("🔌 Conectando ao MongoDB...")
    if not mongo.connect():
        print("❌ Falha crítica: não foi possível conectar ao MongoDB. Abortando.")
        return

    # Popula DB (seed). Seed usa mongo conectado internamente.
    print("🌱 Executando seed do banco de dados...")
    try:
        seed.run()
        print("✅ Seed executado com sucesso.")
    except Exception as e:
        print(f"⚠️ Aviso: falha/erro ao executar seed: {e}")

    # Inicia FastAPI em thread separada
    print("🚀 Iniciando API FastAPI (uvicorn) em background...")
    api_thread = threading.Thread(target=start_fastapi, daemon=True)
    api_thread.start()

    # Faz health-check com retries (dá mais robustez em máquinas lentas)
    print("🔍 Verificando saúde da API...")
    max_retries = 8
    wait_between = 0.8
    api_ok = False
    for attempt in range(max_retries):
        if silent_health_check("http://127.0.0.1:8000/docs", timeout=1.0):
            api_ok = True
            break
        time.sleep(wait_between)

    if api_ok:
        print("✅ API respondendo corretamente")
        # Abre docs em thread para não bloquear
        threading.Thread(target=open_docs_delayed, args=(2.5,), daemon=True).start()
    else:
        print("⚠️ API não respondeu no tempo esperado. Você pode acessar manualmente em http://127.0.0.1:8000/docs")

    # Preparação para encerramento limpo
    def terminate():
        try:
            print("🧹 Finalizando aplicação (salvando estado e desconectando)...")
            try:
                mongo.disconnect()
            except Exception:
                pass
            # Fecha janela do arcade caso esteja rodando
            try:
                arcade.close_window()
            except Exception:
                pass
            # saída do processo
            sys.exit(0)
        except SystemExit:
            raise
        except Exception:
            os._exit(0)

    register_signal_handlers(terminate)

    # Inicia o jogo (Arcade)
    print("🎮 Iniciando Dungeons of Questions (janela do jogo)...")
    try:
        game = RPGGame()
        arcade.run()
    except Exception as e:
        print(f"❌ Erro crítico no jogo: {e}")
    finally:
        # Certifica-se de desconectar do Mongo e encerrar
        try:
            mongo.disconnect()
        except Exception:
            pass
        print("👋 Aplicação encerrada")


if __name__ == "__main__":
    main()
