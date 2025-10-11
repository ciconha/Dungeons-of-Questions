# views/game_view.py

import arcade
import xml.etree.ElementTree as ET
import requests
import math

from config import RAW_MAP_PATH, TEMP_MAP_PATH, TILE_SIZE, PHASE_TRIGGER_CODES
from assets.xp.xp import XPBar
from auth.user_manager import user_manager
from auth.simple_auth import auth_system


class GameView(arcade.View):
    """
    Carrega o mapa TMX, controla movimento de Emilly,
    detecta triggers de fase e inicia o QuizView ao ENTER.
    AGORA INTEGRADO COM USER_MANAGER E AUTH_SYSTEM
    """

    def __init__(self, xp_bar: XPBar = None, session_id: str = "", on_exit_callback=None):
        super().__init__()
        self.xp_bar = xp_bar
        self.session_id = session_id
        self.on_exit_callback = on_exit_callback
        
        # Obtém usuário atual do UserManager
        self.current_user = user_manager.get_current_user()
        self.user_data = None

        self.scene = None
        self.player_sprite = None

        self.keys = {
            arcade.key.W: False,
            arcade.key.A: False,
            arcade.key.S: False,
            arcade.key.D: False,
        }

        self.trigger_list = arcade.SpriteList()
        self.near_trigger = None
        self.animation_time = 0.0
        self.status_message = ""
        self.status_timer = 0.0

        # Configurações do mapa
        self.map_width = 0
        self.map_height = 0
        
        # Flag para controle de inicialização
        self.setup_complete = False

    def setup(self):
        """Configura o mapa, player e triggers COM VERIFICAÇÃO DE USUÁRIO"""
        try:
            # VERIFICA SE HÁ USUÁRIO AUTENTICADO
            if not self.current_user:
                self.set_status("❌ Nenhum usuário autenticado. Voltando ao menu...", 3.0)
                arcade.schedule(self._force_return_to_menu, 3.0)
                return

            # CARREGA DADOS DO USUÁRIO DO AUTH_SYSTEM
            self.user_data = auth_system.get_user_data(self.current_user)
            if not self.user_data:
                self.set_status("❌ Dados do usuário não encontrados", 3.0)
                arcade.schedule(self._force_return_to_menu, 3.0)
                return

            # CONFIGURA XP BAR COM DADOS DO USUÁRIO
            self._setup_xp_bar()

            # Injeta tileset inline no TMX
            self._process_tmx_map()
            
            # Carrega e monta cena
            tile_map = arcade.load_tilemap(
                TEMP_MAP_PATH,
                scaling=1.0,
                use_spatial_hash=True,
                lazy=False
            )
            self.scene = arcade.Scene.from_tilemap(tile_map)

            # Configura dimensões do mapa
            self.map_width = tile_map.width * TILE_SIZE
            self.map_height = tile_map.height * TILE_SIZE

            # Cria jogador
            self.player_sprite = arcade.Sprite(
                "assets/characters/Emilly.png", 
                scale=0.15,
                hit_box_algorithm="Detailed"
            )
            self.player_sprite.center_x = TILE_SIZE * 2
            self.player_sprite.center_y = TILE_SIZE * 2
            self.scene.add_sprite("Player", self.player_sprite)

            # Mapeia triggers invisíveis
            self._setup_triggers(tile_map)

            # CORREÇÃO: Verifica se existe a sprite list "Walls" de forma diferente
            if not self._has_sprite_list("Walls"):
                self.scene.add_sprite_list("Walls")

            self.set_status(f"🏃‍♀️ {self.current_user}, explore o mapa e encontre as fases!")
            self.setup_complete = True

        except Exception as e:
            print(f"❌ Erro no setup do GameView: {e}")
            self.set_status("❌ Erro ao carregar jogo")
            self.setup_complete = False

    def _setup_xp_bar(self):
        """Configura a XP bar com os dados do usuário do auth_system"""
        try:
            if not self.xp_bar:
                self.xp_bar = XPBar()
            
            # Carrega progresso do usuário do auth_system
            current_xp = self.user_data.get("xp", 0)
            level = self.user_data.get("level", 1)
            max_xp = level * 100  # Sistema infinito
            
            self.xp_bar.current_xp = current_xp
            self.xp_bar.level = level
            self.xp_bar.max_xp = max_xp
            
            print(f"✅ Progresso carregado - {self.current_user}: Level {level}, XP {current_xp}/{max_xp}")
            
        except Exception as e:
            print(f"❌ Erro ao configurar XP bar: {e}")
            if not self.xp_bar:
                self.xp_bar = XPBar()

    def _save_user_progress(self):
        """Salva o progresso do usuário no auth_system"""
        try:
            if not self.current_user or not self.xp_bar:
                return False
            
            # Atualiza dados do usuário no auth_system
            success = auth_system.update_user_xp(
                self.current_user,
                self.xp_bar.current_xp,
                self.xp_bar.level
            )
            
            if success:
                print(f"✅ Progresso salvo para {self.current_user}: Level {self.xp_bar.level}, XP {self.xp_bar.current_xp}")
                return True
            else:
                print(f"❌ Falha ao salvar progresso para {self.current_user}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar progresso: {e}")
            return False

    def _has_sprite_list(self, name: str) -> bool:
        """Verifica se uma sprite list existe na cena"""
        try:
            # Tenta acessar a sprite list
            self.scene[name]
            return True
        except (KeyError, AttributeError):
            return False

    def _process_tmx_map(self):
        """Processa o arquivo TMX e injeta tileset"""
        try:
            tree = ET.parse(RAW_MAP_PATH)
            root = tree.getroot()
            
            # Remove tilesets externos
            for ts in root.findall("tileset"):
                if ts.get("source"):
                    root.remove(ts)
            
            # Adiciona tileset inline
            tileset = ET.Element("tileset", {
                "firstgid": "1", 
                "name": "floresta",
                "tilewidth": str(TILE_SIZE), 
                "tileheight": str(TILE_SIZE),
                "tilecount": "30", 
                "columns": "6"
            })
            image = ET.SubElement(tileset, "image", {
                "source": "assets/maps/tilesets/tilemap_packed.png",
                "width": "192", 
                "height": "160"
            })
            root.insert(0, tileset)
            
            tree.write(TEMP_MAP_PATH, encoding="utf-8", xml_declaration=True)
            
        except Exception as e:
            print(f"❌ Erro ao processar mapa TMX: {e}")
            raise

    def _setup_triggers(self, tile_map):
        """Configura os triggers de fase no mapa"""
        try:
            # Encontra a layer de objetos ou a primeira layer de tiles
            object_layer = None
            for layer in tile_map.tiled_map.layers:
                if hasattr(layer, 'data'):
                    object_layer = layer
                    break
            
            if not object_layer:
                print("❌ Nenhuma layer encontrada no mapa")
                return

            rows = len(object_layer.data)
            cols = len(object_layer.data[0]) if rows > 0 else 0
            
            for r in range(rows):
                for c in range(cols):
                    gid = object_layer.data[r][c]
                    if gid in PHASE_TRIGGER_CODES:
                        x = c * TILE_SIZE + TILE_SIZE / 2
                        y = (rows - r - 1) * TILE_SIZE + TILE_SIZE / 2
                        
                        trig = arcade.SpriteSolidColor(
                            TILE_SIZE - 4, TILE_SIZE - 4, arcade.color.TRANSPARENT_BLACK
                        )
                        trig.center_x = x
                        trig.center_y = y
                        trig.phase = PHASE_TRIGGER_CODES[gid]
                        self.trigger_list.append(trig)
                        
                        print(f"✅ Trigger Fase {trig.phase} em ({x}, {y})")

        except Exception as e:
            print(f"❌ Erro ao configurar triggers: {e}")

    def set_status(self, message: str, duration: float = 3.0):
        """Define mensagem de status temporária"""
        self.status_message = message
        self.status_timer = duration

    def on_show(self):
        """Chamado quando a view é mostrada"""
        arcade.set_background_color(arcade.color.AMAZON)
        self.animation_time = 0.0

    def on_draw(self):
        """Renderiza a cena"""
        self.clear()
        
        # Desenha a cena apenas se estiver configurada
        if self.scene and self.setup_complete:
            self.scene.draw()
        
        # Desenha UI
        self._draw_ui()

    def _draw_ui(self):
        """Desenha a interface do usuário"""
        # Barra de XP
        if self.xp_bar:
            self.xp_bar.draw()
        
        # Indicador de trigger (apenas se setup completo)
        if self.near_trigger and self.setup_complete:
            self._draw_trigger_indicator()
        
        # Mensagem de status
        if self.status_message and self.status_timer > 0:
            arcade.draw_text(
                self.status_message,
                self.window.width / 2,
                self.window.height - 50,
                arcade.color.YELLOW,
                18,
                anchor_x="center",
                bold=True
            )
        
        # Instruções (apenas se setup completo)
        if self.setup_complete:
            arcade.draw_text(
                "WASD: Mover • ENTER: Iniciar fase • ESC: Voltar ao menu",
                self.window.width / 2,
                30,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center"
            )

        # Informações do jogador (apenas se setup completo)
        if self.xp_bar and self.setup_complete:
            # Nome do jogador
            arcade.draw_text(
                f"Jogador: {self.current_user}",
                20,
                self.window.height - 40,
                arcade.color.WHITE,
                14,
                bold=True
            )

            # Level
            arcade.draw_text(
                f"LEVEL {self.xp_bar.level}",
                self.window.width - 100,
                self.window.height - 40,
                arcade.color.GOLD,
                14,
                anchor_x="center",
                bold=True
            )

            # XP atual / XP necessário
            arcade.draw_text(
                f"XP: {self.xp_bar.current_xp}/{self.xp_bar.max_xp}",
                self.window.width - 100,
                self.window.height - 60,
                arcade.color.LIGHT_BLUE,
                12,
                anchor_x="center"
            )

    def _draw_trigger_indicator(self):
        """Desenha indicador visual quando perto de um trigger"""
        if self.near_trigger and self.player_sprite:
            # Pulsação suave
            pulse = (math.sin(self.animation_time * 8) + 1) * 0.3 + 0.7
            
            # Texto flutuante
            arcade.draw_text(
                f"🎯 Fase {self.near_trigger.phase} - Pressione ENTER",
                self.window.width / 2,
                self.window.height - 100,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                bold=True
            )

            # Indicador visual no jogador - CORREÇÃO: alpha entre 0-255
            alpha = int(200 * pulse)
            alpha = max(0, min(255, alpha))  # Garante que fique entre 0-255
            
            arcade.draw_circle_outline(
                self.player_sprite.center_x,
                self.player_sprite.center_y,
                30 * pulse,
                (255, 255, 0, alpha),
                3
            )

    def on_update(self, delta_time: float):
        """Atualiza a lógica do jogo"""
        self.animation_time += delta_time
        
        # Atualiza temporizador de status
        if self.status_timer > 0:
            self.status_timer -= delta_time
        
        # Apenas atualiza movimento e triggers se o setup estiver completo
        if self.setup_complete and self.player_sprite:
            self._handle_movement(delta_time)
            self._check_triggers()

    def _handle_movement(self, delta_time: float):
        """Controla o movimento do jogador"""
        if not self.player_sprite:
            return
            
        speed = 180 * delta_time
        
        dx = dy = 0
        if self.keys[arcade.key.W]: 
            dy += speed
        if self.keys[arcade.key.S]: 
            dy -= speed
        if self.keys[arcade.key.A]: 
            dx -= speed
        if self.keys[arcade.key.D]: 
            dx += speed

        # Normaliza movimento diagonal
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        # Move o jogador
        new_x = self.player_sprite.center_x + dx
        new_y = self.player_sprite.center_y + dy

        # Limita ao mapa
        new_x = max(self.player_sprite.width / 2, min(new_x, self.map_width - self.player_sprite.width / 2))
        new_y = max(self.player_sprite.height / 2, min(new_y, self.map_height - self.player_sprite.height / 2))

        self.player_sprite.center_x = new_x
        self.player_sprite.center_y = new_y

    def _check_triggers(self):
        """Verifica colisão com triggers"""
        if not self.player_sprite:
            return
            
        hits = arcade.check_for_collision_with_list(
            self.player_sprite,
            self.trigger_list
        )
        self.near_trigger = hits[0] if hits else None

    def on_key_press(self, key: int, modifiers: int):
        """Lida com pressionamento de teclas"""
        if key in self.keys:
            self.keys[key] = True

        elif key == arcade.key.ENTER and self.near_trigger and self.setup_complete:
            self._start_quiz()
            
        elif key == arcade.key.ESCAPE:
            self._return_to_menu()
            
        elif key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
            self.set_status("🖥️  Tela cheia: " + ("ON" if self.window.fullscreen else "OFF"))
            
        elif key == arcade.key.R and self.setup_complete:
            # Reset para debug
            if self.player_sprite:
                self.player_sprite.center_x = TILE_SIZE * 2
                self.player_sprite.center_y = TILE_SIZE * 2
                self.set_status("🔄 Posição resetada")

        elif key == arcade.key.T and self.setup_complete and self.player_sprite:
            # Debug: mostra posição do jogador
            x, y = self.player_sprite.center_x, self.player_sprite.center_y
            self.set_status(f"📍 Posição: ({x:.1f}, {y:.1f})")

        elif key == arcade.key.X and self.setup_complete:
            # Debug: adiciona XP para teste
            if self.xp_bar:
                levels = self.xp_bar.add_xp(50)
                self._save_user_progress()
                if levels > 0:
                    self.set_status(f"🎉 LEVEL UP! Novo nível: {self.xp_bar.level}")
                else:
                    self.set_status(f"➕ +50 XP | Progresso: {self.xp_bar.current_xp}/{self.xp_bar.max_xp}")

    def on_key_release(self, key: int, modifiers: int):
        """Lida com liberação de teclas"""
        if key in self.keys:
            self.keys[key] = False

    def _start_quiz(self):
        """Inicia a view do quiz para a fase atual"""
        try:
            if not self.near_trigger:
                return
                
            phase = self.near_trigger.phase
            self.set_status(f"🚀 Iniciando Fase {phase}...")
            
            from views.quiz_view import QuizView
            quiz_view = QuizView(
                phase=phase,
                xp_bar=self.xp_bar,
                session_id=self.session_id,
                parent=self
            )
            quiz_view.setup()
            self.window.show_view(quiz_view)
            
        except Exception as e:
            print(f"❌ Erro ao iniciar quiz: {e}")
            self.set_status("❌ Erro ao carregar fase")

    def _force_return_to_menu(self, delta_time):
        """Força retorno ao menu após erro"""
        arcade.unschedule(self._force_return_to_menu)
        self._return_to_menu()

    def _return_to_menu(self):
        """Retorna ao menu principal usando UserManager"""
        try:
            # SALVA PROGRESSO antes de sair
            self._save_user_progress()
            
            if self.on_exit_callback:
                self.on_exit_callback()
            
            # ATUALIZA USER_MANAGER com XP bar atual
            user_manager.set_current_user(self.current_user, self.xp_bar)
            
            from views.menu_view import MenuView
            
            # Obtém dados do usuário para o menu
            user_data = auth_system.get_user_data(self.current_user)
            avatar_path = user_data.get("avatar_path") if user_data else None
            
            # Cria menu com usuário correto
            menu_view = MenuView(
                username=self.current_user,
                avatar_path=avatar_path
            )
            self.window.show_view(menu_view)
            self.set_status("💾 Progresso salvo! Voltando ao menu...")
            
        except Exception as e:
            print(f"❌ Erro ao voltar ao menu: {e}")
            # Fallback seguro
            from views.menu_view import MenuView
            menu_view = MenuView()
            self.window.show_view(menu_view)

    def on_hide_view(self):
        """Chamado quando a view é escondida - SALVA PROGRESSO"""
        print("⏸️  GameView pausada - Salvando progresso...")
        self._save_user_progress()
        if self.on_exit_callback:
            self.on_exit_callback()

    def on_show_view(self):
        """Chamado quando a view é mostrada"""
        print(f"🎮 GameView ativa para usuário: {self.current_user}")
        
    def on_resize(self, width: int, height: int):
        """Lida com redimensionamento da janela"""
        # Atualiza a XP bar se existir
        if self.xp_bar:
            self.xp_bar.window_width = width
            self.xp_bar.window_height = height