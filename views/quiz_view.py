# views/quiz_view.py

import arcade
import requests
import time
from typing import List, Dict, Tuple

from config import SCREEN_WIDTH, SCREEN_HEIGHT
from assets.xp.xp import XPBar


class FloatingText:
    """Texto que sobe e desvanece após 1 segundo."""
    def __init__(self, text: str, x: float, y: float):
        self.text       = text
        self.x          = x
        self.y          = y
        self.start_time = time.time()
        self.duration   = 1.0

    def update(self, delta_time: float) -> bool:
        elapsed = time.time() - self.start_time
        if elapsed > self.duration:
            return False
        self.y += 50 * delta_time
        return True

    def draw(self):
        # Calcula alpha e monta uma tupla RGBA válida
        elapsed = time.time() - self.start_time
        alpha   = int(255 * max(0, 1 - (elapsed / self.duration)))
        base    = arcade.color.GOLDEN_POPPY  # (R, G, B)
        color4  = (base[0], base[1], base[2], alpha)
        arcade.draw_text(
            self.text,
            self.x,
            self.y,
            color4,
            font_size=20,
            anchor_x="center"
        )


class QuizView(arcade.View):

    def __init__(self, phase: int, xp_bar: XPBar, parent):
        super().__init__()
        self.phase        = phase
        self.xp_bar       = xp_bar
        self.parent       = parent

        self.max_lives    = 5
        self.lives        = self.max_lives

        self.questions: List[Dict] = []
        self.current             = 0
        self.option_boxes: List[Dict] = []
        self.floating_texts: List[FloatingText] = []

        
        self.heart_list = arcade.SpriteList()
        for i in range(self.max_lives):
            heart = arcade.Sprite("assets/ui/coracao.png", scale=0.5)
            heart.center_x = 20 + i * 30
            heart.center_y = SCREEN_HEIGHT - 20
            heart.empty_texture = arcade.load_texture("assets/ui/vazio.png")
            self.heart_list.append(heart)

    def setup(self):
        resp = requests.get(f"http://127.0.0.1:8000/api/quiz/{self.phase}")
        if resp.status_code != 200:
            return self._return_to_map()

        data = resp.json()
        if not isinstance(data, list) or not data:
            return self._return_to_map()

        self.questions    = data
        self.current      = 0
        self.lives        = self.max_lives
        self.floating_texts.clear()
        self._build_option_boxes()

    def _return_to_map(self):
        self.parent.setup()
        self.window.show_view(self.parent)

    def _build_option_boxes(self):
        self.option_boxes.clear()
        self.question_rect = (
            SCREEN_WIDTH * 0.1,
            SCREEN_WIDTH * 0.9,
            SCREEN_HEIGHT * 0.75,
            SCREEN_HEIGHT * 0.90,
        )

        opts    = self.questions[self.current]["options"]
        box_h   = 40
        start_y = SCREEN_HEIGHT * 0.60
        gap     = 60

        for i, text in enumerate(opts):
            cy = start_y - i * gap
            l  = SCREEN_WIDTH * 0.1
            r  = SCREEN_WIDTH * 0.9
            b  = cy - box_h / 2
            t  = cy + box_h / 2
            self.option_boxes.append({
                "rect": (l, r, b, t),
                "text": text
            })

    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        self.xp_bar.draw()
        for idx, heart in enumerate(self.heart_list):
            if idx >= self.lives:
                heart.texture = heart.empty_texture
        self.heart_list.draw()

        if not self.questions:
            return

        
        l, r, b, t = self.question_rect
        arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.BLUE_GRAY)
        arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, border_width=2)

        
        question = self.questions[self.current]["question"]
        arcade.draw_text(
            question,
            (l + r) / 2, (b + t) / 2,
            arcade.color.WHITE,
            18,
            width=int(r - l) - 20,
            align="center",
            anchor_x="center", anchor_y="center"
        )

        # Caixas de opção
        for box in self.option_boxes:
            l, r, b, t = box["rect"]
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.DARK_BLUE)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, border_width=2)
            arcade.draw_text(
                box["text"],
                (l + r) / 2, (b + t) / 2,
                arcade.color.WHITE,
                14,
                width=int(r - l) - 20,
                align="center",
                anchor_x="center", anchor_y="center"
            )

        # Textos flutuantes de +10 XP
        for ft in self.floating_texts:
            ft.draw()

    def on_update(self, delta_time: float):
        self.floating_texts[:] = [ft for ft in self.floating_texts if ft.update(delta_time)]

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if not self.questions:
            return

        correct = self.questions[self.current]["answer"]
        for box in self.option_boxes:
            l, r, b, t = box["rect"]
            if l < x < r and b < y < t:
                if box["text"] == correct:
                    self.xp_bar.add_xp(10)
                    bx, by = SCREEN_WIDTH / 2, SCREEN_HEIGHT - 10
                    self.floating_texts.append(FloatingText("+10", bx, by))
                else:
                    self.lives = max(0, self.lives - 1)

                self.current += 1
                if self.current >= len(self.questions) or self.lives == 0:
                    return self._return_to_map()
                self._build_option_boxes()
                break

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            self._return_to_map()
