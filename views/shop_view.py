# views/shop_view.py

import os
import json
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
                "description": "Recupera 1 vida no quiz",
                "price": 10,
                "icon": "❤️",
                "type": "potion",
                "rarity": "common"
            },
            {
                "id": "potion_mana", 
                "name": "Poção de Mana",
                "description": "Recupera 2 pontos de mana",
                "price": 15,
                "icon": "🔵",
                "type": "potion",
                "rarity": "common"
            },
            {
                "id": "weapon_sword",
                "name": "Espada do Saber",
                "description": "Dobra XP ganho por 1 quiz",
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
        """Carrega dados do usuário com verificação de persistência"""
        try:
            self.user = user_manager.get_current_user()
            if not self.user:
                self.user = "user"
            print(f"👤 Usuário atual: {self.user}")
        except Exception as e:
            print(f"⚠️ Erro no user_manager: {e}")
            self.user = "user"

        # Carrega dados via auth_system
        user_data = {}
        try:
            user_data = auth_system.get_user_data(self.user) or {}
            print(f"📊 Dados carregados: {len(user_data)} campos")
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            user_data = self._load_fallback_data()

        # Garante estrutura completa
        self.data = user_data
        self.display_name = user_data.get("display_name", self.user)
        self.coins = user_data.get("coins", 100)
        self.inventory = user_data.get("inventory", {})
        self.hotbar = user_data.get("hotbar", {})
        self.equipped_items = user_data.get("equipped_items", {})

        # Garante que inventory seja um dicionário
        if not isinstance(self.inventory, dict):
            self.inventory = {}

        print(f"🏪 Loja inicializada para: {self.display_name}")
        print(f"💰 Moedas: {self.coins}")
        print(f"📦 Itens no inventário: {len(self.inventory)}")
        print(f"🎯 Slots na hotbar: {len(self.hotbar)}")
        print(f"⚔️ Itens equipados: {len(self.equipped_items)}")

    def _load_fallback_data(self):
        """Carrega dados de fallback do user.json"""
        fallback_file = "user.json"
        try:
            if os.path.exists(fallback_file):
                with open(fallback_file, "r", encoding="utf-8") as f:
                    all_users = json.load(f)
                    if isinstance(all_users, dict) and self.user in all_users:
                        print("🔄 Carregando dados de fallback")
                        return all_users[self.user]
        except Exception as e:
            print(f"⚠️ Erro no fallback: {e}")
        
        # Retorna estrutura padrão
        return {
            "coins": 100,
            "inventory": {},
            "display_name": self.user,
            "hotbar": {},
            "equipped_items": {}
        }

    def _save_user_data(self):
        """Salva dados do usuário de forma robusta"""
        try:
            # Atualiza estrutura de dados
            self.data.update({
                "coins": self.coins,
                "inventory": self.inventory,
                "hotbar": self.hotbar,
                "equipped_items": self.equipped_items,
                "display_name": self.display_name
            })
            
            # Salva via auth_system
            success = auth_system.update_user_data(self.user, self.data)
            
            # Backup no user.json
            self._save_fallback_data()
            
            print("💾 Dados salvos com sucesso")
            return success
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")
            return False

    def _save_fallback_data(self):
        """Salva dados no user.json como backup"""
        try:
            fallback_file = "user.json"
            existing_data = {}
            
            if os.path.exists(fallback_file):
                with open(fallback_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            
            existing_data[self.user] = self.data
            
            with open(fallback_file, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            print("💾 Backup salvo no user.json")
            return True
        except Exception as e:
            print(f"❌ Erro no backup: {e}")
            return False

    def on_show(self):
        arcade.set_background_color((20, 15, 35))
        self._initialize_user_data()
        print("🔁 Loja reinicializada com dados atualizados")

    def on_draw(self):
        self.clear()
        self._draw_background()
        self._draw_main_layout()
        self._draw_header()
        self._draw_shop_items()
        self._draw_info_panel()
        self._draw_messages()
        self._draw_back_button()

    def _draw_background(self):
        width, height = self.window.width, self.window.height
        arcade.draw_lrbt_rectangle_filled(0, width, 0, height, (15, 10, 25))

    def _draw_main_layout(self):
        width, height = self.window.width, self.window.height
        arcade.draw_lrbt_rectangle_filled(20, width - 20, 20, height - 20, (25, 20, 35, 220))
        arcade.draw_lrbt_rectangle_outline(20, width - 20, 20, height - 20, (212, 175, 55), 3)

    def _draw_header(self):
        width, height = self.window.width, self.window.height
        arcade.draw_text("🏪 LOJA RPG - ITENS PERMANENTES", width / 2, height - 60, 
                         (255, 215, 0), 28, anchor_x="center", bold=True)
        arcade.draw_text(f"💰 {self.coins} Moedas", width - 30, height - 40, 
                         (255, 215, 0), 20, anchor_x="right", bold=True)
        arcade.draw_text(f"👤 {self.display_name}", 30, height - 40, 
                         (200, 200, 200), 16)

    def _draw_shop_items(self):
        width, height = self.window.width, self.window.height
        start_x, start_y = 50, height - 120
        item_width, item_height = 200, 180
        spacing = 20

        for i, item in enumerate(self.shop_items):
            row, col = i // 2, i % 2
            x = start_x + col * (item_width + spacing)
            y = start_y - row * (item_height + spacing)
            self._draw_shop_item(x, y, item_width, item_height, item)

    def _draw_shop_item(self, x, y, width, height, item):
        rarity_color = self.rarity_colors.get(item["rarity"], (200, 200, 200))
        bg_color = (40, 35, 60) if item["id"] != self.selected_item else (60, 55, 80)

        arcade.draw_lrbt_rectangle_filled(x, x + width, y - height, y, bg_color)
        arcade.draw_lrbt_rectangle_outline(x, x + width, y - height, y, rarity_color, 3)

        arcade.draw_text(item["icon"], x + width / 2, y - 30, rarity_color, 36, 
                         anchor_x="center", anchor_y="center")
        arcade.draw_text(item["name"], x + width / 2, y - 70, (255, 255, 255), 16, 
                         anchor_x="center", anchor_y="center", bold=True)
        arcade.draw_text(item["description"], x + width / 2, y - 100, (180, 180, 180), 12, 
                         anchor_x="center", anchor_y="center", width=width - 20)

        price_color = (0, 255, 0) if self.coins >= item["price"] else (255, 50, 50)
        arcade.draw_text(f"💰 {item['price']}", x + width / 2, y - 130, price_color, 18, 
                         anchor_x="center", anchor_y="center", bold=True)

        button_y = y - 160
        button_color = (0, 150, 0) if self.coins >= item["price"] else (100, 100, 100)
        arcade.draw_lrbt_rectangle_filled(x + 20, x + width - 20, button_y - 10, button_y + 10, button_color)

        button_text = "COMPRAR" if self.coins >= item["price"] else "MOEDAS INSUFICIENTES"
        arcade.draw_text(button_text, x + width / 2, button_y, (255, 255, 255), 12, 
                         anchor_x="center", anchor_y="center", bold=True)

    def _draw_info_panel(self):
        width, height = self.window.width, self.window.height
        panel_x, panel_y = width * 0.75, height * 0.5
        panel_width, panel_height = width * 0.4, height * 0.7

        arcade.draw_lrbt_rectangle_filled(panel_x - panel_width / 2, panel_x + panel_width / 2,
                                          panel_y - panel_height / 2, panel_y + panel_height / 2, 
                                          (35, 30, 45))
        arcade.draw_lrbt_rectangle_outline(panel_x - panel_width / 2, panel_x + panel_width / 2,
                                           panel_y - panel_height / 2, panel_y + panel_height / 2, 
                                           (212, 175, 55), 2)
        
        arcade.draw_text("📦 INVENTÁRIO PERMANENTE", panel_x, panel_y + panel_height / 2 - 30, 
                         (255, 215, 0), 20, anchor_x="center", bold=True)

        inventory_y = panel_y + panel_height / 2 - 70
        if not self.inventory:
            arcade.draw_text("Nenhum item comprado ainda", panel_x, inventory_y, 
                             (150, 150, 150), 16, anchor_x="center")
        else:
            for i, (item_id, quantity) in enumerate(self.inventory.items()):
                item = next((it for it in self.shop_items if it["id"] == item_id), None)
                if item:
                    item_y = inventory_y - (i * 40)
                    rarity_color = self.rarity_colors.get(item["rarity"], (200, 200, 200))
                    arcade.draw_text(f"{item['icon']} {item['name']}", 
                                   panel_x - panel_width / 2 + 20, item_y,
                                   rarity_color, 14, anchor_y="center", bold=True)
                    arcade.draw_text(f"x{quantity}", panel_x + panel_width / 2 - 20, item_y, 
                                   (200, 200, 200), 14, anchor_x="right", anchor_y="center")

        hotbar_y = inventory_y - (len(self.inventory) * 40) - 40
        arcade.draw_text("🎯 HOTBAR ATIVA", panel_x, hotbar_y, 
                         (255, 215, 0), 16, anchor_x="center", bold=True)
        
        if not self.hotbar:
            arcade.draw_text("Nenhum item equipado", panel_x, hotbar_y - 30, 
                             (150, 150, 150), 14, anchor_x="center")
        else:
            for i, (slot, item_id) in enumerate(self.hotbar.items()):
                item = next((it for it in self.shop_items if it["id"] == item_id), None)
                if item:
                    slot_y = hotbar_y - 30 - (i * 25)
                    rarity_color = self.rarity_colors.get(item["rarity"], (200, 200, 200))
                    arcade.draw_text(f"{slot}: {item['icon']} {item['name']}", 
                                   panel_x - panel_width / 2 + 20, slot_y,
                                   rarity_color, 12, anchor_y="center")

    def _draw_back_button(self):
        button_x, button_y = 70, 40
        button_width, button_height = 100, 40

        arcade.draw_lrbt_rectangle_filled(button_x - button_width / 2, button_x + button_width / 2,
                                          button_y - button_height / 2, button_y + button_height / 2, 
                                          (60, 55, 80))
        arcade.draw_lrbt_rectangle_outline(button_x - button_width / 2, button_x + button_width / 2,
                                           button_y - button_height / 2, button_y + button_height / 2, 
                                           (212, 175, 55), 2)
        arcade.draw_text("🚪 VOLTAR", button_x, button_y, (255, 255, 255), 16, 
                         anchor_x="center", anchor_y="center", bold=True)

    def _draw_messages(self):
        if self.message and self.message_timer > 0:
            width, height = self.window.width, self.window.height
            arcade.draw_lrbt_rectangle_filled(width / 2 - 200, width / 2 + 200, 
                                              height / 2 - 25, height / 2 + 25,
                                              (30, 30, 40, 240))
            arcade.draw_lrbt_rectangle_outline(width / 2 - 200, width / 2 + 200, 
                                               height / 2 - 25, height / 2 + 25,
                                               (212, 175, 55), 2)
            arcade.draw_text(self.message, width / 2, height / 2, (255, 255, 255), 18, 
                             anchor_x="center", anchor_y="center", bold=True)

    def on_mouse_press(self, x, y, button, modifiers):
        self._handle_shop_item_click(x, y)
        self._handle_back_button_click(x, y)

    def _handle_shop_item_click(self, x, y):
        width, height = self.window.width, self.window.height
        start_x, start_y = 50, height - 120
        item_width, item_height = 200, 180
        spacing = 20

        for i, item in enumerate(self.shop_items):
            row, col = i // 2, i % 2
            item_x = start_x + col * (item_width + spacing)
            item_y = start_y - row * (item_height + spacing)

            if (item_x <= x <= item_x + item_width and item_y - item_height <= y <= item_y):
                button_y = item_y - 160
                if (item_x + 20 <= x <= item_x + item_width - 20 and button_y - 10 <= y <= button_y + 10):
                    self._purchase_item(item)
                    return
                self.selected_item = item["id"]
                return

    def _handle_back_button_click(self, x, y):
        button_x, button_y = 70, 40
        button_width, button_height = 100, 40

        if (button_x - button_width / 2 <= x <= button_x + button_width / 2 and
                button_y - button_height / 2 <= y <= button_y + button_height / 2):
            self._return_to_menu()

    def _purchase_item(self, item):
        """COMPRA ITEM COM PERSISTÊNCIA GARANTIDA - MÉTODO CORRIGIDO"""
        if self.coins < item["price"]:
            self._show_message("❌ Moedas insuficientes!", 2.0)
            return

        print(f"🛍️ Iniciando compra: {item['id']} por {item['price']} moedas")

        try:
            # 1. Verifica se usuário existe
            if not self.user:
                self._show_message("❌ Usuário não identificado!", 2.0)
                return

            # 2. Atualiza moedas localmente
            self.coins -= item["price"]
            
            # 3. Atualiza inventário localmente
            if item["id"] in self.inventory:
                self.inventory[item["id"]] += 1
            else:
                self.inventory[item["id"]] = 1

            # 4. Atualiza estrutura de dados
            self.data.update({
                "coins": self.coins,
                "inventory": self.inventory,
                "display_name": self.display_name
            })

            # 5. Salva via auth_system
            success = auth_system.update_user_data(self.user, self.data)
            
            if success:
                # 6. Auto-equipar em slot vazio se for item de hotbar
                if item["type"] in ["weapon", "skill", "potion"]:
                    self._auto_equip_item(item["id"])
                
                self._show_message(f"✅ {item['name']} comprado!", 2.0)
                print(f"🎯 Compra bem-sucedida: {item['id']}")
                print(f"💰 Moedas restantes: {self.coins}")
                print(f"📦 Inventário atualizado: {self.inventory}")
                
                # 7. Backup adicional
                self._save_fallback_data()
            else:
                # Reverte mudanças locais se falhar
                self.coins += item["price"]
                if item["id"] in self.inventory:
                    self.inventory[item["id"]] -= 1
                    if self.inventory[item["id"]] <= 0:
                        del self.inventory[item["id"]]
                self._show_message("❌ Erro ao salvar compra!", 2.0)

        except Exception as e:
            print(f"❌ Erro crítico na compra: {e}")
            self._show_message("❌ Erro na compra!", 2.0)

    def _auto_equip_item(self, item_id):
        """Equipa automaticamente o item em um slot vazio da hotbar"""
        try:
            # Ordem de prioridade para slots
            slot_order = ['1', '2', '3', '4', '5', '6', '7', '8', 
                         'A', 'B', 'C', 'D', 'E', 'F', 'G']
            
            for slot in slot_order:
                if slot not in self.hotbar or not self.hotbar[slot]:
                    self.hotbar[slot] = item_id
                    self.data["hotbar"] = self.hotbar
                    print(f"🎯 Item {item_id} equipado no slot {slot}")
                    
                    # Salva imediatamente
                    auth_system.update_user_data(self.user, self.data)
                    break
                    
        except Exception as e:
            print(f"⚠️ Erro ao equipar item: {e}")

    def _force_reload_user_data(self):
        """Recarrega dados do usuário FORÇADAMENTE"""
        try:
            user_data = auth_system.get_user_data(self.user)
            if user_data:
                self.data = user_data
                self.coins = user_data.get("coins", 0)
                self.inventory = user_data.get("inventory", {})
                self.hotbar = user_data.get("hotbar", {})
                self.equipped_items = user_data.get("equipped_items", {})
                
                print(f"🔄 Dados recarregados: {self.coins} moedas, {len(self.inventory)} itens")
                
                # Log detalhado
                if self.inventory:
                    print("📦 Inventário atualizado:")
                    for item_id, quantity in self.inventory.items():
                        print(f"   - {item_id}: x{quantity}")
        except Exception as e:
            print(f"❌ Erro ao recarregar dados: {e}")

    def _show_message(self, message, duration):
        self.message = message
        self.message_timer = duration

    def on_update(self, delta_time):
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.message = None

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ESCAPE, arcade.key.BACKSPACE, arcade.key.B):
            self._return_to_menu()

    def _return_to_menu(self):
        """Volta ao menu com garantia de persistência"""
        try:
            print("💾 Verificando persistência final...")
            
            # Força recarregar dados atualizados
            self._force_reload_user_data()
            
            # Backup final
            self._save_fallback_data()
            
            # Navegação
            if self.menu_view:
                self.window.show_view(self.menu_view)
            else:
                from views.menu_view import MenuView
                self.window.show_view(MenuView())
                
            print("🚪 Saindo da loja com dados persistentes")
        except Exception as e:
            print(f"❌ Erro ao voltar: {e}")
            # Tenta navegar mesmo com erro
            try:
                from views.menu_view import MenuView
                self.window.show_view(MenuView())
            except:
                pass