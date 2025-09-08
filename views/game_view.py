import arcade
import xml.etree.ElementTree as ET
from config import RAW_MAP_PATH, TEMP_MAP_PATH

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.tile_map = None
        self.scene = None
        self.player_sprite = None
        self.keys = {
            arcade.key.W: False,
            arcade.key.A: False,
            arcade.key.S: False,
            arcade.key.D: False
        }

    def setup(self):
        # Processa o mapa
        tree = ET.parse(RAW_MAP_PATH)
        root = tree.getroot()

        for tileset in root.findall("tileset"):
            if tileset.get("source"):
                root.remove(tileset)

        tileset = ET.Element("tileset", {
            "firstgid": "1",
            "name": "floresta",
            "tilewidth": "32",
            "tileheight": "32",
            "tilecount": "30",
            "columns": "6"
        })

        ET.SubElement(tileset, "image", {
            "source": "assets/maps/tilesets/tilemap_packed.png",
            "width": "192",
            "height": "176"
        })

        root.insert(0, tileset)

        for layer in root.findall("layer"):
            data = layer.find("data")
            if data is not None and data.text:
                data.text = data.text.replace("4,", "1,")

        tree.write(TEMP_MAP_PATH, encoding="utf-8")

        # Carrega o mapa
        self.tile_map = arcade.load_tilemap(
            TEMP_MAP_PATH, scaling=1.0, use_spatial_hash=False, lazy=True
        )
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Cria o jogador
        self.player_sprite = arcade.Sprite("assets/characters/Emilly.png", scale=0.1)
        self.player_sprite.center_x = 100
        self.player_sprite.center_y = 100
        self.scene.add_sprite("Player", self.player_sprite)

    def on_draw(self):
        self.clear()
        if self.scene:
            self.scene.draw()

    def on_update(self, delta_time):
        speed = 5
        dx = dy = 0

        if self.keys[arcade.key.W]:
            dy += speed
        if self.keys[arcade.key.S]:
            dy -= speed
        if self.keys[arcade.key.A]:
            dx -= speed
        if self.keys[arcade.key.D]:
            dx += speed

        self.player_sprite.center_x += dx
        self.player_sprite.center_y += dy

    def on_key_press(self, key, modifiers):
        if key in self.keys:
            self.keys[key] = True

        if key == arcade.key.ESCAPE:
            # Importação local para evitar ciclo
            from views.menu_view import MenuView
            menu_view = MenuView()
            self.window.show_view(menu_view)

    def on_key_release(self, key, modifiers):
        if key in self.keys:
            self.keys[key] = False
