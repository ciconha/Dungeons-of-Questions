import arcade
from config import SCREEN_WIDTH, SCREEN_HEIGHT, MENU_BACKGROUND, EMILLY_SPRITE, BUTTON_FONT
from views.rpg_button import RPGButton
from views.game_view import GameView
from assets.xp.xp import XPBar

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_id = "Jogador #001"

        # Fonte Minecraft ou Arial
        font_name = BUTTON_FONT if arcade.resources.resolve(BUTTON_FONT) else "Arial"

        # Título épico com sombra
        self.title_shadow = arcade.Text(
            "Dungeons of Questions",
            SCREEN_WIDTH/2 + 2, SCREEN_HEIGHT - 20 - 2,
            arcade.color.BLACK, font_size=48,
            font_name=font_name,
            anchor_x="center", anchor_y="top"
        )
        self.title_text = arcade.Text(
            "Dungeons of Questions",
            SCREEN_WIDTH/2, SCREEN_HEIGHT - 20,
            arcade.color.WHITE, font_size=48,
            font_name=font_name,
            anchor_x="center", anchor_y="top"
        )

        # ID do jogador
        self.id_text = arcade.Text(
            f"ID: {self.player_id}",
            50, 50,
            arcade.color.WHITE, font_size=20,
            font_name="Arial"
        )

        # Background
        self.background = arcade.SpriteList()
        bg = arcade.Sprite(MENU_BACKGROUND, scale=1.0)
        bg.center_x = SCREEN_WIDTH/2
        bg.center_y = SCREEN_HEIGHT/2
        bg.width  = SCREEN_WIDTH
        bg.height = SCREEN_HEIGHT
        self.background.append(bg)

        # Emilly
        self.emilly = arcade.SpriteList()
        em = arcade.Sprite(EMILLY_SPRITE, scale=0.5)
        em.center_x = 200
        em.center_y = 300
        self.emilly.append(em)

        # Botões
        self.buttons = [
            RPGButton("CAMPANHA", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40),
            RPGButton("TREINO",   SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40),
        ]

        # Barra de XP (inicial estática aqui)
        self.xp_bar = XPBar(
            current_xp=40, max_xp=100,
            center_x=SCREEN_WIDTH - 200, center_y=50,
            width=300, height=24
        )

    def on_draw(self):
        self.clear()
        self.background.draw()

        # Emilly + contorno
        self.emilly.draw()
        for sprite in self.emilly:
            arcade.draw_lrbt_rectangle_outline(
                sprite.left - 2, sprite.right + 2,
                sprite.bottom - 2, sprite.top + 2,
                arcade.color.WHITE, border_width=2
            )

        # Botões
        for btn in self.buttons:
            btn.draw()

        # Título
        self.title_shadow.draw()
        self.title_text.draw()

        # ID e XP
        self.id_text.draw()
        self.xp_bar.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.texture_index = 1 if btn.check_hover(x, y) else 0

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            if btn.check_click(x, y) and btn.label == "CAMPANHA":
                gv = GameView(xp_bar=self.xp_bar)
                gv.setup()
                self.window.show_view(gv)
