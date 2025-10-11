# views/profile/components/background.py

import arcade

class Background:
    def __init__(self, width: float, height: float):
        self.w = width
        self.h = height

    def draw(self):
        # CORREÇÃO: Usar draw_lrbt_rectangle_filled para fundo completo
        arcade.draw_lrbt_rectangle_filled(
            0,              # left
            self.w,         # right  
            0,              # bottom
            self.h,         # top
            (30, 20, 10)    # color
        )
        
        # CORREÇÃO: Usar draw_lrbt_rectangle_outline para borda
        arcade.draw_lrbt_rectangle_outline(
            10,                     # left
            self.w - 10,            # right
            10,                     # bottom
            self.h - 10,            # top
            arcade.color.GOLD,      # color
            3                       # border_width
        )