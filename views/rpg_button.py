# views/rpg_button.py - VERSÃO CORRIGIDA
import arcade
from arcade import color as arcade_color

class RPGButton:
    def __init__(self, label, center_x, center_y, width=200, height=50):
        self.label = label
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.texture_index = 0  # 0 = normal, 1 = hover
        
        # Cores para os estados do botão
        self.colors = {
            'normal': (70, 70, 100),
            'hover': (100, 100, 150),
            'border': (255, 215, 0),
            'text': (255, 255, 255)
        }

    def check_hover(self, x, y):
        """Verifica se o mouse está sobre o botão"""
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        top = self.center_y + self.height / 2
        bottom = self.center_y - self.height / 2
        
        return (left <= x <= right) and (bottom <= y <= top)

    def check_click(self, x, y):
        """Verifica se o botão foi clicado"""
        return self.check_hover(x, y)

    def draw(self):
        # Cor baseada no estado
        color = self.colors['hover'] if self.texture_index == 1 else self.colors['normal']
        
        # Fundo do botão - USANDO draw_lrbt_rectangle_filled
        arcade.draw_lrbt_rectangle_filled(
            self.center_x - self.width/2, 
            self.center_x + self.width/2,
            self.center_y - self.height/2,
            self.center_y + self.height/2,
            color
        )
        
        # Borda - USANDO draw_lrbt_rectangle_outline
        arcade.draw_lrbt_rectangle_outline(
            self.center_x - self.width/2,
            self.center_x + self.width/2,
            self.center_y - self.height/2,
            self.center_y + self.height/2,
            self.colors['border'], 3
        )
        
        # Texto
        arcade.draw_text(
            self.label,
            self.center_x, self.center_y,
            self.colors['text'],
            font_size=20,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )