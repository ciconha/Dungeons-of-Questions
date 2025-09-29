import arcade

class RPGButton:
    def __init__(self, label, center_x, center_y, enabled=True):
        self.label      = label
        self.center_x   = center_x
        self.center_y   = center_y
        self.enabled    = enabled
        self.width      = 238
        self.height     = 64

    def draw(self):
        color = arcade.color.GRAY if not self.enabled else arcade.color.WHITE_SMOKE
        left   = self.center_x - self.width  / 2
        right  = self.center_x + self.width  / 2
        bottom = self.center_y - self.height / 2
        top    = self.center_y + self.height / 2

        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)
        arcade.draw_text(
            self.label,
            self.center_x, self.center_y,
            arcade.color.BLACK, 18,
            anchor_x="center", anchor_y="center"
        )

    def check_hover(self, x, y):
        return (
            abs(x - self.center_x) < self.width/2 and
            abs(y - self.center_y) < self.height/2
        )

    def check_click(self, x, y):
        return self.enabled and self.check_hover(x, y)
