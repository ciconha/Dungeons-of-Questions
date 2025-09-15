import arcade
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from views.rpg_button import RPGButton
from views.game_view import GameView
from assets.xp.xp import XPBar

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.player_id = "Jogador #001"

        # Fundo
        try:
            bg = arcade.Sprite("assets/ui/menu_background.jpg", scale=1.0)
            bg.center_x = SCREEN_WIDTH // 2
            bg.center_y = SCREEN_HEIGHT // 2
            self.background_sprite_list = arcade.SpriteList()
            self.background_sprite_list.append(bg)
        except Exception as e:
            print("Erro ao carregar imagem de fundo:", e)

        # Emily
        try:
            em = arcade.Sprite("assets/ui/Emilly.png", scale=0.5)
            em.center_x = 300
            em.center_y = 500
            self.emilly_sprite_list = arcade.SpriteList()
            self.emilly_sprite_list.append(em)
        except Exception as e:
            print("Erro ao carregar sprite da Emily:", e)

        # Botões
        self.buttons = [
            RPGButton("CAMPANHA", 1100, 600, texture_index=0, enabled=True),
            RPGButton("TREINO",   1100, 460, texture_index=0, enabled=True),
        ]

        # Barra de XP
        self.xp_bar = XPBar(
            current_xp=40,
            max_xp=100,
            center_x=SCREEN_WIDTH - 400,
            center_y=100,
            width=300,
            height=24
        )

    def on_draw(self):
        self.clear()

        # Fundo
        if hasattr(self, "background_sprite_list"):
            self.background_sprite_list.draw()

        # Emily + contorno
        if hasattr(self, "emilly_sprite_list"):
            self.emilly_sprite_list.draw()
            for sprite in self.emilly_sprite_list:
                arcade.draw_lrbt_rectangle_outline(
                    sprite.left - 2, sprite.right + 2,
                    sprite.bottom - 2, sprite.top + 2,
                    arcade.color.WHITE, border_width=2
                )

        # Botões
        for btn in self.buttons:
            btn.draw()

        # Texto do jogador
        arcade.draw_text(
            f"ID: {self.player_id}",
            50, 50,
            arcade.color.WHITE,
            20,
            font_name="Arial"
        )

        # XP
        self.xp_bar.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            if btn.check_click(x, y):
                if btn.label == "CAMPANHA":
                    gv = GameView()
                    gv.setup()
                    self.window.show_view(gv)
                else:
                    print(f"Botão '{btn.label}' clicado!")
