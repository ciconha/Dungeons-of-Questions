import arcade

class InventarioComponent:
    def __init__(self):
        self.itens = []
        self.carregar_itens()
    
    def carregar_itens(self):
        """Carrega todos os itens do inventário"""
        self.itens = [
            {
                "id": 1,
                "nome": "Espada Longa",
                "tipo": "arma",
                "raridade": "raro",
                "dano": 45,
                "quantidade": 1,
                "equipado": True,
                "icone": "⚔️"
            },
            {
                "id": 2,
                "nome": "Armadura de Couro",
                "tipo": "armadura",
                "raridade": "comum",
                "defesa": 25,
                "quantidade": 1,
                "equipado": True,
                "icone": "🛡️"
            },
            {
                "id": 3,
                "nome": "Poção de Cura",
                "tipo": "consumivel",
                "raridade": "comum",
                "cura": 100,
                "quantidade": 5,
                "equipado": False,
                "icone": "🧪"
            },
            {
                "id": 4,
                "nome": "Cajado Arcano",
                "tipo": "arma",
                "raridade": "épico",
                "dano_magico": 65,
                "quantidade": 1,
                "equipado": False,
                "icone": "🔮"
            },
            {
                "id": 5,
                "nome": "Elmo do Poder",
                "tipo": "capacete",
                "raridade": "raro",
                "defesa": 15,
                "quantidade": 1,
                "equipado": False,
                "icone": "⛑️"
            },
            {
                "id": 6,
                "nome": "Poção de Mana",
                "tipo": "consumivel",
                "raridade": "comum",
                "mana": 150,
                "quantidade": 3,
                "equipado": False,
                "icone": "🔵"
            }
        ]
    
    def get_itens_por_tipo(self, tipo):
        """Retorna itens filtrados por tipo"""
        return [item for item in self.itens if item["tipo"] == tipo]
    
    def equipar_item(self, item_id):
        """Equipa um item"""
        for item in self.itens:
            if item["id"] == item_id:
                # Desequipa outros do mesmo tipo
                for other in self.itens:
                    if other["tipo"] == item["tipo"] and other["equipado"]:
                        other["equipado"] = False
                item["equipado"] = True
                return True
        return False
    
    def adicionar_item(self, item):
        """Adiciona um novo item ao inventário"""
        self.itens.append(item)
    
    def draw_inventario(self, x, y, width, height):
        """Desenha o inventário"""
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
        
        # Categorias
        categorias = ["arma", "armadura", "capacete", "consumivel"]
        categoria_width = width / len(categorias)
        
        for i, categoria in enumerate(categorias):
            cat_x = x - width/2 + (i * categoria_width) + categoria_width/2
            cat_y = y + height/2 - 70
            
            itens_categoria = self.get_itens_por_tipo(categoria)
            self._draw_categoria(cat_x, cat_y, categoria_width * 0.9, 200, categoria, itens_categoria)
    
    def _draw_categoria(self, x, y, width, height, categoria, itens):
        """Desenha uma categoria do inventário"""
        # Fundo da categoria
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
        
        # Nome da categoria
        arcade.draw_text(
            categoria.upper(), x, y + height/2 - 20,
            (255, 215, 0), 14,
            anchor_x="center", bold=True
        )
        
        # Itens
        for i, item in enumerate(itens[:3]):  # Mostra até 3 itens por categoria
            item_y = y + height/2 - 50 - (i * 50)
            self._draw_item(x, item_y, width * 0.8, 40, item)
    
    def _draw_item(self, x, y, width, height, item):
        """Desenha um item individual"""
        # Cor baseada na raridade
        cores_raridade = {
            "comum": (200, 200, 200),
            "raro": (65, 105, 225),
            "épico": (138, 43, 226)
        }
        cor_item = cores_raridade.get(item["raridade"], (200, 200, 200))
        
        # Fundo do item
        arcade.draw_lrbt_rectangle_filled(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            (50, 45, 70)
        )
        
        # Borda (diferente se estiver equipado)
        border_color = (0, 255, 0) if item["equipado"] else cor_item
        arcade.draw_lrbt_rectangle_outline(
            x - width/2, x + width/2,
            y - height/2, y + height/2,
            border_color, 2
        )
        
        # Ícone
        arcade.draw_text(
            item["icone"], x - width/2 + 15, y,
            cor_item, 16,
            anchor_y="center"
        )
        
        # Nome do item
        nome_color = (0, 255, 0) if item["equipado"] else (255, 255, 255)
        arcade.draw_text(
            item["nome"], x - width/2 + 40, y + 8,
            nome_color, 12,
            bold=True
        )
        
        # Estatísticas
        stats_text = ""
        if "dano" in item:
            stats_text += f"⚔{item['dano']} "
        if "defesa" in item:
            stats_text += f"🛡{item['defesa']} "
        if "quantidade" in item and item["quantidade"] > 1:
            stats_text += f"x{item['quantidade']}"
        
        arcade.draw_text(
            stats_text, x - width/2 + 40, y - 8,
            (200, 200, 200), 10
        )