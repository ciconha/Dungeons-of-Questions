# views/profile_view.py

import arcade
from auth.simple_auth import auth_system
from auth.user_manager import user_manager


class ProfileView(arcade.View):
    def __init__(self, menu_view=None):
        super().__init__()
        self.menu_view = menu_view
        
        # Inicialização segura dos dados do usuário
        self._initialize_user_data()
        
        # Avatar e sprites
        self.avatar_texture = None
        self.character_texture = None
        self.current_character_index = 0
        self.characters = self._load_characters()
        
        # SpriteLists para desenho
        self.character_sprite_list = arcade.SpriteList()
        self.avatar_sprite_list = arcade.SpriteList()
        
        # Componentes de UI
        self.active_tab = 0
        self.tabs = ["PERSONAGEM", "EQUIPAMENTOS"]
        
        # Dados do personagem
        self.personagem_data = {
            "vida": 3264,
            "vida_maxima": 9264,
            "mana": 1920,
            "mana_maxima": 2600,
            "atributos": {
                "ataque_fisico": 2647,
                "ataque_magico": 2647,
                "defesa_fisica": 2647,
                "defesa_magica": 2647,
                "precisao": 130,
                "velocidade_ataque": 1.63
            }
        }
        
        # Sistema de barra de ativação (HOTBAR)
        self.hotbar_slots = {
            # Slots numéricos (1-8) para armas/habilidades
            '1': None, '2': None, '3': None, '4': None,
            '5': None, '6': None, '7': None, '8': None,
            # Slots de letras (A-G) para poções
            'A': None, 'B': None, 'C': None, 'D': None,
            'E': None, 'F': None, 'G': None
        }
        
        # Item selecionado para equipar
        self.selected_item = None
        self.showing_hotbar = False
        self.hotbar_message = None
        self.hotbar_message_timer = 0
        
        # Carrega texturas
        self._load_textures()
        
        # Carrega hotbar do usuário
        self._load_hotbar_from_data()

    def _initialize_user_data(self):
        """Inicializa dados do usuário de forma segura"""
        try:
            self.user = user_manager.get_current_user()
            self.data = auth_system.get_user_data(self.user) or {}
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados do usuário: {e}")
            self.user = "user"
            self.data = {}
        
        # Dados do usuário com fallbacks seguros
        self.display_name = self.data.get("display_name", "玩家名字七个字")
        self.username = self.data.get("username", self.user)
        self.level = self.data.get("level", 64)
        self.xp = self.data.get("xp", 75)
        self.max_xp = 100
        self.trophies = self.data.get("trophies", 5721636)
        self.phase = self.data.get("phase", 1)
        self.guild = self.data.get("guild", "黄龙会小帮派")
        self.coins = self.data.get("coins", 100)  # Moedas do usuário
        
        # Inventário da loja
        self.inventory = self.data.get("inventory", {})
        
        print(f"👤 Perfil carregado: {self.display_name} (Nível {self.level})")

    def _load_hotbar_from_data(self):
        """Carrega a configuração da hotbar dos dados do usuário"""
        hotbar_data = self.data.get("hotbar", {})
        for slot, item_id in hotbar_data.items():
            if slot in self.hotbar_slots:
                self.hotbar_slots[slot] = item_id

    def _save_hotbar_to_data(self):
        """Salva a configuração da hotbar nos dados do usuário"""
        try:
            # Filtra apenas os slots que têm itens equipados
            hotbar_to_save = {slot: item_id for slot, item_id in self.hotbar_slots.items() if item_id is not None}
            self.data["hotbar"] = hotbar_to_save
            auth_system.update_user_data(self.user, self.data)
            print("💾 Hotbar salva no banco de dados")
        except Exception as e:
            print(f"❌ Erro ao salvar hotbar: {e}")

    def _load_characters(self):
        """Carrega lista de personagens disponíveis de forma segura"""
        characters = [
            {"name": "Emily", "sprite": "assets/ui/Emilly.png"},
            {"name": "Guerreiro", "sprite": "assets/avatars/default.png"},
            {"name": "Mago", "sprite": "assets/ui/cristal.png"}
        ]
        
        # Filtra personagens com sprites válidos
        valid_characters = []
        for char in characters:
            try:
                arcade.load_texture(char["sprite"])
                valid_characters.append(char)
            except Exception as e:
                print(f"⚠️ Personagem não carregado {char['name']}: {e}")
        
        return valid_characters if valid_characters else [
            {"name": "Personagem Padrão", "sprite": "assets/avatars/default.png"}
        ]

    def _load_textures(self):
        """Carrega todas as texturas necessárias com tratamento de erro"""
        # Avatar do usuário
        avatar_path = self.data.get("avatar_path")
        if avatar_path:
            try:
                self.avatar_texture = arcade.load_texture(avatar_path)
                print(f"✅ Avatar carregado: {avatar_path}")
            except Exception as e:
                print(f"❌ Erro ao carregar avatar {avatar_path}: {e}")
                self.avatar_texture = None
        
        # Personagem atual
        if self.characters:
            current_char = self.characters[self.current_character_index]
            try:
                self.character_texture = arcade.load_texture(current_char["sprite"])
                print(f"✅ Personagem carregado: {current_char['name']}")
            except Exception as e:
                print(f"❌ Erro ao carregar personagem {current_char['sprite']}: {e}")
                self.character_texture = None

    def on_show(self):
        """Chamado quando a view é mostrada"""
        arcade.set_background_color((20, 15, 35))
        print("🎮 Tela de perfil aberta")

    def on_draw(self):
        """Renderiza toda a tela do perfil"""
        self.clear()
        
        # Fundo gradiente escuro
        self._draw_background()
        
        # Layout principal
        self._draw_main_layout()
        
        # Painel esquerdo - Avatar e informações básicas
        self._draw_left_panel()
        
        # Painel central - Conteúdo da aba ativa
        self._draw_active_tab_content()
        
        # Abas de navegação
        self._draw_navigation_tabs()
        
        # Rodapé com estatísticas
        self._draw_footer_stats()
        
        # Mensagens da hotbar
        self._draw_hotbar_messages()

    def _draw_background(self):
        """Desenha fundo dark estilo RPG"""
        width, height = self.window.width, self.window.height
        
        # Gradiente escuro
        arcade.draw_lrbt_rectangle_filled(
            0, width, 0, height,
            (15, 10, 25)
        )
        
        # Padrão decorativo
        for i in range(0, width, 80):
            for j in range(0, height, 80):
                if (i + j) % 160 == 0:
                    arcade.draw_text(
                        "◆", i, j, 
                        (139, 0, 0, 30), 16,
                        anchor_x="center", anchor_y="center"
                    )

    def _draw_main_layout(self):
        """Desenha estrutura principal do layout"""
        width, height = self.window.width, self.window.height
        
        # Painel central principal
        arcade.draw_lrbt_rectangle_filled(
            20, width - 20, 20, height - 20,
            (25, 20, 35, 220)
        )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            20, width - 20, 20, height - 20,
            (139, 0, 0), 3
        )

    def _draw_left_panel(self):
        """Desenha painel esquerdo com avatar e info básica"""
        width, height = self.window.width, self.window.height
        
        # Painel esquerdo
        panel_width = width * 0.25
        panel_height = height * 0.8
        panel_x = panel_width / 2 + 20
        panel_y = height / 2
        
        # Fundo do painel
        arcade.draw_lrbt_rectangle_filled(
            panel_x - panel_width/2, panel_x + panel_width/2,
            panel_y - panel_height/2, panel_y + panel_height/2,
            (35, 30, 45)
        )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            panel_x - panel_width/2, panel_x + panel_width/2,
            panel_y - panel_height/2, panel_y + panel_height/2,
            (139, 0, 0), 2
        )
        
        # Avatar
        avatar_x = panel_x
        avatar_y = panel_y + panel_height/2 - 80
        
        # Círculo do avatar com borda vermelha
        arcade.draw_circle_filled(avatar_x, avatar_y, 50, (45, 40, 55))
        arcade.draw_circle_outline(avatar_x, avatar_y, 50, (139, 0, 0), 3)
        
        if self.avatar_texture:
            self._draw_avatar_sprite(avatar_x, avatar_y)
        else:
            arcade.draw_text(
                "👤", avatar_x, avatar_y,
                (200, 200, 200), 32,
                anchor_x="center", anchor_y="center"
            )
        
        # Informações do usuário
        info_y = avatar_y - 80
        
        arcade.draw_text(
            self.display_name, panel_x, info_y,
            (255, 255, 255), 20,
            anchor_x="center", bold=True
        )
        
        arcade.draw_text(
            f"@{self.username}", panel_x, info_y - 25,
            (150, 150, 150), 14,
            anchor_x="center"
        )
        
        # Guilda
        arcade.draw_text(
            self.guild, panel_x, info_y - 50,
            (255, 215, 0), 16,
            anchor_x="center", bold=True
        )
        
        # Level e XP
        level_y = info_y - 85
        
        arcade.draw_text(
            f"LEVEL {self.level}", panel_x, level_y,
            (255, 215, 0), 18,
            anchor_x="center", bold=True
        )
        
        # Barra de XP
        bar_width = panel_width * 0.8
        bar_x = panel_x - bar_width/2
        bar_y = level_y - 25
        
        # Fundo da barra
        arcade.draw_lrbt_rectangle_filled(
            bar_x, bar_x + bar_width, bar_y - 6, bar_y + 6,
            (50, 30, 30)
        )
        
        # Preenchimento da barra
        xp_percent = min(1.0, self.xp / self.max_xp) if self.max_xp > 0 else 0
        if xp_percent > 0:
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + (bar_width * xp_percent), 
                bar_y - 6, bar_y + 6,
                (220, 20, 60)
            )
        
        # Borda da barra
        arcade.draw_lrbt_rectangle_outline(
            bar_x, bar_x + bar_width, bar_y - 6, bar_y + 6,
            (139, 0, 0), 2
        )
        
        # Texto XP
        arcade.draw_text(
            f"{self.xp}%", panel_x, bar_y - 20,
            (200, 200, 200), 12,
            anchor_x="center"
        )
        
        # Troféus
        arcade.draw_text(
            f"🏆 {self.trophies}", panel_x, bar_y - 45,
            (255, 215, 0), 16,
            anchor_x="center", bold=True
        )
        
        # Moedas
        arcade.draw_text(
            f"💰 {self.coins} moedas", panel_x, bar_y - 75,
            (255, 215, 0), 16,
            anchor_x="center", bold=True
        )

    def _draw_active_tab_content(self):
        """Desenha o conteúdo da aba ativa"""
        width, height = self.window.width, self.window.height
        
        # Painel central
        panel_width = width * 0.7
        panel_height = height * 0.75
        panel_x = width * 0.625
        panel_y = height * 0.5 + 20
        
        # Desenha conteúdo baseado na aba ativa
        if self.active_tab == 0:  # PERSONAGEM
            self._draw_personagem_tab(panel_x, panel_y, panel_width, panel_height)
        elif self.active_tab == 1:  # EQUIPAMENTOS
            if self.showing_hotbar:
                self._draw_hotbar_config(panel_x, panel_y, panel_width, panel_height)
            else:
                self._draw_equipamentos_tab(panel_x, panel_y, panel_width, panel_height)

    def _draw_personagem_tab(self, x, y, width, height):
        """Desenha aba de personagem"""
        # Fundo
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            (30, 25, 45, 230)
        )
        
        # Título
        arcade.draw_text(
            "ATRIBUTOS DO PERSONAGEM",
            x, y + height/2 - 30,
            (255, 215, 0), 24,
            anchor_x="center", bold=True
        )
        
        # Sprite do personagem
        char_x = x - width/3
        char_y = y
        if self.character_texture:
            self._draw_character_sprite(char_x, char_y, 150)
        else:
            arcade.draw_text(
                "🎮", char_x, char_y,
                (200, 200, 200), 64,
                anchor_x="center", anchor_y="center"
            )
        
        # Nome do personagem
        if self.characters:
            current_char = self.characters[self.current_character_index]
            arcade.draw_text(
                current_char["name"],
                char_x, char_y - 90,
                (255, 255, 255), 20,
                anchor_x="center", bold=True
            )
        
        # Estatísticas à direita
        stats_x = x + width/4
        stats_y = y + height/2 - 80
        
        # Barras de vida e mana
        self._draw_barra_vida(stats_x, stats_y, width * 0.4, self.personagem_data)
        self._draw_barra_mana(stats_x, stats_y - 40, width * 0.4, self.personagem_data)
        
        # Atributos
        atributos_y = stats_y - 100
        atributos = [
            ("ATAQUE FÍSICO", self.personagem_data["atributos"]["ataque_fisico"], "⚔️"),
            ("ATAQUE MÁGICO", self.personagem_data["atributos"]["ataque_magico"], "🔮"),
            ("DEFESA FÍSICA", self.personagem_data["atributos"]["defesa_fisica"], "🛡️"),
            ("DEFESA MÁGICA", self.personagem_data["atributos"]["defesa_magica"], "✨"),
            ("PRECISÃO", self.personagem_data["atributos"]["precisao"], "🎯"),
            ("VELOC. ATAQUE", self.personagem_data["atributos"]["velocidade_ataque"], "⚡")
        ]
        
        for i, (nome, valor, icone) in enumerate(atributos):
            attr_y = atributos_y - (i * 35)
            
            # Ícone
            arcade.draw_text(
                icone, stats_x - 100, attr_y,
                (255, 215, 0), 14,
                anchor_x="center", anchor_y="center"
            )
            
            # Nome do atributo
            arcade.draw_text(
                nome, stats_x - 80, attr_y,
                (200, 200, 200), 12,
                anchor_y="center"
            )
            
            # Valor
            arcade.draw_text(
                str(valor), stats_x + 120, attr_y,
                (255, 255, 255), 14,
                anchor_x="right", anchor_y="center", bold=True
            )

    def _draw_equipamentos_tab(self, x, y, width, height):
        """Desenha aba de equipamentos principal"""
        # Fundo
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            (30, 25, 45, 230)
        )
        
        # Título
        arcade.draw_text(
            "INVENTÁRIO - EQUIPAMENTOS",
            x, y + height/2 - 30,
            (255, 215, 0), 24,
            anchor_x="center", bold=True
        )
        
        # Botão para configurar barra de ativação
        button_x = x
        button_y = y + height/2 - 80
        button_width = 300
        button_height = 50
        
        # Fundo do botão
        arcade.draw_lrbt_rectangle_filled(
            button_x - button_width/2, button_x + button_width/2,
            button_y - button_height/2, button_y + button_height/2,
            (100, 150, 255)
        )
        
        # Borda do botão
        arcade.draw_lrbt_rectangle_outline(
            button_x - button_width/2, button_x + button_width/2,
            button_y - button_height/2, button_y + button_height/2,
            (255, 255, 255), 2
        )
        
        # Texto do botão
        arcade.draw_text(
            "⚙️ CONFIGURAR BARRA DE ATIVAÇÃO",
            button_x, button_y,
            (255, 255, 255), 16,
            anchor_x="center", anchor_y="center", bold=True
        )
        
        # Guardar posição do botão para clique
        self.hotbar_button_rect = (
            button_x - button_width/2, button_x + button_width/2,
            button_y - button_height/2, button_y + button_height/2
        )
        
        # Lista de itens do inventário
        start_y = button_y - 80
        arcade.draw_text(
            "SEU INVENTÁRIO:",
            x - width/2 + 40, start_y,
            (255, 215, 0), 18,
            bold=True
        )
        
        # Itens da loja disponíveis no inventário
        shop_items_data = {
            "potion_health": {"name": "Poção de Vida", "icon": "❤️", "type": "potion"},
            "potion_mana": {"name": "Poção de Mana", "icon": "🔵", "type": "potion"},
            "weapon_sword": {"name": "Espada do Saber", "icon": "⚔️", "type": "weapon"},
            "weapon_staff": {"name": "Cajado Mágico", "icon": "🔮", "type": "weapon"},
            "skill_focus": {"name": "Foco Mental", "icon": "🧠", "type": "skill"},
            "skill_time": {"name": "Tempo Extra", "icon": "⏱️", "type": "skill"}
        }
        
        # Mostra itens do inventário
        inventory_y = start_y - 40
        item_index = 0
        for item_id, quantity in self.inventory.items():
            if item_id in shop_items_data:
                item_data = shop_items_data[item_id]
                item_y = inventory_y - (item_index * 70)
                self._draw_inventory_item(x, item_y, width * 0.8, 60, item_data, quantity, item_id)
                item_index += 1

    def _draw_hotbar_config(self, x, y, width, height):
        """Desenha a tela de configuração da barra de ativação"""
        # Fundo
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            (30, 25, 45, 230)
        )
        
        # Título
        arcade.draw_text(
            "CONFIGURAÇÃO DA BARRA DE ATIVAÇÃO",
            x, y + height/2 - 30,
            (255, 215, 0), 24,
            anchor_x="center", bold=True
        )
        
        # Instruções
        arcade.draw_text(
            "Clique em um item do inventário e depois em um slot para equipar",
            x, y + height/2 - 60,
            (200, 200, 200), 14,
            anchor_x="center"
        )
        
        # Desenha a barra de ativação
        self._draw_hotbar(x, y - 50, width * 0.8)
        
        # Lista de itens do inventário abaixo da hotbar
        inventory_y = y - 200
        arcade.draw_text(
            "SEU INVENTÁRIO:",
            x - width/2 + 40, inventory_y,
            (255, 215, 0), 18,
            bold=True
        )
        
        # Itens da loja disponíveis
        shop_items_data = {
            "potion_health": {"name": "Poção de Vida", "icon": "❤️", "type": "potion"},
            "potion_mana": {"name": "Poção de Mana", "icon": "🔵", "type": "potion"},
            "weapon_sword": {"name": "Espada do Saber", "icon": "⚔️", "type": "weapon"},
            "weapon_staff": {"name": "Cajado Mágico", "icon": "🔮", "type": "weapon"},
            "skill_focus": {"name": "Foco Mental", "icon": "🧠", "type": "skill"},
            "skill_time": {"name": "Tempo Extra", "icon": "⏱️", "type": "skill"}
        }
        
        # Mostra itens do inventário
        item_y = inventory_y - 40
        item_index = 0
        for item_id, quantity in self.inventory.items():
            if item_id in shop_items_data:
                item_data = shop_items_data[item_id]
                current_y = item_y - (item_index * 70)
                self._draw_inventory_item(x, current_y, width * 0.8, 60, item_data, quantity, item_id)
                item_index += 1
        
        # Botão voltar
        back_button_y = y - height/2 + 50
        arcade.draw_lrbt_rectangle_filled(
            x - 80, x + 80, back_button_y - 20, back_button_y + 20,
            (139, 0, 0)
        )
        arcade.draw_text(
            "VOLTAR", x, back_button_y,
            (255, 255, 255), 14,
            anchor_x="center", anchor_y="center", bold=True
        )
        self.back_button_rect = (x - 80, x + 80, back_button_y - 20, back_button_y + 20)
        
        # Botão salvar
        save_button_y = back_button_y - 50
        arcade.draw_lrbt_rectangle_filled(
            x - 80, x + 80, save_button_y - 20, save_button_y + 20,
            (0, 150, 0)
        )
        arcade.draw_text(
            "SALVAR", x, save_button_y,
            (255, 255, 255), 14,
            anchor_x="center", anchor_y="center", bold=True
        )
        self.save_button_rect = (x - 80, x + 80, save_button_y - 20, save_button_y + 20)

    def _draw_hotbar(self, x, y, width):
        """Desenha a barra de ativação (hotbar)"""
        slot_size = 60
        spacing = 10
        start_x = x - (width / 2) + slot_size/2
        
        # Título dos slots numéricos
        arcade.draw_text(
            "ARMAS/HABILIDADES (1-8)",
            x, y + 100,
            (255, 215, 0), 16,
            anchor_x="center", bold=True
        )
        
        # Slots numéricos (1-8) - Quadrados
        for i in range(8):
            slot_x = start_x + (i * (slot_size + spacing))
            slot_id = str(i + 1)
            self._draw_hotbar_slot(slot_x, y + 50, slot_size, slot_id, is_circle=False)
        
        # Título dos slots de poções
        arcade.draw_text(
            "POÇÕES (A-G)",
            x, y - 30,
            (255, 215, 0), 16,
            anchor_x="center", bold=True
        )
        
        # Slots de letras (A-G) - Círculos
        for i in range(7):
            slot_x = start_x + (i * (slot_size + spacing))
            slot_id = chr(65 + i)  # A, B, C, D, E, F, G
            self._draw_hotbar_slot(slot_x, y - 80, slot_size, slot_id, is_circle=True)

    def _draw_hotbar_slot(self, x, y, size, slot_id, is_circle=False):
        """Desenha um slot individual da hotbar"""
        # Cores
        bg_color = (60, 55, 80)
        border_color = (139, 0, 0)
        
        if self.selected_item == slot_id:
            border_color = (255, 215, 0)  # Dourado para slot selecionado
        
        # Desenha o slot
        if is_circle:
            # Slot circular para poções
            arcade.draw_circle_filled(x, y, size/2, bg_color)
            arcade.draw_circle_outline(x, y, size/2, border_color, 3)
        else:
            # Slot quadrado para armas/habilidades
            arcade.draw_lrbt_rectangle_filled(
                x - size/2, x + size/2, y - size/2, y + size/2,
                bg_color
            )
            arcade.draw_lrbt_rectangle_outline(
                x - size/2, x + size/2, y - size/2, y + size/2,
                border_color, 3
            )
        
        # ID do slot (número ou letra)
        arcade.draw_text(
            slot_id, x, y,
            (255, 255, 255), 16,
            anchor_x="center", anchor_y="center", bold=True
        )
        
        # Item equipado (se houver)
        item_id = self.hotbar_slots.get(slot_id)
        if item_id:
            # Ícones dos itens baseados no ID
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

    def _draw_inventory_item(self, x, y, width, height, item_data, quantity, item_id):
        """Desenha um item do inventário"""
        # Fundo do item
        bg_color = (60, 55, 80) if self.selected_item != item_id else (80, 75, 100)
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            bg_color
        )
        
        # Borda
        border_color = (0, 255, 0) if self.selected_item == item_id else (139, 0, 0)
        arcade.draw_lrbt_rectangle_outline(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            border_color, 2
        )
        
        # Ícone
        arcade.draw_text(
            item_data["icon"], x - width/2 + 30, y,
            (255, 215, 0), 24,
            anchor_y="center"
        )
        
        # Nome
        arcade.draw_text(
            item_data["name"], x - width/2 + 70, y + 10,
            (255, 255, 255), 16,
            bold=True
        )
        
        # Tipo
        type_color = (100, 200, 255) if item_data["type"] == "weapon" else (
            (255, 100, 255) if item_data["type"] == "skill" else (100, 255, 100)
        )
        arcade.draw_text(
            f"Tipo: {item_data['type']}", x - width/2 + 70, y - 10,
            type_color, 12
        )
        
        # Quantidade
        arcade.draw_text(
            f"Quantidade: {quantity}", x + width/2 - 20, y,
            (200, 200, 200), 12,
            anchor_x="right", anchor_y="center"
        )

    def _draw_barra_vida(self, x, y, width, personagem):
        """Desenha barra de vida"""
        vida_percent = personagem["vida"] / personagem["vida_maxima"]
        
        # Fundo da barra
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2, y - 10, y + 10,
            (50, 20, 20)
        )
        
        # Vida atual
        if vida_percent > 0:
            arcade.draw_lrbt_rectangle_filled(
                x - width/2, x - width/2 + (width * vida_percent),
                y - 10, y + 10,
                (220, 20, 60)
            )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            x - width/2, x + width/2, y - 10, y + 10,
            (139, 0, 0), 2
        )
        
        # Texto
        arcade.draw_text(
            f"VIDA: {personagem['vida']}/{personagem['vida_maxima']}",
            x, y - 25,
            (255, 255, 255), 12,
            anchor_x="center"
        )

    def _draw_barra_mana(self, x, y, width, personagem):
        """Desenha barra de mana"""
        mana_percent = personagem["mana"] / personagem["mana_maxima"]
        
        # Fundo da barra
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2, y - 10, y + 10,
            (20, 20, 50)
        )
        
        # Mana atual
        if mana_percent > 0:
            arcade.draw_lrbt_rectangle_filled(
                x - width/2, x - width/2 + (width * mana_percent),
                y - 10, y + 10,
                (65, 105, 225)
            )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            x - width/2, x + width/2, y - 10, y + 10,
            (30, 144, 255), 2
        )
        
        # Texto
        arcade.draw_text(
            f"MANA: {personagem['mana']}/{personagem['mana_maxima']}",
            x, y - 25,
            (255, 255, 255), 12,
            anchor_x="center"
        )

    def _draw_navigation_tabs(self):
        """Desenha abas de navegação"""
        width, height = self.window.width, self.window.height
        
        tab_width = width / len(self.tabs)
        tab_height = 40
        tab_y = height - 60
        
        for i, tab in enumerate(self.tabs):
            tab_x = (i * tab_width) + (tab_width / 2)
            
            # Cor da aba ativa/inativa
            if i == self.active_tab:
                color = (139, 0, 0)
                text_color = (255, 255, 255)
            else:
                color = (60, 55, 80)
                text_color = (150, 150, 150)
            
            # Fundo da aba
            arcade.draw_lrbt_rectangle_filled(
                tab_x - tab_width/2, tab_x + tab_width/2,
                tab_y - tab_height/2, tab_y + tab_height/2,
                color
            )
            
            # Texto da aba
            arcade.draw_text(
                tab, tab_x, tab_y,
                text_color, 16,
                anchor_x="center", anchor_y="center",
                bold=True
            )

    def _draw_footer_stats(self):
        """Desenha estatísticas no rodapé"""
        width, height = self.window.width, self.window.height
        
        # Painel de estatísticas do rodapé
        arcade.draw_lrbt_rectangle_filled(
            20, width - 20, 20, 80,
            (35, 30, 45)
        )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            20, width - 20, 20, 80,
            (139, 0, 0), 2
        )
        
        # Estatísticas do personagem
        stats = [
            ("ATAQUE FÍSICO", self.personagem_data["atributos"]["ataque_fisico"], "⚔️"),
            ("ATAQUE MÁGICO", self.personagem_data["atributos"]["ataque_magico"], "🔮"),
            ("DEFESA FÍSICA", self.personagem_data["atributos"]["defesa_fisica"], "🛡️"),
            ("DEFESA MÁGICA", self.personagem_data["atributos"]["defesa_magica"], "✨"),
            ("PRECISÃO", self.personagem_data["atributos"]["precisao"], "🎯"),
            ("VELOC. ATAQUE", self.personagem_data["atributos"]["velocidade_ataque"], "⚡")
        ]
        
        stat_spacing = (width - 40) / len(stats)
        
        for i, (label, value, icon) in enumerate(stats):
            x_pos = 40 + (i * stat_spacing)
            
            arcade.draw_text(
                icon, x_pos, 60,
                (255, 215, 0), 16,
                anchor_x="center"
            )
            
            arcade.draw_text(
                label, x_pos, 45,
                (150, 150, 150), 10,
                anchor_x="center"
            )
            
            arcade.draw_text(
                str(value), x_pos, 30,
                (255, 255, 255), 14,
                anchor_x="center", bold=True
            )

    def _draw_hotbar_messages(self):
        """Desenha mensagens da hotbar"""
        if self.hotbar_message and self.hotbar_message_timer > 0:
            width, height = self.window.width, self.window.height
            
            # Fundo da mensagem
            arcade.draw_lrbt_rectangle_filled(
                width/2 - 200, width/2 + 200,
                height/2 - 25, height/2 + 25,
                (30, 30, 40, 240)
            )
            
            # Borda
            arcade.draw_lrbt_rectangle_outline(
                width/2 - 200, width/2 + 200,
                height/2 - 25, height/2 + 25,
                (212, 175, 55), 2
            )
            
            # Texto da mensagem
            arcade.draw_text(
                self.hotbar_message,
                width/2, height/2,
                (255, 255, 255), 16,
                anchor_x="center", anchor_y="center",
                bold=True
            )

    def _draw_character_sprite(self, x, y, size):
        """Desenha o sprite do personagem"""
        self.character_sprite_list.clear()
        
        character_sprite = arcade.Sprite()
        character_sprite.texture = self.character_texture
        
        # Calcula escala para manter proporção
        scale_x = size / self.character_texture.width
        scale_y = size / self.character_texture.height
        scale = min(scale_x, scale_y)
        
        character_sprite.scale = scale
        character_sprite.center_x = x
        character_sprite.center_y = y
        self.character_sprite_list.append(character_sprite)
        self.character_sprite_list.draw()

    def _draw_avatar_sprite(self, x, y):
        """Desenha sprite do avatar"""
        self.avatar_sprite_list.clear()
        
        avatar_sprite = arcade.Sprite()
        avatar_sprite.texture = self.avatar_texture
        
        # Calcula escala para caber no círculo
        scale_x = 90 / self.avatar_texture.width
        scale_y = 90 / self.avatar_texture.height
        scale = min(scale_x, scale_y)
        
        avatar_sprite.scale = scale
        avatar_sprite.center_x = x
        avatar_sprite.center_y = y
        self.avatar_sprite_list.append(avatar_sprite)
        self.avatar_sprite_list.draw()

    def on_key_press(self, key, modifiers):
        """Lida com pressionamento de teclas"""
        # Navegação entre abas
        if key == arcade.key.LEFT:
            self.active_tab = (self.active_tab - 1) % len(self.tabs)
        elif key == arcade.key.RIGHT:
            self.active_tab = (self.active_tab + 1) % len(self.tabs)
        
        # Navegação entre personagens
        elif key == arcade.key.A:
            self._previous_character()
        elif key == arcade.key.D:
            self._next_character()
        
        # Voltar ao menu
        elif key in (arcade.key.ESCAPE, arcade.key.BACKSPACE, arcade.key.P):
            if self.showing_hotbar:
                self.showing_hotbar = False
                self.selected_item = None
            else:
                self._return_to_menu()

    def _previous_character(self):
        """Navega para o personagem anterior"""
        if self.characters:
            self.current_character_index = (self.current_character_index - 1) % len(self.characters)
            self._load_textures()

    def _next_character(self):
        """Navega para o próximo personagem"""
        if self.characters:
            self.current_character_index = (self.current_character_index + 1) % len(self.characters)
            self._load_textures()

    def _return_to_menu(self):
        """Volta para o menu principal"""
        try:
            if self.menu_view:
                self.window.show_view(self.menu_view)
            elif hasattr(self.window, 'menu_view'):
                self.window.show_view(self.window.menu_view)
            else:
                from views.menu_view import MenuView
                self.window.menu_view = MenuView()
                self.window.show_view(self.window.menu_view)
            print("↩️ Voltando para o menu principal")
        except Exception as e:
            print(f"❌ Erro ao voltar para o menu: {e}")

    def on_mouse_press(self, x, y, button, modifiers):
        """Lida com cliques do mouse"""
        # Verifica clique nas abas
        self._handle_tab_click(x, y)
        
        if self.active_tab == 0:  # PERSONAGEM
            self._handle_character_navigation_click(x, y)
        elif self.active_tab == 1:  # EQUIPAMENTOS
            if self.showing_hotbar:
                self._handle_hotbar_config_click(x, y)
            else:
                self._handle_equipamentos_click(x, y)

    def _handle_tab_click(self, x, y):
        """Verifica clique nas abas de navegação"""
        width, height = self.window.width, self.window.height
        tab_width = width / len(self.tabs)
        tab_height = 40
        tab_y = height - 60
        
        for i in range(len(self.tabs)):
            tab_x1 = i * tab_width
            tab_x2 = (i + 1) * tab_width
            
            if (tab_x1 <= x <= tab_x2 and 
                tab_y - tab_height/2 <= y <= tab_y + tab_height/2):
                self.active_tab = i
                self.showing_hotbar = False
                self.selected_item = None
                break

    def _handle_character_navigation_click(self, x, y):
        """Verifica clique nas setas de navegação do personagem"""
        width, height = self.window.width, self.window.height
        panel_x = width * 0.625
        panel_y = height * 0.5 + 20
        char_x = panel_x - (width * 0.7)/3
        
        # Seta esquerda
        if (char_x - 80 <= x <= char_x - 40 and 
            panel_y - 15 <= y <= panel_y + 15):
            self._previous_character()
        
        # Seta direita  
        elif (char_x + 40 <= x <= char_x + 80 and 
              panel_y - 15 <= y <= panel_y + 15):
            self._next_character()

    def _handle_equipamentos_click(self, x, y):
        """Verifica clique na aba de equipamentos principal"""
        # Botão da hotbar
        if hasattr(self, 'hotbar_button_rect'):
            l, r, b, t = self.hotbar_button_rect
            if l <= x <= r and b <= y <= t:
                self.showing_hotbar = True
                self.selected_item = None

    def _handle_hotbar_config_click(self, x, y):
        """Verifica clique na configuração da hotbar"""
        width, height = self.window.width, self.window.height
        
        # Botão voltar
        if hasattr(self, 'back_button_rect'):
            l, r, b, t = self.back_button_rect
            if l <= x <= r and b <= y <= t:
                self.showing_hotbar = False
                self.selected_item = None
                return
        
        # Botão salvar
        if hasattr(self, 'save_button_rect'):
            l, r, b, t = self.save_button_rect
            if l <= x <= r and b <= y <= t:
                self._save_hotbar_to_data()
                self._show_hotbar_message("✅ Configuração salva!")
                return
        
        # Verifica clique nos slots da hotbar
        panel_x = width * 0.625
        panel_y = height * 0.5 + 20
        hotbar_y = panel_y - 50
        slot_size = 60
        spacing = 10
        start_x = panel_x - ((width * 0.7) / 2) + slot_size/2
        
        # Slots numéricos (1-8)
        for i in range(8):
            slot_x = start_x + (i * (slot_size + spacing))
            slot_id = str(i + 1)
            slot_rect = (slot_x - slot_size/2, slot_x + slot_size/2, 
                        hotbar_y + 50 - slot_size/2, hotbar_y + 50 + slot_size/2)
            
            if self._point_in_rect(x, y, slot_rect):
                self._assign_item_to_slot(slot_id)
                return
        
        # Slots de letras (A-G)
        for i in range(7):
            slot_x = start_x + (i * (slot_size + spacing))
            slot_id = chr(65 + i)  # A, B, C, D, E, F, G
            slot_center_y = hotbar_y - 80
            # Para círculos, verifica distância do centro
            distance = ((x - slot_x) ** 2 + (y - slot_center_y) ** 2) ** 0.5
            if distance <= slot_size/2:
                self._assign_item_to_slot(slot_id)
                return
        
        # Verifica clique nos itens do inventário
        inventory_y = hotbar_y - 200
        item_y = inventory_y - 40
        
        shop_items_data = {
            "potion_health": {"name": "Poção de Vida", "icon": "❤️", "type": "potion"},
            "potion_mana": {"name": "Poção de Mana", "icon": "🔵", "type": "potion"},
            "weapon_sword": {"name": "Espada do Saber", "icon": "⚔️", "type": "weapon"},
            "weapon_staff": {"name": "Cajado Mágico", "icon": "🔮", "type": "weapon"},
            "skill_focus": {"name": "Foco Mental", "icon": "🧠", "type": "skill"},
            "skill_time": {"name": "Tempo Extra", "icon": "⏱️", "type": "skill"}
        }
        
        item_index = 0
        for item_id in self.inventory.keys():
            if item_id in shop_items_data:
                current_y = item_y - (item_index * 70)
                item_rect = (panel_x - (width * 0.7)/2, panel_x + (width * 0.7)/2,
                           current_y - 30, current_y + 30)
                
                if self._point_in_rect(x, y, item_rect):
                    self.selected_item = item_id
                    self._show_hotbar_message(f"Selecionado: {shop_items_data[item_id]['name']}")
                    return
                item_index += 1

    def _point_in_rect(self, x, y, rect):
        """Verifica se um ponto está dentro de um retângulo"""
        l, r, b, t = rect
        return l <= x <= r and b <= y <= t

    def _assign_item_to_slot(self, slot_id):
        """Atribui o item selecionado a um slot da hotbar"""
        if not self.selected_item:
            self._show_hotbar_message("❌ Selecione um item primeiro!")
            return
        
        # Verifica se o slot já está ocupado
        current_item = self.hotbar_slots.get(slot_id)
        if current_item:
            self._show_hotbar_message("❌ Slot já ocupado! Selecione outro.")
            return
        
        # Atribui o item ao slot
        self.hotbar_slots[slot_id] = self.selected_item
        self._show_hotbar_message(f"✅ Item equipado no slot {slot_id}!")
        self.selected_item = None

    def _show_hotbar_message(self, message):
        """Mostra mensagem temporária na hotbar"""
        self.hotbar_message = message
        self.hotbar_message_timer = 3.0  # 3 segundos

    def on_update(self, delta_time):
        """Atualiza a lógica da view"""
        # Atualiza timer da mensagem da hotbar
        if self.hotbar_message_timer > 0:
            self.hotbar_message_timer -= delta_time
            if self.hotbar_message_timer <= 0:
                self.hotbar_message = None