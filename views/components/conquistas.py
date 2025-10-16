import arcade

class ConquistasComponent:
    def __init__(self):
        self.conquistas = []
        self.carregar_conquistas()
    
    def carregar_conquistas(self):
        """Carrega todas as conquistas"""
        self.conquistas = [
            {
                "id": 1,
                "titulo": "Primeiros Passos",
                "descricao": "Complete o tutorial",
                "icone": "🎯",
                "raridade": "bronze",
                "concluida": True,
                "data_conquista": "2024-01-15",
                "pontos": 10
            },
            {
                "id": 2,
                "titulo": "Mestre dos Quiz",
                "descricao": "Acertar 100 quiz com perfeição",
                "icone": "🧠",
                "raridade": "prata",
                "concluida": False,
                "data_conquista": None,
                "pontos": 50,
                "progresso_atual": 67,
                "progresso_total": 100
            },
            {
                "id": 3,
                "titulo": "Colecionador Épico",
                "descricao": "Obter todos os itens raros",
                "icone": "💎",
                "raridade": "ouro",
                "concluida": False,
                "data_conquista": None,
                "pontos": 100
            },
            {
                "id": 4,
                "titulo": "Lenda Viva",
                "descricao": "Alcance o nível 50",
                "icone": "👑",
                "raridade": "platina",
                "concluida": False,
                "data_conquista": None,
                "pontos": 200,
                "progresso_atual": 15,
                "progresso_total": 50
            },
            {
                "id": 5,
                "titulo": "Explorador Incansável",
                "descricao": "Complete todas as fases",
                "icone": "🗺️",
                "raridade": "diamante",
                "concluida": False,
                "data_conquista": None,
                "pontos": 150
            }
        ]
    
    def get_conquistas_concluidas(self):
        """Retorna conquistas concluídas"""
        return [c for c in self.conquistas if c["concluida"]]
    
    def get_pontuacao_total(self):
        """Calcula pontuação total"""
        return sum(c["pontos"] for c in self.conquistas if c["concluida"])
    
    def draw_conquistas(self, x, y, width, height):
        """Desenha a tela de conquistas"""
        # Fundo
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            (30, 25, 45, 230)
        )
        
        # Título e estatísticas
        conquistas_concluidas = len(self.get_conquistas_concluidas())
        pontuacao_total = self.get_pontuacao_total()
        
        arcade.draw_text(
            "CONQUISTAS E TROFÉUS",
            x, y + height/2 - 30,
            (255, 215, 0), 24,
            anchor_x="center", bold=True
        )
        
        arcade.draw_text(
            f"Concluídas: {conquistas_concluidas}/{len(self.conquistas)}",
            x - width/2 + 20, y + height/2 - 70,
            (200, 200, 200), 16
        )
        
        arcade.draw_text(
            f"Pontuação Total: {pontuacao_total}",
            x + width/2 - 20, y + height/2 - 70,
            (255, 215, 0), 16,
            anchor_x="right"
        )
        
        # Lista de conquistas
        start_y = y + height/2 - 100
        for i, conquista in enumerate(self.conquistas):
            conquista_y = start_y - (i * 90)
            self._draw_conquista_item(x, conquista_y, width * 0.9, 80, conquista)
    
    def _draw_conquista_item(self, x, y, width, height, conquista):
        """Desenha um item de conquista individual"""
        # Cores baseadas na raridade
        cores_raridade = {
            "bronze": (205, 127, 50),
            "prata": (192, 192, 192),
            "ouro": (255, 215, 0),
            "platina": (229, 228, 226),
            "diamante": (185, 242, 255)
        }
        
        cor_raridade = cores_raridade.get(conquista["raridade"], (200, 200, 200))
        
        # Fundo do item
        bg_color = (60, 55, 80) if conquista["concluida"] else (40, 35, 60)
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            bg_color
        )
        
        # Borda com cor da raridade
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
        
        # Informações da conquista
        info_x = x - width/2 + 70
        
        # Título
        title_color = (255, 255, 255) if conquista["concluida"] else (150, 150, 150)
        arcade.draw_text(
            conquista["titulo"], info_x, y + 15,
            title_color, 16,
            bold=True
        )
        
        # Descrição
        arcade.draw_text(
            conquista["descricao"], info_x, y - 5,
            (200, 200, 200), 12,
            width=width - 150
        )
        
        # Pontos e progresso
        pontos_x = x + width/2 - 20
        
        if conquista["concluida"]:
            # Data de conquista
            arcade.draw_text(
                f"★ {conquista['pontos']} pts", pontos_x, y + 10,
                (255, 215, 0), 14,
                anchor_x="right", bold=True
            )
            arcade.draw_text(
                conquista["data_conquista"], pontos_x, y - 10,
                (150, 150, 150), 10,
                anchor_x="right"
            )
        else:
            # Progresso (se aplicável)
            arcade.draw_text(
                f"{conquista['pontos']} pts", pontos_x, y + 10,
                (150, 150, 150), 14,
                anchor_x="right"
            )
            
            if "progresso_atual" in conquista:
                progresso = conquista["progresso_atual"] / conquista["progresso_total"]
                bar_width = width * 0.3
                bar_x = x + width/2 - bar_width - 10
                bar_y = y - height/2 + 15
                
                # Barra de progresso
                arcade.draw_lrbt_rectangle_filled(
                    bar_x, bar_x + bar_width, bar_y - 3, bar_y + 3,
                    (50, 50, 50)
                )
                
                arcade.draw_lrbt_rectangle_filled(
                    bar_x, bar_x + (bar_width * progresso), bar_y - 3, bar_y + 3,
                    cor_raridade
                )
                
                arcade.draw_text(
                    f"{conquista['progresso_atual']}/{conquista['progresso_total']}",
                    bar_x + bar_width + 5, bar_y,
                    (200, 200, 200), 10,
                    anchor_y="center"
                )