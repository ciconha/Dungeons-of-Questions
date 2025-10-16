import arcade
import random

# Configurações da janela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Demo XPBar Completo"

class XPBar:
    """
    Barra de XP estática no canto esquerdo com cristal ao lado.
    Level 1 precisa de 100 XP, Level 2 precisa de 200 XP, Level 3 de 300 XP, etc.
    Aceita current_xp, level e max_xp vindos da API ou calculados automaticamente.
    """

    def __init__(
        self,
        current_xp:   int    = 0,
        level:        int    = 1,
        max_xp:       int    = None,
        center_x:     float  = 150,
        center_y:     float  = 580,
        width:        float  = 250,
        height:       float  = 20,
        crystal_path: str    = "assets/ui/cristal.png",
        border_color: tuple  = (120,  80, 200),
        fill_color:   tuple  = (160, 100, 255),
        background_color:tuple = (30,   20,  50),
        text_color:   tuple  = (255, 255, 255),
        font_size:    int    = 12
    ):
        # Nível e XP máximo (100 × level se max_xp não for fornecido)
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

        # Tenta carregar o cristal como Sprite e agrupa em SpriteList
        try:
            self.crystal_sprite = arcade.Sprite(crystal_path, scale=1.0)
            # Ajusta tamanho do cristal
            self.crystal_sprite.width  = self.height * 1.2
            self.crystal_sprite.height = self.height * 1.2
            self._crystal_list = arcade.SpriteList()
            self._crystal_list.append(self.crystal_sprite)
        except Exception:
            self._crystal_list = None

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
            self.level    += 1
            levels_gained += 1
            self.max_xp    = self.level * 100

        # Mantém current_xp dentro dos limites [0, max_xp]
        self.current_xp = max(0, min(self.current_xp, self.max_xp))
        return levels_gained

    def draw(self):
        # Calcula bordas da barra
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

        # 3) Preenchimento proporcional
        frac = (self.current_xp / self.max_xp) if self.max_xp else 0
        fill_w = frac * self.width
        if fill_w > 0:
            arcade.draw_lrbt_rectangle_filled(
                left, left + fill_w, bottom, top,
                self.fill_color
            )

        # 4) Borda
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom, top,
            self.border_color, 2
        )

        # 5) Texto de XP
        arcade.draw_text(
            f"{self.current_xp}/{self.max_xp} XP",
            right + 5, self.center_y,
            self.text_color,
            self.font_size,
            anchor_x="left", anchor_y="center"
        )

        # 6) Cristal ao lado esquerdo via SpriteList
        if self._crystal_list:
            cr_x = left - (self.crystal_sprite.width / 2) - 5
            cr_y = self.center_y
            self.crystal_sprite.center_x = cr_x
            self.crystal_sprite.center_y = cr_y
            self._crystal_list.draw()

        # 7) Texto de nível à esquerda do cristal
        lvl_x = (
            left - (self.crystal_sprite.width + 5)
            if self._crystal_list
            else left - 15
        )
        arcade.draw_text(
            f"Lv.{self.level}",
            lvl_x, self.center_y,
            self.text_color,
            self.font_size,
            anchor_x="right", anchor_y="center"
        )


class DemoXPWindow(arcade.Window):
    """Janela de demonstração do XPBar."""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.xp_bar = XPBar(current_xp=0, level=1)

    def on_draw(self):
        self.clear()
        # Instruções
        arcade.draw_text(
            "Pressione ESPAÇO para ganhar XP aleatório (50–150).",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
            arcade.color.WHITE, 16,
            anchor_x="center"
        )
        # Desenha a barra de XP
        self.xp_bar.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            gained = random.randint(50, 150)
            self.xp_bar.add_xp(gained)
            print(f"Ganhou {gained} XP!")


def main():
    window = DemoXPWindow()
    arcade.run()


if __name__ == "__main__":
    main()
