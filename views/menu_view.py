import os
import requests
import arcade
from typing import List, Optional
import tempfile
import threading

from arcade import color as arcade_color

from config import SCREEN_WIDTH, SCREEN_HEIGHT, MENU_BACKGROUND, BUTTON_FONT, get_avatar_by_username, get_random_avatar, CRYSTAL_IMAGE
from views.rpg_button import RPGButton
from views.game_view import GameView
from assets.xp.xp import XPBar
from auth.simple_auth import auth_system
from views.profile_view import ProfileView

BASE_API_URL = "http://127.0.0.1:8000/api"


class MenuView(arcade.View):
    """
    Tela principal que mantém estado persistente entre navegações
    """

    def __init__(self, username: str = "Jogador", avatar_path: Optional[str] = None):
        super().__init__()
        
        # Salva referência na window para reutilização
        self.window.menu_view = self
        
        # Estado do usuário
        self._original_username = username
        self._original_avatar_path = avatar_path
        
        self.player_id = username
        self.avatar_path = avatar_path
        self.avatar_texture = None
        self.avatar_sprite = None
        self.crystal_sprite = None
        self.crystal_list = None
        self.session_id = ""
        self.xp_bar: Optional[XPBar] = None
        self.status_message = ""
        self.status_timer = 0.0
        self.user_data = None
        self.loading_avatar = False
        self.avatar_temp_file = None

        # UI Components
        self.background = arcade.SpriteList()
        self.buttons: List[RPGButton] = []
        
        # Avatar
        self.avatar_button = {
            "x": 120,
            "y": SCREEN_HEIGHT - 120,
            "radius": 40,
            "hovered": False
        }

        # Text elements
        self.title_shadow = None
        self.menu_title = None
        self.id_text = None
        self.level_text = None
        self.welcome_text = None
        self.stats_text = None
        self.footer_text = None

        # Inicialização
        self._initialize_user_data()
        self._load_crystal_image()
        self._setup_ui()
        self._load_session_silently()
        
        print(f"🎮 MenuView criado para: {self._original_username}")

    def _initialize_user_data(self):
        """Inicializa dados do usuário uma única vez"""
        if self._original_username != "Jogador":
            self.user_data = auth_system.get_user_data(self._original_username)
            if self.user_data and not self._original_avatar_path:
                self.avatar_path = self.user_data.get("avatar_path")

        # Se não tem avatar, busca um automaticamente
        if not self.avatar_path:
            if self._original_username != "Jogador":
                self.avatar_path = get_avatar_by_username(self._original_username)
            else:
                self.avatar_path = get_random_avatar()
            
            print(f"🎨 Avatar automático selecionado: {self.avatar_path}")

        # Carrega avatar
        self._load_avatar()

    def _load_crystal_image(self):
        """Carrega a imagem do cristal para a barra de XP"""
        try:
            if os.path.exists(CRYSTAL_IMAGE):
                # Criar sprite do cristal em uma SpriteList (MÉTODO CORRETO)
                self.crystal_sprite = arcade.Sprite(CRYSTAL_IMAGE, scale=0.08)  # Bem pequeno
                self.crystal_list = arcade.SpriteList()
                self.crystal_list.append(self.crystal_sprite)
                print(f"✅ Cristal carregado: {CRYSTAL_IMAGE}")
            else:
                print(f"❌ Cristal não encontrado: {CRYSTAL_IMAGE}")
                self.crystal_sprite = None
                self.crystal_list = None
        except Exception as e:
            print(f"❌ Erro ao carregar cristal: {e}")
            self.crystal_sprite = None
            self.crystal_list = None

    def _load_avatar(self):
        """Carrega o avatar (suporte a URLs e arquivos locais)"""
        if not self.avatar_path:
            self._load_fallback_avatar()
            return

        if self.avatar_path.startswith('http'):
            self.loading_avatar = True
            threading.Thread(target=self._download_avatar, daemon=True).start()
        else:
            self._load_local_avatar()

    def _download_avatar(self):
        """Baixa avatar de URL em thread separada"""
        try:
            print(f"⬇️ Baixando avatar de: {self.avatar_path}")
            response = requests.get(self.avatar_path, timeout=10)
            if response.status_code == 200:
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                temp_file.write(response.content)
                temp_file.close()
                self.avatar_temp_file = temp_file.name
                
                print(f"✅ Avatar baixado: {self.avatar_temp_file}")
                arcade.schedule(self._load_downloaded_avatar, 0)
            else:
                print(f"❌ Status code {response.status_code} ao baixar avatar")
                arcade.schedule(lambda dt: self._load_fallback_avatar(), 0)
                
        except Exception as e:
            print(f"❌ Erro ao baixar avatar: {e}")
            arcade.schedule(lambda dt: self._load_fallback_avatar(), 0)

    def _load_downloaded_avatar(self, dt):
        """Carrega avatar baixado (thread principal)"""
        try:
            if self.avatar_temp_file and os.path.exists(self.avatar_temp_file):
                self.avatar_texture = arcade.load_texture(self.avatar_temp_file)
                self._create_avatar_sprite()
                self.loading_avatar = False
                print(f"✅ Avatar carregado do arquivo temporário: {self.avatar_temp_file}")
            else:
                raise Exception("Arquivo temporário não encontrado")
        except Exception as e:
            print(f"❌ Erro ao carregar avatar baixado: {e}")
            self._load_fallback_avatar()

    def _load_local_avatar(self):
        """Carrega avatar de arquivo local"""
        try:
            if os.path.exists(self.avatar_path):
                self.avatar_texture = arcade.load_texture(self.avatar_path)
                self._create_avatar_sprite()
                print(f"✅ Avatar local carregado: {self.avatar_path}")
            else:
                # Tenta encontrar o arquivo em locais alternativos
                possible_paths = [
                    self.avatar_path,
                    os.path.join("assets", "avatars", os.path.basename(self.avatar_path)),
                    os.path.join(os.path.dirname(__file__), "..", "assets", "avatars", os.path.basename(self.avatar_path)),
                ]
                
                found = False
                for path in possible_paths:
                    if os.path.exists(path):
                        self.avatar_texture = arcade.load_texture(path)
                        self._create_avatar_sprite()
                        print(f"✅ Avatar encontrado em: {path}")
                        found = True
                        break
                
                if not found:
                    raise FileNotFoundError(f"Avatar não encontrado em nenhum local: {possible_paths}")
                    
        except Exception as e:
            print(f"❌ Erro ao carregar avatar local: {e}")
            self._load_fallback_avatar()

    def _create_avatar_sprite(self):
        """Cria um sprite para o avatar PERFEITAMENTE redondo e sem distorção"""
        if self.avatar_texture:
            try:
                # Método CORRETO para avatar redondo
                self.avatar_sprite = arcade.Sprite()
                self.avatar_sprite.texture = self.avatar_texture
                
                # Calcular escala para manter proporção e caber no círculo
                texture = self.avatar_texture
                target_size = 68  # Tamanho do círculo interno
                
                # Manter proporção da imagem
                scale_x = target_size / texture.width
                scale_y = target_size / texture.height
                scale = min(scale_x, scale_y)  # Usar o menor para não distorcer
                
                self.avatar_sprite.scale = scale
                self.avatar_sprite.center_x = self.avatar_button["x"]
                self.avatar_sprite.center_y = self.avatar_button["y"]
                
                print(f"✅ Avatar configurado: {texture.width}x{texture.height} -> escala {scale:.2f}")
                
            except Exception as e:
                print(f"❌ Erro ao criar avatar sprite: {e}")
                self.avatar_sprite = None

    def _load_fallback_avatar(self):
        """Carrega avatar fallback"""
        try:
            fallback_paths = [
                os.path.join(os.path.dirname(__file__), "..", "assets", "avatars", "default.png"),
                os.path.join(os.path.dirname(__file__), "..", "assets", "ui", "Emilly.png"),
                os.path.join(os.path.dirname(__file__), "..", "assets", "ui", "cristal.png"),
            ]
            
            for fallback_path in fallback_paths:
                if os.path.exists(fallback_path):
                    self.avatar_texture = arcade.load_texture(fallback_path)
                    self._create_avatar_sprite()
                    print(f"✅ Avatar fallback carregado: {fallback_path}")
                    break
            else:
                self.avatar_texture = None
                self.avatar_sprite = None
                
            self.loading_avatar = False
        except Exception as e:
            print(f"❌ Erro ao carregar fallback: {e}")
            self.avatar_texture = None
            self.avatar_sprite = None
            self.loading_avatar = False

    def refresh_user_data(self):
        """Atualiza dados do usuário quando volta de outras views"""
        print(f"🔄 Atualizando dados do usuário: {self._original_username}")
        
        if self._original_username != "Jogador":
            fresh_data = auth_system.get_user_data(self._original_username)
            if fresh_data:
                self.user_data = fresh_data
                
                if self.xp_bar:
                    user_xp = self.user_data.get("xp", 0)
                    user_level = self.user_data.get("level", 1)
                    
                    self.xp_bar.current_xp = user_xp
                    self.xp_bar.level = user_level
                    
                    self._update_text_elements()
                    
                    print(f"✅ Dados atualizados: Nível {user_level}, XP {user_xp}/{self.xp_bar.max_xp}")

    def _update_text_elements(self):
        """Atualiza os elementos de texto com dados atuais"""
        if self.xp_bar:
            if self.level_text:
                self.level_text.text = f"LEVEL {self.xp_bar.level}"
            
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
        # Background
        try:
            if os.path.exists(MENU_BACKGROUND):
                bg = arcade.Sprite(MENU_BACKGROUND, scale=1.0)
                bg.center_x = SCREEN_WIDTH / 2
                bg.center_y = SCREEN_HEIGHT / 2
                bg.width = SCREEN_WIDTH
                bg.height = SCREEN_HEIGHT
                self.background.append(bg)
                print(f"✅ Background carregado: {MENU_BACKGROUND}")
            else:
                print(f"❌ Background não encontrado: {MENU_BACKGROUND}")
                raise FileNotFoundError()
        except Exception as e:
            print(f"❌ Erro ao carregar background: {e}")
            pass

        # Título com sombra
        txt = "DUNGEONS OF QUESTIONS"
        self.title_shadow = arcade.Text(
            txt,
            SCREEN_WIDTH/2 + 3, SCREEN_HEIGHT - 83,
            arcade_color.DARK_RED, 42,
            font_name=BUTTON_FONT,
            anchor_x="center", anchor_y="top", bold=True
        )
        self.menu_title = arcade.Text(
            txt,
            SCREEN_WIDTH/2, SCREEN_HEIGHT - 80,
            arcade_color.GOLD, 42,
            font_name=BUTTON_FONT,
            anchor_x="center", anchor_y="top", bold=True
        )

        # ID do jogador (TOP ESQUERDA)
        nome_exibicao = self.user_data.get("nome", self.player_id) if self.user_data else self.player_id
        self.id_text = arcade.Text(
            f"Jogador: {nome_exibicao}",
            40, SCREEN_HEIGHT - 40,
            arcade_color.WHITE, 18,
            font_name="Arial", bold=True
        )

        # Nível do jogador (EMBAIXO DO NOME)
        nivel = self.user_data.get("level", 1) if self.user_data else 1
        self.level_text = arcade.Text(
            f"LEVEL {nivel}",
            40, SCREEN_HEIGHT - 70,
            arcade_color.GOLD, 16,
            font_name="Arial", bold=True
        )

        # Textos de boas-vindas
        nome = self.user_data.get("nome", self.player_id) if self.user_data else self.player_id
        self.welcome_text = arcade.Text(
            f"Bem-vindo, {nome}!",
            SCREEN_WIDTH/2, SCREEN_HEIGHT - 180,
            arcade_color.LIGHT_BLUE, 18,
            anchor_x="center", bold=True
        )
        
        self.stats_text = arcade.Text(
            f"Nível {nivel} • {self.user_data.get('xp', 0) if self.user_data else 0} XP",
            SCREEN_WIDTH/2, SCREEN_HEIGHT - 210,
            arcade_color.LIGHT_GREEN, 14,
            anchor_x="center"
        )

        # Rodapé ATUALIZADO
        self.footer_text = arcade.Text(
            "ESC: Sair  •  C/ENTER: Campanha  •  O: Opções • P/Clique Avatar: Perfil",
            SCREEN_WIDTH/2, 30,
            arcade_color.LIGHT_GRAY, 10,
            anchor_x="center"
        )

        # Botões principais - TODOS DO MESMO TAMANHO NA DIREITA
        button_width = 220
        button_height = 50
        button_spacing = 70
        start_y = SCREEN_HEIGHT / 2 + 80
        
        self.buttons = [
            RPGButton("CAMPAIGN", SCREEN_WIDTH - 150, start_y, width=button_width, height=button_height),
            RPGButton("OPTIONS", SCREEN_WIDTH - 150, start_y - (button_spacing * 1), width=button_width, height=button_height),
            RPGButton("SAIR", SCREEN_WIDTH - 150, start_y - (button_spacing * 2), width=button_width, height=button_height),
        ]

    def _load_session_silently(self):
        """Carrega sessão integrando dados do sistema de autenticação"""
        try:
            resp = requests.post(
                f"{BASE_API_URL}/launch",
                json={"player": self.player_id},
                timeout=2
            )
            resp.raise_for_status()
            data = resp.json()
            self.session_id = data["session_id"]
            current_xp = data.get("xp", 0)
            level = data.get("level", 1)
            
            # Barra de XP PEQUENA EMBAIXO NA ESQUERDA
            self.xp_bar = XPBar(
                current_xp=current_xp,
                level=level,
                center_x=180,  # Mais para a esquerda
                center_y=80,   # Embaixo
                width=250,     # Menor
                height=16      # Mais fina
            )
            
        except Exception as e:
            print(f"❌ Falha em /launch: {e}")
            self._load_from_auth_system()

    def _load_from_auth_system(self):
        """Carrega dados do sistema de autenticação como fallback"""
        if self.user_data:
            user_xp = self.user_data.get("xp", 0)
            user_level = self.user_data.get("level", 1)
            
            self.xp_bar = XPBar(
                current_xp=user_xp,
                level=user_level,
                center_x=180,
                center_y=80,
                width=250,
                height=16
            )
        else:
            self.xp_bar = XPBar(
                current_xp=0,
                level=1,
                center_x=180,
                center_y=80,
                width=250,
                height=16
            )

    def save_user_progress(self):
        """Salva progresso do usuário no sistema de autenticação"""
        if self.user_data and self.xp_bar:
            try:
                self.user_data["xp"] = self.xp_bar.current_xp
                self.user_data["level"] = self.xp_bar.level
                
                auth_system.save_users()
                print(f"✅ Progresso salvo: {self.player_id} - Nível {self.xp_bar.level}")
                
            except Exception as e:
                print(f"❌ Erro ao salvar progresso: {e}")

    def on_show(self):
        """Chamado quando a view é mostrada"""
        print(f"🔄 MenuView mostrado para: {self._original_username}")
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
                arcade_color.DARK_SLATE_BLUE
            )

        # Overlay escura
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 0, 150)
        )

        # Avatar (TOP ESQUERDA)
        ax, ay = self.avatar_button["x"], self.avatar_button["y"]
        hovered = self.avatar_button["hovered"]
        circle_col = arcade_color.GOLD if hovered else arcade_color.DARK_BLUE_GRAY

        # Círculo do avatar PERFEITAMENTE REDONDO
        arcade.draw_circle_filled(ax, ay, 40, circle_col)
        arcade.draw_circle_filled(ax, ay, 38, arcade_color.DARK_BLUE_GRAY)
        arcade.draw_circle_filled(ax, ay, 34, arcade_color.LIGHT_GRAY)

        # Imagem do avatar - MÉTODO DEFINITIVO
        if self.avatar_sprite and self.avatar_texture:
            try:
                # Método universal: usar SpriteList
                sprite_list = arcade.SpriteList()
                sprite_list.append(self.avatar_sprite)
                sprite_list.draw()
            except Exception as e:
                print(f"❌ Erro ao desenhar avatar: {e}")
                arcade.draw_text("👤", ax, ay, arcade_color.DARK_BLUE, 24,
                               anchor_x="center", anchor_y="center", bold=True)
        elif self.loading_avatar:
            arcade.draw_text("⏳", ax, ay, arcade_color.WHITE, 20,
                           anchor_x="center", anchor_y="center", bold=True)
        else:
            arcade.draw_text("👤", ax, ay, arcade_color.DARK_BLUE, 24,
                           anchor_x="center", anchor_y="center", bold=True)

        # Borda do avatar
        border = arcade_color.WHITE if hovered else arcade_color.GOLD
        arcade.draw_circle_outline(ax, ay, 40, border, 3)
        arcade.draw_circle_outline(ax, ay, 38, arcade_color.ORANGE, 1)

        # Tooltip no hover ATUALIZADO
        if hovered and self.xp_bar:
            arcade.draw_text(
                f"Clique para ver perfil\nNv.{self.xp_bar.level} - {self.xp_bar.current_xp}/{self.xp_bar.max_xp} XP", 
                ax, ay - 65, 
                arcade_color.WHITE, 10,
                anchor_x="center", bold=True,
                multiline=True, width=150
            )

        # Desenha textos
        self.title_shadow.draw()
        self.menu_title.draw()
        self.id_text.draw()
        self.level_text.draw()
        self.welcome_text.draw()
        self.stats_text.draw()
        self.footer_text.draw()

        # Desenha botões
        for btn in self.buttons:
            btn.draw()

        # Barra de XP com cristal - EMBAIXO NA ESQUERDA
        if self.xp_bar:
            # Desenha cristal pequeno no início da barra (MÉTODO CORRETO)
            if self.crystal_list and self.crystal_sprite:
                crystal_x = self.xp_bar.center_x - self.xp_bar.width//2 - 20
                crystal_y = self.xp_bar.center_y
                self.crystal_sprite.center_x = crystal_x
                self.crystal_sprite.center_y = crystal_y
                self.crystal_list.draw()
            
            self.xp_bar.draw()

        # Mensagem de status temporária
        if self.status_message and self.status_timer > 0:
            arcade.draw_text(
                self.status_message,
                SCREEN_WIDTH/2, 120,
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
        # Clique no avatar - ABRE O PERFIL
        ax, ay = self.avatar_button["x"], self.avatar_button["y"]
        if ((x - ax)**2 + (y - ay)**2)**0.5 <= self.avatar_button["radius"]:
            # Salva progresso antes de abrir o perfil
            self.save_user_progress()
            
            # Cria e mostra a tela de perfil
            profile_view = ProfileView()
            self.window.show_view(profile_view)
            return

        # Clique nos botões
        for btn in self.buttons:
            if btn.check_click(x, y):
                if btn.label == "CAMPAIGN":
                    self._start_campaign()
                elif btn.label == "MUNDO ABERTO":  # NOVO BOTÃO
                    self._start_open_world()
                elif btn.label == "OPTIONS":
                    self.window.show_view(OptionsView(self))
                elif btn.label == "SAIR":
                    self._sair()
                return

    def on_key_press(self, key, modifiers):
        """Teclas de atalho"""
        if key in (arcade.key.C, arcade.key.ENTER):
            self._start_campaign()
        elif key == arcade.key.M:  # NOVO ATALHO
            self._start_open_world()
        elif key == arcade.key.O:
            self.window.show_view(OptionsView(self))
        elif key == arcade.key.P:
            # Tecla P agora abre o perfil (em vez de mostrar status)
            self.save_user_progress()
            profile_view = ProfileView()
            self.window.show_view(profile_view)
        elif key == arcade.key.ESCAPE:
            self._sair()

    def _sair(self):
        """Salva progresso antes de sair"""
        self.save_user_progress()
        if self.avatar_temp_file and os.path.exists(self.avatar_temp_file):
            try:
                os.unlink(self.avatar_temp_file)
            except:
                pass
        print(f"👋 Saindo do jogo... Até logo, {self.player_id}!")
        arcade.exit()

    def _start_campaign(self):
        """Inicia a GameView"""
        try:
            self.set_status("🚀 Iniciando campanha...")
            self.save_user_progress()
            
            game_view = GameView(
                xp_bar=self.xp_bar,
                session_id=self.session_id,
                on_exit_callback=self.save_user_progress
            )
            
            game_view.previous_menu = self
            game_view.setup()
            self.window.show_view(game_view)
            
            print(f"🎯 Campanha iniciada para: {self._original_username}")
            
        except Exception as e:
            self.set_status("❌ Erro ao iniciar campanha")
            print(f"Erro em _start_campaign: {e}")

    def _start_open_world(self):
        """Inicia o mundo aberto"""
        try:
            self.set_status("🌍 Iniciando mundo aberto...")
            self.save_user_progress()
            
            
            
            
            
            print(f"🌍 Mundo aberto iniciado para: {self._original_username}")
            
        except Exception as e:
            self.set_status("❌ Erro ao iniciar mundo aberto")
            print(f"Erro em _start_open_world: {e}")


class OptionsView(arcade.View):
    """Tela de opções"""

    def __init__(self, parent: MenuView):
        super().__init__()
        self.parent = parent

    def on_draw(self):
        self.clear()
        
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
            print("↩️ Voltando para o menu principal...")
            self.window.show_view(self.parent)