import arcade

class XPBar:
    """
    Barra de XP estática no canto esquerdo com cristal ao lado.
    Level 1 precisa de 100 XP, Level 2 de 200 XP, Level 3 de 300 XP, etc. (ilimitado).
    Aceita current_xp, level e max_xp vindos da API ou calculados automaticamente.
    """

    def __init__(
        self,
        current_xp:   int    = 0,
        level:        int    = 1,
        max_xp:       int    = None,
        center_x:     float  = 150,            # canto esquerdo
        center_y:     float  = 580,            # topo da tela
        width:        float  = 250,            # largura compacta
        height:       float  = 20,             # altura fina
        crystal_path: str    = "assets/ui/cristal.png",
        border_color: tuple  = (120,  80, 200),# roxo forte
        fill_color:   tuple  = (160, 100, 255),# roxo vibrante
        background_color:tuple = (30,   20,  50),# roxo bem escuro
        text_color:   tuple  = (255, 255, 255),
        font_size:    int    = 12
    ):
        # Define nível e XP máximo (100×level se max_xp não for fornecido)
        self.level      = max(1, level)
        self.max_xp     = max_xp if max_xp is not None else self.level * 100
        self.current_xp = max(0, min(current_xp, self.max_xp))

        # Posição e dimensões
        self.center_x = center_x
        self.center_y = center_y
        self.width    = width
        self.height   = height

        # Estilo
        self.border_color     = border_color
        self.fill_color       = fill_color
        self.background_color = background_color
        self.text_color       = text_color
        self.font_size        = font_size

        # Carrega textura do cristal
        self.crystal_texture = arcade.load_texture(crystal_path)

    def add_xp(self, amount: int) -> int:
        """
        Adiciona XP; sobe de nível quando current_xp >= max_xp.
        Cada nível subsequente exige 100×level XP.
        Retorna quantos níveis foram ganhos.
        """
        self.current_xp += amount
        levels_gained = 0

        while self.current_xp >= self.max_xp:
            self.current_xp -= self.max_xp
            self.level      += 1
            levels_gained   += 1
            self.max_xp      = self.level * 100

        # Garante que current_xp fique em [0, max_xp]
        self.current_xp = max(0, min(self.current_xp, self.max_xp))
        return levels_gained

    def draw(self):
        # Cantos da barra
        left   = self.center_x - self.width  / 2
        right  = self.center_x + self.width  / 2
        bottom = self.center_y - self.height / 2
        top    = self.center_y + self.height / 2

        # 1) Sombra
        arcade.draw_lrbt_rectangle_filled(
            left - 1, right + 1,
            bottom - 1, top + 1,
            (0, 0, 0, 100)
        )

        # 2) Fundo da barra
        arcade.draw_lrbt_rectangle_filled(
            left, right, bottom, top,
            self.background_color
        )

        # 3) Preenchimento exato
        frac       = (self.current_xp / self.max_xp) if self.max_xp else 0
        fill_width = frac * self.width
        if fill_width > 0:
            arcade.draw_lrbt_rectangle_filled(
                left, left + fill_width, bottom, top,
                self.fill_color
            )

        # 4) Borda da barra
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom, top,
            self.border_color, 2
        )

        # 5) Texto de XP à direita
        arcade.draw_text(
            f"{self.current_xp}/{self.max_xp} XP",
            right + 5, self.center_y,
            self.text_color,
            self.font_size,
            anchor_x="left", anchor_y="center"
        )

        # 6) Cristal ao lado esquerdo (usando draw_texture_rect)
        cr_w = self.crystal_texture.width
        cr_h = self.crystal_texture.height
        cr_x = left - cr_w / 2 - 5
        cr_y = self.center_y
        

        # 7) Texto de nível à esquerda do cristal
        arcade.draw_text(
            f"Lv.{self.level}",
            cr_x - cr_w / 2 - 5, cr_y,
            self.text_color,
            self.font_size,
            anchor_x="right", anchor_y="center"
        )
