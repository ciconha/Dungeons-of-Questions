import arcade
from views.rpg_button import RPGButton
from views.game_view import GameView

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.player_id = "Jogador #001"

        # Fundo
        self.background_sprite = arcade.Sprite("assets/ui/menu_background.jpg", scale=1.0)
        self.background_sprite.center_x = self.window.width // 2
        self.background_sprite.center_y = self.window.height // 2
        self.background_sprite_list = arcade.SpriteList()
        self.background_sprite_list.append(self.background_sprite)

        # Sprite da Emilly
        self.emilly_sprite_list = arcade.SpriteList()
        emilly_sprite = arcade.Sprite("assets/ui/Emilly.png", scale=0.5)
        emilly_sprite.center_x = 300
        emilly_sprite.center_y = 500
        self.emilly_sprite_list.append(emilly_sprite)

        # Botões
        self.buttons = [
            RPGButton("CAMPANHA", 1100, 600, texture_index=0, enabled=True),
            RPGButton("MULTIJOGADOR", 1100, 530, texture_index=2, enabled=False),
            RPGButton("TREINO", 1100, 460, texture_index=0, enabled=True),
        ]

    def on_draw(self):
        self.clear()

        # Fundo
        self.background_sprite_list.draw()

        # Área do personagem
        x, y = 300, 500
        w, h = 128, 128
        arcade.draw_line(x - w // 2, y - h // 2, x + w // 2, y - h // 2, arcade.color.WHITE, 2)
        arcade.draw_line(x - w // 2, y + h // 2, x + w // 2, y + h // 2, arcade.color.WHITE, 2)
        arcade.draw_line(x - w // 2, y - h // 2, x - w // 2, y + h // 2, arcade.color.WHITE, 2)
        arcade.draw_line(x + w // 2, y - h // 2, x + w // 2, y + h // 2, arcade.color.WHITE, 2)

        # Emilly
        self.emilly_sprite_list.draw()

        # Botões
        for button in self.buttons:
            button.draw()

        # ID do jogador
        arcade.draw_text(
            f"ID: {self.player_id}",
            50,
            50,
            arcade.color.WHITE,
            20,
            font_name="Arial"
        )

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for b in self.buttons:
            if b.check_click(x, y):
                if b.label == "CAMPANHA":
                    game_view = GameView()
                    game_view.setup()
                    self.window.show_view(game_view)
                else:
                    print(f"Botão '{b.label}' clicado!")
