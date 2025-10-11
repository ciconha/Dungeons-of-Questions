# views/quiz_view.py

import arcade
import requests
import threading
import time
import random
import math
from typing import List, Dict, Tuple
from dataclasses import dataclass

from config import SCREEN_WIDTH, SCREEN_HEIGHT
from assets.xp.xp import XPBar
from api.db.mongo import mongo  # instância global já conectada no main.py


@dataclass
class ParticleConfig:
    COUNT: int = 15
    SIZE_RANGE: Tuple[float, float] = (2.0, 6.0)
    SPEED_RANGE_X: Tuple[float, float] = (-50.0, 50.0)
    SPEED_RANGE_Y: Tuple[float, float] = (50.0, 150.0)
    LIFETIME: float = 1.0
    GRAVITY: float = -30.0


class ParticleSystem:
    class Particle:
        def __init__(self, x: float, y: float, color: Tuple[int, int, int], cfg: ParticleConfig):
            self.x = x
            self.y = y
            self.color = color
            self.size = random.uniform(*cfg.SIZE_RANGE)
            self.speed_x = random.uniform(*cfg.SPEED_RANGE_X)
            self.speed_y = random.uniform(*cfg.SPEED_RANGE_Y)
            self.life = cfg.LIFETIME
            self.gravity = cfg.GRAVITY
            self.alpha = 255

        def update(self, dt: float) -> bool:
            self.x += self.speed_x * dt
            self.y += self.speed_y * dt
            self.speed_y += self.gravity * dt
            self.life -= dt
            self.size = max(0, self.size - dt * 2)
            self.alpha = int(255 * max(0.0, min(1.0, self.life)))
            return self.life > 0 and self.size > 0

        def draw(self):
            alpha = max(0, min(255, self.alpha))
            arcade.draw_circle_filled(self.x, self.y, self.size, (*self.color, alpha))

    def __init__(self):
        self.particles: List[ParticleSystem.Particle] = []

    def create_effect(self, x: float, y: float, color: Tuple[int, int, int], cfg: ParticleConfig = None):
        cfg = cfg or ParticleConfig()
        for _ in range(cfg.COUNT):
            self.particles.append(self.Particle(x, y, color, cfg))

    def update(self, dt: float):
        self.particles[:] = [p for p in self.particles if p.update(dt)]

    def draw(self):
        for p in self.particles:
            p.draw()


