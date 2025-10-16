# views/game_view.py

import arcade
import xml.etree.ElementTree as ET
import requests
import math
import json
import os

from config import RAW_MAP_PATH, TEMP_MAP_PATH, TILE_SIZE, PHASE_TRIGGER_CODES
from assets.xp.xp import XPBar
from auth.user_manager import user_manager
from auth.simple_auth import auth_system


class GameView(arcade.View):
    """
    Carrega o mapa TMX, controla movimento do personagem escolhido,
    detecta triggers de fase e inicia o QuizView ao ENTER.
    SISTEMA SIMPLIFICADO E FUNCIONAL
    """

    def __init__(self, xp_bar: XPBar = None, session_id: str = "", on_exit_callback=None):
        super().__init__()
        self.xp_bar = xp_bar
        self.session_id = session_id
        self.on_exit_callback = on_exit_callback
        
        # Obtém usuário atual do UserManager
        self.current_user = user_manager.get_current_user()
        self.user_data = None
        self.character_data = None

        self.scene = None
        self.player_sprite = None

        self.keys = {
            arcade.key.W: False,
            arcade.key.A: False,
            arcade.key.S: False,
            arcade.key.D: False,
        }

        # Sistema de animação
        self.animations = {}
        self.facing_direction = "down"
        self.is_moving = False

        self.trigger_list = arcade.SpriteList()
        self.near_trigger = None
        self.animation_time = 0.0
        self.status_message = ""
        self.status_timer = 0.0

        # Configurações do mapa
        self.map_width = 0
        self.map_height = 0
        
        # Sistema de campanha
        self.campaign_data = None
        self.fase_status = {}
        self.available_phases = []
        
        self.setup_complete = False

    def setup(self):
        """Configura o mapa, player e triggers"""
        try:
            if not self.current_user:
                self.set_status("❌ Nenhum usuário autenticado. Voltando ao menu...", 3.0)
                arcade.schedule(self._force_return_to_menu, 3.0)
                return

            self.user_data = auth_system.get_user_data(self.current_user)
            if not self.user_data:
                self.set_status("❌ Dados do usuário não encontrados", 3.0)
                arcade.schedule(self._force_return_to_menu, 3.0)
                return

            # 🔥 CONFIGURAÇÃO SIMPLES E DIRETA
            self.character_data = self.user_data.get("character", {})
            if not self.character_data:
                self.character_data = {
                    "name": "Emily",
                    "animations": {
                        "up": "assets/characters/Emillywhite_down.png",
                        "down": "assets/characters/Emillywhite_front.png", 
                        "left": "assets/characters/Emillywhite_left.png",
                        "right": "assets/characters/Emillywhite_right.png"
                    }
                }
                print("⚠️ Usando personagem fallback (Emily)")

            print(f"🎮 Personagem carregado: {self.character_data.get('name', 'Emily')}")

            # 🔥 VERIFICAÇÃO SIMPLES E DIRETA DAS IMAGENS
            animations = self.character_data["animations"]
            
            # Verifica cada imagem individualmente
            print("🔍 Verificando imagens...")
            for direction, path in animations.items():
                if os.path.exists(path):
                    print(f"✅ {direction}: {path}")
                else:
                    print(f"❌ {direction}: {path} - NÃO ENCONTRADO")

            # 🔥 CARREGA SPRITE DE FORMA SIMPLES
            if os.path.exists(animations["down"]):
                print(f"🖼️ Carregando sprite: {animations['down']}")

                # MÉTODO MAIS SIMPLES POSSÍVEL - carrega direto
                self.player_sprite = arcade.Sprite(
                    animations["down"],  # Usa a imagem "down" como inicial
                    scale=0.95,
                    hit_box_algorithm="Simple"
                )
                
                # 🔥 SALVA AS ANIMAÇÕES PARA USAR DEPOIS
                self.animations = animations
                print("✅ Sprite carregado com sucesso!")
                
            else:
                print("❌ Imagem 'down' não encontrada, usando fallback")
                self.player_sprite = arcade.SpriteSolidColor(40, 60, arcade.color.RED)

            # CONFIGURA SISTEMAS
            self._setup_campaign_system()
            self._setup_xp_bar()
            self._process_tmx_map()
            
            # Carrega mapa
            tile_map = arcade.load_tilemap(
                TEMP_MAP_PATH,
                scaling=1.0,
                use_spatial_hash=True,
                lazy=False
            )
            self.scene = arcade.Scene.from_tilemap(tile_map)

            self.map_width = tile_map.width * TILE_SIZE
            self.map_height = tile_map.height * TILE_SIZE

            # Posição inicial do jogador
            self.player_sprite.center_x = TILE_SIZE * 2
            self.player_sprite.center_y = TILE_SIZE * 2
            
            # Adiciona à cena
            self.scene.add_sprite("Player", self.player_sprite)

            # Configura triggers
            self._setup_triggers(tile_map)

            if not self._has_sprite_list("Walls"):
                self.scene.add_sprite_list("Walls")

            # Mensagem inicial
            fases_liberadas = [f for f, status in self.fase_status.items() if status == "liberada"]
            if fases_liberadas:
                self.set_status(f"✅ {self.character_data.get('name', 'Emily')} está pronta! Fase {min(fases_liberadas)} liberada!")
            else:
                self.set_status(f"🔒 {self.character_data.get('name', 'Emily')} aguardando... Nenhuma fase liberada.")

            self.setup_complete = True
            print(f"🎮 GameView ativa para: {self.current_user}")

        except Exception as e:
            print(f"❌ Erro no setup do GameView: {e}")
            self.set_status("❌ Erro ao carregar jogo")
            self.setup_complete = False

    def _update_player_texture(self):
        """ATUALIZA A TEXTURA DO SPRITE - MÉTODO SIMPLES"""
        if not self.player_sprite or not self.animations:
            return
            
        # Obtém o caminho da imagem baseado na direção
        texture_path = self.animations.get(self.facing_direction)
        
        if texture_path and os.path.exists(texture_path):
            try:
                print(f"🔄 Mudando para: {self.facing_direction}")
                
                # 🔥 VERIFICA SE É DIREITA PARA ESPELHAR
                if self.facing_direction == "right" and texture_path == self.animations.get("left"):
                    # DIREITA usa imagem da ESQUERDA espelhada
                    new_texture = arcade.load_texture(
                        texture_path,
                        flipped_horizontally=True
                    )
                else:
                    # Outras direções - carrega normal
                    new_texture = arcade.load_texture(texture_path)
                
                # Atualiza a textura
                self.player_sprite.texture = new_texture
                
                print(f"✅ Textura atualizada para: {self.facing_direction}")
                
            except Exception as e:
                print(f"❌ Erro ao carregar textura {texture_path}: {e}")

    def _setup_campaign_system(self):
        """Configura o sistema de campanha com 6 fases"""
        try:
            # Tenta carregar do MongoDB via API
            try:
                resp = requests.get(
                    f"http://127.0.0.1:8000/api/user/{self.current_user}/campaign",
                    timeout=3
                )
                if resp.status_code == 200:
                    campaign_data = resp.json()
                    self.fase_status = campaign_data.get("fases", {})
                    print("✅ Campanha carregada do MongoDB")
            except:
                # Fallback: usa dados locais do auth_system
                campaign_progress = self.user_data.get("campaign_progress", {})
                if campaign_progress and "fases" in campaign_progress:
                    self.fase_status = campaign_progress["fases"]
                    print("✅ Campanha carregada do auth_system")
            
            # SE NÃO EXISTIR, CRIA NOVA CAMPANHA COM 6 FASES
            if not self.fase_status:
                self.fase_status = {
                    1: "liberada",    # Sempre liberada para novos jogadores
                    2: "bloqueada",   # Precisa completar fase 1
                    3: "bloqueada",   # Precisa completar fase 2
                    4: "bloqueada",   # Precisa completar fase 3
                    5: "bloqueada",   # Precisa completar fase 4
                    6: "bloqueada"    # Precisa completar fase 5
                }
                print("✅ Nova campanha criada - 6 fases")
            
            # GARANTE que a fase 1 esteja sempre liberada
            self.fase_status[1] = "liberada"
            
            # Atualiza lista de fases disponíveis
            self.available_phases = [fase for fase, status in self.fase_status.items() if status == "liberada"]
            
            print("📊 Status das 6 fases:")
            for fase, status in sorted(self.fase_status.items()):
                print(f"   Fase {fase}: {status}")
                
        except Exception as e:
            print(f"❌ Erro ao carregar campanha: {e}")
            # Fallback de emergência
            self.fase_status = {1: "liberada", 2: "bloqueada", 3: "bloqueada", 4: "bloqueada", 5: "bloqueada", 6: "bloqueada"}
            self.available_phases = [1]

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

    def _save_campaign_progress(self):
        """Salva progresso da campanha"""
        try:
            # Atualiza dados locais
            self.user_data["campaign_progress"] = {
                "fase_atual": max([f for f, s in self.fase_status.items() if s in ["liberada", "concluida"]], default=1),
                "fases": self.fase_status
            }
            
            # Salva no auth_system
            success = auth_system.update_user_xp(
                self.current_user,
                self.xp_bar.current_xp,
                self.xp_bar.level
            )
            
            # Tenta salvar no MongoDB
            try:
                resp = requests.post(
                    f"http://127.0.0.1:8000/api/user/{self.current_user}/campaign",
                    json={"fases": self.fase_status},
                    timeout=2
                )
            except:
                pass  # Ignora se API não estiver disponível
                
            return success
                
        except Exception as e:
            print(f"❌ Erro ao salvar progresso: {e}")
            return False

    def _has_sprite_list(self, name: str) -> bool:
        """Verifica se uma sprite list existe na cena"""
        try:
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
        """Configura os triggers de fase no mapa - SÓ FASES LIBERADAS"""
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
                        fase_id = PHASE_TRIGGER_CODES[gid]
                        
                        # ✅ SÓ CRIA TRIGGER SE A FASE ESTIVER LIBERADA
                        if fase_id not in self.available_phases:
                            print(f"🔒 Trigger Fase {fase_id} ignorado (não liberada)")
                            continue
                            
                        x = c * TILE_SIZE + TILE_SIZE / 2
                        y = (rows - r - 1) * TILE_SIZE + TILE_SIZE / 2
                        
                        trig = arcade.SpriteSolidColor(
                            TILE_SIZE - 4, TILE_SIZE - 4, arcade.color.TRANSPARENT_BLACK
                        )
                        trig.center_x = x
                        trig.center_y = y
                        trig.phase = fase_id
                        self.trigger_list.append(trig)
                        
                        print(f"✅ Trigger Fase {fase_id} ativo em ({x:.1f}, {y:.1f})")

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
        
        # STATUS DAS 6 FASES
        self._draw_fase_status()
        
        # NOME DO PERSONAGEM
        if self.character_data and self.setup_complete:
            arcade.draw_text(
                f"Personagem: {self.character_data.get('name', 'Emily')}",
                20,
                self.window.height - 60,
                arcade.color.LIGHT_BLUE,
                14,
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
            arcade.draw_text(
                f"Jogador: {self.current_user}",
                20,
                self.window.height - 40,
                arcade.color.WHITE,
                14,
                bold=True
            )

            arcade.draw_text(
                f"LEVEL {self.xp_bar.level}",
                self.window.width - 100,
                self.window.height - 40,
                arcade.color.GOLD,
                14,
                anchor_x="center",
                bold=True
            )

            arcade.draw_text(
                f"XP: {self.xp_bar.current_xp}/{self.xp_bar.max_xp}",
                self.window.width - 100,
                self.window.height - 60,
                arcade.color.LIGHT_BLUE,
                12,
                anchor_x="center"
            )

    def _draw_fase_status(self):
        """Desenha o status das 6 fases na tela"""
        if not self.fase_status:
            return
            
        arcade.draw_text(
            "STATUS DAS FASES:",
            self.window.width - 150,
            self.window.height - 100,
            arcade.color.WHITE,
            16,
            anchor_x="center",
            bold=True
        )
        
        y_pos = self.window.height - 130
        for fase_id in range(1, 7):
            status = self.fase_status.get(fase_id, "bloqueada")
            
            if status == "concluida":
                texto = f"Fase {fase_id}: ✅ Concluída"
                cor = arcade.color.GREEN
            elif status == "liberada":
                texto = f"Fase {fase_id}: 🟡 Liberada" 
                cor = arcade.color.YELLOW
            else:
                texto = f"Fase {fase_id}: ❌ Bloqueada"
                cor = arcade.color.RED
                
            arcade.draw_text(
                texto,
                self.window.width - 150,
                y_pos,
                cor,
                12,
                anchor_x="center"
            )
            y_pos -= 25

    def _draw_trigger_indicator(self):
        """Desenha indicador visual quando perto de um trigger"""
        if self.near_trigger and self.player_sprite:
            fase_id = self.near_trigger.phase
            status = self.fase_status.get(fase_id, "bloqueada")
            
            if status == "liberada":
                texto = f"🎯 Fase {fase_id} - Pressione ENTER"
                cor = arcade.color.GREEN
            elif status == "concluida":
                texto = f"✅ Fase {fase_id} concluída"
                cor = arcade.color.BLUE
            else:
                texto = f"🔒 Fase {fase_id} bloqueada"
                cor = arcade.color.RED
            
            pulse = (math.sin(self.animation_time * 8) + 1) * 0.3 + 0.7
            
            arcade.draw_text(
                texto,
                self.window.width / 2,
                self.window.height - 100,
                cor,
                20,
                anchor_x="center",
                bold=True
            )

            arcade.draw_circle_outline(
                self.player_sprite.center_x,
                self.player_sprite.center_y,
                30 * pulse,
                arcade.color.YELLOW,
                3
            )

    def on_update(self, delta_time: float):
        """Atualiza a lógica do jogo"""
        self.animation_time += delta_time
        
        if self.status_timer > 0:
            self.status_timer -= delta_time
        
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

        # Atualiza direção para animação
        old_direction = self.facing_direction
        if dx != 0 or dy != 0:
            self.is_moving = True
            if abs(dx) > abs(dy):
                self.facing_direction = "right" if dx > 0 else "left"
            else:
                self.facing_direction = "up" if dy > 0 else "down"
        else:
            self.is_moving = False
            
        # Se a direção mudou, atualiza a textura
        if old_direction != self.facing_direction:
            self._update_player_texture()

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
            if self.player_sprite:
                self.player_sprite.center_x = TILE_SIZE * 2
                self.player_sprite.center_y = TILE_SIZE * 2
                self.set_status("🔄 Posição resetada")

        elif key == arcade.key.T and self.setup_complete and self.player_sprite:
            x, y = self.player_sprite.center_x, self.player_sprite.center_y
            self.set_status(f"📍 Posição: ({x:.1f}, {y:.1f})")

        elif key == arcade.key.X and self.setup_complete:
            if self.xp_bar:
                levels = self.xp_bar.add_xp(50)
                self._save_campaign_progress()
                if levels > 0:
                    self.set_status(f"🎉 LEVEL UP! Novo nível: {self.xp_bar.level}")
                else:
                    self.set_status(f"➕ +50 XP | Progresso: {self.xp_bar.current_xp}/{self.xp_bar.max_xp}")

        elif key == arcade.key.C and self.setup_complete:
            if self.near_trigger:
                fase_id = self.near_trigger.phase
                self._completar_fase(fase_id)

    def on_key_release(self, key: int, modifiers: int):
        """Lida com liberação de teclas"""
        if key in self.keys:
            self.keys[key] = False

    def _start_quiz(self):
        """Inicia a view do quiz para a fase atual - SÓ SE ESTIVER LIBERADA"""
        try:
            if not self.near_trigger:
                return
                
            phase = self.near_trigger.phase
            status = self.fase_status.get(phase, "bloqueada")
            
            if status != "liberada":
                if status == "concluida":
                    self.set_status(f"✅ Fase {phase} já concluída!")
                else:
                    self.set_status(f"🔒 Fase {phase} bloqueada! Complete as fases anteriores.")
                return
                
            self.set_status(f"🚀 {self.character_data.get('name', 'Emily')} iniciando Fase {phase}...")
            
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

    def _completar_fase(self, fase_id: int):
        """Marca fase como concluída e libera próxima"""
        try:
            self.fase_status[fase_id] = "concluida"
            
            proxima_fase = fase_id + 1
            if proxima_fase <= 6:
                self.fase_status[proxima_fase] = "liberada"
                self.available_phases.append(proxima_fase)
                self.set_status(f"🎉 {self.character_data.get('name', 'Emily')} completou a Fase {fase_id}! Fase {proxima_fase} liberada!")
                print(f"🔓 Nova fase liberada: {proxima_fase}")
            else:
                self.set_status(f"🎉 {self.character_data.get('name', 'Emily')} completou todas as 6 fases! Parabéns!")
            
            if self.xp_bar:
                xp_ganho = 100
                levels = self.xp_bar.add_xp(xp_ganho)
                if levels > 0:
                    self.set_status(f"🌟 LEVEL UP! Novo nível: {self.xp_bar.level}")
            
            self._save_campaign_progress()
            
            self.trigger_list.clear()
            from arcade import load_tilemap
            tile_map = load_tilemap(TEMP_MAP_PATH, scaling=1.0)
            self._setup_triggers(tile_map)
            
        except Exception as e:
            print(f"❌ Erro ao completar fase: {e}")
            self.set_status("❌ Erro ao salvar progresso")

    def _force_return_to_menu(self, delta_time):
        """Força retorno ao menu após erro"""
        arcade.unschedule(self._force_return_to_menu)
        self._return_to_menu()

    def _return_to_menu(self):
        """Retorna ao menu principal usando UserManager"""
        try:
            self._save_campaign_progress()
            
            if self.on_exit_callback:
                self.on_exit_callback()
            
            user_manager.set_current_user(self.current_user, self.xp_bar)
            
            from views.menu_view import MenuView
            
            user_data = auth_system.get_user_data(self.current_user)
            avatar_path = user_data.get("avatar_path") if user_data else None
            
            menu_view = MenuView(
                username=self.current_user,
                avatar_path=avatar_path
            )
            self.window.show_view(menu_view)
            self.set_status("💾 Progresso salvo! Voltando ao menu...")
            
        except Exception as e:
            print(f"❌ Erro ao voltar ao menu: {e}")
            from views.menu_view import MenuView
            menu_view = MenuView()
            self.window.show_view(menu_view)

    def on_hide_view(self):
        """Chamado quando a view é escondida - SALVA PROGRESSO"""
        print("⏸️  GameView pausada - Salvando progresso...")
        self._save_campaign_progress()
        if self.on_exit_callback:
            self.on_exit_callback()

    def on_show_view(self):
        """Chamado quando a view é mostrada"""
        print(f"🎮 GameView ativa para usuário: {self.current_user}")
        
    def on_resize(self, width: int, height: int):
        """Lida com redimensionamento da janela"""
        if self.xp_bar:
            self.xp_bar.window_width = width
            self.xp_bar.window_height = height