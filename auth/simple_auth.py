# auth/simple_auth.py

import json
import os
import requests
from typing import Dict, Optional, Any
from urllib.parse import urlparse
from pymongo import MongoClient
from bson import ObjectId
import datetime

USER_DATA_FILE = "data/users.json"

class SimpleAuth:
    def __init__(self):
        self.users: Dict = {}
        self.mongo_client = None
        self.db = None
        self.users_collection = None
        
        # Inicializa MongoDB
        self._init_mongodb()
        # Carrega usuários
        self.load_users()
        print("🔄 Sistema de autenticação inicializado com persistência total")
    
    def _init_mongodb(self):
        """Inicializa conexão com MongoDB com múltiplas tentativas"""
        try:
            # Tentativas de conexão com diferentes strings
            connection_strings = [
                'mongodb://localhost:27017/',
                'mongodb://127.0.0.1:27017/',
                'mongodb+srv://username:password@cluster.mongodb.net/'  # Para MongoDB Atlas
            ]
            
            for conn_str in connection_strings:
                try:
                    self.mongo_client = MongoClient(conn_str, serverSelectionTimeoutMS=3000)
                    self.mongo_client.server_info()  # Testa conexão
                    self.db = self.mongo_client['rpg_game_db']
                    self.users_collection = self.db['users']
                    
                    # Cria índices para melhor performance
                    self.users_collection.create_index("_id")
                    self.users_collection.create_index("display_name")
                    
                    print(f"✅ Conectado ao MongoDB: {conn_str}")
                    return
                except Exception as e:
                    print(f"❌ Falha na conexão {conn_str}: {e}")
                    continue
            
            print("🔁 MongoDB não disponível, usando apenas armazenamento local")
            self.mongo_client = None
            self.db = None
            self.users_collection = None
            
        except Exception as e:
            print(f"❌ Erro crítico no MongoDB: {e}")
            self.mongo_client = None
            self.db = None
            self.users_collection = None
    
    def _ensure_data_directory(self):
        """Garante que o diretório de dados existe"""
        try:
            os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        except Exception as e:
            print(f"❌ Erro ao criar diretório: {e}")
    
    def load_users(self):
        """Carrega usuários do MongoDB (prioridade) ou do JSON"""
        try:
            # Tenta carregar do MongoDB primeiro
            mongo_loaded = False
            if self.users_collection is not None:
                try:
                    mongo_users = list(self.users_collection.find({}))
                    if mongo_users:
                        for user_doc in mongo_users:
                            username = user_doc.get('_id')
                            if username:
                                user_data = {k: v for k, v in user_doc.items() if k != '_id'}
                                self.users[username] = self._repair_user_data(user_data, username)
                        
                        print(f"✅ {len(self.users)} usuários carregados do MongoDB")
                        mongo_loaded = True
                        
                        # Sincroniza com JSON
                        self._sync_to_json()
                except Exception as e:
                    print(f"❌ Erro ao carregar do MongoDB: {e}")
            
            # Se MongoDB falhou, carrega do JSON
            if not mongo_loaded:
                self._load_from_json()
                
        except Exception as e:
            print(f"❌ Erro crítico ao carregar usuários: {e}")
            self.users = {}
    
    def _load_from_json(self):
        """Carrega usuários do arquivo JSON"""
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                    loaded_users = json.load(f)
                    
                    for username, user_data in loaded_users.items():
                        self.users[username] = self._repair_user_data(user_data, username)
                    
                    print(f"✅ {len(self.users)} usuários carregados do JSON")
                    
                    # Se MongoDB está disponível, sincroniza
                    if self.users_collection is not None:
                        self._sync_to_mongodb()
            else:
                self._ensure_data_directory()
                self.users = {}
                print("📁 Arquivo JSON não encontrado, criando novo")
                
        except Exception as e:
            print(f"❌ Erro ao carregar do JSON: {e}")
            self.users = {}
    
    def _sync_to_mongodb(self):
        """Sincroniza todos os dados do JSON para o MongoDB"""
        if self.users_collection is None:
            return
            
        try:
            for username, user_data in self.users.items():
                self._save_user_to_mongodb(username, user_data)
            print("🔄 Dados sincronizados para MongoDB")
        except Exception as e:
            print(f"❌ Erro ao sincronizar com MongoDB: {e}")
    
    def _sync_to_json(self):
        """Sincroniza todos os dados do MongoDB para o JSON"""
        try:
            self._ensure_data_directory()
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
            print("🔄 Dados sincronizados para JSON")
        except Exception as e:
            print(f"❌ Erro ao sincronizar com JSON: {e}")
    
    def _save_user_to_mongodb(self, username: str, user_data: dict) -> bool:
        """Salva um usuário específico no MongoDB"""
        if self.users_collection is None:
            return False
            
        try:
            mongo_data = user_data.copy()
            result = self.users_collection.replace_one(
                {'_id': username}, 
                mongo_data, 
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            print(f"❌ Erro ao salvar {username} no MongoDB: {e}")
            return False
    
    def _save_user_to_json(self, username: str, user_data: dict) -> bool:
        """Salva um usuário específico no JSON"""
        try:
            self._ensure_data_directory()
            
            # Carrega dados existentes
            existing_data = {}
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # Atualiza usuário específico
            existing_data[username] = user_data
            
            # Salva arquivo completo
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar {username} no JSON: {e}")
            return False
    
    def _repair_user_data(self, user_data: dict, username: str) -> dict:
        """REPARA e garante estrutura completa dos dados do usuário"""
        try:
            repaired_data = user_data.copy()
            
            # Dados básicos obrigatórios
            required_fields = {
                "nome": username,
                "password": user_data.get("password", "123456"),
                "avatar_path": None,
                "avatar_url": None, 
                "xp": 0,
                "level": 1,
                "max_xp": 100,
                "coins": 100,
                "inventory": {},
                "equipped_items": {},
                "display_name": username,
                "achievements": [],
                "play_time": 0,
                "quizzes_completed": 0,
                "correct_answers": 0,
                "total_answers": 0,
                "hotbar": {},
                "last_login": datetime.datetime.now().isoformat(),
                "created_at": user_data.get("created_at", datetime.datetime.now().isoformat()),
                
                # 🔥 NOVOS CAMPOS PARA PERSISTÊNCIA DO QUIZ
                "quiz_state": {
                    "current_lives": 4,
                    "max_lives": 4,
                    "current_mana": 5,
                    "max_mana": 5,
                    "current_phase": 1,
                    "active_effects": {},
                    "used_items": [],
                    "correct_answers_session": 0,
                    "wrong_answers_session": 0,
                    "total_xp_earned_session": 0
                },
                "quiz_progress": {},  # Progresso por fase
                "item_usage": {},     # Estatísticas de uso de itens
                "session_stats": {}   # Estatísticas da sessão atual
            }
            
            for field, default_value in required_fields.items():
                if field not in repaired_data:
                    repaired_data[field] = default_value
                elif field == "quiz_state" and isinstance(repaired_data[field], dict):
                    # Garante estrutura completa do quiz_state
                    repaired_data[field] = self._repair_quiz_state(repaired_data[field])
            
            # Garante estruturas aninhadas
            repaired_data["character"] = self._repair_character_data(
                repaired_data.get("character", {}), 
                username
            )
            
            repaired_data["campaign_progress"] = self._repair_campaign_progress(
                repaired_data.get("campaign_progress", {}),
                username
            )
            
            return repaired_data
            
        except Exception as e:
            print(f"❌ Erro ao reparar dados de {username}: {e}")
            return user_data
    
    def _repair_quiz_state(self, quiz_state: dict) -> dict:
        """Repara estrutura do estado do quiz"""
        default_quiz_state = {
            "current_lives": 4,
            "max_lives": 4,
            "current_mana": 5,
            "max_mana": 5,
            "current_phase": 1,
            "active_effects": {},
            "used_items": [],
            "correct_answers_session": 0,
            "wrong_answers_session": 0,
            "total_xp_earned_session": 0,
            "last_save": datetime.datetime.now().isoformat()
        }
        
        repaired = quiz_state.copy() if quiz_state else {}
        for field, default_value in default_quiz_state.items():
            if field not in repaired:
                repaired[field] = default_value
        
        return repaired
    
    def _repair_character_data(self, character_data: dict, username: str) -> dict:
        """Repara dados do personagem"""
        default_animations = {
            "up": "assets/characters/Emillywhite_down.png",
            "down": "assets/characters/Emillywhite_front.png", 
            "left": "assets/characters/Emillywhite_left.png",
            "right": "assets/characters/Emillywhite_right.png"
        }
        
        repaired = character_data.copy() if character_data else {}
        repaired["name"] = repaired.get("name", "Emily")
        repaired["animations"] = repaired.get("animations", default_animations)
        repaired["position"] = repaired.get("position", {"x": 64, "y": 64})
        
        return repaired
    
    def _repair_campaign_progress(self, campaign_data: dict, username: str) -> dict:
        """Repara progresso da campanha"""
        repaired = campaign_data.copy() if campaign_data else {}
        repaired["fase_atual"] = repaired.get("fase_atual", 1)
        repaired["fases_concluidas"] = repaired.get("fases_concluidas", [])
        
        # Garante todas as fases
        fases = repaired.get("fases", {})
        for fase_id in range(1, 7):
            if fase_id not in fases:
                fases[fase_id] = "liberada" if fase_id == 1 else "bloqueada"
        repaired["fases"] = fases
        
        return repaired

    def save_users(self):
        """Salva TODOS os usuários no MongoDB e JSON - PERSISTÊNCIA TOTAL"""
        try:
            success_count = 0
            total_users = len(self.users)
            
            for username, user_data in self.users.items():
                # Sempre repara antes de salvar
                repaired_data = self._repair_user_data(user_data, username)
                self.users[username] = repaired_data
                
                # Salva em ambas as fontes
                mongo_success = self._save_user_to_mongodb(username, repaired_data)
                json_success = self._save_user_to_json(username, repaired_data)
                
                if mongo_success or json_success:
                    success_count += 1
            
            print(f"💾 Persistência completa: {success_count}/{total_users} usuários salvos")
            return success_count == total_users
            
        except Exception as e:
            print(f"❌ Erro crítico ao salvar usuários: {e}")
            return False
    
    def save_user(self, username: str) -> bool:
        """Salva um usuário específico com persistência total"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if not actual_username:
            return False
        
        user_data = self.users[actual_username]
        repaired_data = self._repair_user_data(user_data, actual_username)
        self.users[actual_username] = repaired_data
        
        # Salva em ambas as fontes
        mongo_success = self._save_user_to_mongodb(actual_username, repaired_data)
        json_success = self._save_user_to_json(actual_username, repaired_data)
        
        success = mongo_success or json_success
        if success:
            print(f"💾 Usuário {username} salvo com persistência total")
        else:
            print(f"❌ Falha ao salvar usuário {username}")
        
        return success

    # 🔥 MÉTODOS PRINCIPAIS COM PERSISTÊNCIA AUTOMÁTICA
    
    def register_user(self, username: str, password: str, nome: str, avatar_url: str = None, **kwargs) -> bool:
        if self.user_exists(username):
            return False
        
        new_user = {
            "nome": nome,
            "password": password,
            "avatar_path": None,
            "avatar_url": avatar_url,
            "xp": 0,
            "level": 1,
            "max_xp": 100,
            "coins": 100,
            "inventory": {},
            "equipped_items": {},
            "display_name": nome,
            "achievements": [],
            "play_time": 0,
            "quizzes_completed": 0,
            "correct_answers": 0,
            "total_answers": 0,
            "hotbar": {},
            "quiz_state": {
                "current_lives": 4,
                "max_lives": 4,
                "current_mana": 5,
                "max_mana": 5,
                "current_phase": 1,
                "active_effects": {},
                "used_items": [],
                "correct_answers_session": 0,
                "wrong_answers_session": 0,
                "total_xp_earned_session": 0
            },
            "quiz_progress": {},
            "item_usage": {},
            "session_stats": {},
            "created_at": datetime.datetime.now().isoformat()
        }
        
        new_user = self._repair_user_data(new_user, username)
        self.users[username] = new_user
        
        # SALVA IMEDIATAMENTE
        success = self.save_user(username)
        
        if success:
            print(f"🎮 Novo usuário registrado: {username} (salvo permanentemente)")
        return success
    
    def purchase_item(self, username: str, item_id: str, item_price: int) -> bool:
        """COMPRA ITEM COM PERSISTÊNCIA IMEDIATA"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if not actual_username:
            return False
        
        user_data = self.users[actual_username]
        current_coins = user_data.get("coins", 0)
        
        if current_coins < item_price:
            return False
        
        try:
            # Atualiza dados
            user_data["coins"] = current_coins - item_price
            
            inventory = user_data.get("inventory", {})
            if item_id in inventory:
                inventory[item_id] += 1
            else:
                inventory[item_id] = 1
            user_data["inventory"] = inventory
            
            # 🔥 PERSISTÊNCIA IMEDIATA
            success = self.save_user(actual_username)
            
            if success:
                print(f"🛍️ COMPRA PERMANENTE: {username} → {item_id}")
                print(f"💰 Moedas: {current_coins} → {user_data['coins']}")
                print(f"📦 Inventário: {inventory}")
            
            return success
            
        except Exception as e:
            print(f"❌ Erro durante compra: {e}")
            return False
    
    def add_to_inventory(self, username: str, item_id: str, quantity: int = 1) -> bool:
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            inventory = self.users[actual_username].get("inventory", {})
            
            if item_id in inventory:
                inventory[item_id] += quantity
            else:
                inventory[item_id] = quantity
            
            self.users[actual_username]["inventory"] = inventory
            return self.save_user(actual_username)
        return False
    
    def equip_to_hotbar(self, username: str, item_id: str, slot: str) -> bool:
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            inventory = self.users[actual_username].get("inventory", {})
            if item_id not in inventory or inventory[item_id] <= 0:
                return False
            
            hotbar = self.users[actual_username].get("hotbar", {})
            hotbar[slot] = item_id
            self.users[actual_username]["hotbar"] = hotbar
            
            return self.save_user(actual_username)
        return False

    # 🔥 NOVOS MÉTODOS PARA PERSISTÊNCIA DO QUIZ
    
    def save_quiz_state(self, username: str, quiz_state: dict) -> bool:
        """Salva o estado atual do quiz (vidas, mana, fase, etc.)"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if not actual_username:
            return False
        
        try:
            user_data = self.users[actual_username]
            
            # Atualiza estado do quiz
            user_data["quiz_state"] = self._repair_quiz_state(quiz_state)
            user_data["quiz_state"]["last_save"] = datetime.datetime.now().isoformat()
            
            # Persiste imediatamente
            success = self.save_user(actual_username)
            
            if success:
                print(f"💾 Estado do quiz salvo para {username}: {quiz_state.get('current_lives')}v/{quiz_state.get('current_mana')}m")
            
            return success
            
        except Exception as e:
            print(f"❌ Erro ao salvar estado do quiz: {e}")
            return False
    
    def get_quiz_state(self, username: str) -> dict:
        """Obtém o estado salvo do quiz"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            user_data = self.users[actual_username]
            return user_data.get("quiz_state", {})
        return {}
    
    def save_quiz_progress(self, username: str, phase: int, progress_data: dict) -> bool:
        """Salva progresso específico de uma fase do quiz"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if not actual_username:
            return False
        
        try:
            user_data = self.users[actual_username]
            
            # Garante estrutura de quiz_progress
            if "quiz_progress" not in user_data:
                user_data["quiz_progress"] = {}
            
            # Salva progresso da fase
            phase_key = f"phase_{phase}"
            user_data["quiz_progress"][phase_key] = {
                **progress_data,
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            # Atualiza fase máxima se necessário
            current_max_phase = user_data.get("max_phase", 0)
            if phase > current_max_phase:
                user_data["max_phase"] = phase
            
            return self.save_user(actual_username)
            
        except Exception as e:
            print(f"❌ Erro ao salvar progresso do quiz: {e}")
            return False
    
    def get_quiz_progress(self, username: str, phase: int = None) -> dict:
        """Obtém progresso do quiz (geral ou de fase específica)"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            user_data = self.users[actual_username]
            quiz_progress = user_data.get("quiz_progress", {})
            
            if phase is not None:
                phase_key = f"phase_{phase}"
                return quiz_progress.get(phase_key, {})
            
            return quiz_progress
        return {}
    
    def update_item_usage(self, username: str, item_id: str) -> bool:
        """Atualiza estatísticas de uso de itens"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if not actual_username:
            return False
        
        try:
            user_data = self.users[actual_username]
            
            # Garante estrutura de item_usage
            if "item_usage" not in user_data:
                user_data["item_usage"] = {}
            
            # Incrementa contador
            current_count = user_data["item_usage"].get(item_id, 0)
            user_data["item_usage"][item_id] = current_count + 1
            
            return self.save_user(actual_username)
            
        except Exception as e:
            print(f"❌ Erro ao atualizar uso de item: {e}")
            return False
    
    def save_session_stats(self, username: str, session_stats: dict) -> bool:
        """Salva estatísticas da sessão atual"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if not actual_username:
            return False
        
        try:
            user_data = self.users[actual_username]
            user_data["session_stats"] = {
                **session_stats,
                "last_session_end": datetime.datetime.now().isoformat()
            }
            
            return self.save_user(actual_username)
            
        except Exception as e:
            print(f"❌ Erro ao salvar estatísticas da sessão: {e}")
            return False

    # 🔥 MÉTODOS DE CONSULTA
    def user_exists(self, username: str) -> bool:
        return username.lower() in [u.lower() for u in self.users.keys()]
    
    def authenticate(self, username: str, password: str) -> bool:
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            return self.users[actual_username]["password"] == password
        return False
    
    def get_user_data(self, username: str) -> Optional[Dict]:
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            return self._repair_user_data(self.users[actual_username], actual_username)
        return None
    
    def update_user_data(self, username: str, user_data: dict) -> bool:
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            repaired_data = self._repair_user_data(user_data, actual_username)
            self.users[actual_username] = repaired_data
            return self.save_user(actual_username)
        return False
    
    def get_inventory(self, username: str) -> Dict:
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            return self.users[actual_username].get("inventory", {})
        return {}
    
    def get_coins(self, username: str) -> int:
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            return self.users[actual_username].get("coins", 0)
        return 0
    
    def get_hotbar(self, username: str) -> Dict:
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            return self.users[actual_username].get("hotbar", {})
        return {}
    
    def add_coins(self, username: str, amount: int) -> bool:
        """Adiciona moedas ao usuário"""
        actual_username = next((u for u in self.users.keys() if u.lower() == username.lower()), None)
        if actual_username:
            current_coins = self.users[actual_username].get("coins", 0)
            self.users[actual_username]["coins"] = current_coins + amount
            return self.save_user(actual_username)
        return False

# Instância global do auth
auth_system = SimpleAuth()