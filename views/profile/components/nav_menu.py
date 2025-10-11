# views/profile/components/nav_menu.py

import arcade

class NavMenu:
    def __init__(self, options: list, start_x: float, start_y: float, item_height: float = 30):
        self.options = options
        self.cx = start_x
        self.cy = start_y
        self.h = item_height
        self.active = 0

    def draw(self):
        for i, opt in enumerate(self.options):
            y = self.cy - i * self.h
            bg = (80, 60, 20) if i == self.active else (40, 30, 10)
            
            # CORREÇÃO: Usar draw_lrbt_rectangle_filled
            left = self.cx - 80
            right = self.cx + 80
            bottom = y - (self.h - 4) / 2
            top = y + (self.h - 4) / 2
            
            arcade.draw_lrbt_rectangle_filled(
                left, right, bottom, top,
                bg  # color
            )
            
            # CORREÇÃO: Usar draw_lrbt_rectangle_outline
            arcade.draw_lrbt_rectangle_outline(
                left, right, bottom, top,
                arcade.color.GOLD,  # color
                2                   # border_width
            )
            
            arcade.draw_text(
                opt.upper(),
                self.cx, y,
                arcade.color.BEIGE, 14,
                anchor_x="center", anchor_y="center"
            )