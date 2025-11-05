# auth/simple_auth.py

import json
import os
import requests
from typing import Dict, Optional, Any
from urllib.parse import urlparse

USER_DATA_FILE = "data/users.json"

class SimpleAuth:
    def __init__(self):
        self.users: Dict = {}
        self.load_users()
    
    def load_users(self):
        """Carrega usuários do arquivo JSON - PRESERVA DADOS EXISTENTES"""
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                    loaded_users = json.load(f)
                    
                    # 🔥 PRESERVA TODOS OS DADOS EXISTENTES E APENAS CORRIGE PROBLEMAS
                    for username, user_data in loaded_users.items():
                        self.users[username] = self._repair_user_data(user_data, username)
                    
                    print(f"✅ {len(self.users)} usuários carregados e validados")
            else:
                # Cria diretório se não existir
                os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
                self.users = {}
                self.save_users()
        except Exception as e:
            print(f"❌ Erro ao carregar usuários: {e}")
            self.users = {}
    
    def _repair_user_data(self, user_data: dict, username: str) -> dict:
        """REPARA dados do usuário SEM ALTERAR dados válidos existentes"""
        try:
            # 🔥 MANTÉM TODOS OS DADOS ORIGINAIS
            repaired_data = user_data.copy()
            
            # 1. GARANTE DADOS BÁSICOS (INCLUINDO DADOS DA LOJA)
            required_fields = {
                "nome": username,
                "password": "123456",
                "avatar_path": None,
                "avatar_url": None, 
                "xp": 0,
                "level": 1,
                "max_xp": 100,
                "coins": 100,                    # 🔥 MOEDAS PARA A LOJA
                "inventory": {},                 # 🔥 INVENTÁRIO DE ITENS
                "equipped_items": {},           # 🔥 ITENS EQUIPADOS
                "display_name": username,        # 🔥 NOME PARA EXIBIÇÃO
                "achievements": [],              # 🔥 CONQUISTAS
                "play_time": 0,                  # 🔥 TEMPO DE JOGO
                "quizzes_completed": 0,          # 🔥 QUIZZES COMPLETADOS
                "correct_answers": 0,           # 🔥 RESPOSTAS CORRETAS
                "total_answers": 0,             # 🔥 TOTAL DE RESPOSTAS
                "hotbar": {}                    # 🔥 HOTBAR PARA ITENS RÁPIDOS
            }
            
            for field, default_value in required_fields.items():
                if field not in repaired_data:
                    repaired_data[field] = default_value
                    print(f"🔄 Campo {field} adicionado para {username}")
                elif field == "password" and repaired_data[field] == "123456":
                    # Mantém a senha original se existir
                    pass
            
            # 2. GARANTE CHARACTER COMPLETO (RESPEITANDO DADOS EXISTENTES)
            repaired_data["character"] = self._repair_character_data(
                repaired_data.get("character", {}), 
                username
            )
            
            # 3. GARANTE CAMPAIGN_PROGRESS COMPLETO (RESPEITANDO DADOS EXISTENTES)
            repaired_data["campaign_progress"] = self._repair_campaign_progress(
                repaired_data.get("campaign_progress", {}),
                username
            )
            
            # 4. 🔥 GARANTE DADOS DA LOJA (INVENTÁRIO, MOEDAS E HOTBAR)
            repaired_data = self._repair_shop_data(repaired_data, username)
            
            return repaired_data
            
        except Exception as e:
            print(f"❌ Erro ao reparar dados de {username}: {e}")
            return user_data  # Retorna original se der erro
    
    def _repair_shop_data(self, user_data: dict, username: str) -> dict:
        """REPARA dados da loja - moedas, inventário e hotbar"""
        try:
            # 🔥 GARANTE MOEDAS VÁLIDAS
            if "coins" not in user_data or not isinstance(user_data["coins"], (int, float)) or user_data["coins"] < 0:
                user_data["coins"] = 100
                print(f"🔄 Moedas resetadas para 100 em {username}")
            
            # 🔥 GARANTE INVENTÁRIO VÁLIDO
            if "inventory" not in user_data or not isinstance(user_data["inventory"], dict):
                user_data["inventory"] = {}
                print(f"🔄 Inventário resetado em {username}")
            
            # 🔥 GARANTE ITENS EQUIPADOS VÁLIDOS
            if "equipped_items" not in user_data or not isinstance(user_data["equipped_items"], dict):
                user_data["equipped_items"] = {}
                print(f"🔄 Itens equipados resetados em {username}")
            
            # 🔥 GARANTE HOTBAR VÁLIDA
            if "hotbar" not in user_data or not isinstance(user_data["hotbar"], dict):
                user_data["hotbar"] = {}
                print(f"🔄 Hotbar resetada em {username}")
            
            # 🔥 GARANTE DISPLAY_NAME
            if "display_name" not in user_data or not user_data["display_name"]:
                user_data["display_name"] = username
                print(f"🔄 Display name definido para {username}")
            
            # 🔥 LIMPA ITENS DO INVENTÁRIO COM QUANTIDADE ZERO OU NEGATIVA
            user_data["inventory"] = {item_id: qty for item_id, qty in user_data["inventory"].items() 
                                    if isinstance(qty, int) and qty > 0}
            
            # 🔥 LIMPA SLOTS VAZIOS DA HOTBAR
            user_data["hotbar"] = {slot: item_id for slot, item_id in user_data["hotbar"].items() 
                                 if item_id and item_id in user_data["inventory"]}
            
            return user_data
            
        except Exception as e:
            print(f"❌ Erro ao reparar dados da loja de {username}: {e}")
            return user_data
    
    def _repair_character_data(self, character_data: dict, username: str) -> dict:
        """REPARA dados do personagem RESPEITANDO configurações existentes"""
        try:
            # 🔥 USA DADOS EXISTENTES COMO BASE
            repaired_character = character_data.copy() if character_data else {}
            
            # Garante nome Emily
            if "name" not in repaired_character:
                repaired_character["name"] = "Emily"
            elif repaired_character["name"] != "Emily":
                print(f"🔄 Nome do personagem corrigido para Emily em {username}")
                repaired_character["name"] = "Emily"
            
            # 🔥 ANIMAÇÕES - CORRIGE APENAS SE ESTIVEREM INCOMPLETAS
            default_animations = {
                "up": "assets/characters/Emillywhite_down.png",
                "down": "assets/characters/Emillywhite_front.png", 
                "left": "assets/characters/Emillywhite_left.png",
                "right": "assets/characters/Emillywhite_right.png"
            }
            
            if "animations" not in repaired_character:
                repaired_character["animations"] = default_animations
                print(f"🔄 Animações completas adicionadas para {username}")
            else:
                # CORRIGE APENAS ANIMAÇÕES FALTANTES OU INVÁLIDAS
                current_animations = repaired_character["animations"]
                for direction, default_path in default_animations.items():
                    if direction not in current_animations:
                        current_animations[direction] = default_path
                        print(f"🔄 Animação {direction} adicionada para {username}")
                    elif not os.path.exists(current_animations[direction]):
                        # Se o caminho existente não for válido, usa o padrão
                        current_animations[direction] = default_path
                        print(f"🔄 Animação {direction} corrigida (arquivo não encontrado) para {username}")
            
            # Garante posição se não existir
            if "position" not in repaired_character:
                repaired_character["position"] = {"x": 64, "y": 64}
            
            # 🔥 MANTÉM CAMPOS PERSONALIZADOS EXISTENTES (sprite, game_sprite, description, etc.)
            # Estes campos são preservados automaticamente pelo copy()
            
            return repaired_character
            
        except Exception as e:
            print(f"❌ Erro ao reparar character de {username}: {e}")
            return character_data or {"name": "Emily", "animations": default_animations, "position": {"x": 64, "y": 64}}
    
    def _repair_campaign_progress(self, campaign_data: dict, username: str) -> dict:
        """REPARA progresso da campanha RESPEITANDO dados existentes"""
        try:
            # 🔥 USA DADOS EXISTENTES COMO BASE
            repaired_campaign = campaign_data.copy() if campaign_data else {}
            
            # Estrutura básica garantida
            if "fase_atual" not in repaired_campaign:
                repaired_campaign["fase_atual"] = 1
            
            if "fases_concluidas" not in repaired_campaign:
                repaired_campaign["fases_concluidas"] = []
            
            # 🔥 GARANTE TODAS AS 6 FASES EXISTAM
            if "fases" not in repaired_campaign:
                repaired_campaign["fases"] = {}
            
            fases = repaired_campaign["fases"]
            
            # Status padrão para cada fase
            default_fases = {
                1: "liberada",  # Fase 1 sempre liberada
                2: "bloqueada",
                3: "bloqueada", 
                4: "bloqueada",
                5: "bloqueada",
                6: "bloqueada"
            }
            
            # CORRIGE APENAS FASES FALTANTES
            for fase_id in range(1, 7):
                # Verifica ambas as chaves (string e int)
                fase_str = str(fase_id)
                if fase_id not in fases and fase_str not in fases:
                    fases[fase_id] = default_fases[fase_id]
                    print(f"🔄 Fase {fase_id} adicionada para {username}")
                elif fase_str in fases:
                    # Move de string para int para consistência
                    fases[fase_id] = fases.pop(fase_str)
            
            # 🔥 GARANTE QUE FASES CONCLUÍDAS ESTEJEM MARCADAS CORRETAMENTE
            fases_concluidas = repaired_campaign["fases_concluidas"]
            for fase_id in fases_concluidas:
                if fase_id in fases and fases[fase_id] != "concluida":
                    fases[fase_id] = "concluida"
                    print(f"🔄 Fase {fase_id} marcada como concluída para {username}")
            
            # 🔥 GARANTE QUE FASE 1 SEMPRE ESTEJA LIBERADA
            if fases.get(1) != "liberada":
                fases[1] = "liberada"
                print(f"🔄 Fase 1 liberada para {username}")
            
            return repaired_campaign
            
        except Exception as e:
            print(f"❌ Erro ao reparar campanha de {username}: {e}")
            return {"fase_atual": 1, "fases": {1: "liberada", 2: "bloqueada", 3: "bloqueada", 4: "bloqueada", 5: "bloqueada", 6: "bloqueada"}, "fases_concluidas": []}

    def save_users(self):
        """Salva usuários no arquivo JSON - GARANTE PERSISTÊNCIA"""
        try:
            # 🔥 SEMPRE REPARA ANTES DE SALVAR
            for username, user_data in self.users.items():
                self.users[username] = self._repair_user_data(user_data, username)
            
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
            print("💾 Dados dos usuários salvos com validação completa")
            return True
        except Exception as e:
            print(f"❌ Erro crítico ao salvar usuários: {e}")
            # Tenta backup de emergência
            self._emergency_save()
            return False
    
    def _emergency_save(self):
        """Tentativa de salvamento de emergência"""
        try:
            backup_file = USER_DATA_FILE + ".backup"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
            print(f"🆘 Backup de emergência salvo em: {backup_file}")
        except Exception as e:
            print(f"💥 Falha catastrófica no salvamento: {e}")
    
    def user_exists(self, username: str) -> bool:
        """Verifica se usuário existe"""
        return username.lower() in [u.lower() for u in self.users.keys()]
    
    def is_valid_url(self, url: str) -> bool:
        """Verifica se a URL é válida"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def download_avatar(self, url: str, username: str) -> Optional[str]:
        """Faz download do avatar da URL e salva localmente"""
        try:
            if not self.is_valid_url(url):
                return None
                
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return None
            
            avatar_dir = "data/avatars"
            os.makedirs(avatar_dir, exist_ok=True)
            
            ext = '.jpg'
            if 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'jpeg' in content_type:
                ext = '.jpeg'
            elif 'webp' in content_type:
                ext = '.webp'
            
            filename = f"{username}{ext}"
            filepath = os.path.join(avatar_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Avatar baixado: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Erro ao baixar avatar: {e}")
            return None
    
    def register_user(self, username: str, password: str, nome: str, avatar_url: str = None, **kwargs) -> bool:
        """
        Registra novo usuário - JÁ COM DADOS VALIDADOS
        Aceita argumentos extras para compatibilidade
        """
        if self.user_exists(username):
            print(f"❌ Usuário {username} já existe")
            return False
        
        # Log de argumentos extras para debug
        if kwargs:
            print(f"⚠️ Argumentos extras recebidos no register_user: {kwargs}")
        
        avatar_path = None
        if avatar_url and self.is_valid_url(avatar_url):
            avatar_path = self.download_avatar(avatar_url, username)
        
        # Cria usuário com estrutura já validada
        new_user = {
            "nome": nome,
            "password": password,
            "avatar_path": avatar_path,
            "avatar_url": avatar_url,
            "xp": 0,
            "level": 1,
            "max_xp": 100,
            "coins": 100,                    # 🔥 MOEDAS INICIAIS
            "inventory": {},                 # 🔥 INVENTÁRIO VAZIO
            "equipped_items": {},           # 🔥 ITENS EQUIPADOS VAZIO
            "display_name": nome,           # 🔥 NOME PARA EXIBIÇÃO
            "achievements": [],              # 🔥 CONQUISTAS VAZIAS
            "play_time": 0,                  # 🔥 TEMPO DE JOGO ZERO
            "quizzes_completed": 0,          # 🔥 QUIZZES COMPLETADOS ZERO
            "correct_answers": 0,           # 🔥 RESPOSTAS CORRETAS ZERO
            "total_answers": 0,             # 🔥 TOTAL DE RESPOSTAS ZERO
            "hotbar": {}                    # 🔥 HOTBAR VAZIA
        }
        
        # 🔥 APLICA REPARO PARA GARANTIR CHARACTER E CAMPAIGN
        new_user = self._repair_user_data(new_user, username)
        
        self.users[username] = new_user
        self.save_users()
        print(f"🎮 Novo usuário registrado: {username} com dados validados")
        print(f"📊 Dados iniciais: Level {new_user['level']}, {new_user['coins']} moedas, Character: {new_user.get('character', {}).get('name', 'N/A')}")
        return True
    
    def authenticate(self, username: str, password: str) -> bool:
        """Autentica usuário"""
        if not self.user_exists(username):
            print(f"❌ Usuário {username} não existe")
            return False
        
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if not actual_username:
            print(f"❌ Não foi possível encontrar o usuário {username}")
            return False
        
        is_authenticated = self.users[actual_username]["password"] == password
        if is_authenticated:
            print(f"✅ Usuário {username} autenticado com sucesso")
        else:
            print(f"❌ Senha incorreta para {username}")
        
        return is_authenticated
    
    def get_user_data(self, username: str) -> Optional[Dict]:
        """Obtém dados do usuário - SEMPRE VALIDADOS"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            # 🔥 SEMPRE RETORNA DADOS REPARADOS
            user_data = self._repair_user_data(self.users[actual_username], actual_username)
            print(f"📋 Dados do usuário {username} carregados e validados")
            return user_data
        print(f"❌ Não foi possível carregar dados do usuário {username}")
        return None
    
    def update_user_data(self, username: str, user_data: dict) -> bool:
        """ATUALIZA dados do usuário - COM VALIDAÇÃO AUTOMÁTICA"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            # 🔥 REPARA ANTES DE SALVAR
            repaired_data = self._repair_user_data(user_data, actual_username)
            self.users[actual_username] = repaired_data
            self.save_users()
            print(f"💾 Dados completos salvos e validados para {username}")
            return True
        print(f"❌ Não foi possível atualizar dados do usuário {username}")
        return False
    
    def update_user_xp(self, username: str, xp: int, level: int) -> bool:
        """Atualiza XP e nível - COM SALVAMENTO GARANTIDO"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            self.users[actual_username]["xp"] = xp
            self.users[actual_username]["level"] = level
            self.users[actual_username]["max_xp"] = self._calculate_max_xp(level)
            self.save_users()  # 🔥 SALVAMENTO GARANTIDO
            print(f"⭐ XP atualizado para {username}: Level {level}, XP {xp}/{self._calculate_max_xp(level)}")
            return True
        print(f"❌ Não foi possível atualizar XP do usuário {username}")
        return False
    
    def update_campaign_progress(self, username: str, campaign_progress: dict) -> bool:
        """ATUALIZA progresso da campanha - COM VALIDAÇÃO"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            # 🔥 REPARA ANTES DE SALVAR
            repaired_campaign = self._repair_campaign_progress(campaign_progress, actual_username)
            self.users[actual_username]["campaign_progress"] = repaired_campaign
            self.save_users()  # 🔥 SALVAMENTO GARANTIDO
            print(f"📊 Progresso de campanha salvo e validado para {username}")
            return True
        print(f"❌ Não foi possível atualizar progresso da campanha para {username}")
        return False

    # 🔥 MÉTODOS ESPECÍFICOS PARA LOJA - GARANTEM PERSISTÊNCIA
    
    def add_coins(self, username: str, coins: int) -> bool:
        """Adiciona moedas ao usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            current_coins = self.users[actual_username].get("coins", 0)
            self.users[actual_username]["coins"] = current_coins + coins
            self.save_users()
            print(f"💰 {coins} moedas adicionadas para {username} (Total: {current_coins + coins})")
            return True
        print(f"❌ Não foi possível adicionar moedas para {username}")
        return False
    
    def remove_coins(self, username: str, coins: int) -> bool:
        """Remove moedas do usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            current_coins = self.users[actual_username].get("coins", 0)
            if current_coins >= coins:
                self.users[actual_username]["coins"] = current_coins - coins
                self.save_users()
                print(f"💰 {coins} moedas removidas de {username} (Total: {current_coins - coins})")
                return True
            else:
                print(f"❌ Moedas insuficientes para {username}: {current_coins} < {coins}")
                return False
        print(f"❌ Não foi possível remover moedas de {username}")
        return False
    
    def add_to_inventory(self, username: str, item_id: str, quantity: int = 1) -> bool:
        """Adiciona item ao inventário do usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            inventory = self.users[actual_username].get("inventory", {})
            
            if item_id in inventory:
                inventory[item_id] += quantity
            else:
                inventory[item_id] = quantity
            
            self.users[actual_username]["inventory"] = inventory
            self.save_users()
            print(f"📦 {quantity}x {item_id} adicionado ao inventário de {username}")
            return True
        print(f"❌ Não foi possível adicionar item ao inventário de {username}")
        return False
    
    def remove_from_inventory(self, username: str, item_id: str, quantity: int = 1) -> bool:
        """Remove item do inventário do usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            inventory = self.users[actual_username].get("inventory", {})
            
            if item_id in inventory and inventory[item_id] >= quantity:
                inventory[item_id] -= quantity
                
                # Remove se quantidade chegar a zero
                if inventory[item_id] <= 0:
                    del inventory[item_id]
                
                self.users[actual_username]["inventory"] = inventory
                self.save_users()
                print(f"📦 {quantity}x {item_id} removido do inventário de {username}")
                return True
            else:
                print(f"❌ Item {item_id} insuficiente no inventário de {username}")
                return False
        print(f"❌ Não foi possível remover item do inventário de {username}")
        return False
    
    def get_inventory(self, username: str) -> Dict:
        """Obtém o inventário completo do usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            inventory = self.users[actual_username].get("inventory", {})
            print(f"📦 Inventário de {username}: {len(inventory)} itens")
            return inventory
        print(f"❌ Não foi possível obter inventário de {username}")
        return {}
    
    def get_coins(self, username: str) -> int:
        """Obtém a quantidade de moedas do usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            coins = self.users[actual_username].get("coins", 0)
            print(f"💰 Moedas de {username}: {coins}")
            return coins
        print(f"❌ Não foi possível obter moedas de {username}")
        return 0
    
    def purchase_item(self, username: str, item_id: str, item_price: int) -> bool:
        """COMPRA UM ITEM - MÉTODO UNIFICADO PARA GARANTIR CONSISTÊNCIA"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if not actual_username:
            print(f"❌ Usuário {username} não encontrado para compra")
            return False
        
        user_data = self.users[actual_username]
        current_coins = user_data.get("coins", 0)
        
        # Verifica se tem moedas suficientes
        if current_coins < item_price:
            print(f"❌ Moedas insuficientes: {current_coins} < {item_price}")
            return False
        
        try:
            # Remove moedas
            user_data["coins"] = current_coins - item_price
            
            # Adiciona ao inventário
            inventory = user_data.get("inventory", {})
            if item_id in inventory:
                inventory[item_id] += 1
            else:
                inventory[item_id] = 1
            user_data["inventory"] = inventory
            
            # Salva IMEDIATAMENTE
            success = self.save_users()
            
            if success:
                print(f"🛍️ COMPRA BEM-SUCEDIDA: {username} comprou {item_id}")
                print(f"💰 Moedas restantes: {user_data['coins']}")
                print(f"📦 Inventário: {inventory}")
            else:
                print("❌ ERRO: Falha ao salvar compra!")
            
            return success
            
        except Exception as e:
            print(f"❌ Erro durante compra: {e}")
            return False

    # 🔥 MÉTODOS PARA HOTBAR
    
    def equip_to_hotbar(self, username: str, item_id: str, slot: str) -> bool:
        """Equipa um item na hotbar"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            # Verifica se o item está no inventário
            inventory = self.users[actual_username].get("inventory", {})
            if item_id not in inventory or inventory[item_id] <= 0:
                print(f"❌ Item {item_id} não encontrado no inventário de {username}")
                return False
            
            hotbar = self.users[actual_username].get("hotbar", {})
            hotbar[slot] = item_id
            
            self.users[actual_username]["hotbar"] = hotbar
            self.save_users()
            print(f"🎯 Item {item_id} equipado no slot {slot} da hotbar por {username}")
            return True
        print(f"❌ Não foi possível equipar item na hotbar para {username}")
        return False
    
    def unequip_from_hotbar(self, username: str, slot: str) -> bool:
        """Desequipa um item da hotbar"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            hotbar = self.users[actual_username].get("hotbar", {})
            
            if slot in hotbar:
                del hotbar[slot]
                self.users[actual_username]["hotbar"] = hotbar
                self.save_users()
                print(f"🎯 Item desequipado do slot {slot} da hotbar por {username}")
                return True
            else:
                print(f"❌ Nenhum item equipado no slot {slot} da hotbar para {username}")
                return False
        print(f"❌ Não foi possível desequipar item da hotbar para {username}")
        return False
    
    def get_hotbar(self, username: str) -> Dict:
        """Obtém a hotbar completa do usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            hotbar = self.users[actual_username].get("hotbar", {})
            print(f"🎯 Hotbar de {username}: {len(hotbar)} slots ocupados")
            return hotbar
        print(f"❌ Não foi possível obter hotbar de {username}")
        return {}
    
    def clear_hotbar(self, username: str) -> bool:
        """Limpa toda a hotbar do usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            self.users[actual_username]["hotbar"] = {}
            self.save_users()
            print(f"🗑️ Hotbar limpa para {username}")
            return True
        print(f"❌ Não foi possível limpar hotbar para {username}")
        return False

    # 🔥 MÉTODOS PARA ITENS EQUIPADOS (EQUIPAMENTOS)
    
    def equip_item(self, username: str, item_id: str, slot: str) -> bool:
        """Equipa um item no slot especificado"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            # Verifica se o item está no inventário
            inventory = self.users[actual_username].get("inventory", {})
            if item_id not in inventory or inventory[item_id] <= 0:
                print(f"❌ Item {item_id} não encontrado no inventário de {username}")
                return False
            
            equipped_items = self.users[actual_username].get("equipped_items", {})
            equipped_items[slot] = item_id
            
            self.users[actual_username]["equipped_items"] = equipped_items
            self.save_users()
            print(f"🎯 Item {item_id} equipado no slot {slot} por {username}")
            return True
        print(f"❌ Não foi possível equipar item para {username}")
        return False
    
    def unequip_item(self, username: str, slot: str) -> bool:
        """Desequipa um item do slot especificado"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            equipped_items = self.users[actual_username].get("equipped_items", {})
            
            if slot in equipped_items:
                del equipped_items[slot]
                self.users[actual_username]["equipped_items"] = equipped_items
                self.save_users()
                print(f"🎯 Item desequipado do slot {slot} por {username}")
                return True
            else:
                print(f"❌ Nenhum item equipado no slot {slot} para {username}")
                return False
        print(f"❌ Não foi possível desequipar item para {username}")
        return False
    
    def get_equipped_items(self, username: str) -> Dict:
        """Obtém os itens equipados do usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            equipped_items = self.users[actual_username].get("equipped_items", {})
            print(f"🎯 Itens equipados de {username}: {len(equipped_items)} itens")
            return equipped_items
        print(f"❌ Não foi possível obter itens equipados de {username}")
        return {}
    
    def _calculate_max_xp(self, level: int) -> int:
        """Calcula XP máxima para o nível"""
        return int(100 * (level ** 1.5))
    
    def get_all_users(self) -> Dict[str, Dict]:
        """Retorna todos os usuários (para debug/administração)"""
        print(f"👥 Total de usuários no sistema: {len(self.users)}")
        return self.users.copy()
    
    def delete_user(self, username: str) -> bool:
        """Remove um usuário do sistema"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            del self.users[actual_username]
            self.save_users()
            print(f"🗑️ Usuário {username} removido do sistema")
            return True
        print(f"❌ Não foi possível remover usuário {username}")
        return False

# Instância global do auth
auth_system = SimpleAuth()