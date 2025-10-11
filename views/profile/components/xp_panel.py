# views/profile/components/xp_panel.py

import arcade

class XPPanel:
    def __init__(self, current_xp: int, max_xp: int, phase: str, start_x: float, start_y: float):
        self.cx = start_x
        self.cy = start_y
        self.current = current_xp
        self.max = max_xp
        self.phase = phase

    def draw(self):
        # CORREÇÃO: Usar draw_lrbt_rectangle_outline
        bar_left = self.cx - 100
        bar_right = self.cx + 100
        bar_bottom = self.cy - 8
        bar_top = self.cy + 8
        
        arcade.draw_lrbt_rectangle_outline(
            bar_left, bar_right, bar_bottom, bar_top,
            arcade.color.GOLD,  # color
            2                   # border_width
        )
        
        # Preenchimento da barra de XP
        pct = max(0, min(1, self.current / self.max))
        if pct > 0:
            fill_right = bar_left + (200 * pct)
            
            arcade.draw_lrbt_rectangle_filled(
                bar_left, fill_right, bar_bottom, bar_top,
                arcade.color.LIGHT_BLUE  # color
            )
        
        # Texto XP
        arcade.draw_text(
            f"{self.current} / {self.max}",
            self.cx, self.cy + 20,
            arcade.color.WHITE, 12,
            anchor_x="center"
        )
        
        # Texto Fase
        arcade.draw_text(
            f"Fase {self.phase}",
            self.cx, self.cy - 20,
            arcade.color.BEIGE, 14,
            anchor_x="center"
        )