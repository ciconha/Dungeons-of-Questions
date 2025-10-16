import arcade

class DesafiosComponent:
    def __init__(self):
        self.desafios = []
        self.carregar_desafios()
    
    def carregar_desafios(self):
        """Carrega todos os desafios disponíveis"""
        self.desafios = [
            {
                "id": 1,
                "titulo": "Mestre dos Quiz",
                "descricao": "Acertar todos os quiz em 2 fases consecutivas",
                "tipo": "quiz",
                "fases_necessarias": 2,
                "recompensa": "Cristal Arcano",
                "progresso_atual": 1,
                "progresso_total": 2,
                "concluido": False,
                "icone": "📚"
            },
            {
                "id": 2,
                "titulo": "Explorador Incansável",
                "descricao": "Completar 5 fases sem derrotas",
                "tipo": "sobrevivencia",
                "fases_necessarias": 5,
                "recompensa": "Poção da Eternidade",
                "progresso_atual": 3,
                "progresso_total": 5,
                "concluido": False,
                "icone": "🏃"
            },
            {
                "id": 3,
                "titulo": "Colecionador de Relíquias",
                "descricao": "Encontrar 10 itens raros",
                "tipo": "colecao",
                "itens_necessarios": 10,
                "recompensa": "Baú Místico",
                "progresso_atual": 7,
                "progresso_total": 10,
                "concluido": False,
                "icone": "💎"
            },
            {
                "id": 4,
                "titulo": "Guardião das Fases",
                "descricao": "Derrotar todos os chefes do mundo 1",
                "tipo": "chefes",
                "chefes_necessarios": 3,
                "recompensa": "Espada do Guardião",
                "progresso_atual": 2,
                "progresso_total": 3,
                "concluido": False,
                "icone": "⚔️"
            }
        ]
    
    def atualizar_progresso(self, desafio_id, progresso):
        """Atualiza progresso de um desafio"""
        for desafio in self.desafios:
            if desafio["id"] == desafio_id:
                desafio["progresso_atual"] = progresso
                if desafio["progresso_atual"] >= desafio["progresso_total"]:
                    desafio["concluido"] = True
                return True
        return False
    
    def get_desafios_ativos(self):
        """Retorna desafios não concluídos"""
        return [d for d in self.desafios if not d["concluido"]]
    
    def get_desafios_concluidos(self):
        """Retorna desafios concluídos"""
        return [d for d in self.desafios if d["concluido"]]
    
    def draw_desafios(self, x, y, width, height):
        """Desenha a lista de desafios"""
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
        desafios_ativos = self.get_desafios_ativos()
        
        for i, desafio in enumerate(desafios_ativos[:4]):  # Mostra até 4
            desafio_y = start_y - (i * 80)
            self._draw_desafio_item(x, desafio_y, width * 0.9, 70, desafio)
    
    def _draw_desafio_item(self, x, y, width, height, desafio):
        """Desenha um item de desafio individual"""
        # Fundo do item
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            (40, 35, 60)
        )
        
        # Borda
        border_color = (0, 100, 0) if desafio["concluido"] else (139, 0, 0)
        arcade.draw_lrbt_rectangle_outline(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            border_color, 2
        )
        
        # Ícone
        arcade.draw_text(
            desafio["icone"], x - width/2 + 20, y,
            (255, 215, 0), 20,
            anchor_y="center"
        )
        
        # Título e descrição
        arcade.draw_text(
            desafio["titulo"], x - width/2 + 50, y + 10,
            (255, 255, 255), 14,
            bold=True
        )
        
        arcade.draw_text(
            desafio["descricao"], x - width/2 + 50, y - 10,
            (200, 200, 200), 10,
            width=width - 100
        )
        
        # Barra de progresso
        progresso = desafio["progresso_atual"] / desafio["progresso_total"]
        bar_width = width * 0.8
        bar_x = x - bar_width/2
        bar_y = y - height/2 + 15
        
        # Fundo da barra
        arcade.draw_lrbt_rectangle_filled(
            bar_x, bar_x + bar_width, bar_y - 5, bar_y + 5,
            (50, 50, 50)
        )
        
        # Progresso
        if progresso > 0:
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + (bar_width * progresso), bar_y - 5, bar_y + 5,
                (0, 150, 0) if desafio["concluido"] else (220, 20, 60)
            )
        
        # Borda da barra
        arcade.draw_lrbt_rectangle_outline(
            bar_x, bar_x + bar_width, bar_y - 5, bar_y + 5,
            (255, 255, 255), 1
        )
        
        # Texto do progresso
        arcade.draw_text(
            f"{desafio['progresso_atual']}/{desafio['progresso_total']}",
            bar_x + bar_width + 5, bar_y,
            (255, 255, 255), 10,
            anchor_y="center"
        )
        
        # Recompensa
        arcade.draw_text(
            f"🎁 {desafio['recompensa']}",
            x + width/2 - 100, y,
            (255, 215, 0), 10,
            anchor_y="center"
        )