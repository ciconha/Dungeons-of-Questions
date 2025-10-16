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
    AGORA COM 10 XP POR ACERTO
    """
    COLORS = {
        "background": (30, 30, 30),  # RGB escuro conforme prompt
        "frame": (45, 45, 45),       # Tom mais escuro para perguntas
        "frame_border": (100, 100, 100),  # Cinza médio
        "option_normal": (60, 60, 60),    # Botão normal
        "option_hover": (80, 80, 80),     # Botão hover  
        "option_border": (120, 120, 120), # Borda cinza claro
        "text_gold": (212, 175, 55),      # Dourado conforme prompt
        "text_silver": (230, 230, 230),   # Branco conforme prompt
        "life_red": (220, 60, 60),        # Vermelho para vidas
        "angel_blue": (60, 140, 220)      # Azul para anjo (futuro)
    }

    def __init__(self, phase: int, xp_bar: XPBar, session_id: str, parent: arcade.View):
        super().__init__()
        self.phase = phase
        self.xp_bar = xp_bar
        self.session_id = session_id
        self.parent = parent

        # Sistema de vidas e XP ATUALIZADO
        self.max_lives = 4  # 4 tentativas conforme solicitado
        self.lives = self.max_lives
        self.xp_per_correct = 10  # ✅ 10 XP POR ACERTO
        
        self.questions: List[Dict] = []
        self.current = 0
        self.option_boxes: List[Dict] = []
        self.floating_texts: List[FloatingText] = []
        self.particle_system = ParticleSystem()

        self.mouse_x = 0
        self.mouse_y = 0
        self.animation = 0.0

        self.background = None

        self._load_assets()
        self._setup_ui()

    def _load_assets(self):
        try:
            self.background = arcade.load_texture("assets/backgrounds/quiz_bg.jpg")
        except Exception:
            self.background = None

    def _setup_ui(self):
        """Configura a interface do usuário"""
        pass  # Não precisa mais setup complexo

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
            # ✅ CHAMA COMPLETAR FASE NO GAMEVIEW
            if hasattr(self.parent, '_completar_fase'):
                self.parent._completar_fase(self.phase)
            else:
                self.parent.setup()
            self.window.show_view(self.parent)
        except Exception:
            pass

    def _build_option_boxes(self):
        self.option_boxes.clear()
        if not self.questions:
            return
        
        # Caixa de pergunta (80% largura, 150px altura conforme prompt)
        w = SCREEN_WIDTH * 0.8
        h = 150
        cx, cy = SCREEN_WIDTH/2, SCREEN_HEIGHT - 180  # Abaixo do cabeçalho
        self.question_rect = (cx - w/2, cx + w/2, cy - h/2, cy + h/2)
        
        # Botões de resposta (60% largura, 50px altura) - AGORA COM 3 OPÇÕES
        box_w = SCREEN_WIDTH * 0.6
        box_h = 50
        start_y = SCREEN_HEIGHT * 0.45  # Ajustado para 3 opções
        gap = box_h + 15  # 15px entre botões
        
        # Pega até 3 opções da pergunta
        options = self.questions[self.current]["options"][:3]
        
        for i, text in enumerate(options):
            y = start_y - (i * gap)
            l, r = SCREEN_WIDTH * 0.2, SCREEN_WIDTH * 0.8  # Centralizado
            b, t = y - box_h/2, y + box_h/2
            
            self.option_boxes.append({
                "rect": (l, r, b, t),
                "text": text,
                "hover": False,
                "pulse": 0.0
            })

    def _draw_animated_background(self):
        """
        Desenha o background (imagem ou cor sólida).
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

    def _draw_life_bar(self):
        """
        Desenha a barra de vidas com círculos vermelhos.
        Cada erro remove um círculo da direita para a esquerda.
        """
        bar_width = 200
        bar_height = 60
        bar_x = SCREEN_WIDTH - bar_width - 20  # Topo direito
        bar_y = SCREEN_HEIGHT - 50
        
        # Desenha os círculos de vida
        circle_radius = 25
        circle_spacing = 10
        start_x = bar_x + circle_radius
        
        for i in range(self.max_lives):
            x = start_x + (i * (circle_radius * 2 + circle_spacing))
            y = bar_y
            
            # Círculo de fundo (vazio)
            arcade.draw_circle_filled(x, y, circle_radius, (80, 80, 80))
            arcade.draw_circle_outline(x, y, circle_radius, (120, 120, 120), 3)
            
            # Se tiver vida, preenche com vermelho
            if i < self.lives:
                # Efeito de pulsar na última vida
                if self.lives <= 2 and i == self.lives - 1:
                    pulse = math.sin(self.animation * 10) * 0.1 + 1.0
                    current_radius = circle_radius * pulse
                    arcade.draw_circle_filled(x, y, current_radius, self.COLORS["life_red"])
                else:
                    arcade.draw_circle_filled(x, y, circle_radius, self.COLORS["life_red"])
                
                # Borda do círculo preenchido
                arcade.draw_circle_outline(x, y, circle_radius, (255, 100, 100), 2)

    def _draw_xp_bar_at_top(self):
        """
        Desenha a barra de XP no topo esquerdo, completinha.
        """
        if not self.xp_bar:
            return
            
        bar_width = 200
        bar_height = 20
        bar_x = 20  # Topo esquerdo
        bar_y = SCREEN_HEIGHT - 40
        
        # Fundo da barra - CORRIGIDO
        arcade.draw_lrbt_rectangle_filled(
            bar_x, bar_x + bar_width,
            bar_y - bar_height/2, bar_y + bar_height/2,
            (50, 50, 50)
        )
        
        # Preenchimento da barra (XP atual)
        current_xp = self.xp_bar.current_xp
        max_xp = self.xp_bar.max_xp
        fill_width = (current_xp / max_xp) * bar_width if max_xp > 0 else 0
        
        if fill_width > 0:
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + fill_width,
                bar_y - bar_height/2, bar_y + bar_height/2,
                (100, 200, 255)  # Azul para XP
            )
        
        # Borda da barra - CORRIGIDO
        arcade.draw_lrbt_rectangle_outline(
            bar_x, bar_x + bar_width,
            bar_y - bar_height/2, bar_y + bar_height/2,
            (150, 150, 150),
            2
        )
        
        # Texto XP
        arcade.draw_text(
            f"XP: {current_xp}/{max_xp}",
            bar_x,
            bar_y + bar_height + 5,
            self.COLORS["text_silver"],
            14
        )

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
            bold=True
        )

    def _draw_question_frame(self):
        """
        Desenha a caixa de pergunta conforme prompt.
        """
        if not self.questions:
            return

        l, r, b, t = self.question_rect
        cx, cy = (l + r) / 2, (b + t) / 2

        # Caixa de fundo
        arcade.draw_lrbt_rectangle_filled(l, r, b, t, self.COLORS["frame"])
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            l, r, b, t,
            self.COLORS["frame_border"],
            border_width=4
        )

        # Texto da pergunta
        question = self.questions[self.current].get("question", "")
        arcade.draw_text(
            question,
            cx, cy,
            self.COLORS["text_silver"],
            font_size=18,
            width=int(r - l) - 40,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )

    def _draw_options_with_effects(self):
        """
        Desenha botões de opção conforme prompt.
        """
        if not self.questions:
            return

        for idx, box in enumerate(self.option_boxes):
            l, r, b, t = box["rect"]
            cx, cy = (l + r) / 2, (b + t) / 2
            width = r - l
            height = t - b

            # Cor baseada no hover
            if box["hover"]:
                color = self.COLORS["option_hover"]
                border = arcade.color.GOLD
            else:
                color = self.COLORS["option_normal"]
                border = self.COLORS["option_border"]

            # Botão - CORRIGIDO
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, color)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, border, 2)

            # Texto da opção com número (1, 2, 3)
            option_number = f"{idx + 1}. "
            full_text = option_number + box["text"]
            
            arcade.draw_text(
                full_text,
                cx, cy,
                self.COLORS["text_silver"],
                font_size=16,
                width=int(width) - 40,
                align="center",
                anchor_x="center",
                anchor_y="center"
            )

    def _draw_progress_indicator(self):
        """
        Mostra progresso.
        """
        if not self.questions:
            return

        arcade.draw_text(
            f"{self.current + 1} / {len(self.questions)}",
            SCREEN_WIDTH - 60, SCREEN_HEIGHT - 40,
            self.COLORS["text_silver"],
            font_size=16,
            anchor_x="center"
        )

    def _draw_header(self):
        """
        Cabeçalho 'Pergunta' conforme prompt.
        """
        arcade.draw_text(
            "Pergunta",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 60,
            self.COLORS["text_gold"],
            font_size=24,
            anchor_x="center",
            font_name="serif"
        )

    def on_draw(self):
        self.clear()
        self._draw_animated_background()
        
        # Header
        self._draw_header()
        
        # Elementos principais
        if not self.questions:
            arcade.draw_text(
                "Carregando perguntas...",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                arcade.color.WHITE,
                24,
                anchor_x="center",
                anchor_y="center"
            )
        else:
            self._draw_question_frame()
            self._draw_options_with_effects()
            self._draw_progress_indicator()

        # UI fixa - NOVA POSIÇÃO
        self._draw_xp_bar_at_top()  # Barra de XP no topo esquerdo
        self._draw_life_bar()       # Barra de vidas no topo direito
        self._draw_phase_banner()   # Banner da fase

        # Efeitos
        self.particle_system.draw()
        for ft in list(self.floating_texts):
            ft.draw()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """
        Atualiza hover de cada opção conforme o mouse se move.
        """
        self.mouse_x, self.mouse_y = x, y

        for box in self.option_boxes:
            l, r, b, t = box["rect"]
            box["hover"] = (l < x < r and b < y < t)

    def on_update(self, dt: float):
        """
        Anima partículas, textos flutuantes e hover.
        """
        self.animation += dt
        self.particle_system.update(dt)
        self.floating_texts[:] = [ft for ft in self.floating_texts if ft.update(dt)]

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """
        Trata clique em opção: acerto => ganha 10 XP, erro => perde vida.
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
                    # ✅ ACERTOU - GANHA 10 XP
                    xp_ganho = self.xp_per_correct
                    if self.xp_bar:
                        self.xp_bar.add_xp(xp_ganho)
                    self._sync_xp_to_server(xp_ganho)
                    
                    self.floating_texts.append(
                        FloatingText(
                            f"★ +{xp_ganho} XP! ★",
                            SCREEN_WIDTH / 2,
                            SCREEN_HEIGHT * 0.25,
                            (80, 200, 120),
                            "critical"
                        )
                    )
                    self.particle_system.create_effect(x, y, (0, 255, 100))
                else:
                    # ❌ ERROU - PERDE VIDA
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
        Suporta ESC para sair e teclas 1–3 para respostas.
        """
        if key == arcade.key.ESCAPE:
            self._return_to_map()
            return

        # Teclas 1–3 para selecionar opções (agora 3 opções)
        if arcade.key.KEY_1 <= key <= arcade.key.KEY_3:
            idx = key - arcade.key.KEY_1
            if idx < len(self.option_boxes):
                l, r, b, t = self.option_boxes[idx]["rect"]
                cx, cy = (l + r) / 2, (b + t) / 2
                self.on_mouse_press(cx, cy, arcade.MOUSE_BUTTON_LEFT, modifiers)
            return

        # ENTER/RETURN para opção hover
        if key in (arcade.key.ENTER, arcade.key.RETURN):
            for box in self.option_boxes:
                if box["hover"]:
                    l, r, b, t = box["rect"]
                    cx, cy = (l + r) / 2, (b + t) / 2
                    self.on_mouse_press(cx, cy, arcade.MOUSE_BUTTON_LEFT, modifiers)
                    break