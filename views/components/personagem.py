import arcade

class PersonagemComponent:
    def __init__(self):
        self.personagens = []
        self.personagem_principal = None
        self.carregar_personagens()
    
    def carregar_personagens(self):
        """Carrega todos os personagens disponíveis"""
        self.personagens = [
            {
                "id": 1,
                "nome": "Emily",
                "sprite": "assets/ui/Emilly.png",
                "game_sprite": "assets/characters/Emillywhite.png",
                "nivel": 15,
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
                },
                "equipado": True,
                "desbloqueado": True
            },
            {
                "id": 2,
                "nome": "Guerreiro Sombrio",
                "sprite": "assets/characters/warrior.png",
                "game_sprite": "assets/characters/warrior_game.png",
                "nivel": 1,
                "vida": 500,
                "vida_maxima": 500,
                "mana": 200,
                "mana_maxima": 200,
                "atributos": {
                    "forca": 95,
                    "velocidade": 60,
                    "defesa": 85,
                    "magia": 30,
                    "agilidade": 65
                },
                "equipado": False,
                "desbloqueado": False
            },
            {
                "id": 3,
                "nome": "Mago Arcano",
                "sprite": "assets/characters/mage.png",
                "game_sprite": "assets/characters/mage_game.png",
                "nivel": 1,
                "vida": 350,
                "vida_maxima": 350,
                "mana": 800,
                "mana_maxima": 800,
                "atributos": {
                    "forca": 40,
                    "velocidade": 65,
                    "defesa": 45,
                    "magia": 95,
                    "agilidade": 70
                },
                "equipado": False,
                "desbloqueado": False
            }
        ]
        self.personagem_principal = self.personagens[0]
    
    def selecionar_personagem_principal(self, personagem_id):
        """Seleciona um personagem como principal"""
        for personagem in self.personagens:
            if personagem["id"] == personagem_id and personagem["desbloqueado"]:
                self.personagem_principal = personagem
                return True
        return False
    
    def desbloquear_personagem(self, personagem_id):
        """Desbloqueia um novo personagem"""
        for personagem in self.personagens:
            if personagem["id"] == personagem_id:
                personagem["desbloqueado"] = True
                return True
        return False
    
    def get_personagem_por_id(self, personagem_id):
        """Retorna um personagem pelo ID"""
        for personagem in self.personagens:
            if personagem["id"] == personagem_id:
                return personagem
        return None
    
    def draw_personagem_detalhes(self, x, y, width, height):
        """Desenha os detalhes do personagem"""
        if not self.personagem_principal:
            return
        
        p = self.personagem_principal
        
        # Fundo do painel
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            (30, 25, 45, 230)
        )
        
        # Borda decorativa
        arcade.draw_lrbt_rectangle_outline(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            (139, 0, 0), 3  # Vermelho escuro
        )
        
        # Nome e nível
        arcade.draw_text(
            f"{p['nome']} - Nv. {p['nivel']}",
            x, y + height/2 - 40,
            (255, 215, 0), 22,
            anchor_x="center", bold=True
        )
        
        # Barras de vida e mana
        self._draw_barra_vida(x, y + height/2 - 80, width * 0.8, p)
        self._draw_barra_mana(x, y + height/2 - 110, width * 0.8, p)
        
        # Atributos
        self._draw_atributos(x, y, width, height, p)
    
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
    
    def _draw_atributos(self, x, y, width, height, personagem):
        """Desenha atributos do personagem"""
        atributos = personagem["atributos"]
        start_y = y + height/2 - 150
        spacing = 30
        
        for i, (nome, valor) in enumerate(atributos.items()):
            attr_y = start_y - (i * spacing)
            
            # Nome do atributo
            arcade.draw_text(
                nome.upper(), x - width/2 + 20, attr_y,
                (200, 200, 200), 14,
            )
            
            # Barra do atributo
            bar_width = width * 0.6
            bar_x = x - width/2 + 100
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
            
            # Borda
            arcade.draw_lrbt_rectangle_outline(
                bar_x, bar_x + bar_width, attr_y - 8, attr_y + 8,
                (255, 215, 0), 1
            )
            
            # Valor
            arcade.draw_text(
                str(valor), bar_x + bar_width + 10, attr_y,
                (255, 255, 255), 14,
                anchor_y="center"
            )