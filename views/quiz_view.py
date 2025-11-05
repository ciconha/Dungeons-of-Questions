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
from api.db.mongo import mongo
from auth.simple_auth import auth_system
from auth.user_manager import user_manager


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


class ExampleView(arcade.View):
    """Tela de exemplo que aparece quando o usuário usa uma arma educativa"""
    
    def __init__(self, example_text: str, parent_view):
        super().__init__()
        self.example_text = example_text
        self.parent_view = parent_view
        
    def on_show(self):
        arcade.set_background_color((20, 15, 35, 240))
        
    def on_draw(self):
        self.clear()
        
        # Fundo semi-transparente
        arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, self.window.height, (20, 15, 35, 240))
        
        # Painel do exemplo
        panel_width = self.window.width * 0.8
        panel_height = self.window.height * 0.6
        panel_x = self.window.width / 2
        panel_y = self.window.height / 2
        
        # Fundo do painel
        arcade.draw_lrbt_rectangle_filled(
            panel_x - panel_width/2, panel_x + panel_width/2,
            panel_y - panel_height/2, panel_y + panel_height/2,
            (35, 30, 45)
        )
        
        # Borda dourada
        arcade.draw_lrbt_rectangle_outline(
            panel_x - panel_width/2, panel_x + panel_width/2,
            panel_y - panel_height/2, panel_y + panel_height/2,
            (212, 175, 55), 3
        )
        
        # Título
        arcade.draw_text(
            "💡 EXEMPLO ILUSTRATIVO",
            panel_x, panel_y + panel_height/2 - 50,
            (255, 215, 0), 28,
            anchor_x="center", bold=True
        )
        
        # Texto do exemplo
        arcade.draw_text(
            self.example_text,
            panel_x, panel_y,
            (200, 200, 200), 18,
            width=panel_width - 80,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )
        
        # Botão OK
        button_width = 120
        button_height = 50
        button_x = panel_x
        button_y = panel_y - panel_height/2 + 70
        
        # Fundo do botão
        arcade.draw_lrbt_rectangle_filled(
            button_x - button_width/2, button_x + button_width/2,
            button_y - button_height/2, button_y + button_height/2,
            (0, 150, 0)
        )
        
        # Borda do botão
        arcade.draw_lrbt_rectangle_outline(
            button_x - button_width/2, button_x + button_width/2,
            button_y - button_height/2, button_y + button_height/2,
            (255, 255, 255), 2
        )
        
        # Texto do botão
        arcade.draw_text(
            "CONTINUAR",
            button_x, button_y,
            (255, 255, 255), 20,
            anchor_x="center", anchor_y="center", bold=True
        )
        
        # Salvar retângulo do botão para clique
        self.ok_button = (
            button_x - button_width/2, button_x + button_width/2,
            button_y - button_height/2, button_y + button_height/2
        )
        
    def on_mouse_press(self, x, y, button, modifiers):
        # Verifica clique no botão OK
        l, r, b, t = self.ok_button
        if l <= x <= r and b <= y <= t:
            self.window.show_view(self.parent_view)
            
    def on_key_press(self, key, modifiers):
        # Qualquer tecla ou ENTER fecha o exemplo
        if key in (arcade.key.ENTER, arcade.key.RETURN, arcade.key.SPACE, arcade.key.ESCAPE):
            self.window.show_view(self.parent_view)
            
    def on_resize(self, width, height):
        """Handle window resize"""
        self.window.set_viewport(0, width, 0, height)