class FloatingText:
    def __init__(self, text: str, x: float, y: float, color=(255, 215, 0), effect_type="normal"):
        self.text = text
        self.x = x
        self.y = y
        self.start = time.time()
        self.duration = 1.5
        self.color = color
        self.effect = effect_type
        self.offset = random.uniform(0, math.pi * 2)
        self.shake = 3.0 if effect_type == "critical" else 0.0
        self.scale = 1.2 if effect_type == "critical" else 1.0

    def update(self, dt: float) -> bool:
        elapsed = time.time() - self.start
        if elapsed > self.duration:
            return False
        progress = elapsed / self.duration
        self.y += 80 * dt * (1 - progress)
        self.offset += dt * 6
        return True

    def draw(self):
        elapsed = time.time() - self.start
        progress = elapsed / self.duration
        alpha = int(255 * max(0.0, min(1.0, 1 - progress ** 2)))

        if self.effect == "critical":
            pulse = math.sin(time.time() * 10) * 0.1 + 1.0
            font_size = int(28 * self.scale * pulse)
            sx = random.uniform(-self.shake, self.shake)
            sy = random.uniform(-self.shake, self.shake)
        else:
            font_size = 24
            sx = math.sin(self.offset) * 5 * (1 - progress)
            sy = 0

        r, g, b = self.color[:3]
        base_color = (r, g, b, alpha)

        # sombra
        arcade.draw_text(
            self.text,
            self.x + 2 + sx,
            self.y - 2 + sy,
            (0, 0, 0, max(0, alpha // 3)),
            font_size,
            anchor_x="center",
            font_name="Arial"
        )
        # texto principal
        arcade.draw_text(
            self.text,
            self.x + sx,
            self.y + sy,
            base_color,
            font_size,
            anchor_x="center",
            font_name="Arial"
        )


class QuizView(arcade.View):
    """
    Tela de quiz para uma fase específica.
    Ganha XP ao acertar e salva no MongoDB via endpoint /api/score.
    """
    COLORS = {
        "background": (20, 25, 40),
        "frame": (40, 35, 60),
        "frame_border": (180, 160, 100),
        "option_normal": (50, 40, 30),
        "option_hover": (80, 60, 40),
        "option_border": (200, 180, 120),
        "xp_frame": (30, 35, 50),
        "text_gold": (255, 215, 0),
        "text_silver": (200, 200, 210)
    }

    def __init__(self, phase: int, xp_bar: XPBar, session_id: str, parent: arcade.View):
        super().__init__()
        self.phase = phase
        self.xp_bar = xp_bar
        self.session_id = session_id
        self.parent = parent

        self.max_lives = 5
        self.lives = self.max_lives
        self.questions: List[Dict] = []
        self.current = 0
        self.option_boxes: List[Dict] = []
        self.floating_texts: List[FloatingText] = []
        self.particle_system = ParticleSystem()

        self.mouse_x = 0
        self.mouse_y = 0
        self.animation = 0.0

        self.background = None
        self.heart_full = None
        self.heart_empty = None
        self.frame_texture = None
        self.heart_list = arcade.SpriteList()

        self._load_assets()
        self._setup_ui()

    def _load_assets(self):
        try:
            self.background = arcade.load_texture("assets/backgrounds/quiz_bg.jpg")
        except Exception:
            self.background = None
        try:
            self.heart_full = arcade.load_texture("assets/ui/coracao.png")
            self.heart_empty = arcade.load_texture("assets/ui/vazio.png")
        except Exception:
            self.heart_full = arcade.Texture.create_filled("hf", (7, 7), arcade.color.RED)
            self.heart_empty = arcade.Texture.create_filled("he", (7, 7), arcade.color.DARK_GRAY)

    def _setup_ui(self):
        self.heart_list.clear()
        spacing = 20
        start_x = 40
        y_pos = SCREEN_HEIGHT - 90
        for i in range(self.max_lives):
            heart = arcade.Sprite()
            heart.texture = self.heart_full
            heart.scale = 0.3
            heart.center_x = start_x + i * spacing
            heart.center_y = y_pos
            self.heart_list.append(heart)
        try:
            self.frame_texture = arcade.load_texture("assets/ui/wood_frame.png")
        except Exception:
            self.frame_texture = None

    def _sync_xp_to_server(self, added_xp: int):
        """
        Envia o XP ganho para o servidor sem travar a thread principal.
        """
        def job():
            try:
                resp = requests.post(
                    "http://127.0.0.1:8000/api/score",
                    json={"session_id": self.session_id, "added_xp": added_xp},
                    timeout=3
                )
                resp.raise_for_status()
            except Exception as e:
                print("❌ Falha ao salvar XP no servidor:", e)

        threading.Thread(target=job, daemon=True).start()

    def on_show(self):
        arcade.set_background_color(self.COLORS["background"])
        if not self.questions:
            self.setup()

    def setup(self):
        """
        Busca perguntas da fase e reinicia estado de UI.
        """
        try:
            resp = requests.get(f"http://127.0.0.1:8000/api/quiz/{self.phase}", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list) or not data:
                return self._return_to_map()
            self.questions = data
            self.current = 0
            self.lives = self.max_lives
            self.floating_texts.clear()
            self.particle_system.particles.clear()
            self._build_option_boxes()
        except Exception:
            return self._return_to_map()

    def _return_to_map(self):
        """
        Volta para a view pai (mapa ou menu).
        """
        try:
            self.parent.setup()
            self.window.show_view(self.parent)
        except Exception:
            pass

    def _build_option_boxes(self):
        self.option_boxes.clear()
        if not self.questions:
            return
        w = SCREEN_WIDTH * 0.85
        h = SCREEN_HEIGHT * 0.18
        cx, cy = SCREEN_WIDTH/2, SCREEN_HEIGHT*0.80
        self.question_rect = (cx - w/2, cx + w/2, cy - h/2, cy + h/2)
        box_h = SCREEN_HEIGHT * 0.10
        start_y = SCREEN_HEIGHT * 0.50
        gap = box_h + SCREEN_HEIGHT * 0.02
        for i, text in enumerate(self.questions[self.current]["options"]):
            y = start_y - i * gap
            l, r = SCREEN_WIDTH * 0.12, SCREEN_WIDTH * 0.88
            b, t = y - box_h / 2, y + box_h / 2
            self.option_boxes.append({
                "rect": (l, r, b, t),
                "text": text,
                "hover": False,
                "pulse": 0.0
            })


    def _draw_animated_background(self):
        """
        Desenha o background (imagem ou cor sólida) animado.
        """
        if self.background:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                self.background
            )
        else:
            arcade.draw_lrbt_rectangle_filled(
                0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                self.COLORS["background"]
            )


    def _draw_xp_bar_container(self):
        """
        Desenha o contêiner da barra de XP no top da tela.
        """
        left, right = 20, SCREEN_WIDTH - 20
        bottom, top = SCREEN_HEIGHT - 60, SCREEN_HEIGHT - 20
        arcade.draw_lrbt_rectangle_filled(
            left, right, bottom, top,
            self.COLORS["xp_frame"]
        )
        arcade.draw_lrbt_rectangle_outline(
            left + 2, right - 2, bottom + 2, top - 2,
            self.COLORS["frame_border"],
            border_width=3
        )


    def _draw_hearts_with_effects(self):
        """
        Desenha corações de vidas com efeitos de pulsar e cor.
        """
        for idx, heart in enumerate(self.heart_list):
            heart.texture = (
                self.heart_full
                if idx < self.lives
                else self.heart_empty
            )
            # efeito de pulsar quando pouca vida
            if self.lives <= 2 and idx < self.lives:
                pulse = math.sin(self.animation * 10) * 0.10 + 1.0
                heart.scale = 0.35 * pulse
                if idx == self.lives - 1:
                    glow = math.sin(self.animation * 12) * 0.1 + 0.9
                    heart.color = (255, 255, int(200 * glow))
                else:
                    heart.color = (255, 255, 255)
            else:
                heart.scale = 0.3
                heart.color = (255, 255, 255)

            offset = math.sin(self.animation * 4 + idx) * 0.8
            heart.center_y = (SCREEN_HEIGHT - 20) + offset

        self.heart_list.draw()


    def _draw_phase_banner(self):
        """
        Mostra o número da fase no topo.
        """
        arcade.draw_text(
            f"Fase {self.phase}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 100,
            self.COLORS["text_gold"],
            font_size=26,
            anchor_x="center",
            font_name="Arial",
            bold=True
        )


    def _draw_question_frame(self):
        """
        Desenha o quadro que envolve o texto da pergunta.
        """
        if not self.questions:
            return

        l, r, b, t = self.question_rect
        cx, cy = (l + r) / 2, (b + t) / 2

        if self.frame_texture:
            try:
                arcade.draw_texture_rectangle(cx, cy, r - l, t - b, self.frame_texture)
            except Exception:
                # fallback gráfico
                arcade.draw_lrbt_rectangle_filled(l, r, b, t, self.COLORS["frame"])
                arcade.draw_lrbt_rectangle_outline(
                    l + 4, r - 4, b + 4, t - 4,
                    self.COLORS["frame_border"], border_width=2
                )
        else:
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, self.COLORS["frame"])
            arcade.draw_lrbt_rectangle_outline(
                l + 4, r - 4, b + 4, t - 4,
                self.COLORS["frame_border"], border_width=2
            )

        question = self.questions[self.current].get("question", "")
        arcade.draw_text(
            f"§ {question} §",
            cx, cy + 5,
            self.COLORS["text_gold"],
            font_size=22,
            width=int(r - l) - 50,
            align="center",
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True
        )


    def _draw_options_with_effects(self):
        """
        Desenha cada opção, com borda, cor e pulso.
        """
        if not self.questions:
            return

        for idx, box in enumerate(self.option_boxes):
            l, r, b, t = box["rect"]
            if box["hover"]:
                color = self.COLORS["option_hover"]
                border = arcade.color.GOLD
                box["pulse"] = min(box["pulse"] + 0.1, 0.3)
            else:
                color = self.COLORS["option_normal"]
                border = self.COLORS["option_border"]
                box["pulse"] = max(box["pulse"] - 0.05, 0.0)

            pulse = math.sin(self.animation * 8) * box["pulse"]
            cw = (r - l) + pulse * 10
            ch = (t - b) + pulse * 5
            cx, cy = (l + r) / 2, (b + t) / 2
            adj_l, adj_r = cx - cw / 2, cx + cw / 2
            adj_b, adj_t = cy - ch / 2, cy + ch / 2

            arcade.draw_lrbt_rectangle_filled(adj_l, adj_r, adj_b, adj_t, color)
            arcade.draw_lrbt_rectangle_outline(adj_l, adj_r, adj_b, adj_t, border, border_width=3 + int(pulse * 2))

            # número da opção
            arcade.draw_text(
                f"〔{idx+1}〕",
                l + 25, cy,
                self.COLORS["text_gold"],
                font_size=18,
                anchor_y="center",
                font_name="Arial",
                bold=True
            )
            # texto da opção
            arcade.draw_text(
                box["text"],
                l + 70, cy,
                arcade.color.WHITE,
                font_size=17,
                width=int(r - l) - 90,
                anchor_y="center",
                font_name="Arial"
            )


    def _draw_progress_indicator(self):
        """
        Mostra progresso Qtd Respondidas / Total.
        """
        if not self.questions:
            return

        arcade.draw_text(
            f"⦿ {self.current + 1} / {len(self.questions)} ⦿",
            SCREEN_WIDTH - 60, 35,
            self.COLORS["text_silver"],
            font_size=16,
            anchor_x="center",
            font_name="Arial"
        )


    def _draw_message(self, msg: str):
        """
        Mensagens centrais de status (ex: aguardando ou sem perguntas).
        """
        arcade.draw_text(
            msg,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            arcade.color.WHITE,
            font_size=26,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial"
        )


    def on_draw(self):
        self.clear()
        self._draw_animated_background()
        self._draw_xp_bar_container()
        self.xp_bar.draw()
        self._draw_hearts_with_effects()
        self._draw_phase_banner()

        if not self.questions:
            self._draw_message("Buscando perguntas...")
        else:
            self._draw_question_frame()
            self._draw_options_with_effects()
            self._draw_progress_indicator()

        self.particle_system.draw()
        for ft in list(self.floating_texts):
            ft.draw()


    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """
        Atualiza hover de cada opção conforme o mouse se move.
        """
        self.mouse_x, self.mouse_y = x, y


    def on_update(self, dt: float):
        """
        Anima partículas, textos flutuantes e hover.
        """
        self.animation += dt
        self.particle_system.update(dt)
        self.floating_texts[:] = [ft for ft in self.floating_texts if ft.update(dt)]

        for box in self.option_boxes:
            l, r, b, t = box["rect"]
            box["hover"] = (l < self.mouse_x < r and b < self.mouse_y < t)


    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """
        Trata clique em opção: acerto => ganha XP, erro => perde vida.
        No fim retorna ao mapa.
        """
        if not self.questions or self.lives <= 0:
            return
        if not (0 <= self.current < len(self.questions)):
            return

        correct_answer = self.questions[self.current]["answer"]

        for box in self.option_boxes:
            l, r, b, t = box["rect"]
            if l < x < r and b < y < t:
                hit = (box["text"] == correct_answer)
                if hit:
                    self.xp_bar.add_xp(15)
                    self._sync_xp_to_server(15)
                    self.floating_texts.append(
                        FloatingText(
                            "★ +15 XP! ★",
                            SCREEN_WIDTH / 2,
                            SCREEN_HEIGHT * 0.25,
                            (80, 200, 120),
                            "critical"
                        )
                    )
                    self.particle_system.create_effect(x, y, (0, 255, 100))
                else:
                    self.lives = max(0, self.lives - 1)
                    self.floating_texts.append(
                        FloatingText(
                            "✗ Errado! ✗",
                            SCREEN_WIDTH / 2,
                            SCREEN_HEIGHT * 0.25,
                            (255, 80, 80),
                            "critical"
                        )
                    )
                    self.particle_system.create_effect(x, y, (255, 50, 50))

                # Próxima pergunta ou retorno
                if self.current + 1 >= len(self.questions) or self.lives <= 0:
                    arcade.schedule(self._delayed_return, 1.5)
                else:
                    self.current += 1
                    self._build_option_boxes()
                break


    def _delayed_return(self, dt: float):
        """
        Aguarda animação e retorna à view pai.
        """
        arcade.unschedule(self._delayed_return)
        self._return_to_map()


    def on_key_press(self, key: int, modifiers: int):
        """
        Suporta ESC para sair e teclas 1–4 para respostas.
        """
        if key == arcade.key.ESCAPE:
            self._return_to_map()
            return

        # Teclas 1–4 replicam clique
        if arcade.key.KEY_1 <= key <= arcade.key.KEY_4:
            idx = key - arcade.key.KEY_1
            if idx < len(self.option_boxes):
                l, r, b, t = self.option_boxes[idx]["rect"]
                cx, cy = (l + r) / 2, (b + t) / 2
                self.on_mouse_press(cx, cy, arcade.MOUSE_BUTTON_LEFT, modifiers)
            return

        # ENTER/RETURN
        if key in (arcade.key.ENTER, arcade.key.RETURN):
            for box in self.option_boxes:
                l, r, b, t = box["rect"]
                if l < self.mouse_x < r and b < self.mouse_y < t:
                    self.on_mouse_press(self.mouse_x, self.mouse_y, arcade.MOUSE_BUTTON_LEFT, modifiers)
                    break
