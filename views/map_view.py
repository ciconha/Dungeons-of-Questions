# views/map_view.py

import arcade
from config import RAW_MAP_PATH, TEMP_MAP_PATH, TILE_SIZE, PHASE_TRIGGER_CODES
import xml.etree.ElementTree as ET

class MapView(arcade.View):
    def __init__(self, xp_bar):
        super().__init__()
        self.xp_bar        = xp_bar
        self.scene         = None
        self.player_sprite = None
        self.trigger_list  = arcade.SpriteList()
        self.keys          = {
            arcade.key.W: False,
            arcade.key.A: False,
            arcade.key.S: False,
            arcade.key.D: False
        }
        self.near_trigger  = None  # ← novo: guarda trigger atual

    def setup_phase(self, idx):
        # ... (código de setup do mapa igual ao anterior)

        # Triggers
        raw = tile_map.tiled_map.layers[0]
        h, w = raw.height, raw.width
        self.trigger_list.clear()
        for row in range(h):
            for col in range(w):
                gid = raw.data[row][col]
                if gid in PHASE_TRIGGER_CODES:
                    x = col * TILE_SIZE + TILE_SIZE/2
                    y = (h - row - 1) * TILE_SIZE + TILE_SIZE/2
                    trig = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE, arcade.color.TRANSPARENT)
                    trig.center_x, trig.center_y = x, y
                    trig.phase = PHASE_TRIGGER_CODES[gid]
                    self.trigger_list.append(trig)

    def on_draw(self):
        self.clear()
        self.scene.draw()
        self.player_sprite.draw()

        # Se estiver perto de uma fase, mostra mensagem
        if self.near_trigger:
            arcade.draw_text(
                f"Pressione ENTER para iniciar a fase {self.near_trigger.phase}",
                self.player_sprite.center_x,
                self.player_sprite.center_y + 60,
                arcade.color.YELLOW,
                font_size=16,
                anchor_x="center"
            )

    def on_update(self, dt):
        speed = 4
        dx = dy = 0
        if self.keys[arcade.key.W]: dy += speed
        if self.keys[arcade.key.S]: dy -= speed
        if self.keys[arcade.key.A]: dx -= speed
        if self.keys[arcade.key.D]: dx += speed

        self.player_sprite.center_x += dx
        self.player_sprite.center_y += dy

        # Verifica se está perto de algum trigger
        hits = arcade.check_for_collision_with_list(self.player_sprite, self.trigger_list)
        self.near_trigger = hits[0] if hits else None

    def on_key_press(self, key, modifiers):
        if key in self.keys:
            self.keys[key] = True

        # Se estiver perto de uma fase e apertar ENTER
        if key == arcade.key.ENTER and self.near_trigger:
            from views.quiz_view import QuizView
            qv = QuizView(self.near_trigger.phase, self.xp_bar, parent=self)
            qv.setup()
            self.window.show_view(qv)

    def on_key_release(self, key, modifiers):
        if key in self.keys:
            self.keys[key] = False
