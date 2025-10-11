# views/profile/profile_view.py

import arcade
from auth.simple_auth import auth_system
from auth.user_manager import user_manager
from assets.xp.xp import XPBar

from views.profile.components.header import Header
from views.profile.components.avatar_panel import AvatarPanel
from views.profile.components.identity_info import IdentityInfo
from views.profile.components.xp_panel import XPPanel
from views.profile.components.nav_menu import NavMenu
from views.profile.components.sprite_area import SpriteArea
from views.profile.components.background import Background


class ProfileView(arcade.View):
    def __init__(self):
        super().__init__()
        self.user = user_manager.get_current_user()
        self.data = auth_system.get_user_data(self.user) or {}
        self.avatar_tex = None

        # Carrega avatar
        avatar_path = self.data.get("avatar_path")
        if avatar_path:
            try:
                self.avatar_tex = arcade.load_texture(avatar_path)
            except:
                self.avatar_tex = None

        # Componentes
        w, h = self.window.width, self.window.height
        self.bg = Background(w, h)
        self.header = Header(self.data.get("hero_name", "EMILY THE EXPLODER"), w/2, h - 20)
        self.avatar = AvatarPanel(self.avatar_tex, 120, h - 120, 60)
        self.identity = IdentityInfo(
            self.data.get("display_name", "Sara Simpson"),
            f"@{self.data.get('username','user')}",
            60, h - 200
        )
        xp, lvl = self.data.get("xp",0), self.data.get("level",1)
        self.xpp = XPPanel(xp, lvl*10, self.data.get("phase",1), 120, h - 260)
        self.menu = NavMenu(
            ["Personagem", "Inventario", "Habilidades", "Resumo", "Conquistas"],
            260, h - 140
        )
        # Sprite full-body (estática ou animada)
        sprite_path = self.data.get("sprite_path")
        tex = None
        if sprite_path:
            try:
                tex = arcade.load_texture(sprite_path)
            except:
                tex = None
        self.sprite_area = SpriteArea(tex, w - 200, h/2, 160, 200)

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        # Desenha na ordem correta
        self.bg.draw()
        self.header.draw()
        self.avatar.draw()
        self.identity.draw()
        self.xpp.draw()
        self.menu.draw()
        self.sprite_area.draw()

    def on_key_press(self, key, modifiers):
        # Navegação do menu
        if key == arcade.key.UP:
            self.menu.active = max(0, self.menu.active - 1)
        elif key == arcade.key.DOWN:
            self.menu.active = min(len(self.menu.options)-1, self.menu.active + 1)
        elif key in (arcade.key.ESCAPE, arcade.key.BACKSPACE):
            from views.menu_view import MenuView
            self.window.show_view(MenuView())
        elif key == arcade.key.ENTER:
            # Aqui você trata o clique na aba ativa
            print("Selecionou aba:", self.menu.options[self.menu.active])

    def on_resize(self, width, height):
        # Atualiza background e header
        self.bg.w = width
        self.bg.h = height
        self.header.center_x = width/2
        self.header.top_y = height - 20
