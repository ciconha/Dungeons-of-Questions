# views/login_view.py

import arcade
import os
import tkinter as tk
from tkinter import filedialog
from typing import Dict, List

from config import SCREEN_WIDTH, SCREEN_HEIGHT, MENU_BACKGROUND, BUTTON_FONT, get_avatar_by_username, LOGIN_BACKGROUND, LOGIN_MUSIC
from views.rpg_button import RPGButton
from views.menu_view import MenuView
from auth.simple_auth import auth_system
from auth.user_manager import user_manager


class CharacterSelectionView(arcade.View):
    """Tela de seleção de personagem após o cadastro"""
    
    def __init__(self, username: str, nome: str, senha: str, avatar_path: str = None):
        super().__init__()
        self.username = username
        self.nome = nome
        self.senha = senha
        self.avatar_path = avatar_path
        
        # Lista de personagens disponíveis
        self.characters = [
            {
                "name": "Emily",
                "sprite": "assets/ui/Emilly.png",
                "game_sprite": "assets/characters/Emillywhite.png",  # Sprite para o jogo
                "description": "Aventureira corajosa com poderes mágicos"
            },
        ]
        
        self.selected_character_index = 0
        self.character_texture = None
        self.character_sprite_list = arcade.SpriteList()
        
        self._load_character_texture()
        
        # Botões
        self.buttons = [
            RPGButton("SELECIONAR", SCREEN_WIDTH/10, 150, width=200, height=50),
            RPGButton("VOLTAR", SCREEN_WIDTH/10, 80, width=200, height=50)
        ]

    def _load_character_texture(self):
        """Carrega a textura do personagem selecionado"""
        if self.characters:
            char = self.characters[self.selected_character_index]
            try:
                self.character_texture = arcade.load_texture(char["sprite"])
            except:
                self.character_texture = None

    def on_draw(self):
        self.clear()
        
        # Fundo
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (20, 15, 35)  # Roxo escuro
        )
        
        # Título
        arcade.draw_text(
            "ESCOLHA SEU PERSONAGEM",
            SCREEN_WIDTH, SCREEN_HEIGHT - 100,
            arcade.color.GOLD, 32,
            anchor_x="center", font_name=BUTTON_FONT, bold=True
        )
        
        # Personagem selecionado
        if self.characters:
            char = self.characters[self.selected_character_index]
            
            # Área do personagem
            arcade.draw_lrbt_rectangle_filled(
                SCREEN_WIDTH/2 - 200, SCREEN_WIDTH/2 ,
                SCREEN_HEIGHT/2 - 100, SCREEN_HEIGHT/2,
                (40, 35, 60, 200)
            )
            
            # Sprite do personagem
            if self.character_texture:
                self.character_sprite_list.clear()
                sprite = arcade.Sprite()
                sprite.texture = self.character_texture
                sprite.center_x = SCREEN_WIDTH/2
                sprite.center_y = SCREEN_HEIGHT/2 
                sprite.scale = 0.5
                self.character_sprite_list.append(sprite)
                self.character_sprite_list.draw()
            else:
                arcade.draw_text(
                    "🎮", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50,
                    arcade.color.WHITE, 64,
                    anchor_x="center", anchor_y="center"
                )
            
            # Nome e descrição
            arcade.draw_text(
                char["name"],
                SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30,
                arcade.color.GOLD, 28,
                anchor_x="left", bold=True
            )
            
            arcade.draw_text(
                char["description"],
                SCREEN_WIDTH, SCREEN_HEIGHT/2,
                arcade.color.LIGHT_GRAY, 16,
                anchor_x="left", width=250, align="left"
            )
        
        # Controles de navegação
        arcade.draw_text(
            "← A / D → : Navegar entre personagens",
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 120,
            arcade.color.LIGHT_BLUE, 14,
            anchor_x="center"
        )
        
        # Botões
        for btn in self.buttons:
            btn.draw()

    def on_key_press(self, key, modifiers):
        # Navegação entre personagens
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.selected_character_index = (self.selected_character_index - 1) % len(self.characters)
            self._load_character_texture()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.selected_character_index = (self.selected_character_index + 1) % len(self.characters)
            self._load_character_texture()
        elif key == arcade.key.ENTER:
            self._select_character()
        elif key == arcade.key.ESCAPE:
            self._go_back()

    def on_mouse_press(self, x, y, button, modifiers):
        # Botões
        for btn in self.buttons:
            if btn.check_click(x, y):
                if btn.label == "SELECIONAR":
                    self._select_character()
                elif btn.label == "VOLTAR":
                    self._go_back()

    def _select_character(self):
        """Seleciona o personagem e cria a conta"""
        if self.characters:
            selected_char = self.characters[self.selected_character_index]
            
            # Cria a conta com o personagem selecionado
            if auth_system.register_user(
                self.username, 
                self.senha, 
                self.nome, 
                avatar_url=self.avatar_path,
                character_data=selected_char  # Salva dados do personagem
            ):
                print(f"✅ Conta criada com personagem: {selected_char['name']}")
                
                # Define o usuário atual
                user_manager.set_current_user(self.username)
                
                # Vai para o menu
                menu_view = MenuView(
                    username=self.username,
                    avatar_path=self.avatar_path
                )
                self.window.show_view(menu_view)
            else:
                print("❌ Erro ao criar conta com personagem")

    def _go_back(self):
        """Volta para o cadastro"""
        from views.login_view import LoginView
        login_view = LoginView()
        self.window.show_view(login_view)


