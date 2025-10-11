# views/menu_view.py (COMPLETO E CORRIGIDO)

import os
import requests
import arcade
from typing import List, Optional

from arcade import color as arcade_color

from config import SCREEN_WIDTH, SCREEN_HEIGHT, MENU_BACKGROUND, BUTTON_FONT
from views.rpg_button import RPGButton
from views.game_view import GameView
from assets.xp.xp import XPBar
from auth.simple_auth import auth_system

BASE_API_URL = "http://127.0.0.1:8000/api"


class MenuView(arcade.View):
    """
    Tela principal que mantém estado persistente entre navegações
    """

    def __init__(self, username: str = "Jogador", avatar_path: Optional[str] = None):
        super().__init__()
        
        # Estado do usuário
        self._original_username = username
        self._original_avatar_path = avatar_path
        
        self.player_id = username
        self.avatar_path = avatar_path
        self.avatar_texture = None
        self.avatar_sprite = None
        self.session_id = ""
        self.xp_bar: Optional[XPBar] = None
        self.status_message = ""
        self.status_timer = 0.0
        self.user_data = None

        # UI Components
        self.background = arcade.SpriteList()
        self.buttons: List[RPGButton] = []
        
        # Avatar como sprite para melhor performance
        self.avatar_button = {
            "x": 60,
            "y": SCREEN_HEIGHT - 60,
            "radius": 40,
            "hovered": False
        }

        # Text elements como objetos Text para melhor performance
        self.title_shadow = None
        self.menu_title = None
        self.id_text = None
        self.level_text = None
        self.xp_text = None
        self.welcome_text = None
        self.stats_text = None
        self.footer_text = None

        # Inicialização
        self._initialize_user_data()
        self._setup_ui()
        self._load_session_silently()
        
        print(f"🎮 MenuView criado para: {self._original_username}")

    def _initialize_user_data(self):
        """Inicializa dados do usuário uma única vez"""
        if self._original_username != "Jogador":
            self.user_data = auth_system.get_user_data(self._original_username)
            if self.user_data and not self._original_avatar_path:
                self.avatar_path = self.user_data.get("avatar_path")

        # Carrega avatar se existir
        if self.avatar_path and os.path.exists(self.avatar_path):
            try:
                self.avatar_texture = arcade.load_texture(self.avatar_path)
                # Cria sprite do avatar para melhor performance
                self.avatar_sprite = arcade.Sprite(self.avatar_path, scale=0.15)
                self.avatar_sprite.center_x = self.avatar_button["x"]
                self.avatar_sprite.center_y = self.avatar_button["y"]
            except Exception as e:
                print(f"❌ Erro ao carregar avatar: {e}")
                self.avatar_texture = None
                self.avatar_sprite = None

    def refresh_user_data(self):
        """Atualiza dados do usuário quando volta de outras views"""
        print(f"🔄 Atualizando dados do usuário: {self._original_username}")
        
        if self._original_username != "Jogador":
            # Recarrega dados do arquivo
            fresh_data = auth_system.get_user_data(self._original_username)
            if fresh_data:
                self.user_data = fresh_data
                
                if self.xp_bar:
                    # Atualiza XP bar com dados mais recentes
                    user_xp = self.user_data.get("xp", 0)
                    user_level = self.user_data.get("level", 1)
                    max_xp = user_level * 100
                    
                    self.xp_bar.current_xp = user_xp
                    self.xp_bar.level = user_level
                    self.xp_bar.max_xp = max_xp
                    
                    # Atualiza textos
                    self._update_text_elements()
                    
                    print(f"✅ Dados atualizados: Nível {user_level}, XP {user_xp}/{max_xp}")

    def _update_text_elements(self):
        """Atualiza os elementos de texto com dados atuais"""
        if self.xp_bar:
            # Atualiza textos de nível e XP
            if self.level_text:
                self.level_text.text = f"LEVEL {self.xp_bar.level}"
            if self.xp_text:
                self.xp_text.text = f"{self.xp_bar.current_xp}/{self.xp_bar.max_xp} XP"
            
            # Atualiza texto de boas-vindas
            if self.user_data and self.welcome_text:
                nome = self.user_data.get("nome", self.player_id)
                nivel = self.user_data.get("level", 1)
                xp = self.user_data.get("xp", 0)
                self.welcome_text.text = f"Bem-vindo, {nome}!"
                self.stats_text.text = f"Nível {nivel} • {xp} XP"

    def set_status(self, message: str, duration: float = 2.0):
        """Define mensagem de status temporária."""
        self.status_message = message
        self.status_timer = duration

    def _setup_ui(self):
        """Monta background, título, ID e botões."""
        # Background full screen
        try:
            bg = arcade.Sprite(MENU_BACKGROUND, scale=1.0)
            bg.center_x = SCREEN_WIDTH / 2
            bg.center_y = SCREEN_HEIGHT / 2
            bg.width = SCREEN_WIDTH
            bg.height = SCREEN_HEIGHT
            self.background.append(bg)
        except Exception:
            # Fallback para background simples
            pass

        # Título com sombra (usando objetos Text para performance)
        txt = "DUNGEONS OF QUESTIONS"
        self.title_shadow = arcade.Text(
            txt,
            SCREEN_WIDTH/2 + 3, SCREEN_HEIGHT - 123,
            arcade_color.DARK_RED, 42,
            font_name=BUTTON_FONT,
            anchor_x="center", anchor_y="top", bold=True
        )
        self.menu_title = arcade.Text(
            txt,
            SCREEN_WIDTH/2, SCREEN_HEIGHT - 120,
            arcade_color.GOLD, 42,
            font_name=BUTTON_FONT,
            anchor_x="center", anchor_y="top", bold=True
        )

        # ID do jogador
        nome_exibicao = self.user_data.get("nome", self.player_id) if self.user_data else self.player_id
        self.id_text = arcade.Text(
            f"Jogador: {nome_exibicao}",
            120, SCREEN_HEIGHT - 60,
            arcade_color.WHITE, 16,
            font_name="Arial", bold=True
        )

        # Textos de nível e XP
        nivel = self.user_data.get("level", 1) if self.user_data else 1
        xp = self.user_data.get("xp", 0) if self.user_data else 0
        max_xp = nivel * 100
        
        self.level_text = arcade.Text(
            f"LEVEL {nivel}",
            120, 60,
            arcade_color.GOLD, 14,
            anchor_x="center", bold=True
        )
        
        self.xp_text = arcade.Text(
            f"{xp}/{max_xp} XP",
            120, 45,
            arcade_color.LIGHT_BLUE, 10,
            anchor_x="center"
        )

        # Textos de boas-vindas
        nome = self.user_data.get("nome", self.player_id) if self.user_data else self.player_id
        self.welcome_text = arcade.Text(
            f"Bem-vindo, {nome}!",
            SCREEN_WIDTH/2, SCREEN_HEIGHT - 180,
            arcade_color.LIGHT_BLUE, 16,
            anchor_x="center", bold=True
        )
        
        self.stats_text = arcade.Text(
            f"Nível {nivel} • {xp} XP",
            SCREEN_WIDTH/2, SCREEN_HEIGHT - 200,
            arcade_color.LIGHT_GREEN, 14,
            anchor_x="center"
        )

        # Rodapé
        self.footer_text = arcade.Text(
            "ESC: Sair  •  C/ENTER: Campanha  •  O: Opções • P: Perfil",
            SCREEN_WIDTH/2, 30,
            arcade_color.LIGHT_GRAY, 10,
            anchor_x="center"
        )

        # Botões principais
        cy = SCREEN_HEIGHT / 2
        self.buttons = [
            RPGButton("CAMPAIGN", SCREEN_WIDTH/2, cy + 60, width=280, height=60),
            RPGButton("OPTIONS", SCREEN_WIDTH/2, cy - 20, width=240, height=50),
            RPGButton("SAIR", SCREEN_WIDTH/2, cy - 100, width=200, height=45),
        ]

    def _load_session_silently(self):
        """
        Carrega sessão integrando dados do sistema de autenticação
        """
        try:
            # Primeiro tenta carregar da API
            resp = requests.post(
                f"{BASE_API_URL}/launch",
                json={"player": self.player_id},
                timeout=2
            )
            resp.raise_for_status()
            data = resp.json()
            self.session_id = data["session_id"]
            current_xp = data.get("xp", 0)
            max_xp = data.get("max_xp", 100)
            
            # Cria barra de XP com dados da API
            self.xp_bar = XPBar(
                current_xp=current_xp,
                max_xp=max_xp,
                center_x=120,
                center_y=40,
                width=200,
                height=16
            )
            
        except Exception as e:
            print(f"❌ Falha em /launch: {e}")
            # Fallback: usa dados do sistema de autenticação
            self._load_from_auth_system()

    def _load_from_auth_system(self):
        """Carrega dados do sistema de autenticação como fallback"""
        if self.user_data:
            user_xp = self.user_data.get("xp", 0)
            user_level = self.user_data.get("level", 1)
            max_xp = user_level * 100  # Progressão linear
            
            self.xp_bar = XPBar(
                current_xp=user_xp,
                level=user_level,
                max_xp=max_xp,
                center_x=120,
                center_y=40,
                width=200,
                height=16
            )
        else:
            # Fallback final
            self.xp_bar = XPBar(
                current_xp=0,
                level=1,
                max_xp=100,
                center_x=120,
                center_y=40,
                width=200,
                height=16
            )

    def save_user_progress(self):
        """Salva progresso do usuário no sistema de autenticação"""
        if self.user_data and self.xp_bar:
            try:
                # Atualiza dados locais
                self.user_data["xp"] = self.xp_bar.current_xp
                self.user_data["level"] = self.xp_bar.level
                
                # Salva no arquivo
                auth_system.save_users()
                print(f"✅ Progresso salvo: {self.player_id} - Nível {self.xp_bar.level}")
                
            except Exception as e:
                print(f"❌ Erro ao salvar progresso: {e}")

    def on_show(self):
        """Chamado quando a view é mostrada (quando volta do GameView)"""
        print(f"🔄 MenuView mostrado para: {self._original_username}")
        # Atualiza dados do usuário quando volta para o menu
        self.refresh_user_data()

    def on_draw(self):
        """Renderiza toda a UI da tela de menu."""
        self.clear()

        # Desenha background
        if self.background:
            self.background.draw()
        else:
            arcade.draw_lrbt_rectangle_filled(
                0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                arcade_color.DARK_BLUE
            )

        # Overlay escura
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 0, 150)
        )

        # Avatar
        ax, ay = self.avatar_button["x"], self.avatar_button["y"]
        hovered = self.avatar_button["hovered"]
        circle_col = arcade_color.GOLD if hovered else arcade_color.DARK_BLUE_GRAY

        # Círculo do avatar
        arcade.draw_circle_filled(ax, ay, 40, circle_col)
        arcade.draw_circle_filled(ax, ay, 38, arcade_color.DARK_BLUE_GRAY)
        arcade.draw_circle_filled(ax, ay, 34, arcade_color.LIGHT_GRAY)

        # Imagem do avatar ou fallback
        if self.avatar_sprite:
            self.avatar_sprite.draw()
        else:
            arcade.draw_text("👤", ax, ay, arcade_color.DARK_BLUE, 24,
                           anchor_x="center", anchor_y="center", bold=True)

        # Borda do avatar
        border = arcade_color.WHITE if hovered else arcade_color.GOLD
        arcade.draw_circle_outline(ax, ay, 40, border, 3)
        arcade.draw_circle_outline(ax, ay, 38, arcade_color.ORANGE, 1)

        # Tooltip no hover
        if hovered and self.xp_bar:
            arcade.draw_text(
                f"Nv.{self.xp_bar.level} - {self.xp_bar.current_xp}/{self.xp_bar.max_xp} XP", 
                ax, ay - 55, 
                arcade_color.WHITE, 10,
                anchor_x="center", bold=True
            )

        # Desenha textos (agora usando objetos Text para performance)
        self.title_shadow.draw()
        self.menu_title.draw()
        self.id_text.draw()
        self.level_text.draw()
        self.xp_text.draw()
        self.welcome_text.draw()
        self.stats_text.draw()
        self.footer_text.draw()

        # Desenha botões
        for btn in self.buttons:
            btn.draw()

        # Barra de XP
        if self.xp_bar:
            self.xp_bar.draw()

        # Mensagem de status temporária
        if self.status_message and self.status_timer > 0:
            arcade.draw_text(
                self.status_message,
                SCREEN_WIDTH/2, 100,
                arcade_color.YELLOW, 14,
                anchor_x="center", bold=True
            )

    def on_update(self, delta_time: float):
        """Atualiza temporizador da mensagem de status."""
        if self.status_timer > 0:
            self.status_timer -= delta_time
            if self.status_timer <= 0:
                self.status_message = ""

    def on_mouse_motion(self, x, y, dx, dy):
        """Detecta hover em botões e avatar."""
        for btn in self.buttons:
            btn.texture_index = 1 if btn.check_hover(x, y) else 0

        ax, ay = self.avatar_button["x"], self.avatar_button["y"]
        dist = ((x - ax)**2 + (y - ay)**2)**0.5
        self.avatar_button["hovered"] = dist <= self.avatar_button["radius"]

    def on_mouse_press(self, x, y, button, modifiers):
        """Trata clique em avatar, botões e navega sem retornar ao menu."""
        # Clique no avatar
        ax, ay = self.avatar_button["x"], self.avatar_button["y"]
        if ((x - ax)**2 + (y - ay)**2)**0.5 <= self.avatar_button["radius"]:
            nivel = self.xp_bar.level if self.xp_bar else 1
            xp_atual = self.xp_bar.current_xp if self.xp_bar else 0
            xp_max = self.xp_bar.max_xp if self.xp_bar else 100
            self.set_status(f"👤 {self.player_id} • Nível {nivel} • XP: {xp_atual}/{xp_max}")
            return

        # Clique nos botões
        for btn in self.buttons:
            if btn.check_click(x, y):
                if btn.label == "CAMPAIGN":
                    self._start_campaign()
                elif btn.label == "OPTIONS":
                    self.window.show_view(OptionsView(self))
                elif btn.label == "SAIR":
                    self._sair()
                return

    def on_key_press(self, key, modifiers):
        """Teclas de atalho sem fallback involuntário."""
        if key in (arcade.key.C, arcade.key.ENTER):
            self._start_campaign()
        elif key == arcade.key.O:
            self.window.show_view(OptionsView(self))
        elif key == arcade.key.P:
            nivel = self.xp_bar.level if self.xp_bar else 1
            xp_atual = self.xp_bar.current_xp if self.xp_bar else 0
            xp_max = self.xp_bar.max_xp if self.xp_bar else 100
            nome = self.user_data.get("nome", self.player_id) if self.user_data else self.player_id
            self.set_status(f"👤 {nome} • Nível {nivel} • XP: {xp_atual}/{xp_max}")
        elif key == arcade.key.ESCAPE:
            self._sair()

    def _sair(self):
        """Salva progresso antes de sair"""
        self.save_user_progress()
        print(f"👋 Saindo do jogo... Até logo, {self.player_id}!")
        arcade.exit()

    def _start_campaign(self):
        """
        Inicia a GameView compartilhando a mesma XP Bar
        """
        try:
            self.set_status("🚀 Iniciando campanha...")
            
            # Salva estado atual antes de iniciar
            self.save_user_progress()
            
            game_view = GameView(
                xp_bar=self.xp_bar,  # MESMA REFERÊNCIA COMPARTILHADA
                session_id=self.session_id,
                on_exit_callback=self.save_user_progress
            )
            
            # CORREÇÃO CRUCIAL: Passa esta instância como referência
            game_view.previous_menu = self
            
            game_view.setup()
            self.window.show_view(game_view)
            
            print(f"🎯 Campanha iniciada para: {self._original_username}")
            
        except Exception as e:
            self.set_status("❌ Erro ao iniciar campanha")
            print(f"Erro em _start_campaign: {e}")


class OptionsView(arcade.View):
    """
    Tela de opções. ESC volta unicamente ao MenuView pai.
    """

    def __init__(self, parent: MenuView):
        super().__init__()
        self.parent = parent

    def on_draw(self):
        self.clear()
        
        # Background similar ao menu
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 50, 200)
        )
        
        arcade.draw_text(
            "OPÇÕES",
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 80,
            arcade_color.GOLD, 48,
            anchor_x="center", anchor_y="center",
            font_name=BUTTON_FONT, bold=True
        )
        
        arcade.draw_text(
            "Configurações em desenvolvimento...",
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
            arcade_color.WHITE, 20,
            anchor_x="center", anchor_y="center"
        )
        
        arcade.draw_text(
            "ESC para voltar ao menu",
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 60,
            arcade_color.LIGHT_GRAY, 16,
            anchor_x="center", anchor_y="center"
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            # Volta apenas para a instância de MenuView original
            print("↩️ Voltando para o menu principal...")
            self.window.show_view(self.parent)