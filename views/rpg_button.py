# views/rpg_button.py - VERSÃO ESTILIZADA COM DETALHES ROXOS
import arcade
import math
import random

class RPGButton:
    def __init__(self, label, center_x, center_y, width=250, height=60):
        self.label = label
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.texture_index = 0  # 0 = normal, 1 = hover
        self.pulse_time = 0
        self.glow_intensity = 0
        self.glow_direction = 1
        
        # Cores com tema roxo intenso
        self.colors = {
            'normal': (50, 15, 80),        # Roxo escuro base
            'hover': (80, 25, 120),        # Roxo mais claro
            'border': (180, 70, 255),      # Roxo neon para borda
            'text': (255, 255, 255),       # Texto branco
            'glow': (150, 50, 220, 100),   # Brilho roxo com transparência
            'crystal': (200, 150, 255),    # Roxo claro para cristais
            'highlight': (220, 180, 255)   # Destaque muito claro
        }

    def update(self, delta_time):
        """Atualiza animações do botão"""
        self.pulse_time += delta_time * 5
        self.glow_intensity += delta_time * 3 * self.glow_direction
        
        # Controla a intensidade do brilho
        if self.glow_intensity >= 1.0:
            self.glow_intensity = 1.0
            self.glow_direction = -1
        elif self.glow_intensity <= 0.3:
            self.glow_intensity = 0.3
            self.glow_direction = 1

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

    def draw_crystal(self, x, y, size):
        """Desenha um cristal decorativo"""
        # Cristal principal
        arcade.draw_polygon_filled([
            (x, y + size),
            (x - size/2, y),
            (x + size/2, y)
        ], self.colors['crystal'])
        
        # Brilho no cristal
        arcade.draw_polygon_filled([
            (x, y + size*0.7),
            (x - size/4, y + size*0.2),
            (x + size/4, y + size*0.2)
        ], self.colors['highlight'])

    def draw_rune(self, x, y, size, time):
        """Desenha uma runa mágica giratória"""
        points = []
        for i in range(6):
            angle = time + i * (3.14159 / 3)
            radius = size * (0.8 + 0.2 * math.sin(time * 2 + i))
            points.append((
                x + radius * math.cos(angle),
                y + radius * math.sin(angle)
            ))
        
        arcade.draw_polygon_outline(points, self.colors['border'], 2)

    def draw(self):
        # Cor baseada no estado
        is_hover = self.texture_index == 1
        base_color = self.colors['hover'] if is_hover else self.colors['normal']
        
        # Efeito de brilho de fundo quando em hover
        if is_hover:
            glow_radius = self.glow_intensity * 15
            arcade.draw_circle_filled(
                self.center_x, self.center_y, 
                self.width/2 + glow_radius,
                (self.colors['glow'][0], self.colors['glow'][1], 
                 self.colors['glow'][2], int(80 * self.glow_intensity))
            )
        
        # Fundo do botão com gradiente
        for i in range(5):
            shade_factor = 0.8 + (i * 0.05)
            shaded_color = (
                int(base_color[0] * shade_factor),
                int(base_color[1] * shade_factor),
                int(base_color[2] * shade_factor)
            )
            
            offset = i * 2
            arcade.draw_lrbt_rectangle_filled(
                self.center_x - self.width/2 + offset, 
                self.center_x + self.width/2 - offset,
                self.center_y - self.height/2 + offset,
                self.center_y + self.height/2 - offset,
                shaded_color
            )
        
        # Borda com efeito pulsante
        border_width = 3 + math.sin(self.pulse_time) * 1.5
        arcade.draw_lrbt_rectangle_outline(
            self.center_x - self.width/2,
            self.center_x + self.width/2,
            self.center_y - self.height/2,
            self.center_y + self.height/2,
            self.colors['border'], border_width
        )
        
        # Cantos decorativos
        corner_size = 8
        # Canto superior esquerdo
        arcade.draw_lrbt_rectangle_filled(
            self.center_x - self.width/2,
            self.center_x - self.width/2 + corner_size,
            self.center_y + self.height/2 - corner_size,
            self.center_y + self.height/2,
            self.colors['border']
        )
        # Canto superior direito
        arcade.draw_lrbt_rectangle_filled(
            self.center_x + self.width/2 - corner_size,
            self.center_x + self.width/2,
            self.center_y + self.height/2 - corner_size,
            self.center_y + self.height/2,
            self.colors['border']
        )
        # Canto inferior esquerdo
        arcade.draw_lrbt_rectangle_filled(
            self.center_x - self.width/2,
            self.center_x - self.width/2 + corner_size,
            self.center_y - self.height/2,
            self.center_y - self.height/2 + corner_size,
            self.colors['border']
        )
        # Canto inferior direito
        arcade.draw_lrbt_rectangle_filled(
            self.center_x + self.width/2 - corner_size,
            self.center_x + self.width/2,
            self.center_y - self.height/2,
            self.center_y - self.height/2 + corner_size,
            self.colors['border']
        )
        
        # Cristais decorativos nos cantos (apenas no hover)
        if is_hover:
            self.draw_crystal(
                self.center_x - self.width/2 + 15,
                self.center_y + self.height/2 - 15,
                6
            )
            self.draw_crystal(
                self.center_x + self.width/2 - 15,
                self.center_y + self.height/2 - 15,
                6
            )
            self.draw_crystal(
                self.center_x - self.width/2 + 15,
                self.center_y - self.height/2 + 15,
                6
            )
            self.draw_crystal(
                self.center_x + self.width/2 - 15,
                self.center_y - self.height/2 + 15,
                6
            )
        
        # Runa mágica central (apenas no hover)
        if is_hover:
            self.draw_rune(
                self.center_x, 
                self.center_y, 
                15, 
                self.pulse_time
            )
        
        # Texto com sombra para melhor legibilidade
        # Sombra
        arcade.draw_text(
            self.label,
            self.center_x + 2, self.center_y - 2,
            (0, 0, 0, 150),
            font_size=20,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        # Texto principal
        arcade.draw_text(
            self.label,
            self.center_x, self.center_y,
            self.colors['text'],
            font_size=20,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )