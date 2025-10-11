# views/profile/components/identity_info.py

import arcade

class IdentityInfo:
    def __init__(self, display_name: str, username: str, start_x: float, start_y: float):
        self.display_name = display_name
        self.username = username
        self.x = start_x
        self.y = start_y

    def draw(self):
        # Placa do nome
        name_left = self.x
        name_right = self.x + 120
        name_bottom = self.y - 20
        name_top = self.y + 20
        
        # Fundo
        arcade.draw_lrbt_rectangle_filled(
            name_left, name_right, name_bottom, name_top,
            (101, 67, 33)  # cor madeira
        )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            name_left, name_right, name_bottom, name_top,
            arcade.color.GOLD, 2
        )
        
        # Texto do nome
        arcade.draw_text(
            self.display_name,
            self.x + 60, self.y,
            arcade.color.CREAM, 18,
            anchor_x="center", anchor_y="center",
            bold=True
        )
        
        # Placa do username
        user_left = self.x
        user_right = self.x + 120
        user_bottom = self.y - 45
        user_top = self.y - 5
        
        # Fundo
        arcade.draw_lrbt_rectangle_filled(
            user_left, user_right, user_bottom, user_top,
            (101, 67, 33)  # cor madeira
        )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            user_left, user_right, user_bottom, user_top,
            arcade.color.GOLD, 2
        )
        
        # Texto do username
        arcade.draw_text(
            self.username,
            self.x + 60, self.y - 25,
            arcade.color.LIGHT_GRAY, 12,
            anchor_x="center", anchor_y="center"
        )