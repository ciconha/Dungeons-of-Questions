import arcade
from pathlib import Path
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from views.rpg_button import RPGButton
from views.game_view import GameView
from assets.xp.xp import XPBar

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_id = "Jogador #001"

        
        project_root = Path(__file__).resolve().parent.parent
        assets_ui    = project_root / "assets" / "ui"
        font_path    = assets_ui / "Minecraft.ttf"
        bg_path      = assets_ui / "menu_background.jpg"
        em_path      = assets_ui / "Emilly.png"

        
        if not font_path.exists():
            print(f"Atenção: fonte não encontrada em {font_path}. Usando fonte padrão.")
            font_name = "Arial"
        else:
            font_name = str(font_path)
        self.title_shadow = arcade.Text(
            "Dungeons of Questions",
            SCREEN_WIDTH / 2 + 2,
            SCREEN_HEIGHT - 12 - 2,
            arcade.color.BLACK,
            font_size=44,
            font_name=font_name,
            anchor_x="center",
            anchor_y="top"
        )
        self.title_text = arcade.Text(
            "Dungeons of Questions",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 20,
            arcade.color.WHITE,
            font_size=45,
            font_name=font_name,
            anchor_x="center",
            anchor_y="top"
        )

        
        self.id_text = arcade.Text(
            f"ID: {self.player_id}",
            50, 50,
            arcade.color.WHITE,
            font_size=20,
            font_name="Arial"
        )

        
        self.background_sprite_list = arcade.SpriteList()
        if not bg_path.exists():
            print(f"Atenção: background não encontrado em {bg_path}")
        else:
            bg = arcade.Sprite(str(bg_path), scale=1.0)
            bg.center_x = SCREEN_WIDTH / 2
            bg.center_y = SCREEN_HEIGHT / 2
            
            bg.width  = SCREEN_WIDTH
            bg.height = SCREEN_HEIGHT
            self.background_sprite_list.append(bg)

      
        self.emilly_sprite_list = arcade.SpriteList()
        if not em_path.exists():
            print(f"Atenção: Emilly.png não encontrado em {em_path}")
        else:
            em = arcade.Sprite(str(em_path), scale=0.5)
            em.center_x = 200
            em.center_y = 300
            self.emilly_sprite_list.append(em)

        
        self.buttons = [
            RPGButton("CAMPANHA", 1100, 600, texture_index=0, enabled=True),
            RPGButton("TREINO",   1100, 460, texture_index=0, enabled=True),
        ]

        
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

        
        self.background_sprite_list.draw()

        
        self.emilly_sprite_list.draw()
        for sprite in self.emilly_sprite_list:
            arcade.draw_lrbt_rectangle_outline(
                sprite.left - 2,
                sprite.right + 2,
                sprite.bottom - 2,
                sprite.top + 2,
                arcade.color.WHITE,
                border_width=2
            )

        
        for btn in self.buttons:
            btn.draw()

        
        self.title_shadow.draw()
        self.title_text.draw()

        
        self.id_text.draw()
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