class QuizResultView(arcade.View):
    """Tela de resultado do quiz"""
    
    def __init__(self, phase: int, correct_answers: int, wrong_answers: int, xp_earned: int, 
                 coins_earned: int, parent: arcade.View):
        super().__init__()
        self.phase = phase
        self.correct_answers = correct_answers
        self.wrong_answers = wrong_answers
        self.xp_earned = xp_earned
        self.coins_earned = coins_earned
        self.parent = parent
        
        # Verifica se passou de fase (3 ou mais acertos)
        self.passed_phase = correct_answers >= 3
        
        # Botões
        self.retry_button = None
        self.next_phase_button = None
        
    def on_show(self):
        arcade.set_background_color((20, 15, 35))
        
    def on_draw(self):
        self.clear()
        
        # Fundo
        arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, self.window.height, (20, 15, 35))
        
        # Painel principal
        panel_width = self.window.width * 0.7
        panel_height = self.window.height * 0.7
        panel_x = self.window.width / 2
        panel_y = self.window.height / 2
        
        # Fundo do painel
        arcade.draw_lrbt_rectangle_filled(
            panel_x - panel_width/2, panel_x + panel_width/2,
            panel_y - panel_height/2, panel_y + panel_height/2,
            (35, 30, 45)
        )
        
        # Borda dourada
        arcade.draw_lrbt_rectangle_outline(
            panel_x - panel_width/2, panel_x + panel_width/2,
            panel_y - panel_height/2, panel_y + panel_height/2,
            (212, 175, 55), 3
        )
        
        # Título
        title = "🎉 PARABÉNS! 🎉" if self.passed_phase else "💀 FASE FALHADA"
        title_color = (0, 255, 0) if self.passed_phase else (255, 50, 50)
        
        arcade.draw_text(
            title,
            panel_x, panel_y + panel_height/2 - 50,
            title_color, 32,
            anchor_x="center", bold=True
        )
        
        # Resultados
        results_y = panel_y + panel_height/2 - 120
        
        # XP Ganho
        arcade.draw_text(
            f"⭐ XP Ganho: {self.xp_earned}",
            panel_x, results_y,
            (255, 215, 0), 24,
            anchor_x="center"
        )
        
        # Moedas Ganhas
        arcade.draw_text(
            f"💰 Moedas: +{self.coins_earned}",
            panel_x, results_y - 40,
            (255, 215, 0), 24,
            anchor_x="center"
        )
        
        # Acertos
        arcade.draw_text(
            f"✅ Acertos: {self.correct_answers}",
            panel_x, results_y - 80,
            (0, 255, 0), 20,
            anchor_x="center"
        )
        
        # Erros
        arcade.draw_text(
            f"❌ Erros: {self.wrong_answers}",
            panel_x, results_y - 110,
            (255, 50, 50), 20,
            anchor_x="center"
        )
        
        # Status da fase
        status_text = "✅ FASE COMPLETADA!" if self.passed_phase else "❌ FALHOU - TENTE NOVAMENTE"
        arcade.draw_text(
            status_text,
            panel_x, results_y - 160,
            title_color, 22,
            anchor_x="center", bold=True
        )
        
        # Botões
        button_width = 200
        button_height = 50
        button_y = panel_y - panel_height/2 + 100
        
        # Botão Refazer
        self.retry_button = (
            panel_x - button_width - 20, panel_x - 20,
            button_y - button_height/2, button_y + button_height/2
        )
        
        arcade.draw_lrbt_rectangle_filled(*self.retry_button, (139, 0, 0))
        arcade.draw_lrbt_rectangle_outline(*self.retry_button, (255, 255, 255), 2)
        arcade.draw_text(
            "🔁 REFAZER",
            panel_x - button_width/2 - 20, button_y,
            (255, 255, 255), 18,
            anchor_x="center", anchor_y="center", bold=True
        )
        
        # Botão Próxima Fase (só se passou)
        if self.passed_phase:
            self.next_phase_button = (
                panel_x + 20, panel_x + button_width + 20,
                button_y - button_height/2, button_y + button_height/2
            )
            
            arcade.draw_lrbt_rectangle_filled(*self.next_phase_button, (0, 150, 0))
            arcade.draw_lrbt_rectangle_outline(*self.next_phase_button, (255, 255, 255), 2)
            arcade.draw_text(
                "➡️ PRÓXIMA FASE",
                panel_x + button_width/2 + 20, button_y,
                (255, 255, 255), 18,
                anchor_x="center", anchor_y="center", bold=True
            )
        
        # Instrução F11
        arcade.draw_text(
            "💡 Dica: Pressione F11 para tela cheia",
            self.window.width / 2, 30,
            (150, 150, 150), 14,
            anchor_x="center"
        )
    
    def on_mouse_press(self, x, y, button, modifiers):
        # Botão Refazer
        if self.retry_button:
            l, r, b, t = self.retry_button
            if l <= x <= r and b <= y <= t:
                # Reseta completamente o quiz
                self.parent.setup()
                self.window.show_view(self.parent)
                return
        
        # Botão Próxima Fase
        if self.passed_phase and self.next_phase_button:
            l, r, b, t = self.next_phase_button
            if l <= x <= r and b <= y <= t:
                # Avança para próxima fase
                if hasattr(self.parent, 'avancar_fase'):
                    self.parent.avancar_fase()
                self.window.show_view(self.parent)
                return
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
            self.window.set_viewport(0, self.window.width, 0, self.window.height)
            
    def on_resize(self, width, height):
        """Handle window resize"""
        self.window.set_viewport(0, width, 0, height)


