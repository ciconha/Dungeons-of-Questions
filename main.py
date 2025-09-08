import arcade
from config import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from views.menu_view import MenuView

class RPGGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.set_fullscreen(True)
        self.show_view(MenuView())

    def on_key_press(self, key, modifiers):
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

def main():
    game = RPGGame()
    arcade.run()

if __name__ == "__main__":
    main()
