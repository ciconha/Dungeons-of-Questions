# views/shop_view.py

import arcade
from auth.simple_auth import auth_system
from auth.user_manager import user_manager

class ShopView(arcade.View):
    def __init__(self, menu_view=None):
        super().__init__()
        self.menu_view = menu_view
        self._initialize_user_data()
        
        # Itens da loja
        self.shop_items = [
            {
                "id": "potion_health",
                "name": "Poção de Vida",
                "description": "Cura 1 erro no quiz",
                "price": 10,
                "icon": "❤️",
                "type": "potion",
                "rarity": "common"
            },
            {
                "id": "potion_mana", 
                "name": "Poção de Mana",
                "description": "Ativa habilidades especiais",
                "price": 15,
                "icon": "🔵",
                "type": "potion",
                "rarity": "common"
            },
            {
                "id": "weapon_sword",
                "name": "Espada do Saber",
                "description": "+2% chance de acerto",
                "price": 50,
                "icon": "⚔️",
                "type": "weapon",
                "rarity": "uncommon"
            },
            {
                "id": "weapon_staff",
                "name": "Cajado Mágico",
                "description": "Revela uma letra da resposta",
                "price": 75,
                "icon": "🔮",
                "type": "weapon", 
                "rarity": "rare"
            },
            {
                "id": "skill_focus",
                "name": "Foco Mental",
                "description": "Remove 1 opção incorreta",
                "price": 100,
                "icon": "🧠",
                "type": "skill",
                "rarity": "epic"
            },
            {
                "id": "skill_time",
                "name": "Tempo Extra", 
                "description": "+10 segundos para responder",
                "price": 120,
                "icon": "⏱️",
                "type": "skill",
                "rarity": "legendary"
            }
        ]
        
        self.rarity_colors = {
            "common": (200, 200, 200),
            "uncommon": (0, 200, 0),
            "rare": (0, 100, 255),
            "epic": (160, 0, 255),
            "legendary": (255, 165, 0)
        }
        
        self.selected_item = None
        self.message = None
        self.message_timer = 0

    def _initialize_user_data(self):
        """Inicializa dados do usuário"""
        try:
            self.user = user_manager.get_current_user()
            user_data = auth_system.get_user_data(self.user)
            
            if user_data:
                self.data = user_data
                self.display_name = user_data.get("display_name", self.user)
                self.coins = user_data.get("coins", 100)
                self.inventory = user_data.get("inventory", {})
                print(f"✅ Loja carregada para: {self.display_name} (💰 {self.coins} moedas)")
            else:
                self._create_default_data()
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            self._create_default_data()

    def _create_default_data(self):
        """Cria dados padrão em caso de erro"""
        self.user = "user"
        self.data = {
            "coins": 100,
            "inventory": {},
            "display_name": "Jogador"
        }
        self.display_name = self.data["display_name"]
        self.coins = self.data["coins"]
        self.inventory = self.data["inventory"]

    def on_show(self):
        """Chamado quando a view é mostrada"""
        arcade.set_background_color((20, 15, 35))
        # 🔥 RECARREGA OS DADOS SEMPRE QUE ABRIR A LOJA
        self._initialize_user_data()
        print("🏪 Loja aberta - dados recarregados")

    def on_draw(self):
        """Renderiza a tela da loja"""
        self.clear()
        self._draw_background()
        self._draw_main_layout()
        self._draw_header()
        self._draw_shop_items()
        self._draw_info_panel()
        self._draw_messages()
        self._draw_back_button()

    def _draw_background(self):
        """Desenha fundo"""
        width, height = self.window.width, self.window.height
        arcade.draw_lrbt_rectangle_filled(0, width, 0, height, (15, 10, 25))

    def _draw_main_layout(self):
        """Desenha estrutura principal"""
        width, height = self.window.width, self.window.height
        arcade.draw_lrbt_rectangle_filled(20, width-20, 20, height-20, (25, 20, 35, 220))
        arcade.draw_lrbt_rectangle_outline(20, width-20, 20, height-20, (212, 175, 55), 3)

    def _draw_header(self):
        """Desenha cabeçalho"""
        width, height = self.window.width, self.window.height
        arcade.draw_text("LOJA RPG - ITENS ESPECIAIS", width/2, height-60, (255,215,0), 28, anchor_x="center", bold=True)
        arcade.draw_text(f"💰 {self.coins} Moedas", width-30, height-40, (255,215,0), 20, anchor_x="right", bold=True)
        arcade.draw_text(f"Comprador: {self.display_name}", 30, height-40, (200,200,200), 16)

    def _draw_shop_items(self):
        """Desenha itens da loja"""
        width, height = self.window.width, self.window.height
        start_x, start_y = 50, height-120
        item_width, item_height = 200, 180
        spacing = 20
        
        for i, item in enumerate(self.shop_items):
            row, col = i // 2, i % 2
            x = start_x + col * (item_width + spacing)
            y = start_y - row * (item_height + spacing)
            self._draw_shop_item(x, y, item_width, item_height, item)

    def _draw_shop_item(self, x, y, width, height, item):
        """Desenha um item individual"""
        rarity_color = self.rarity_colors.get(item["rarity"], (200,200,200))
        bg_color = (40,35,60) if item["id"] != self.selected_item else (60,55,80)
        
        arcade.draw_lrbt_rectangle_filled(x, x+width, y-height, y, bg_color)
        arcade.draw_lrbt_rectangle_outline(x, x+width, y-height, y, rarity_color, 3)
        arcade.draw_text(item["icon"], x+width/2, y-30, rarity_color, 36, anchor_x="center", anchor_y="center")
        arcade.draw_text(item["name"], x+width/2, y-70, (255,255,255), 16, anchor_x="center", anchor_y="center", bold=True)
        arcade.draw_text(item["description"], x+width/2, y-100, (180,180,180), 12, anchor_x="center", anchor_y="center", width=width-20)
        
        price_color = (0,255,0) if self.coins >= item["price"] else (255,50,50)
        arcade.draw_text(f"💰 {item['price']}", x+width/2, y-130, price_color, 18, anchor_x="center", anchor_y="center", bold=True)
        
        button_y = y-160
        button_color = (0,150,0) if self.coins >= item["price"] else (100,100,100)
        arcade.draw_lrbt_rectangle_filled(x+20, x+width-20, button_y-10, button_y+10, button_color)
        
        button_text = "COMPRAR" if self.coins >= item["price"] else "MOEDAS INSUFICIENTES"
        arcade.draw_text(button_text, x+width/2, button_y, (255,255,255), 12, anchor_x="center", anchor_y="center", bold=True)

    def _draw_info_panel(self):
        """Desenha painel de informações"""
        width, height = self.window.width, self.window.height
        panel_x, panel_y = width*0.75, height*0.5
        panel_width, panel_height = width*0.4, height*0.7
        
        arcade.draw_lrbt_rectangle_filled(panel_x-panel_width/2, panel_x+panel_width/2, panel_y-panel_height/2, panel_y+panel_height/2, (35,30,45))
        arcade.draw_lrbt_rectangle_outline(panel_x-panel_width/2, panel_x+panel_width/2, panel_y-panel_height/2, panel_y+panel_height/2, (212,175,55), 2)
        arcade.draw_text("INVENTÁRIO ATUAL", panel_x, panel_y+panel_height/2-30, (255,215,0), 20, anchor_x="center", bold=True)
        
        inventory_y = panel_y+panel_height/2-70
        if not self.inventory:
            arcade.draw_text("Nenhum item comprado ainda", panel_x, inventory_y, (150,150,150), 16, anchor_x="center")
        else:
            for i, (item_id, quantity) in enumerate(self.inventory.items()):
                item = next((it for it in self.shop_items if it["id"] == item_id), None)
                if item:
                    item_y = inventory_y - (i*40)
                    rarity_color = self.rarity_colors.get(item["rarity"], (200,200,200))
                    arcade.draw_text(f"{item['icon']} {item['name']}", panel_x-panel_width/2+20, item_y, rarity_color, 14, anchor_y="center", bold=True)
                    arcade.draw_text(f"x{quantity}", panel_x+panel_width/2-20, item_y, (200,200,200), 14, anchor_x="right", anchor_y="center")

    def _draw_back_button(self):
        """Desenha botão voltar"""
        button_x, button_y = 70, 40
        button_width, button_height = 100, 40
        
        arcade.draw_lrbt_rectangle_filled(button_x-button_width/2, button_x+button_width/2, button_y-button_height/2, button_y+button_height/2, (60,55,80))
        arcade.draw_lrbt_rectangle_outline(button_x-button_width/2, button_x+button_width/2, button_y-button_height/2, button_y+button_height/2, (212,175,55), 2)
        arcade.draw_text("VOLTAR", button_x, button_y, (255,255,255), 16, anchor_x="center", anchor_y="center", bold=True)

    def _draw_messages(self):
        """Desenha mensagens temporárias"""
        if self.message and self.message_timer > 0:
            width, height = self.window.width, self.window.height
            arcade.draw_lrbt_rectangle_filled(width/2-200, width/2+200, height/2-25, height/2+25, (30,30,40,240))
            arcade.draw_lrbt_rectangle_outline(width/2-200, width/2+200, height/2-25, height/2+25, (212,175,55), 2)
            arcade.draw_text(self.message, width/2, height/2, (255,255,255), 18, anchor_x="center", anchor_y="center", bold=True)

    def on_mouse_press(self, x, y, button, modifiers):
        """Lida com cliques do mouse"""
        self._handle_shop_item_click(x, y)
        self._handle_back_button_click(x, y)

    def _handle_shop_item_click(self, x, y):
        """Verifica clique nos itens"""
        width, height = self.window.width, self.window.height
        start_x, start_y = 50, height-120
        item_width, item_height = 200, 180
        spacing = 20
        
        for i, item in enumerate(self.shop_items):
            row, col = i // 2, i % 2
            item_x = start_x + col * (item_width + spacing)
            item_y = start_y - row * (item_height + spacing)
            
            if (item_x <= x <= item_x+item_width and item_y-item_height <= y <= item_y):
                button_y = item_y-160
                if (item_x+20 <= x <= item_x+item_width-20 and button_y-10 <= y <= button_y+10):
                    self._purchase_item(item)
                    return
                self.selected_item = item["id"]
                return

    def _handle_back_button_click(self, x, y):
        """Verifica clique no botão voltar"""
        button_x, button_y = 70, 40
        button_width, button_height = 100, 40
        
        if (button_x-button_width/2 <= x <= button_x+button_width/2 and 
            button_y-button_height/2 <= y <= button_y+button_height/2):
            self._return_to_menu()

    def _purchase_item(self, item):
        """PROCESSO DE COMPRA CORRIGIDO - USA MÉTODO UNIFICADO"""
        if self.coins < item["price"]:
            self._show_message("❌ Moedas insuficientes!", 2.0)
            return
        
        # 🔥 USA O MÉTODO UNIFICADO DO AUTH_SYSTEM
        success = auth_system.purchase_item(self.user, item["id"], item["price"])
        
        if success:
            # 🔥 ATUALIZA OS DADOS LOCAIS APÓS COMPRA BEM-SUCEDIDA
            self.coins -= item["price"]
            if item["id"] in self.inventory:
                self.inventory[item["id"]] += 1
            else:
                self.inventory[item["id"]] = 1
            
            self._show_message(f"✅ {item['name']} comprado!", 2.0)
            print(f"🎯 Item {item['id']} adicionado ao inventário")
        else:
            self._show_message("❌ Erro ao processar compra!", 2.0)

    def _show_message(self, message, duration):
        """Mostra mensagem temporária"""
        self.message = message
        self.message_timer = duration

    def on_update(self, delta_time):
        """Atualiza a view"""
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.message = None

    def on_key_press(self, key, modifiers):
        """Teclas para voltar"""
        if key in (arcade.key.ESCAPE, arcade.key.BACKSPACE, arcade.key.B):
            self._return_to_menu()

    def _return_to_menu(self):
        """Volta para o menu"""
        try:
            # 🔥 GARANTE QUE OS DADOS ESTÃO SALVOS ANTES DE SAIR
            auth_system.update_user_data(self.user, self.data)
            
            if self.menu_view:
                self.window.show_view(self.menu_view)
            else:
                from views.menu_view import MenuView
                self.window.show_view(MenuView())
        except Exception as e:
            print(f"❌ Erro ao voltar: {e}")