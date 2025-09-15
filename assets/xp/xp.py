import arcade

class XPBar:
    def __init__(
        self,
        current_xp: int    = 0,
        max_xp:     int    = 100,
        center_x:   float  = 200,
        center_y:   float  = 100,
        width:      float  = 300,
        height:     float  =  24,
        border_color       = arcade.color.WHITE,
        fill_color         = arcade.color.GREEN,
        background_color   = arcade.color.DARK_GRAY,
        text_color         = arcade.color.WHITE,
        font_size:  int    =  14
    ):
        self.current_xp       = current_xp
        self.max_xp           = max_xp
        self.center_x         = center_x
        self.center_y         = center_y
        self.width            = width
        self.height           = height
        self.border_color     = border_color
        self.fill_color       = fill_color
        self.background_color = background_color
        self.text_color       = text_color
        self.font_size        = font_size

    def draw(self):
        
        left   = self.center_x - self.width  / 2
        right  = self.center_x + self.width  / 2
        bottom = self.center_y - self.height / 2
        top    = self.center_y + self.height / 2

        
        arcade.draw_lrbt_rectangle_filled(
            left, right, bottom, top,
            self.background_color
        )

        
        fill_width = (self.current_xp / self.max_xp) * self.width
        arcade.draw_lrbt_rectangle_filled(
            left, left + fill_width, bottom, top,
            self.fill_color
        )

        
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom, top,
            self.border_color,
            border_width=2
        )

        
        arcade.draw_text(
            f"{self.current_xp} / {self.max_xp} XP",
            left,
            bottom - self.font_size - 4,
            self.text_color,
            self.font_size
        )

    def add_xp(self, amount: int):
        self.current_xp = min(self.current_xp + amount, self.max_xp)
