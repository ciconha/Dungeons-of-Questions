import arcade
import os
from config import BUTTON_FONT, BUTTON_SHEET, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLUMNS, BUTTON_COUNT
from PIL import Image

def load_button_textures(sheet_path, button_width, button_height, columns, count):
    textures = []
    sheet_image = Image.open(sheet_path)
    for i in range(count):
        x = (i % columns) * button_width
        y = (i // columns) * button_height
        cropped = sheet_image.crop((x, y, x + button_width, y + button_height))
        texture = arcade.Texture(name=f"button_{i}", image=cropped)
        textures.append(texture)
    return textures

button_textures = load_button_textures(
    BUTTON_SHEET, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLUMNS, BUTTON_COUNT
)

class RPGButton:
    def __init__(self, label, x, y, texture_index=0, enabled=True):
        self.label = label
        self.x = x
        self.y = y
        self.enabled = enabled
        self.hovered = False
        self.sprite = arcade.Sprite(center_x=x, center_y=y)
        self.sprite.texture = button_textures[texture_index]
        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self.sprite)

    def draw(self):
        self.sprite_list.draw()
        color = arcade.color.WHITE if self.enabled else arcade.color.GRAY
        if self.hovered:
            color = arcade.color.YELLOW
        arcade.draw_text(
            self.label,
            self.x - 80,
            self.y - 10,
            color,
            18,
            font_name=BUTTON_FONT if os.path.exists(BUTTON_FONT) else None
        )

    def check_hover(self, x, y):
        self.hovered = self.sprite.left < x < self.sprite.right and self.sprite.bottom < y < self.sprite.top

    def check_click(self, x, y):
        return self.enabled and self.sprite.left < x < self.sprite.right and self.sprite.bottom < y < self.sprite.top