class LoginView(arcade.View):
    """
    Tela de login e cadastro com seleção de personagem
    """

    def __init__(self):
        super().__init__()

        # Background
        self.background = arcade.SpriteList()
        try:
            if os.path.exists(LOGIN_BACKGROUND):
                bg = arcade.Sprite(LOGIN_BACKGROUND, scale=1.0)
                bg.center_x = SCREEN_WIDTH / 2
                bg.center_y = SCREEN_HEIGHT / 2
                bg.width = SCREEN_WIDTH
                bg.height = SCREEN_HEIGHT
                self.background.append(bg)
                print(f"✅ Background carregado: {LOGIN_BACKGROUND}")
            else:
                print(f"❌ Background não encontrado: {LOGIN_BACKGROUND}")
                if os.path.exists(MENU_BACKGROUND):
                    bg = arcade.Sprite(MENU_BACKGROUND, scale=1.0)
                    bg.center_x = SCREEN_WIDTH / 2
                    bg.center_y = SCREEN_HEIGHT / 2
                    bg.width = SCREEN_WIDTH
                    bg.height = SCREEN_HEIGHT
                    self.background.append(bg)
                    print(f"✅ Usando fallback: {MENU_BACKGROUND}")
        except Exception as e:
            print(f"❌ Erro ao carregar background: {e}")
            pass

        # Áudio de fundo
        self.background_music = None
        self.music_player = None
        try:
            if os.path.exists(LOGIN_MUSIC):
                self.background_music = arcade.Sound(LOGIN_MUSIC)
                self.music_player = self.background_music.play(volume=0.5)
                self.background_music.set_volume(0.5, self.music_player)
                self.background_music.set_loop(True, self.music_player)
                print("🎵 Áudio de fundo iniciado: specular_city.mp3")
            else:
                print(f"❌ Áudio não encontrado: {LOGIN_MUSIC}")
        except Exception as e:
            print(f"❌ Erro ao carregar áudio de fundo: {e}")
            self.background_music = None

        # Estado: "login" ou "cadastro"
        self.current_form = "login"

        # Avatar selecionado
        self.avatar_path = None
        self.avatar_texture = None

        # Campos de texto e campo ativo
        self.text_entries: Dict[str, Dict] = {}
        self.active_field: str = None

        # Botões de login (no form de login)
        self.buttons: List[RPGButton] = []

        # Mensagem de status
        self.status_message = ""
        self.status_timer = 0

        # Inicializa UI
        self._setup_text_entries()
        self._setup_ui()

    def on_hide_view(self):
        """Para a música quando a view é trocada"""
        if self.background_music and self.music_player:
            self.background_music.stop(self.music_player)

    def set_status(self, message: str, duration: float = 3.0):
        """Define mensagem de status temporária"""
        self.status_message = message
        self.status_timer = duration

    def selecionar_avatar(self):
        """Abre seletor de arquivos para escolher avatar"""
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        file_path = filedialog.askopenfilename(
            title="Selecionar Avatar",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if file_path:
            self.avatar_path = file_path
            try:
                self.avatar_texture = arcade.load_texture(file_path)
                self.set_status("✅ Avatar selecionado!")
            except Exception as e:
                print(f"❌ Erro ao carregar avatar: {e}")
                self.set_status("❌ Erro ao carregar avatar")
                self.avatar_texture = None

    def _setup_text_entries(self):
        """Configura todos os campos de texto (login + cadastro)."""
        cx = SCREEN_WIDTH / 2
        cy = SCREEN_HEIGHT / 2

        # LOGIN
        self.text_entries["login_usuario"] = {
            "text": "", "x": cx - 100, "y": cy + 40,
            "width": 200, "height": 40,
            "visible": True
        }
        self.text_entries["login_senha"] = {
            "text": "", "x": cx - 100, "y": cy - 20,
            "width": 200, "height": 40,
            "visible": True, "password": True
        }

        # CADASTRO
        self.text_entries["cadastro_nome"] = {
            "text": "", "x": cx - 100, "y": cy + 80,
            "width": 200, "height": 40,
            "visible": False
        }
        self.text_entries["cadastro_usuario"] = {
            "text": "", "x": cx - 100, "y": cy + 20,
            "width": 200, "height": 40,
            "visible": False
        }
        self.text_entries["cadastro_senha"] = {
            "text": "", "x": cx - 100, "y": cy - 40,
            "width": 200, "height": 40,
            "visible": False, "password": True
        }

    def _setup_ui(self):
        """Cria os botões 'ENTRAR' e 'CRIAR CONTA' (visíveis apenas no login)."""
        cx = SCREEN_WIDTH / 2
        cy = SCREEN_HEIGHT / 2
        self.buttons = [
            RPGButton("ENTRAR", cx, cy - 80),
            RPGButton("CRIAR CONTA", cx, cy - 180),
        ]

    def update_field_visibility(self):
        """Mostra apenas os campos do formulário atual."""
        for key, fld in self.text_entries.items():
            fld["visible"] = key.startswith(self.current_form)

    def validar_campos_cadastro(self) -> bool:
        """Valida se todos os campos do cadastro estão preenchidos"""
        nome = self.text_entries["cadastro_nome"]["text"].strip()
        usuario = self.text_entries["cadastro_usuario"]["text"].strip()
        senha = self.text_entries["cadastro_senha"]["text"].strip()

        if not nome:
            self.set_status("❌ Nome é obrigatório")
            return False
        if not usuario:
            self.set_status("❌ Usuário é obrigatório")
            return False
        if not senha:
            self.set_status("❌ Senha é obrigatória")
            return False
        if len(senha) < 4:
            self.set_status("❌ Senha deve ter pelo menos 4 caracteres")
            return False

        return True

    def validar_campos_login(self) -> bool:
        """Valida se todos os campos do login estão preenchidos"""
        usuario = self.text_entries["login_usuario"]["text"].strip()
        senha = self.text_entries["login_senha"]["text"].strip()

        if not usuario:
            self.set_status("❌ Usuário é obrigatório")
            return False
        if not senha:
            self.set_status("❌ Senha é obrigatória")
            return False

        return True

    def fazer_login(self):
        """Lógica de login"""
        if not self.validar_campos_login():
            return

        usuario = self.text_entries["login_usuario"]["text"].strip()
        senha = self.text_entries["login_senha"]["text"].strip()
        
        self.set_status("🔐 Verificando credenciais...")
        
        if auth_system.authenticate(usuario, senha):
            self.set_status("✅ Login realizado com sucesso!")
            print(f"✅ Login bem-sucedido! Usuário: {usuario}")
            
            user_manager.set_current_user(usuario)
            
            user_data = auth_system.get_user_data(usuario)
            avatar_path = user_data.get("avatar_path") if user_data else None
            
            if not avatar_path:
                avatar_path = get_avatar_by_username(usuario)
                print(f"🎨 Avatar automático atribuído: {avatar_path}")
            
            if self.background_music and self.music_player:
                self.background_music.stop(self.music_player)
            
            menu_view = MenuView(
                username=usuario,
                avatar_path=avatar_path
            )
            self.window.show_view(menu_view)
        else:
            self.set_status("❌ Usuário ou senha incorretos")
            print("❌ Login falhou - usuário não existe ou credenciais inválidas")

    def criar_conta(self):
        """Lógica de criação de conta - agora vai para seleção de personagem"""
        if not self.validar_campos_cadastro():
            return

        nome = self.text_entries["cadastro_nome"]["text"].strip()
        usuario = self.text_entries["cadastro_usuario"]["text"].strip()
        senha = self.text_entries["cadastro_senha"]["text"].strip()
        
        self.set_status("📝 Criando conta...")
        
        # CORREÇÃO: Usa avatar automático baseado no username
        avatar_to_use = self.avatar_path if self.avatar_path else get_avatar_by_username(usuario)
        
        print(f"🎨 Avatar para nova conta: {avatar_to_use}")
        
        # Verifica se o usuário já existe
        if auth_system.user_exists(usuario):
            self.set_status("❌ Usuário já existe")
            return
        
        # Para a música antes de trocar de view
        if self.background_music and self.music_player:
            self.background_music.stop(self.music_player)
        
        # Vai para a tela de seleção de personagem
        character_view = CharacterSelectionView(
            username=usuario,
            nome=nome,
            senha=senha,
            avatar_path=avatar_to_use
        )
        self.window.show_view(character_view)

    def draw_login_form(self):
        """Desenha título, campos e labels do login."""
        # Título
        arcade.draw_text(
            "ENTRAR NA AVENTURA",
            SCREEN_WIDTH/2, SCREEN_HEIGHT - 120,
            arcade.color.WHITE, 28,
            anchor_x="center", font_name=BUTTON_FONT, bold=True
        )

        # Campos de texto
        for fid, fld in self.text_entries.items():
            if not fld["visible"]:
                continue

            left = fld["x"]
            right = left + fld["width"]
            bottom = fld["y"] - fld["height"]/2
            top = fld["y"] + fld["height"]/2

            # Fundo
            arcade.draw_lrbt_rectangle_filled(
                left, right, bottom, top,
                (40, 40, 60, 200)
            )
            # Borda
            color = arcade.color.GOLD if self.active_field == fid else arcade.color.GRAY
            arcade.draw_lrbt_rectangle_outline(
                left, right, bottom, top, color, 2
            )
            # Texto (mascara senha se necessário)
            disp = fld["text"]
            if fld.get("password"):
                disp = "*" * len(disp)
            arcade.draw_text(
                disp,
                left + 10, fld["y"],
                arcade.color.WHITE, 16,
                anchor_y="center", font_name="Arial"
            )

        # Labels
        arcade.draw_text(
            "Usuário:",
            SCREEN_WIDTH/2 - 120, SCREEN_HEIGHT/2 + 40,
            arcade.color.WHITE, 16,
            anchor_x="right", anchor_y="center"
        )
        arcade.draw_text(
            "Senha:",
            SCREEN_WIDTH/2 - 120, SCREEN_HEIGHT/2 - 20,
            arcade.color.WHITE, 16,
            anchor_x="right", anchor_y="center"
        )

    def draw_cadastro_form(self):
        """Desenha título, avatar picker e campos do cadastro."""
        # Título
        arcade.draw_text(
            "CRIAR CONTA ÉPICA",
            SCREEN_WIDTH/2, SCREEN_HEIGHT - 120,
            arcade.color.WHITE, 28,
            anchor_x="center", font_name=BUTTON_FONT, bold=True
        )

        # Avatar preview
        ax, ay = SCREEN_WIDTH/2, SCREEN_HEIGHT - 200
        if self.avatar_texture:
            try:
                arcade.draw_texture_rectangle(ax, ay, 90, 90, self.avatar_texture)
            except:
                arcade.draw_text(
                    "🎮", ax, ay,
                    arcade.color.WHITE, 24,
                    anchor_x="center", anchor_y="center"
                )
        else:
            arcade.draw_text(
                "🎮", ax, ay,
                arcade.color.WHITE, 24,
                anchor_x="center", anchor_y="center"
            )

        # Botão ESCOLHER AVATAR
        left = SCREEN_WIDTH/2 - 80
        right = SCREEN_WIDTH/2 + 80
        bottom = SCREEN_HEIGHT - 270
        top = SCREEN_HEIGHT - 230
        arcade.draw_lrbt_rectangle_filled(
            left, right, bottom, top,
            (80, 60, 120, 200)
        )
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom, top,
            arcade.color.GOLD, 2
        )
        arcade.draw_text(
            "ESCOLHER AVATAR",
            SCREEN_WIDTH/2, SCREEN_HEIGHT - 250,
            arcade.color.WHITE, 12,
            anchor_x="center", anchor_y="center"
        )

        # Instrução do avatar automático
        arcade.draw_text(
            "Ou deixe em branco para um avatar automático de anime!",
            SCREEN_WIDTH/2, SCREEN_HEIGHT - 290,
            arcade.color.LIGHT_GRAY, 10,
            anchor_x="center", anchor_y="center"
        )

        # Campos de texto do cadastro
        for fid, fld in self.text_entries.items():
            if not fld["visible"]:
                continue

            left = fld["x"]
            right = left + fld["width"]
            bottom = fld["y"] - fld["height"]/2
            top = fld["y"] + fld["height"]/2

            arcade.draw_lrbt_rectangle_filled(
                left, right, bottom, top,
                (40, 40, 60, 200)
            )
            bc = arcade.color.GOLD if self.active_field == fid else arcade.color.GRAY
            arcade.draw_lrbt_rectangle_outline(
                left, right, bottom, top, bc, 2
            )
            disp = fld["text"]
            if fld.get("password"):
                disp = "*" * len(disp)
            arcade.draw_text(
                disp,
                left + 10, fld["y"],
                arcade.color.WHITE, 16,
                anchor_y="center", font_name="Arial"
            )

        # Labels
        labels = [
            ("Nome:", SCREEN_HEIGHT/2 + 80),
            ("Usuário:", SCREEN_HEIGHT/2 + 20),
            ("Senha:", SCREEN_HEIGHT/2 - 40),
        ]
        for label, y_pos in labels:
            arcade.draw_text(
                label,
                SCREEN_WIDTH/2 - 120, y_pos,
                arcade.color.WHITE, 16,
                anchor_x="right", anchor_y="center"
            )

        # Botão CRIAR CONTA
        arcade.draw_lrbt_rectangle_filled(
            SCREEN_WIDTH/2 - 100, SCREEN_WIDTH/2 + 100,
            SCREEN_HEIGHT/2 - 100, SCREEN_HEIGHT/2 - 60,
            (100, 80, 160, 200)
        )
        arcade.draw_lrbt_rectangle_outline(
            SCREEN_WIDTH/2 - 100, SCREEN_WIDTH/2 + 100,
            SCREEN_HEIGHT/2 - 100, SCREEN_HEIGHT/2 - 60,
            arcade.color.GOLD, 2
        )
        arcade.draw_text(
            "CRIAR CONTA",
            SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 80,
            arcade.color.WHITE, 16,
            anchor_x="center", anchor_y="center", bold=True
        )

    def on_draw(self):
        self.clear()

        # Fundo
        if self.background:
            self.background.draw()
        else:
            arcade.draw_lrbt_rectangle_filled(
                0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                arcade.color.DARK_SLATE_GRAY
            )

        # Overlay escuro
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 0, 120)
        )

        # Atualiza visibilidade de campos
        self.update_field_visibility()

        # Desenha o formulário correto
        if self.current_form == "login":
            self.draw_login_form()
            for btn in self.buttons:
                btn.draw()
        else:
            self.draw_cadastro_form()

        # Botão Voltar (cadastro)
        if self.current_form == "cadastro":
            arcade.draw_text(
                "← Voltar para Login",
                50, SCREEN_HEIGHT - 40,
                arcade.color.LIGHT_GRAY, 14,
                font_name="Arial"
            )

        # Mensagem de status
        if self.status_message and self.status_timer > 0:
            arcade.draw_text(
                self.status_message,
                SCREEN_WIDTH/2, 100,
                arcade.color.YELLOW, 16,
                anchor_x="center", bold=True
            )

        # Instruções
        arcade.draw_text(
            "Clique nos campos para digitar • ESC para sair",
            SCREEN_WIDTH/2, 30,
            arcade.color.LIGHT_GRAY, 12,
            anchor_x="center", font_name="Arial"
        )

    def on_update(self, delta_time: float):
        """Atualiza timer da mensagem"""
        if self.status_timer > 0:
            self.status_timer -= delta_time

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        # Avatar picker (cadastro)
        if (self.current_form == "cadastro" and
            SCREEN_WIDTH/2 - 80 <= x <= SCREEN_WIDTH/2 + 80 and
            SCREEN_HEIGHT - 270 <= y <= SCREEN_HEIGHT - 230):
            self.selecionar_avatar()
            return

        # Voltar ao login (cadastro)
        if (self.current_form == "cadastro" and x <= 200 and y >= SCREEN_HEIGHT - 50):
            self.current_form = "login"
            self.active_field = None
            return

        # Criar conta (cadastro)
        if (self.current_form == "cadastro" and
            SCREEN_WIDTH/2 - 100 <= x <= SCREEN_WIDTH/2 + 100 and
            SCREEN_HEIGHT/2 - 100 <= y <= SCREEN_HEIGHT/2 - 60):
            self.criar_conta()
            return

        # Seleção de campo de texto
        self.active_field = None
        for fid, fld in self.text_entries.items():
            if not fld["visible"]:
                continue
            left = fld["x"]
            right = left + fld["width"]
            bottom = fld["y"] - fld["height"]/2
            top = fld["y"] + fld["height"]/2
            if left <= x <= right and bottom <= y <= top:
                self.active_field = fid
                break

        # Botões de login
        if self.current_form == "login":
            for btn in self.buttons:
                if btn.check_click(x, y):
                    if btn.label == "ENTRAR":
                        self.fazer_login()
                    elif btn.label == "CRIAR CONTA":
                        self.current_form = "cadastro"
                        self.active_field = None
                        # Reseta o avatar quando vai para cadastro
                        self.avatar_path = None
                        self.avatar_texture = None

    def on_key_press(self, key: int, modifiers: int):
        # ESC
        if key == arcade.key.ESCAPE:
            if self.current_form == "cadastro":
                self.current_form = "login"
                self.active_field = None
                # Reseta o avatar quando volta para login
                self.avatar_path = None
                self.avatar_texture = None
            else:
                # Para a música antes de sair
                if self.background_music and self.music_player:
                    self.background_music.stop(self.music_player)
                arcade.exit()
            return

        # Texto
        if not self.active_field:
            return

        fld = self.text_entries[self.active_field]
        if key == arcade.key.BACKSPACE:
            fld["text"] = fld["text"][:-1]
        elif key == arcade.key.ENTER:
            # Enter confirma o formulário atual
            if self.current_form == "login":
                self.fazer_login()
            else:
                self.criar_conta()
        else:
            ch = self.key_to_char(key, modifiers)
            if ch:
                fld["text"] += ch

    def key_to_char(self, key: int, modifiers: int) -> str:
        """Converte tecla para caractere legível, considerando SHIFT."""
        shift_pressed = modifiers & arcade.key.MOD_SHIFT

        # Letras A–Z
        if arcade.key.A <= key <= arcade.key.Z:
            char = chr(key)
            return char if shift_pressed else char.lower()

        # Números 0–9
        if arcade.key.KEY_0 <= key <= arcade.key.KEY_9:
            return chr(key)

        # Espaço
        if key == arcade.key.SPACE:
            return " "

        # Pontuação básica
        punct_map = {
            arcade.key.PERIOD: "." if not shift_pressed else ">",
            arcade.key.COMMA: "," if not shift_pressed else "<",
            arcade.key.SEMICOLON: ";" if not shift_pressed else ":",
            arcade.key.QUOTE: "'" if not shift_pressed else '"',
            arcade.key.SLASH: "/" if not shift_pressed else "?",
            arcade.key.BACKSLASH: "\\" if not shift_pressed else "|",
            arcade.key.MINUS: "-" if not shift_pressed else "_",
            arcade.key.EQUAL: "=" if not shift_pressed else "+",
            arcade.key.LEFT_BRACKET: "[" if not shift_pressed else "{",
            arcade.key.RIGHT_BRACKET: "]" if not shift_pressed else "}",
        }
        return punct_map.get(key, "")