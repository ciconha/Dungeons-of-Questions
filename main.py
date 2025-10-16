#!/usr/bin/env python3

import os
import sys
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


# 🔥 VERIFICAÇÃO DE COMPATIBILIDADE DO ARCADE
def check_arcade_version():
    """Verifica se a versão do Arcade é compatível"""
    try:
        arcade_version = arcade.__version__
        print(f"🎯 Arcade Version: {arcade_version}")
        
        # Versões muito antigas não têm Camera
        if arcade_version.startswith('2.') or arcade_version.startswith('1.'):
            print("⚠️  Versão antiga do Arcade detectada - Usando modo compatível")
            return False
        else:
            print("✅ Versão moderna do Arcade - Recursos completos disponíveis")
            return True
            
    except AttributeError:
        print("⚠️  Não foi possível detectar versão do Arcade - Usando modo compatível")
        return False


class RPGGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        # 🔥 CONFIGURAÇÃO COMPATÍVEL
        self.set_fullscreen(False)
        
        # Verifica compatibilidade
        self.modern_arcade = check_arcade_version()
        
        # Começa com a tela de login
        self.show_view(LoginView())

    def on_key_press(self, key, modifiers):
        # Atalho de fullscreen global
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
        
        # Encaminha evento para a view atual
        current_view = getattr(self, 'view', None)
        if current_view and hasattr(current_view, "on_key_press"):
            current_view.on_key_press(key, modifiers)
    
    def on_resize(self, width, height):
        """Lida com redimensionamento da janela"""
        super().on_resize(width, height)
        
        # Notifica a view atual sobre o redimensionamento
        current_view = getattr(self, 'view', None)
        if current_view and hasattr(current_view, "on_resize"):
            current_view.on_resize(width, height)


def start_fastapi():
    """Inicia a API FastAPI em background"""
    try:
        uvicorn.run(
            fastapi_app,
            host="127.0.0.1",
            port=8000,
            log_level="error",
            access_log=False,
        )
    except Exception as e:
        print(f"❌ Erro na API FastAPI: {e}")


def silent_health_check() -> bool:
    """Verifica silenciosamente se a API está no ar"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def setup_environment():
    """Configura o ambiente antes de iniciar o jogo"""
    # Força X11 no Wayland (Linux)
    if sys.platform == "linux":
        os.environ["SDL_VIDEODRIVER"] = "x11"
    
    # Otimizações de performance
    os.environ["ARCADE_HEADLESS"] = "0"
    
    print("🔧 Configurando ambiente...")


def main():
    # 1) Configura ambiente
    setup_environment()
    
    # 2) Conecta no MongoDB
    print("🔌 Conectando ao MongoDB...")
    if not mongo.connect():
        print("❌ Falha crítica: Não foi possível conectar ao MongoDB")
        return

    # 3) Popula perguntas (seed)
    print("🌱 Executando seed do banco de dados...")
    try:
        seed.run()
        print("✅ Seed executado com sucesso")
    except Exception as e:
        print(f"⚠️  Aviso no seed: {e}")

    # 4) Inicia a API em thread background
    print("🚀 Iniciando API FastAPI...")
    api_thread = threading.Thread(target=start_fastapi, daemon=True)
    api_thread.start()

    # 5) Health check da API
    print("🔍 Verificando saúde da API...")
    time.sleep(2.0)  # Dá mais tempo para a API iniciar
    
    if not silent_health_check():
        print("⚠️  API não respondeu - Continuando sem API...")
    else:
        print("✅ API respondendo corretamente")

    # 6) Cria e inicia o jogo
    print("🎮 Iniciando Dungeons of Questions...")
    try:
        game = RPGGame()
        
        # 7) Abre docs do FastAPI (opcional)
        def open_docs():
            time.sleep(3.0)
            try:
                webbrowser.open("http://127.0.0.1:8000/docs")
                print("📚 Docs abertos no navegador")
            except:
                print("⚠️  Não foi possível abrir os docs automaticamente")
        
        docs_thread = threading.Thread(target=open_docs, daemon=True)
        docs_thread.start()
        
        # 8) Loop principal do Arcade
        arcade.run()
        
    except Exception as e:
        print(f"❌ Erro crítico no jogo: {e}")
    
    finally:
        # 9) Limpeza final
        print("🧹 Finalizando aplicação...")
        mongo.disconnect()
        print("👋 Aplicação encerrada")


if __name__ == "__main__":
    main()