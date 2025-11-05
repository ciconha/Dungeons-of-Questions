# views/game_view.py

import arcade
import xml.etree.ElementTree as ET
import requests
import math
import json
import os
import threading

from config import RAW_MAP_PATH, TEMP_MAP_PATH, TILE_SIZE, PHASE_TRIGGER_CODES
from assets.xp.xp import XPBar
from auth.user_manager import user_manager
from auth.simple_auth import auth_system
from assets.characters.character_movement import CharacterMovement  # 🔥 NOVO IMPORT


class GameView(arcade.View):
    """
    Carrega o mapa TMX, controla movimento do personagem escolhido,
    detecta triggers de fase e inicia o QuizView ao ENTER.
    SISTEMA ROBUSTO - FUNCIONA COM QUALQUER CONTA
    """

    def __init__(self, xp_bar: XPBar = None, session_id: str = "", on_exit_callback=None):
        super().__init__()
        self.xp_bar = xp_bar
        self.session_id = session_id
        self.on_exit_callback = on_exit_callback

        # SISTEMA MELHORADO - Fallbacks robustos
        self.current_user = self._get_current_user_safe()
        self.user_data = self._load_user_data_safe()
        self.character_data = self._load_character_data_safe()

        self.scene = None
        self.player_sprite = None

        # MELHORIA: Controles WASD padronizados para todos os usuários
        self.keys = {
            arcade.key.W: False,
            arcade.key.A: False,
            arcade.key.S: False,
            arcade.key.D: False,
        }

        # Sistema de animação - SIMPLIFICADO
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

        # Sistema de campanha - MELHORADO para persistência
        self.campaign_data = None
        self.fase_status = {}
        self.available_phases = []
        self.fases_concluidas = []

        self.setup_complete = False

        # NOVO: Sistema de salvamento automático melhorado
        self.last_save_time = 0.0
        self.save_interval = 5.0  # Salva a cada 5 segundos (mais frequente)

        # NOVO: Controle de fase/quiz para permitir RETENTATIVA e retorno ao mapa
        self.last_started_phase = None
        self.awaiting_quiz_result = False
        self.last_trigger_position = None
        self.allow_retry_on_failure = True

    def _get_current_user_safe(self):
        """Obtém usuário atual com fallbacks robustos"""
        try:
            # Tenta pelo UserManager primeiro
            user = user_manager.get_current_user()
            if user:
                print(f"✅ Usuário do UserManager: {user}")
                return user

            # Fallback: tenta pela session do auth_system (se disponível)
            if self.session_id:
                try:
                    user_data = getattr(auth_system, "get_user_by_session", lambda s: None)(self.session_id)
                    if user_data and isinstance(user_data, dict) and "username" in user_data:
                        username = user_data["username"]
                        print(f"✅ Usuário do auth_system: {username}")
                        return username
                except Exception:
                    pass

            # Fallback: tenta pela janela
            if hasattr(self, "window") and hasattr(self.window, "current_user") and self.window.current_user:
                print(f"✅ Usuário da janela: {self.window.current_user}")
                return self.window.current_user

        except Exception as e:
            print(f"⚠️ UserManager falhou: {e}")

        # FALLBACK FINAL: usuário padrão
        default_user = "player_001"
        print(f"⚠️ Usando usuário padrão: {default_user}")
        return default_user

    def _load_user_data_safe(self):
        """Carrega dados do usuário com fallbacks robustos"""
        user_data = {}

        try:
            # Tenta pelo auth_system
            if self.current_user:
                data = getattr(auth_system, "get_user_data", lambda u: None)(self.current_user)
                if data:
                    user_data = data
                    print(f"✅ Dados carregados do auth_system para {self.current_user}")
        except Exception as e:
            print(f"⚠️ auth_system falhou: {e}")

        # SE NÃO CONSEGUIU, TENTA DO MONGODB (API local) como backup
        if not user_data:
            try:
                resp = requests.get(
                    f"http://127.0.0.1:8000/api/user/{self.current_user}/progress",
                    timeout=3
                )
                if resp.status_code == 200:
                    user_data = resp.json()
                    print(f"✅ Dados carregados do MongoDB para {self.current_user}")
            except Exception as e:
                print(f"⚠️ MongoDB não disponível: {e}")

        # Se não conseguiu carregar, cria dados padrão
        if not user_data:
            user_data = {
                "username": self.current_user,
                "level": 1,
                "xp": 0,
                "character": CharacterMovement.create_default_character(),  # 🔥 USA SISTEMA NOVO
                "campaign_progress": {
                    "fase_atual": 1,
                    "fases": {1: "liberada", 2: "bloqueada", 3: "bloqueada", 4: "bloqueada", 5: "bloqueada", 6: "bloqueada"},
                    "fases_concluidas": []
                }
            }
            print(f"🆕 Dados padrão criados para {self.current_user}")

        return user_data

    def _load_character_data_safe(self):
        """Carrega dados do personagem com fallbacks robustos"""
        try:
            # Tenta pegar do user_data
            character_data = self.user_data.get("character") if self.user_data else None
            if character_data:
                # 🔥 USA SISTEMA NOVO DE VALIDAÇÃO
                validated_data = CharacterMovement.validate_character_data(character_data)
                print(f"✅ Personagem carregado: {validated_data.get('name', 'Desconhecido')}")
                return validated_data
        except Exception as e:
            print(f"⚠️ Erro ao carregar personagem: {e}")

        # Fallback: personagem padrão Emily do sistema novo
        return CharacterMovement.create_default_character()

    def _load_player_sprite_safe(self):
        """Carrega o sprite do jogador de forma segura - ATUALIZADO"""
        try:
            # 🔥 USA SISTEMA NOVO DE CRIAÇÃO DE SPRITE
            self.player_sprite = CharacterMovement.create_character_sprite(self.character_data)
            print("✅ Sprite carregado com sistema de movimentação!")
            
        except Exception as e:
            print(f"❌ Erro ao carregar sprite: {e}")
            self.player_sprite = arcade.SpriteSolidColor(40, 60, arcade.color.RED)

    def _setup_campaign_system_robust(self):
        """Configura sistema de campanha robusto - MELHORADO para persistência"""
        try:
            # Tenta carregar campanha existente
            if self.user_data and "campaign_progress" in self.user_data:
                campaign_progress = self.user_data["campaign_progress"]
                if campaign_progress and "fases" in campaign_progress:
                    self.fase_status = campaign_progress["fases"]
                    self.fases_concluidas = campaign_progress.get("fases_concluidas", [])
                    print("✅ Campanha carregada do user_data")
                    self._liberar_fases_automaticamente()
                else:
                    self.fase_status = {1: "liberada", 2: "bloqueada", 3: "bloqueada", 4: "bloqueada", 5: "bloqueada", 6: "bloqueada"}
                    self.fases_concluidas = []
                    print("🆕 Nova campanha criada")
            else:
                self.fase_status = {1: "liberada", 2: "bloqueada", 3: "bloqueada", 4: "bloqueada", 5: "bloqueada", 6: "bloqueada"}
                self.fases_concluidas = []
                print("🆕 Nova campanha criada (user_data vazio)")

            # GARANTE fase 1 liberada
            self.fase_status[1] = "liberada"

            # ATUALIZA LISTA DE FASES DISPONÍVEIS (INCLUI CONCLUÍDAS)
            self.available_phases = [fase for fase, status in self.fase_status.items()
                                     if status in ["liberada", "concluida"]]

            print("📊 Status das fases:")
            for fase, status in sorted(self.fase_status.items()):
                print(f"   Fase {fase}: {status}")
            print(f"✅ Fases concluídas: {self.fases_concluidas}")

        except Exception as e:
            print(f"❌ Erro na campanha: {e}")
            self.fase_status = {1: "liberada", 2: "bloqueada", 3: "bloqueada", 4: "bloqueada", 5: "bloqueada", 6: "bloqueada"}
            self.available_phases = [1]
            self.fases_concluidas = []

    def _liberar_fases_automaticamente(self):
        """Libera fases automaticamente baseado nas fases concluídas - MELHORADO"""
        try:
            for fase_concluida in self.fases_concluidas:
                proxima_fase = fase_concluida + 1
                if proxima_fase <= 6 and self.fase_status.get(proxima_fase) == "bloqueada":
                    self.fase_status[proxima_fase] = "liberada"
                    print(f"🔓 Fase {proxima_fase} liberada automaticamente (Fase {fase_concluida} concluída)")

            # Atualiza lista de fases disponíveis
            self.available_phases = [fase for fase, status in self.fase_status.items()
                                     if status in ["liberada", "concluida"]]

        except Exception as e:
            print(f"❌ Erro ao liberar fases automaticamente: {e}")

    def _setup_xp_bar_robust(self):
        """Configura XP bar robusta"""
        try:
            if not self.xp_bar:
                self.xp_bar = XPBar()

            # Usa dados do user_data ou padrões
            current_xp = self.user_data.get("xp", 0) if self.user_data else 0
            level = self.user_data.get("level", 1) if self.user_data else 1
            max_xp = level * 100

            self.xp_bar.current_xp = current_xp
            self.xp_bar.level = level
            self.xp_bar.max_xp = max_xp

            print(f"✅ XP Bar: Level {level}, XP {current_xp}/{max_xp}")

        except Exception as e:
            print(f"❌ Erro na XP bar: {e}")
            if not self.xp_bar:
                self.xp_bar = XPBar()

    def _load_map_safe(self):
        """Carrega mapa com tratamento de erro"""
        try:
            self._process_tmx_map()

            tile_map = arcade.load_tilemap(
                TEMP_MAP_PATH,
                scaling=1.0,
                use_spatial_hash=True,
                lazy=False
            )
            self.scene = arcade.Scene.from_tilemap(tile_map)

            self.map_width = tile_map.width * TILE_SIZE
            self.map_height = tile_map.height * TILE_SIZE

            # 🔥 USA SISTEMA NOVO PARA POSIÇÃO INICIAL
            start_x, start_y = CharacterMovement.get_initial_position(self.character_data)

            if self.player_sprite:
                self.player_sprite.center_x = start_x
                self.player_sprite.center_y = start_y

                # Adiciona à cena
                self.scene.add_sprite("Player", self.player_sprite)

            print("✅ Mapa carregado com sucesso")

        except Exception as e:
            print(f"❌ Erro ao carregar mapa: {e}")
            self._create_emergency_scene()

    def _create_emergency_scene(self):
        """Cria cena de emergência se o mapa falhar"""
        self.scene = arcade.Scene()
        self.scene.add_sprite_list("Player")
        if self.player_sprite:
            self.scene.add_sprite("Player", self.player_sprite)

        # Define tamanhos seguros
        self.map_width = 800
        self.map_height = 600

        print("🆘 Cena de emergência criada")

    def _setup_triggers_robust(self):
        """Configura triggers de forma robusta"""
        try:
            from arcade import load_tilemap
            tile_map = load_tilemap(TEMP_MAP_PATH, scaling=1.0)
            self._setup_triggers(tile_map)
            print("✅ Triggers configurados")
        except Exception as e:
            print(f"⚠️ Erro nos triggers: {e}")
            # Continua sem triggers

    def _emergency_setup(self):
        """Setup de emergência quando tudo falha"""
        print("🚨 INICIANDO SETUP DE EMERGÊNCIA")

        # Configurações mínimas
        self.player_sprite = arcade.SpriteSolidColor(40, 60, arcade.color.GREEN)

        self._create_emergency_scene()

        self.fase_status = {1: "liberada"}
        self.available_phases = [1]
        self.fases_concluidas = []

        if not self.xp_bar:
            self.xp_bar = XPBar()

        self.setup_complete = True
        self.set_status("⚠️ Modo de emergência ativado - Funcionalidades limitadas")

        print("✅ Setup de emergência concluído")

    def setup(self):
        """Configura o mapa, player e triggers - VERSÃO SIMPLIFICADA"""
        try:
            print(f"🎮 Iniciando GameView para: {self.current_user}")

            # VERIFICAÇÕES ROBUSTAS
            if not self.current_user:
                self.current_user = "player_unknown"
                print("⚠️ Usuário desconhecido, usando fallback")

            if not self.user_data:
                self.user_data = self._load_user_data_safe()

            if not self.character_data:
                self.character_data = self._load_character_data_safe()

            # CONFIGURAÇÃO DO PERSONAGEM - SIMPLIFICADA
            print(f"🎭 Configurando personagem: {self.character_data.get('name', 'Emily')}")

            # 🔥 CARREGA SPRITE COM SISTEMA NOVO
            self._load_player_sprite_safe()

            # CONFIGURA SISTEMAS ESSENCIAIS
            self._setup_campaign_system_robust()
            self._setup_xp_bar_robust()

            # CARREGA MAPA COM FALLBACK
            self._load_map_safe()

            # CONFIGURA TRIGGERS
            self._setup_triggers_robust()

            self.setup_complete = True
            print(f"✅ GameView configurada com sucesso para: {self.current_user}")

        except Exception as e:
            print(f"❌ Erro crítico no setup: {e}")
            self._emergency_setup()

    def _save_user_progress_robust(self):
        """SALVA TODO O PROGRESSO DO USUÁRIO DE FORMA ROBUSTA - MELHORADO"""
        try:
            # ATUALIZA DADOS LOCAIS
            if self.user_data:
                # Dados de XP e nível
                self.user_data["xp"] = self.xp_bar.current_xp if self.xp_bar else 0
                self.user_data["level"] = self.xp_bar.level if self.xp_bar else 1

                # Progresso da campanha - SALVA TODOS OS DADOS ATUAIS
                self.user_data["campaign_progress"] = {
                    "fase_atual": max([f for f, s in self.fase_status.items() if s in ["liberada", "concluida"]], default=1),
                    "fases": self.fase_status,
                    "fases_concluidas": self.fases_concluidas
                }

                # POSIÇÃO DO PERSONAGEM - SALVA SEMPRE
                if self.player_sprite:
                    self.character_data["position"] = {
                        "x": self.player_sprite.center_x,
                        "y": self.player_sprite.center_y
                    }
                self.user_data["character"] = self.character_data

            # SALVA NO AUTH_SYSTEM (PRINCIPAL)
            try:
                if self.current_user and self.user_data:
                    if hasattr(auth_system, "update_user_data"):
                        success = auth_system.update_user_data(self.current_user, self.user_data)
                    else:
                        success = getattr(auth_system, "update_user_xp", lambda u, xp, lvl: False)(
                            self.current_user,
                            self.user_data.get("xp", 0),
                            self.user_data.get("level", 1)
                        )
                    if success:
                        print("💾 Progresso salvo no auth_system")
                    else:
                        print("⚠️ Falha ao salvar no auth_system")
            except Exception as e:
                print(f"⚠️ auth_system indisponível: {e}")

            # SALVA NO MONGODB (BACKUP)
            try:
                if self.current_user:
                    progress_data = {
                        "username": self.current_user,
                        "level": self.user_data.get("level", 1),
                        "xp": self.user_data.get("xp", 0),
                        "campaign_progress": self.user_data.get("campaign_progress", {}),
                        "character": self.user_data.get("character", {})
                    }

                    resp = requests.put(
                        f"http://127.0.0.1:8000/api/user/{self.current_user}/progress",
                        json=progress_data,
                        timeout=3
                    )
                    if resp.status_code == 200:
                        print("💾 Progresso salvo no MongoDB")
                    else:
                        print(f"⚠️ MongoDB retornou status: {resp.status_code}")
            except Exception as e:
                print(f"⚠️ MongoDB não disponível: {e}")

            # SALVA LOCALMENTE (EMERGÊNCIA) - MELHORADO
            try:
                backup_dir = "game_saves"
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                
                local_backup_path = os.path.join(backup_dir, f"backup_{self.current_user}.json")
                with open(local_backup_path, 'w', encoding='utf-8') as f:
                    json.dump(self.user_data, f, indent=2, ensure_ascii=False)
                print(f"💾 Backup local salvo: {local_backup_path}")
            except Exception as e:
                print(f"⚠️ Backup local falhou: {e}")

            # ATUALIZA USER_MANAGER PARA SINCRONIZAR COM O MENU
            try:
                if self.xp_bar:
                    user_manager.set_current_user(self.current_user, self.xp_bar)
                    print("✅ UserManager atualizado")
            except Exception as e:
                print(f"⚠️ UserManager não atualizado: {e}")

            return True

        except Exception as e:
            print(f"❌ Erro crítico ao salvar progresso: {e}")
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

                        # SÓ CRIA TRIGGER SE A FASE ESTIVER DISPONÍVEL
                        if fase_id not in self.available_phases:
                            print(f"🔒 Trigger Fase {fase_id} ignorado (não disponível)")
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

        # STATUS DAS 6 FASES - MELHORADO
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

        # Instruções (apenas se setup completo) - MELHORADO
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
        """Desenha o status das 6 fases na tela - MELHORADO"""
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
        """Atualiza a lógica do jogo - MELHORADO"""
        self.animation_time += delta_time
        self.last_save_time += delta_time

        if self.status_timer > 0:
            self.status_timer -= delta_time

        if self.setup_complete and self.player_sprite:
            self._handle_movement(delta_time)
            self._check_triggers()

            # SALVA PROGRESSO AUTOMATICAMENTE A CADA save_interval (mais frequente)
            if self.last_save_time >= self.save_interval:
                if self._save_user_progress_robust():
                    print("💾 Salvamento automático realizado")
                self.last_save_time = 0.0

    def _handle_movement(self, delta_time: float):
        """Controla o movimento do jogador - ATUALIZADO COM SISTEMA NOVO"""
        if not self.player_sprite:
            return

        # 🔥 USA SISTEMA NOVO DE MOVIMENTAÇÃO
        new_x, new_y, new_direction, is_moving = CharacterMovement.update_movement(
            self.player_sprite,
            self.keys,
            delta_time,
            self.map_width,
            self.map_height
        )

        # Aplica nova posição
        self.player_sprite.center_x = new_x
        self.player_sprite.center_y = new_y

        # Atualiza estado de movimento
        self.is_moving = is_moving

        # Se a direção mudou, atualiza a textura
        if new_direction != self.facing_direction:
            self.facing_direction = new_direction
            CharacterMovement.update_sprite_texture(self.player_sprite, self.facing_direction)

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
        """Lida com pressionamento de teclas - MELHORADO"""
        if key in self.keys:
            self.keys[key] = True

        # ENTER behavior extended:
        # - If near trigger and setup complete: start quiz (existing behavior)
        # - Else if last_started_phase is set and awaiting_quiz_result is False: allow retry of last started phase
        elif key == arcade.key.ENTER and self.setup_complete:
            if self.near_trigger:
                self._start_quiz()
            elif self.last_started_phase and not self.awaiting_quiz_result:
                # Permite reiniciar o quiz da última fase iniciada mesmo que o jogador tenha se afastado
                self.set_status(f"🔁 Reiniciando Fase {self.last_started_phase}...", 2.0)
                self._start_quiz(phase_override=self.last_started_phase)

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
                self._save_user_progress_robust()
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

    def _start_quiz(self, phase_override: int = None):
        """Inicia a view do quiz para a fase atual - SÓ SE ESTIVER LIBERADA
        Agora também armazena a fase iniciada para permitir reentrada caso o jogador falhe no quiz.
        Se phase_override for fornecido, usa essa fase em vez do trigger atual.
        """
        try:
            phase = None
            if phase_override:
                phase = phase_override
            else:
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

            # Armazena dados para possibilitar reentrada em caso de falha
            self.last_started_phase = phase
            self.awaiting_quiz_result = True
            # Grava posição do trigger para reposicionar em caso de falha do quiz
            if self.near_trigger:
                self.last_trigger_position = (self.near_trigger.center_x, self.near_trigger.center_y)

            self.set_status(f"🚀 {self.character_data.get('name', 'Emily')} iniciando Fase {phase}...")

            from views.quiz_view import QuizView
            # Passa 'parent=self' para que o QuizView possa notificar o resultado chamando
            # parent.on_quiz_result(phase, success: bool)
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
            self.awaiting_quiz_result = False
            self.set_status("❌ Erro ao carregar fase")

    def on_quiz_result(self, phase: int, success: bool, xp_reward: int = 0):
        """
        Método público que o QuizView deve chamar ao finalizar.
        - phase: id da fase que foi jogada
        - success: True se o jogador passou no quiz; False se falhou
        - xp_reward: XP ganho se passou (opcional)
        Com essa função, o GameView decide se marca a fase como concluída, libera próxima fase,
        dá XP, salva progresso e permite reentrada em caso de falha.
        """
        try:
            # Marca que o quiz terminou (GameView não aguarda mais resultado)
            self.awaiting_quiz_result = False

            # Se o resultado veio de outra fase, ignora com log
            if phase != self.last_started_phase:
                print(f"⚠️ Resultado do quiz recebido para fase {phase} mas última iniciada foi {self.last_started_phase}")

            if success:
                # Jogador passou no quiz: completa fase normalmente
                print(f"✅ Jogador passou na fase {phase}")
                # Se houver XP, adiciona
                if xp_reward and self.xp_bar:
                    levels = self.xp_bar.add_xp(xp_reward)
                    if levels > 0:
                        self.set_status(f"🌟 LEVEL UP! Novo nível: {self.xp_bar.level}", 3.0)
                    else:
                        self.set_status(f"✅ Fase {phase} concluída! +{xp_reward} XP", 3.0)
                else:
                    self.set_status(f"✅ Fase {phase} concluída!", 3.0)

                # Atualiza sistema de fases
                if phase not in self.fases_concluidas:
                    self.fases_concluidas.append(phase)
                self.fase_status[phase] = "concluida"

                # Libera próxima fase
                proxima_fase = phase + 1
                if proxima_fase <= 6:
                    if self.fase_status.get(proxima_fase) == "bloqueada":
                        self.fase_status[proxima_fase] = "liberada"
                        if proxima_fase not in self.available_phases:
                            self.available_phases.append(proxima_fase)
                        print(f"🔓 Nova fase liberada: {proxima_fase}")

                # Salva progresso completo
                self._save_user_progress_robust()

                # Atualiza triggers (remonta)
                self.trigger_list.clear()
                from arcade import load_tilemap
                tile_map = load_tilemap(TEMP_MAP_PATH, scaling=1.0)
                self._setup_triggers(tile_map)

                # Limpa referência de última fase (já concluída)
                self.last_started_phase = None
                self.last_trigger_position = None

            else:
                # Jogador falhou no quiz
                print(f"❌ Jogador falhou na fase {phase}")
                # Mensagem informando que pode tentar novamente ou retornar
                if self.allow_retry_on_failure:
                    self.set_status(f"❌ Falhou na Fase {phase}. Pressione ENTER para tentar novamente ou ESC para voltar ao menu.", 5.0)
                else:
                    self.set_status(f"❌ Falhou na Fase {phase}. Retorne ao mapa para tentar novamente.", 4.0)

                # Reposiciona jogador próximo ao trigger para facilitar retry (se soubermos a posição)
                if self.last_trigger_position and self.player_sprite:
                    try:
                        tx, ty = self.last_trigger_position
                        # Aproxima o jogador do trigger (centra sobre ele com pequeno deslocamento)
                        self.player_sprite.center_x = max(self.player_sprite.width/2, min(tx, self.map_width - self.player_sprite.width/2))
                        self.player_sprite.center_y = max(self.player_sprite.height/2, min(ty - TILE_SIZE, self.map_height - self.player_sprite.height/2))
                        print(f"🔁 Jogador reposicionado para retry em ({self.player_sprite.center_x:.1f}, {self.player_sprite.center_y:.1f})")
                    except Exception as e:
                        print(f"⚠️ Falha ao reposicionar jogador: {e}")

                # NÃO marca a fase como concluída e mantém triggers ativos para retry
                # last_started_phase permanece para permitir retry via ENTER

            # Se o menu anterior (MenuView) estiver referenciado, sincroniza XP/estado
            try:
                if hasattr(self, "previous_menu") and self.previous_menu:
                    # atualiza dados que o menu pode ler
                    if self.xp_bar:
                        self.previous_menu.user_data = self.user_data or self.previous_menu.user_data
                        self.previous_menu.xp_bar = self.xp_bar
            except Exception:
                pass

        except Exception as e:
            print(f"❌ Erro ao processar resultado do quiz: {e}")
            self.set_status("❌ Erro interno ao processar resultado do quiz", 3.0)
            self.awaiting_quiz_result = False

    def _completar_fase(self, fase_id: int):
        """Marca fase como concluída e libera próxima"""
        try:
            # ATUALIZA SISTEMA DE FASES CONCLUÍDAS
            if fase_id not in self.fases_concluidas:
                self.fases_concluidas.append(fase_id)

            self.fase_status[fase_id] = "concluida"

            proxima_fase = fase_id + 1
            if proxima_fase <= 6:
                self.fase_status[proxima_fase] = "liberada"
                if proxima_fase not in self.available_phases:
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

            # SALVA PROGRESSO COMPLETO
            self._save_user_progress_robust()

            # Atualiza triggers
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
        """Retorna ao menu principal usando UserManager - MELHORADO"""
        try:
            # SALVA PROGRESSO ANTES DE SAIR (GARANTIDO)
            self._save_user_progress_robust()

            if self.on_exit_callback:
                self.on_exit_callback()

            # ATUALIZA USER_MANAGER PARA SINCRONIZAR COM O MENU
            user_manager.set_current_user(self.current_user, self.xp_bar)

            from views.menu_view import MenuView

            user_data = getattr(auth_system, "get_user_data", lambda u: None)(self.current_user) if self.current_user else None
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
        self._save_user_progress_robust()
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