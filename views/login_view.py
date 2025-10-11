# views/login_view.py

import arcade
import os
import tkinter as tk
from tkinter import filedialog
from typing import Dict, List

from config import SCREEN_WIDTH, SCREEN_HEIGHT, MENU_BACKGROUND, BUTTON_FONT
from views.rpg_button import RPGButton
from views.menu_view import MenuView
from auth.simple_auth import auth_system  # Importa o sistema de autenticação
from auth.user_manager import user_manager  # Importa o gerenciador de usuários


class LoginView(arcade.View):
    """
    Tela de login e cadastro com formulários de texto
    e seletor de avatar via file dialog do tkinter.
    """

    def __init__(self):
        super().__init__()

        # Background
        try:
            self.bg_texture = arcade.load_texture(MENU_BACKGROUND)
        except Exception:
            self.bg_texture = None

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
            RPGButton("CRIAR CONTA", cx, cy - 140),
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
        """Lógica de login - SÓ ENTRA SE USUÁRIO EXISTIR"""
        if not self.validar_campos_login():
            return

        usuario = self.text_entries["login_usuario"]["text"].strip()
        senha = self.text_entries["login_senha"]["text"].strip()
        
        self.set_status("🔐 Verificando credenciais...")
        
        # Usa o SimpleAuth para validar - SÓ CONTINUA SE O LOGIN FOR BEM-SUCEDIDO
        if auth_system.authenticate(usuario, senha):
            # Login bem-sucedido - vai para o menu
            self.set_status("✅ Login realizado com sucesso!")
            print(f"✅ Login bem-sucedido! Usuário: {usuario}")
            
            # CORREÇÃO: Define o usuário atual no UserManager
            user_manager.set_current_user(usuario)
            
            # Obtém dados do usuário para passar para o menu
            user_data = auth_system.get_user_data(usuario)
            avatar_path = user_data.get("avatar_path") if user_data else None
            
            # CORREÇÃO: Remove o parâmetro 'token' que não existe no MenuView
            menu_view = MenuView(
                username=usuario,
                avatar_path=avatar_path
            )
            self.window.show_view(menu_view)
        else:
            # Login falhou - NÃO AVANÇA, fica na tela de login
            self.set_status("❌ Usuário ou senha incorretos")
            print("❌ Login falhou - usuário não existe ou credenciais inválidas")

    def criar_conta(self):
        """Lógica de criação de conta"""
        if not self.validar_campos_cadastro():
            return

        nome = self.text_entries["cadastro_nome"]["text"].strip()
        usuario = self.text_entries["cadastro_usuario"]["text"].strip()
        senha = self.text_entries["cadastro_senha"]["text"].strip()
        
        self.set_status("📝 Criando conta...")
        
        # Usa o SimpleAuth para criar conta
        if auth_system.register_user(usuario, senha, nome, avatar_url=self.avatar_path):
            # Cadastro bem-sucedido - faz login automático
            self.set_status("✅ Conta criada com sucesso!")
            print(f"✅ Conta criada! Usuário: {usuario}")
            
            # CORREÇÃO: Define o usuário atual no UserManager
            user_manager.set_current_user(usuario)
            
            # CORREÇÃO: Remove o parâmetro 'token' que não existe no MenuView
            menu_view = MenuView(
                username=usuario,
                avatar_path=self.avatar_path
            )
            self.window.show_view(menu_view)
        else:
            # Cadastro falhou
            self.set_status("❌ Usuário já existe")
            print("❌ Cadastro falhou - usuário já existe")

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
        arcade.draw_circle_filled(ax, ay, 50, (60, 60, 80))
        if self.avatar_texture:
            try:
                arcade.draw_texture_rectangle(ax, ay, 90, 90, self.avatar_texture)
            except:
                # Fallback se der erro
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
        if self.bg_texture:
            try:
                arcade.draw_texture_rectangle(
                    SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                    SCREEN_WIDTH, SCREEN_HEIGHT,
                    self.bg_texture
                )
            except:
                # Fallback se der erro
                arcade.draw_lrbt_rectangle_filled(
                    0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                    arcade.color.DARK_SLATE_GRAY
                )
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

    def on_key_press(self, key: int, modifiers: int):
        # ESC
        if key == arcade.key.ESCAPE:
            if self.current_form == "cadastro":
                self.current_form = "login"
                self.active_field = None
            else:
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