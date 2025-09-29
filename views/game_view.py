import arcade
import xml.etree.ElementTree as ET

from config import RAW_MAP_PATH, TEMP_MAP_PATH, TILE_SIZE, PHASE_TRIGGER_CODES
from assets.xp.xp import XPBar

class GameView(arcade.View):
    """
    Carrega o mapa TMX, controla a movimentação de Emilly,
    detecta triggers de fase e exige ENTER para iniciar o quiz.
    """

    def __init__(self, xp_bar: XPBar = None):
        super().__init__()

        # Barra de XP compartilhada (pode ser None se não usar aqui)
        self.xp_bar = xp_bar

        # Cena (tilemap + sprites) e sprite do jogador
        self.scene         = None
        self.player_sprite = None

        # Controle de teclas W/A/S/D
        self.keys = {
            arcade.key.W: False,
            arcade.key.A: False,
            arcade.key.S: False,
            arcade.key.D: False,
        }

        # Lista de triggers invisíveis e trigger mais próximo
        self.trigger_list = arcade.SpriteList()
        self.near_trigger = None

    def setup(self):
        # 1) Injeta inline o tileset no TMX
        tree = ET.parse(RAW_MAP_PATH)
        root = tree.getroot()
        for ts in root.findall("tileset"):
            if ts.get("source"):
                root.remove(ts)

        tileset = ET.Element("tileset", {
            "firstgid":"1",
            "name":"floresta",
            "tilewidth":"32",
            "tileheight":"32",
            "tilecount":"30",
            "columns":"6"
        })
        ET.SubElement(tileset, "image", {
            "source":"assets/maps/tilesets/tilemap_packed.png",
            "width":"192", "height":"176"
        })
        root.insert(0, tileset)
        tree.write(TEMP_MAP_PATH, encoding="utf-8")

        # 2) Carrega tilemap e monta a cena
        tile_map = arcade.load_tilemap(
            TEMP_MAP_PATH,
            scaling=1.0,
            use_spatial_hash=False,
            lazy=True
        )
        self.scene = arcade.Scene.from_tilemap(tile_map)

        # 3) Cria sprite do jogador (Emilly) e adiciona na cena
        self.player_sprite = arcade.Sprite(
            "assets/characters/Emilly.png",  # ajuste o caminho se necessário
            scale=0.1
        )
        self.player_sprite.center_x = TILE_SIZE
        self.player_sprite.center_y = TILE_SIZE
        self.scene.add_sprite("Player", self.player_sprite)

        # 4) Varre layer CSV para criar triggers invisíveis
        raw = tile_map.tiled_map.layers[0]
        rows = len(raw.data)
        cols = len(raw.data[0])
        self.trigger_list.clear()

        for r in range(rows):
            for c in range(cols):
                gid = raw.data[r][c]
                if gid in PHASE_TRIGGER_CODES:
                    x = c * TILE_SIZE + TILE_SIZE / 2
                    y = (rows - r - 1) * TILE_SIZE + TILE_SIZE / 2

                    trig = arcade.SpriteSolidColor(
                        TILE_SIZE, TILE_SIZE,
                        (0, 0, 0, 0)  # RGBA totalmente transparente
                    )
                    trig.center_x = x
                    trig.center_y = y
                    trig.phase    = PHASE_TRIGGER_CODES[gid]
                    self.trigger_list.append(trig)

    def on_show(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.clear()

        # Desenha o mapa + todas as sprites (inclui o player)
        if self.scene:
            self.scene.draw()

        # Se Emilly estiver sobre um trigger, mostra o hint
        if self.near_trigger:
            arcade.draw_text(
                f"Pressione ENTER para iniciar a fase {self.near_trigger.phase}",
                self.player_sprite.center_x,
                self.player_sprite.center_y + 60,
                arcade.color.YELLOW,
                font_size=16,
                anchor_x="center"
            )

        # Desenha a XPBar, se passada no construtor
        if self.xp_bar:
            self.xp_bar.draw()

    def on_update(self, delta_time: float):
        # Movimenta Emilly via WASD
        speed = 5
        dx = dy = 0
        if self.keys[arcade.key.W]: dy += speed
        if self.keys[arcade.key.S]: dy -= speed
        if self.keys[arcade.key.A]: dx -= speed
        if self.keys[arcade.key.D]: dx += speed

        self.player_sprite.center_x += dx
        self.player_sprite.center_y += dy

        # Detecta colisão com triggers
        hits = arcade.check_for_collision_with_list(
            self.player_sprite,
            self.trigger_list
        )
        self.near_trigger = hits[0] if hits else None

    def on_key_press(self, key: int, modifiers: int):
        # Marca teclas de movimento
        if key in self.keys:
            self.keys[key] = True

        # ENTER dispara o QuizView se estiver num trigger
        if key == arcade.key.ENTER and self.near_trigger:
            from views.quiz_view import QuizView

            qv = QuizView(
                phase=self.near_trigger.phase,
                xp_bar=self.xp_bar,
                parent=self
            )
            qv.setup()
            self.window.show_view(qv)

        # ESC volta ao menu principal
        if key == arcade.key.ESCAPE:
            from views.menu_view import MenuView
            self.window.show_view(MenuView())

        # F11 toggle fullscreen
        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

    def on_key_release(self, key: int, modifiers: int):
        # Desmarca teclas de movimento
        if key in self.keys:
            self.keys[key] = False
