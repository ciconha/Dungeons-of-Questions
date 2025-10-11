# views/profile/components/avatar_panel.py

import arcade

class AvatarPanel:
    def __init__(self, texture, center_x: float, center_y: float, radius: float):
        self.texture = texture
        self.cx = center_x
        self.cy = center_y
        self.radius = radius

    def draw(self):
        # Círculo de fundo
        arcade.draw_circle_filled(self.cx, self.cy, self.radius, arcade.color.DARK_BLUE_GRAY)
        
        # Moldura dourada
        arcade.draw_circle_outline(self.cx, self.cy, self.radius, arcade.color.GOLD, 3)
        
        # Avatar ou fallback
        if self.texture:
            arcade.draw_texture_rectangle(
                self.cx, self.cy,
                self.radius * 1.8, self.radius * 1.8,
                self.texture
            )
        else:
            arcade.draw_text(
                "👤", self.cx, self.cy,
                arcade.color.WHITE, 24,
                anchor_x="center", anchor_y="center"
            )