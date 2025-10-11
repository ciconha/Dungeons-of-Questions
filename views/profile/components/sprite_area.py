# views/profile/components/sprite_area.py

import arcade

class SpriteArea:
    def __init__(self, texture, center_x: float, center_y: float, width: float, height: float):
        self.texture = texture
        self.cx = center_x
        self.cy = center_y
        self.width = width
        self.height = height

    def draw(self):
        # Área de fundo - CORREÇÃO: Usar draw_lrbt_rectangle_filled
        left = self.cx - self.width / 2
        right = self.cx + self.width / 2
        bottom = self.cy - self.height / 2
        top = self.cy + self.height / 2
        
        arcade.draw_lrbt_rectangle_filled(
            left, right, bottom, top,
            (40, 40, 40)  # color
        )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom, top,
            arcade.color.GOLD,  # color
            2                   # border_width
        )
        
        # Sprite ou placeholder
        if self.texture:
            arcade.draw_texture_rectangle(
                self.cx,                    # center_x
                self.cy,                    # center_y
                self.width - 20,            # width
                self.height - 20,           # height
                self.texture                # texture
            )
        else:
            arcade.draw_text(
                "🎮", self.cx, self.cy,
                arcade.color.LIGHT_GRAY, 48,
                anchor_x="center", anchor_y="center"
            )