class QuizView(arcade.View):
    """
    Tela de quiz para uma fase específica.
    Sistema completo com hotbar, mana, vidas e recompensas.
    """
    COLORS = {
        "background": (30, 30, 30),
        "frame": (45, 45, 45),
        "frame_border": (100, 100, 100),
        "option_normal": (60, 60, 60),
        "option_hover": (80, 80, 80),
        "option_border": (120, 120, 120),
        "text_gold": (212, 175, 55),
        "text_silver": (230, 230, 230),
        "life_red": (220, 60, 60),
        "mana_blue": (60, 140, 220),
        "hotbar_slot": (80, 80, 80),
        "hotbar_active": (100, 200, 100)
    }

    def __init__(self, phase: int, xp_bar: XPBar, session_id: str, parent: arcade.View):
        super().__init__()
        self.phase = phase
        self.xp_bar = xp_bar
        self.session_id = session_id
        self.parent = parent

        # Sistema de vidas e mana
        self.max_lives = 4
        self.lives = self.max_lives
        self.max_mana = 5
        self.mana = self.max_mana
        self.xp_per_correct = 10
        
        # Sistema de hotbar
        self.hotbar_slots = {
            '1': None, '2': None, '3': None, '4': None,
            '5': None, '6': None, '7': None, '8': None,
            'A': None, 'B': None, 'C': None, 'D': None,
            'E': None, 'F': None, 'G': None
        }
        
        # Estatísticas da sessão
        self.correct_answers = 0
        self.wrong_answers = 0
        self.total_xp_earned = 0
        
        # Itens usados nesta fase
        self.used_items = set()
        
        # Efeitos ativos
        self.active_effects = {
            "double_xp": False,
            "reveal_letter": False,
            "remove_wrong": False,
            "extra_time": False
        }
        
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
        self._load_hotbar_from_user()
        self._setup_ui()

    def _load_assets(self):
        try:
            self.background = arcade.load_texture("assets/backgrounds/quiz_bg.jpg")
        except Exception:
            self.background = None

    def _load_hotbar_from_user(self):
        """Carrega a hotbar do usuário a partir dos dados salvos"""
        try:
            user = user_manager.get_current_user()
            user_data = auth_system.get_user_data(user) or {}
            hotbar_data = user_data.get("hotbar", {})
            
            for slot, item_id in hotbar_data.items():
                if slot in self.hotbar_slots:
                    self.hotbar_slots[slot] = item_id
            
            print(f"🎮 Hotbar carregada: {len([x for x in self.hotbar_slots.values() if x])} itens equipados")
        except Exception as e:
            print(f"⚠️ Erro ao carregar hotbar: {e}")

    def _setup_ui(self):
        """Configura a interface do usuário"""
        pass

    def _sync_xp_to_server(self, added_xp: int):
        """Envia o XP ganho para o servidor"""
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

    def _save_coins_to_user(self, coins: int):
        """Salva as moedas ganhas no perfil do usuário"""
        try:
            user = user_manager.get_current_user()
            user_data = auth_system.get_user_data(user) or {}
            current_coins = user_data.get("coins", 0)
            user_data["coins"] = current_coins + coins
            
            auth_system.update_user_data(user, user_data)
            print(f"💰 {coins} moedas salvas no perfil do usuário")
        except Exception as e:
            print(f"❌ Erro ao salvar moedas: {e}")

    def on_show(self):
        arcade.set_background_color(self.COLORS["background"])
        if not self.questions:
            self.setup()

    def setup(self):
        """Busca perguntas da fase e reinicia estado COMPLETAMENTE"""
        try:
            resp = requests.get(f"http://127.0.0.1:8000/api/quiz/{self.phase}", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list) or not data:
                return self._return_to_map()
            self.questions = data
            self.current = 0
            self.lives = self.max_lives
            self.mana = self.max_mana
            self.correct_answers = 0
            self.wrong_answers = 0
            self.total_xp_earned = 0
            self.used_items.clear()
            self.active_effects = {key: False for key in self.active_effects}
            self.floating_texts.clear()
            self.particle_system.particles.clear()
            self._build_option_boxes()
            print(f"🔄 Quiz da fase {self.phase} resetado completamente")
        except Exception:
            return self._return_to_map()

    def _return_to_map(self):
        """Volta para a view pai (mapa ou menu)"""
        try:
            if hasattr(self.parent, '_completar_fase'):
                self.parent._completar_fase(self.phase)
            else:
                self.parent.setup()
            self.window.show_view(self.parent)
        except Exception:
            pass

    def _show_result_screen(self):
        """Mostra a tela de resultados"""
        # Calcula moedas ganhas (10 moedas por fase completada)
        coins_earned = 10 if self.correct_answers >= 3 else 0
        
        # Salva moedas no perfil
        if coins_earned > 0:
            self._save_coins_to_user(coins_earned)
        
        # Cria e mostra a tela de resultados
        result_view = QuizResultView(
            phase=self.phase,
            correct_answers=self.correct_answers,
            wrong_answers=self.wrong_answers,
            xp_earned=self.total_xp_earned,
            coins_earned=coins_earned,
            parent=self
        )
        self.window.show_view(result_view)

    def avancar_fase(self):
        """Avança para a próxima fase"""
        try:
            if hasattr(self.parent, 'avancar_fase'):
                self.parent.avancar_fase()
        except Exception as e:
            print(f"❌ Erro ao avançar fase: {e}")

    def _build_option_boxes(self):
        self.option_boxes.clear()
        if not self.questions:
            return
        
        # Caixa de pergunta
        w = self.window.width * 0.8
        h = 150
        cx, cy = self.window.width/2, self.window.height - 180
        self.question_rect = (cx - w/2, cx + w/2, cy - h/2, cy + h/2)
        
        # Botões de resposta
        box_w = self.window.width * 0.6
        box_h = 50
        start_y = self.window.height * 0.45
        gap = box_h + 15
        
        options = self.questions[self.current]["options"][:3]
        
        for i, text in enumerate(options):
            y = start_y - (i * gap)
            l, r = self.window.width * 0.2, self.window.width * 0.8
            b, t = y - box_h/2, y + box_h/2
            
            self.option_boxes.append({
                "rect": (l, r, b, t),
                "text": text,
                "hover": False,
                "pulse": 0.0
            })

    def _draw_animated_background(self):
        if self.background:
            arcade.draw_texture_rectangle(
                self.window.width / 2,
                self.window.height / 2,
                self.window.width,
                self.window.height,
                self.background
            )
        else:
            arcade.draw_lrbt_rectangle_filled(
                0, self.window.width, 0, self.window.height,
                self.COLORS["background"]
            )

    def _draw_life_bar(self):
        bar_width = 200
        bar_height = 60
        bar_x = self.window.width - bar_width - 20
        bar_y = self.window.height - 50
        
        # Título
        arcade.draw_text(
            "VIDA",
            bar_x + bar_width/2,
            bar_y + 40,
            self.COLORS["text_silver"],
            16,
            anchor_x="center",
            bold=True
        )
        
        # Círculos de vida
        circle_radius = 20
        circle_spacing = 8
        start_x = bar_x + circle_radius
        
        for i in range(self.max_lives):
            x = start_x + (i * (circle_radius * 2 + circle_spacing))
            y = bar_y
            
            # Círculo de fundo
            arcade.draw_circle_filled(x, y, circle_radius, (80, 80, 80))
            arcade.draw_circle_outline(x, y, circle_radius, (120, 120, 120), 2)
            
            # Vida preenchida
            if i < self.lives:
                if self.lives <= 2 and i == self.lives - 1:
                    pulse = math.sin(self.animation * 10) * 0.1 + 1.0
                    current_radius = circle_radius * pulse
                    arcade.draw_circle_filled(x, y, current_radius, self.COLORS["life_red"])
                else:
                    arcade.draw_circle_filled(x, y, circle_radius, self.COLORS["life_red"])
                arcade.draw_circle_outline(x, y, circle_radius, (255, 100, 100), 2)

    def _draw_mana_bar(self):
        bar_width = 200
        bar_height = 60
        bar_x = self.window.width - bar_width - 20
        bar_y = self.window.height - 120
        
        # Título
        arcade.draw_text(
            "MANA",
            bar_x + bar_width/2,
            bar_y + 40,
            self.COLORS["text_silver"],
            16,
            anchor_x="center",
            bold=True
        )
        
        # Círculos de mana
        circle_radius = 20
        circle_spacing = 8
        start_x = bar_x + circle_radius
        
        for i in range(self.max_mana):
            x = start_x + (i * (circle_radius * 2 + circle_spacing))
            y = bar_y
            
            # Círculo de fundo
            arcade.draw_circle_filled(x, y, circle_radius, (80, 80, 80))
            arcade.draw_circle_outline(x, y, circle_radius, (120, 120, 120), 2)
            
            # Mana preenchida
            if i < self.mana:
                if self.mana <= 2 and i == self.mana - 1:
                    pulse = math.sin(self.animation * 10) * 0.1 + 1.0
                    current_radius = circle_radius * pulse
                    arcade.draw_circle_filled(x, y, current_radius, self.COLORS["mana_blue"])
                else:
                    arcade.draw_circle_filled(x, y, circle_radius, self.COLORS["mana_blue"])
                arcade.draw_circle_outline(x, y, circle_radius, (100, 180, 255), 2)

    def _draw_hotbar(self):
        bar_width = min(500, self.window.width * 0.8)
        bar_height = 80
        bar_x = self.window.width / 2
        bar_y = 60
        
        # Fundo da hotbar
        arcade.draw_lrbt_rectangle_filled(
            bar_x - bar_width/2, bar_x + bar_width/2,
            bar_y - bar_height/2, bar_y + bar_height/2,
            (40, 40, 40, 200)
        )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            bar_x - bar_width/2, bar_x + bar_width/2,
            bar_y - bar_height/2, bar_y + bar_height/2,
            (100, 100, 100), 2
        )
        
        # Slots
        slot_size = min(50, bar_width / 16)
        spacing = 10
        start_x = bar_x - (bar_width / 2) + slot_size/2
        
        # Slots numéricos (1-8)
        for i in range(8):
            slot_x = start_x + (i * (slot_size + spacing))
            slot_id = str(i + 1)
            self._draw_hotbar_slot(slot_x, bar_y, slot_size, slot_id, is_circle=False)
        
        # Slots de letras (A-G)
        for i in range(7):
            slot_x = start_x + (i * (slot_size + spacing))
            slot_id = chr(65 + i)
            self._draw_hotbar_slot(slot_x, bar_y - 65, slot_size, slot_id, is_circle=True)

    def _draw_hotbar_slot(self, x, y, size, slot_id, is_circle=False):
        bg_color = self.COLORS["hotbar_slot"]
        
        item_id = self.hotbar_slots.get(slot_id)
        if item_id:
            if slot_id in self.used_items:
                bg_color = (100, 100, 100)
            else:
                bg_color = self.COLORS["hotbar_active"]
        
        if is_circle:
            arcade.draw_circle_filled(x, y, size/2, bg_color)
            arcade.draw_circle_outline(x, y, size/2, (200, 200, 200), 2)
        else:
            arcade.draw_lrbt_rectangle_filled(
                x - size/2, x + size/2, y - size/2, y + size/2,
                bg_color
            )
            arcade.draw_lrbt_rectangle_outline(
                x - size/2, x + size/2, y - size/2, y + size/2,
                (200, 200, 200), 2
            )
        
        arcade.draw_text(
            slot_id, x, y,
            (255, 255, 255), 14,
            anchor_x="center", anchor_y="center", bold=True
        )
        
        item_id = self.hotbar_slots.get(slot_id)
        if item_id:
            item_icons = {
                "potion_health": "❤️",
                "potion_mana": "🔵", 
                "weapon_sword": "⚔️",
                "weapon_staff": "🔮",
                "skill_focus": "🧠",
                "skill_time": "⏱️"
            }
            
            icon = item_icons.get(item_id, "❓")
            arcade.draw_text(
                icon, x, y - 2,
                (255, 255, 255), 20,
                anchor_x="center", anchor_y="center"
            )

    def _draw_xp_bar_at_top(self):
        if not self.xp_bar:
            return
            
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = self.window.height - 40
        
        arcade.draw_lrbt_rectangle_filled(
            bar_x, bar_x + bar_width,
            bar_y - bar_height/2, bar_y + bar_height/2,
            (50, 50, 50)
        )
        
        current_xp = self.xp_bar.current_xp
        max_xp = self.xp_bar.max_xp
        fill_width = (current_xp / max_xp) * bar_width if max_xp > 0 else 0
        
        if fill_width > 0:
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + fill_width,
                bar_y - bar_height/2, bar_y + bar_height/2,
                (100, 200, 255)
            )
        
        arcade.draw_lrbt_rectangle_outline(
            bar_x, bar_x + bar_width,
            bar_y - bar_height/2, bar_y + bar_height/2,
            (150, 150, 150), 2
        )
        
        arcade.draw_text(
            f"XP: {current_xp}/{max_xp}",
            bar_x,
            bar_y + bar_height + 5,
            self.COLORS["text_silver"],
            14
        )

    def _draw_phase_banner(self):
        arcade.draw_text(
            f"Fase {self.phase}",
            self.window.width / 2,
            self.window.height - 100,
            self.COLORS["text_gold"],
            font_size=26,
            anchor_x="center",
            bold=True
        )

    def _draw_question_frame(self):
        if not self.questions:
            return

        l, r, b, t = self.question_rect
        cx, cy = (l + r) / 2, (b + t) / 2

        arcade.draw_lrbt_rectangle_filled(l, r, b, t, self.COLORS["frame"])
        arcade.draw_lrbt_rectangle_outline(
            l, r, b, t,
            self.COLORS["frame_border"],
            border_width=4
        )

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
        if not self.questions:
            return

        for idx, box in enumerate(self.option_boxes):
            l, r, b, t = box["rect"]
            cx, cy = (l + r) / 2, (b + t) / 2
            width = r - l
            height = t - b

            if box["hover"]:
                color = self.COLORS["option_hover"]
                border = arcade.color.GOLD
            else:
                color = self.COLORS["option_normal"]
                border = self.COLORS["option_border"]

            arcade.draw_lrbt_rectangle_filled(l, r, b, t, color)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, border, 2)

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
        if not self.questions:
            return

        arcade.draw_text(
            f"{self.current + 1} / {len(self.questions)}",
            self.window.width - 60, self.window.height - 40,
            self.COLORS["text_silver"],
            font_size=16,
            anchor_x="center"
        )

    def _draw_header(self):
        arcade.draw_text(
            "Pergunta",
            self.window.width / 2,
            self.window.height - 60,
            self.COLORS["text_gold"],
            font_size=24,
            anchor_x="center",
            font_name="serif"
        )

    def _draw_active_effects(self):
        if any(self.active_effects.values()):
            effects_x = self.window.width - 200
            effects_y = self.window.height - 180
            
            arcade.draw_text(
                "Efeitos Ativos:",
                effects_x, effects_y,
                self.COLORS["text_gold"],
                14,
                bold=True
            )
            
            effect_icons = {
                "double_xp": "⭐",
                "reveal_letter": "🔤", 
                "remove_wrong": "❌",
                "extra_time": "⏱️"
            }
            
            y_offset = effects_y - 25
            for effect, active in self.active_effects.items():
                if active:
                    arcade.draw_text(
                        effect_icons.get(effect, "✨"),
                        effects_x, y_offset,
                        (0, 255, 0), 20
                    )
                    y_offset -= 25

    def _draw_fullscreen_hint(self):
        """Desenha aviso sobre F11 para tela cheia"""
        arcade.draw_text(
            "💡 Pressione F11 para Tela Cheia",
            self.window.width / 2, 30,
            (150, 150, 150), 14,
            anchor_x="center"
        )

    def on_draw(self):
        self.clear()
        self._draw_animated_background()
        
        self._draw_header()
        
        if not self.questions:
            arcade.draw_text(
                "Carregando perguntas...",
                self.window.width / 2,
                self.window.height / 2,
                arcade.color.WHITE,
                24,
                anchor_x="center",
                anchor_y="center"
            )
        else:
            self._draw_question_frame()
            self._draw_options_with_effects()
            self._draw_progress_indicator()

        self._draw_xp_bar_at_top()
        self._draw_life_bar()
        self._draw_mana_bar()
        self._draw_phase_banner()
        self._draw_hotbar()
        self._draw_active_effects()
        self._draw_fullscreen_hint()

        self.particle_system.draw()
        for ft in list(self.floating_texts):
            ft.draw()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x, self.mouse_y = x, y

        for box in self.option_boxes:
            l, r, b, t = box["rect"]
            box["hover"] = (l < x < r and b < y < t)

    def on_update(self, dt: float):
        self.animation += dt
        self.particle_system.update(dt)
        self.floating_texts[:] = [ft for ft in self.floating_texts if ft.update(dt)]

    def _use_item(self, slot_id: str, item_id: str):
        """Usa um item da hotbar - SÓ PODE SER USADO UMA VEZ POR FASE"""
        if slot_id in self.used_items:
            self._show_message(f"❌ Item já usado nesta fase!", 2.0)
            return False
        
        if item_id in ["weapon_staff", "skill_focus", "skill_time"] and self.mana < 2:
            self._show_message("❌ Mana insuficiente!", 2.0)
            return False
        
        success = False
        message = ""
        
        if item_id == "potion_health":
            if self.lives < self.max_lives:
                self.lives = min(self.max_lives, self.lives + 1)
                success = True
                message = "❤️ +1 Vida!"
            else:
                message = "❌ Vida máxima!"
        
        elif item_id == "potion_mana":
            if self.mana < self.max_mana:
                self.mana = min(self.max_mana, self.mana + 2)
                success = True
                message = "🔵 +2 Mana!"
            else:
                message = "❌ Mana máxima!"
        
        elif item_id == "weapon_sword":
            self.active_effects["double_xp"] = True
            success = True
            message = "⚔️ XP Dobrado!"
            # Mostra exemplo educativo
            self._show_example()
        
        elif item_id == "weapon_staff":
            self.active_effects["reveal_letter"] = True
            self.mana -= 2
            success = True
            message = "🔮 Revelar Letra!"
            # Mostra exemplo educativo
            self._show_example()
        
        elif item_id == "skill_focus":
            self.active_effects["remove_wrong"] = True
            self.mana -= 2
            success = True
            message = "🧠 Remover Opção!"
            # Mostra exemplo educativo
            self._show_example()
        
        elif item_id == "skill_time":
            self.active_effects["extra_time"] = True
            self.mana -= 2
            success = True
            message = "⏱️ Tempo Extra!"
        
        if success:
            self.used_items.add(slot_id)
            self._show_message(message, 2.0)
            self.particle_system.create_effect(
                self.window.width / 2, self.window.height / 2,
                (0, 255, 255)
            )
            return True
        else:
            self._show_message(message, 2.0)
            return False

    def _show_example(self):
        """Mostra tela de exemplo educativo"""
        if self.questions and self.current < len(self.questions):
            example_text = self.questions[self.current].get("example", "📚 Exemplo educativo não disponível para esta pergunta.")
            example_view = ExampleView(example_text, self)
            self.window.show_view(example_view)

    def _show_message(self, message: str, duration: float):
        self.floating_texts.append(
            FloatingText(
                message,
                self.window.width / 2,
                self.window.height * 0.75,
                (255, 255, 255),
                "critical" if "❌" in message else "normal"
            )
        )

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """Lida com cliques do mouse - números e áreas de opção"""
        if not self.questions or self.lives <= 0:
            return
        if not (0 <= self.current < len(self.questions)):
            return

        correct_answer = self.questions[self.current]["answer"]

        # Verifica clique nas opções
        for box in self.option_boxes:
            l, r, b, t = box["rect"]
            if l < x < r and b < y < t:
                self._process_answer(box["text"] == correct_answer, x, y)
                return

        # Verifica clique na hotbar
        bar_width = min(500, self.window.width * 0.8)
        bar_height = 80
        bar_x = self.window.width / 2
        bar_y = 60
        
        slot_size = min(50, bar_width / 16)
        spacing = 10
        start_x = bar_x - (bar_width / 2) + slot_size/2
        
        # Slots numéricos (1-8)
        for i in range(8):
            slot_x = start_x + (i * (slot_size + spacing))
            slot_id = str(i + 1)
            slot_rect = (slot_x - slot_size/2, slot_x + slot_size/2, bar_y - slot_size/2, bar_y + slot_size/2)
            l, r, b, t = slot_rect
            if l < x < r and b < y < t:
                item_id = self.hotbar_slots.get(slot_id)
                if item_id:
                    self._use_item(slot_id, item_id)
                return
        
        # Slots de letras (A-G)
        for i in range(7):
            slot_x = start_x + (i * (slot_size + spacing))
            slot_id = chr(65 + i)
            slot_radius = slot_size/2
            # Verifica clique em círculo (teorema de Pitágoras)
            dx = x - slot_x
            dy = y - (bar_y - 65)
            distance = math.sqrt(dx*dx + dy*dy)
            if distance <= slot_radius:
                item_id = self.hotbar_slots.get(slot_id)
                if item_id:
                    self._use_item(slot_id, item_id)
                return

    def _process_answer(self, is_correct: bool, x: float, y: float):
        """Processa a resposta do usuário"""
        xp_multiplier = 2 if self.active_effects["double_xp"] else 1
        
        if is_correct:
            xp_ganho = self.xp_per_correct * xp_multiplier
            if self.xp_bar:
                self.xp_bar.add_xp(xp_ganho)
            self._sync_xp_to_server(xp_ganho)
            
            self.correct_answers += 1
            self.total_xp_earned += xp_ganho
            
            self.floating_texts.append(
                FloatingText(
                    f"★ +{xp_ganho} XP! ★",
                    self.window.width / 2,
                    self.window.height * 0.25,
                    (80, 200, 120),
                    "critical"
                )
            )
            self.particle_system.create_effect(x, y, (0, 255, 100))
        else:
            self.lives = max(0, self.lives - 1)
            self.wrong_answers += 1
            
            self.floating_texts.append(
                FloatingText(
                    "✗ Errado! ✗",
                    self.window.width / 2,
                    self.window.height * 0.25,
                    (255, 80, 80),
                    "critical"
                )
            )
            self.particle_system.create_effect(x, y, (255, 50, 50))

        # Verifica se terminou o quiz ou perdeu todas as vidas
        if self.current + 1 >= len(self.questions) or self.lives <= 0:
            arcade.schedule(self._delayed_result, 1.5)
        else:
            self.current += 1
            self._build_option_boxes()

    def _delayed_result(self, dt: float):
        arcade.unschedule(self._delayed_result)
        self._show_result_screen()

    def on_key_press(self, key: int, modifiers: int):
        """Lida com pressionamento de teclas - números e letras"""
        if key == arcade.key.ESCAPE:
            self._return_to_map()
            return

        # Teclas 1, 2, 3 para opções
        if arcade.key.KEY_1 <= key <= arcade.key.KEY_3:
            option_index = key - arcade.key.KEY_1
            if 0 <= option_index < len(self.option_boxes):
                box = self.option_boxes[option_index]
                l, r, b, t = box["rect"]
                cx, cy = (l + r) / 2, (b + t) / 2
                self.on_mouse_press(cx, cy, arcade.MOUSE_BUTTON_LEFT, modifiers)
            return

        # Teclas A, B, C para opções
        if arcade.key.A <= key <= arcade.key.C:
            option_index = key - arcade.key.A
            if 0 <= option_index < len(self.option_boxes):
                box = self.option_boxes[option_index]
                l, r, b, t = box["rect"]
                cx, cy = (l + r) / 2, (b + t) / 2
                self.on_mouse_press(cx, cy, arcade.MOUSE_BUTTON_LEFT, modifiers)
            return

        # ENTER para opção hover
        if key in (arcade.key.ENTER, arcade.key.RETURN):
            for box in self.option_boxes:
                if box["hover"]:
                    l, r, b, t = box["rect"]
                    cx, cy = (l + r) / 2, (b + t) / 2
                    self.on_mouse_press(cx, cy, arcade.MOUSE_BUTTON_LEFT, modifiers)
                    break

        # HOTBAR: Teclas 1-8 para armas/habilidades
        if arcade.key.KEY_1 <= key <= arcade.key.KEY_8:
            slot_id = str(key - arcade.key.KEY_1 + 1)
            item_id = self.hotbar_slots.get(slot_id)
            if item_id:
                self._use_item(slot_id, item_id)
            return

        # HOTBAR: Teclas A-G para poções
        if arcade.key.A <= key <= arcade.key.G:
            slot_id = chr(key)
            item_id = self.hotbar_slots.get(slot_id)
            if item_id:
                self._use_item(slot_id, item_id)
            return

        # F11 para tela cheia
        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
            self.window.set_viewport(0, self.window.width, 0, self.window.height)
            
    def on_resize(self, width, height):
        """Handle window resize - mantém a proporção e viewport correta"""
        self.window.set_viewport(0, width, 0, height)
        # Recalcula as posições dos elementos
        if self.questions:
            self._build_option_boxes()