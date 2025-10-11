# views/profile/components/header.py

import arcade

class Header:
    def __init__(self, title: str, center_x: float, top_y: float):
        self.title = title
        self.center_x = center_x
        self.top_y = top_y

    def draw(self):
        # CORREÇÃO: Usar draw_lrbt_rectangle_filled
        left = self.center_x - 200
        right = self.center_x + 200
        bottom = self.top_y - 60
        top = self.top_y
        
        arcade.draw_lrbt_rectangle_filled(
            left, right, bottom, top,
            (101, 67, 33)  # color
        )
        
        # CORREÇÃO: Usar draw_lrbt_rectangle_outline
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom, top,
            arcade.color.GOLD,  # color
            3                   # border_width
        )
        
        arcade.draw_text(
            self.title,
            self.center_x, self.top_y - 30,
            arcade.color.CREAM, 32,
            anchor_x="center", anchor_y="center",
            bold=True
        )