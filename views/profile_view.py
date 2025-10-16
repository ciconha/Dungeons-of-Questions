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
        self.tabs = ["PERSONAGEM", "EQUIPAMENTOS", "DESAFIOS", "CONQUISTAS"]
        
        # Dados do personagem (simulados)
        self.personagem_data = {
            "vida": 850,
            "vida_maxima": 1000,
            "mana": 420,
            "mana_maxima": 500,
            "atributos": {
                "forca": 85,
                "velocidade": 72,
                "defesa": 63,
                "magia": 91,
                "agilidade": 78
            }
        }
        
        # Dados de desafios (simulados)
        self.desafios = [
            {"titulo": "Mestre dos Quiz", "progresso": 1, "total": 2, "concluido": False},
            {"titulo": "Explorador Incansável", "progresso": 3, "total": 5, "concluido": False},
            {"titulo": "Colecionador de Relíquias", "progresso": 7, "total": 10, "concluido": False}
        ]
        
        # Dados de equipamentos (simulados)
        self.equipamentos = [
            {"nome": "Espada Longa", "tipo": "arma", "equipado": True, "icone": "⚔️"},
            {"nome": "Armadura de Couro", "tipo": "armadura", "equipado": True, "icone": "🛡️"},
            {"nome": "Poção de Cura", "tipo": "consumivel", "equipado": False, "icone": "🧪"},
            {"nome": "Cajado Arcano", "tipo": "arma", "equipado": False, "icone": "🔮"}
        ]
        
        # Dados de conquistas (simulados)
        self.conquistas = [
            {"titulo": "Primeiros Passos", "concluida": True, "icone": "🎯", "raridade": "bronze"},
            {"titulo": "Mestre dos Quiz", "concluida": False, "icone": "🧠", "raridade": "prata"},
            {"titulo": "Colecionador Épico", "concluida": False, "icone": "💎", "raridade": "ouro"}
        ]
        
        # Carrega texturas
        self._load_textures()

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
        self.display_name = self.data.get("display_name", self.data.get("nome", "Sara Simpson"))
        self.username = self.data.get("username", self.user)
        self.level = self.data.get("level", 1)
        self.xp = self.data.get("xp", 0)
        self.max_xp = self.level * 100
        self.trophies = self.data.get("trophies", 568878)
        self.phase = self.data.get("phase", 1)
        
        print(f"👤 Perfil carregado: {self.display_name} (Nível {self.level})")

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
                # Tenta carregar a textura para verificar se existe
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

    def _draw_background(self):
        """Desenha fundo dark estilo RPG"""
        width, height = self.window.width, self.window.height
        
        # Gradiente escuro
        arcade.draw_lrbt_rectangle_filled(
            0, width, 0, height,
            (15, 10, 25)  # Preto-roxo muito escuro
        )
        
        # Padrão decorativo
        for i in range(0, width, 80):
            for j in range(0, height, 80):
                if (i + j) % 160 == 0:
                    arcade.draw_text(
                        "◆", i, j, 
                        (139, 0, 0, 30), 16,  # Vermelho escuro transparente
                        anchor_x="center", anchor_y="center"
                    )

    def _draw_main_layout(self):
        """Desenha estrutura principal do layout"""
        width, height = self.window.width, self.window.height
        
        # Painel central principal
        arcade.draw_lrbt_rectangle_filled(
            20, width - 20, 20, height - 20,
            (25, 20, 35, 220)  # Roxo muito escuro
        )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            20, width - 20, 20, height - 20,
            (139, 0, 0), 3  # Vermelho escuro
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
            (35, 30, 45)  # Roxo escuro
        )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            panel_x - panel_width/2, panel_x + panel_width/2,
            panel_y - panel_height/2, panel_y + panel_height/2,
            (139, 0, 0), 2  # Vermelho escuro
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
        
        # Level e XP
        level_y = info_y - 60
        
        arcade.draw_text(
            f"LEVEL {self.level}", panel_x, level_y,
            (255, 215, 0), 18,
            anchor_x="center", bold=True
        )
        
        # Barra de XP
        bar_width = panel_width * 0.8
        bar_x = panel_x - bar_width/2
        bar_y = level_y - 30
        
        # Fundo da barra
        arcade.draw_lrbt_rectangle_filled(
            bar_x, bar_x + bar_width, bar_y - 6, bar_y + 6,
            (50, 30, 30)  # Vermelho muito escuro
        )
        
        # Preenchimento da barra
        xp_percent = min(1.0, self.xp / self.max_xp) if self.max_xp > 0 else 0
        if xp_percent > 0:
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + (bar_width * xp_percent), 
                bar_y - 6, bar_y + 6,
                (220, 20, 60)  # Vermelho
            )
        
        # Borda da barra
        arcade.draw_lrbt_rectangle_outline(
            bar_x, bar_x + bar_width, bar_y - 6, bar_y + 6,
            (139, 0, 0), 2
        )
        
        # Texto XP
        arcade.draw_text(
            f"{self.xp}/{self.max_xp} XP", panel_x, bar_y - 20,
            (200, 200, 200), 12,
            anchor_x="center"
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
            self._draw_equipamentos_tab(panel_x, panel_y, panel_width, panel_height)
        elif self.active_tab == 2:  # DESAFIOS
            self._draw_desafios_tab(panel_x, panel_y, panel_width, panel_height)
        elif self.active_tab == 3:  # CONQUISTAS
            self._draw_conquistas_tab(panel_x, panel_y, panel_width, panel_height)

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
            "DETALHES DO PERSONAGEM",
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
        for i, (nome, valor) in enumerate(self.personagem_data["atributos"].items()):
            attr_y = atributos_y - (i * 30)
            
            arcade.draw_text(
                nome.upper(), stats_x - 80, attr_y,
                (200, 200, 200), 14,
            )
            
            # Barra do atributo
            bar_width = 150
            bar_x = stats_x - 30
            bar_value = valor / 100.0
            
            # Fundo
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + bar_width, attr_y - 8, attr_y + 8,
                (50, 50, 50)
            )
            
            # Preenchimento
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + (bar_width * bar_value), attr_y - 8, attr_y + 8,
                (139, 0, 0)  # Vermelho escuro
            )
            
            # Valor
            arcade.draw_text(
                str(valor), bar_x + bar_width + 10, attr_y,
                (255, 255, 255), 14,
                anchor_y="center"
            )

    def _draw_equipamentos_tab(self, x, y, width, height):
        """Desenha aba de equipamentos"""
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
        
        # Lista de equipamentos
        start_y = y + height/2 - 70
        for i, equip in enumerate(self.equipamentos):
            equip_y = start_y - (i * 60)
            self._draw_equipamento_item(x, equip_y, width * 0.8, 50, equip)

    def _draw_desafios_tab(self, x, y, width, height):
        """Desenha aba de desafios"""
        # Fundo
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            (30, 25, 45, 230)
        )
        
        # Título
        arcade.draw_text(
            "DESAFIOS ÉPICOS",
            x, y + height/2 - 30,
            (255, 215, 0), 24,
            anchor_x="center", bold=True
        )
        
        # Lista de desafios
        start_y = y + height/2 - 70
        for i, desafio in enumerate(self.desafios):
            desafio_y = start_y - (i * 80)
            self._draw_desafio_item(x, desafio_y, width * 0.8, 70, desafio)

    def _draw_conquistas_tab(self, x, y, width, height):
        """Desenha aba de conquistas"""
        # Fundo
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            (30, 25, 45, 230)
        )
        
        # Título
        arcade.draw_text(
            "CONQUISTAS E TROFÉUS",
            x, y + height/2 - 30,
            (255, 215, 0), 24,
            anchor_x="center", bold=True
        )
        
        # Lista de conquistas
        start_y = y + height/2 - 70
        for i, conquista in enumerate(self.conquistas):
            conquista_y = start_y - (i * 90)
            self._draw_conquista_item(x, conquista_y, width * 0.8, 80, conquista)

    def _draw_barra_vida(self, x, y, width, personagem):
        """Desenha barra de vida"""
        vida_percent = personagem["vida"] / personagem["vida_maxima"]
        
        # Fundo da barra
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2, y - 10, y + 10,
            (50, 20, 20)  # Vermelho escuro
        )
        
        # Vida atual
        if vida_percent > 0:
            arcade.draw_lrbt_rectangle_filled(
                x - width/2, x - width/2 + (width * vida_percent),
                y - 10, y + 10,
                (220, 20, 60)  # Vermelho
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
            (20, 20, 50)  # Azul escuro
        )
        
        # Mana atual
        if mana_percent > 0:
            arcade.draw_lrbt_rectangle_filled(
                x - width/2, x - width/2 + (width * mana_percent),
                y - 10, y + 10,
                (65, 105, 225)  # Azul real
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

    def _draw_equipamento_item(self, x, y, width, height, equipamento):
        """Desenha um item de equipamento"""
        # Fundo do item
        bg_color = (60, 55, 80) if equipamento["equipado"] else (40, 35, 60)
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            bg_color
        )
        
        # Borda
        border_color = (0, 255, 0) if equipamento["equipado"] else (139, 0, 0)
        arcade.draw_lrbt_rectangle_outline(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            border_color, 2
        )
        
        # Ícone
        arcade.draw_text(
            equipamento["icone"], x - width/2 + 20, y,
            (255, 215, 0), 20,
            anchor_y="center"
        )
        
        # Nome
        nome_color = (0, 255, 0) if equipamento["equipado"] else (255, 255, 255)
        arcade.draw_text(
            equipamento["nome"], x - width/2 + 50, y,
            nome_color, 16,
            anchor_y="center", bold=True
        )
        
        # Tipo
        arcade.draw_text(
            equipamento["tipo"].upper(), x + width/2 - 20, y,
            (150, 150, 150), 12,
            anchor_x="right", anchor_y="center"
        )

    def _draw_desafio_item(self, x, y, width, height, desafio):
        """Desenha um item de desafio"""
        # Fundo do item
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            (40, 35, 60)
        )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            (139, 0, 0), 2
        )
        
        # Título
        arcade.draw_text(
            desafio["titulo"], x - width/2 + 20, y + 10,
            (255, 255, 255), 16,
            bold=True
        )
        
        # Barra de progresso
        progresso = desafio["progresso"] / desafio["total"]
        bar_width = width * 0.7
        bar_x = x - width/2 + 20
        bar_y = y - 10
        
        # Fundo
        arcade.draw_lrbt_rectangle_filled(
            bar_x, bar_x + bar_width, bar_y - 5, bar_y + 5,
            (50, 50, 50)
        )
        
        # Progresso
        if progresso > 0:
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + (bar_width * progresso), bar_y - 5, bar_y + 5,
                (220, 20, 60)  # Vermelho
            )
        
        # Texto do progresso
        arcade.draw_text(
            f"{desafio['progresso']}/{desafio['total']}",
            bar_x + bar_width + 10, bar_y,
            (255, 255, 255), 12,
            anchor_y="center"
        )

    def _draw_conquista_item(self, x, y, width, height, conquista):
        """Desenha um item de conquista"""
        # Cores baseadas na raridade
        cores_raridade = {
            "bronze": (205, 127, 50),
            "prata": (192, 192, 192),
            "ouro": (255, 215, 0)
        }
        cor_raridade = cores_raridade.get(conquista["raridade"], (200, 200, 200))
        
        # Fundo do item
        bg_color = (60, 55, 80) if conquista["concluida"] else (40, 35, 60)
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            bg_color
        )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            cor_raridade, 3
        )
        
        # Ícone
        arcade.draw_text(
            conquista["icone"], x - width/2 + 30, y,
            cor_raridade, 24,
            anchor_y="center"
        )
        
        # Título
        title_color = (255, 255, 255) if conquista["concluida"] else (150, 150, 150)
        arcade.draw_text(
            conquista["titulo"], x - width/2 + 70, y + 10,
            title_color, 16,
            bold=True
        )
        
        # Status
        status = "CONCLUÍDA" if conquista["concluida"] else "EM ANDAMENTO"
        status_color = (0, 255, 0) if conquista["concluida"] else (255, 215, 0)
        arcade.draw_text(
            status, x + width/2 - 20, y,
            status_color, 12,
            anchor_x="right", anchor_y="center"
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
                color = (139, 0, 0)  # Vermelho escuro
                text_color = (255, 255, 255)  # Branco
            else:
                color = (60, 55, 80)  # Roxo médio
                text_color = (150, 150, 150)  # Cinza
            
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
            (35, 30, 45)  # Roxo escuro
        )
        
        # Borda
        arcade.draw_lrbt_rectangle_outline(
            20, width - 20, 20, 80,
            (139, 0, 0), 2  # Vermelho escuro
        )
        
        # Estatísticas do personagem
        stats = [
            ("FORÇA", self.personagem_data["atributos"]["forca"], "⚔"),
            ("VELOCIDADE", self.personagem_data["atributos"]["velocidade"], "🏃"), 
            ("DEFESA", self.personagem_data["atributos"]["defesa"], "🛡"),
            ("MAGIA", self.personagem_data["atributos"]["magia"], "🔮"),
            ("AGILIDADE", self.personagem_data["atributos"]["agilidade"], "💨")
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
                (150, 150, 150), 12,
                anchor_x="center"
            )
            
            arcade.draw_text(
                str(value), x_pos, 30,
                (255, 255, 255), 16,
                anchor_x="center", bold=True
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
        
        # Verifica clique nas setas do personagem (se estiver na aba de personagem)
        if self.active_tab == 0:
            self._handle_character_navigation_click(x, y)

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
                break

    def _handle_character_navigation_click(self, x, y):
        """Verifica clique nas setas de navegação do personagem"""
        width, height = self.window.width, self.window.height
        panel_x = width * 0.625
        panel_y = height * 0.5 + 20
        char_x = panel_x - (width * 0.7)/3  # Posição do sprite do personagem
        
        # Seta esquerda
        if (char_x - 80 <= x <= char_x - 40 and 
            panel_y - 15 <= y <= panel_y + 15):
            self._previous_character()
        
        # Seta direita  
        elif (char_x + 40 <= x <= char_x + 80 and 
              panel_y - 15 <= y <= panel_y + 15):
            self._next_character()