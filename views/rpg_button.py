import arcade

class RPGButton:
    def __init__(self, label, center_x, center_y, texture_index=0, enabled=True):
        self.label      = label
        self.center_x   = center_x
        self.center_y   = center_y
        self.enabled    = enabled
        self.width      = 238
        self.height     =  64
        self.hover      = False

    def draw(self):
        # Define cor do botão
        color = arcade.color.GRAY if not self.enabled else arcade.color.WHITE_SMOKE

        # Cálculo dos limites
        left   = self.center_x - self.width  / 2
        right  = self.center_x + self.width  / 2
        bottom = self.center_y - self.height / 2
        top    = self.center_y + self.height / 2

        # Desenha retângulo preenchido
        arcade.draw_lrbt_rectangle_filled(
            left, right, bottom, top,
            color
        )

        # Texto centralizado
        arcade.draw_text(
            self.label,
            self.center_x,
            self.center_y,
            arcade.color.BLACK,
            14,
            anchor_x="center",
            anchor_y="center"
        )

    def check_hover(self, x, y):
        self.hover = (
            abs(x - self.center_x) < self.width/2 and
            abs(y - self.center_y) < self.height/2
        )

    def check_click(self, x, y):
        return (
            self.enabled and
            abs(x - self.center_x) < self.width/2 and
            abs(y - self.center_y) < self.height/2
        )
