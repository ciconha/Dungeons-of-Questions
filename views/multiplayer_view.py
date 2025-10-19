# multiplayer_view.py
import arcade
import aiohttp
import asyncio
import json
import os
import pymongo
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid

class DiscordUser:
    def __init__(self, user_id: str, username: str, discriminator: str, avatar_url: str, 
                 status: str, game: str = "", is_bot: bool = False):
        self.user_id = user_id
        self.username = username
        self.discriminator = discriminator
        self.avatar_url = avatar_url
        self.status = status
        self.game = game
        self.is_bot = is_bot
        self.avatar_texture = None
        self.loaded = False

class GameGroup:
    def __init__(self, group_id: str, name: str, owner_id: str, description: str = "", 
                 max_members: int = 10, is_public: bool = True):
        self.group_id = group_id
        self.name = name
        self.owner_id = owner_id
        self.description = description
        self.max_members = max_members
        self.is_public = is_public
        self.members = []
        self.created_at = datetime.now()
        self.icon = "👥"

class DiscordGateway:
    def __init__(self, token: str):
        self.token = token
        self.ws_url = "wss://gateway.discord.gg/?v=10&encoding=json"
        self.session = None
        self.ws = None
        self.heartbeat_interval = None
        self.sequence = None
        self.connected = False

    async def connect(self):
        """Conecta ao Gateway do Discord"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Primeiro, obter o gateway
            async with self.session.get("https://discord.com/api/v10/gateway") as resp:
                gateway_data = await resp.json()
                self.ws_url = gateway_data['url'] + "?v=10&encoding=json"
            
            # Conectar ao WebSocket
            self.ws = await self.session.ws_connect(self.ws_url)
            
            # Receber HELLO
            hello = await self.ws.receive_json()
            self.heartbeat_interval = hello['d']['heartbeat_interval'] / 1000
            
            # Identificar
            identify_payload = {
                "op": 2,
                "d": {
                    "token": self.token,
                    "properties": {
                        "$os": "linux",
                        "$browser": "disco",
                        "$device": "disco"
                    },
                    "intents": 513  # Guilds + Guild Messages
                }
            }
            await self.ws.send_json(identify_payload)
            
            # Iniciar heartbeat
            asyncio.create_task(self._heartbeat())
            self.connected = True
            return True
            
        except Exception as e:
            print(f"Erro no Gateway: {e}")
            return False

    async def _heartbeat(self):
        """Mantém a conexão com heartbeat"""
        while self.connected:
            await asyncio.sleep(self.heartbeat_interval)
            if self.ws and not self.ws.closed:
                await self.ws.send_json({"op": 1, "d": self.sequence})

    async def close(self):
        """Fecha a conexão"""
        self.connected = False
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()

class MongoDBManager:
    def __init__(self, connection_string: str = "mongodb://localhost:27017/"):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client.game_multiplayer
        self.users = self.db.users
        self.groups = self.db.groups
        self.sessions = self.db.sessions

    def save_user(self, discord_user: DiscordUser, game_user_id: str = None):
        """Salva/atualiza usuário no MongoDB"""
        user_data = {
            "user_id": discord_user.user_id,
            "username": discord_user.username,
            "discriminator": discord_user.discriminator,
            "avatar_url": discord_user.avatar_url,
            "game_user_id": game_user_id,
            "last_seen": datetime.now(),
            "status": discord_user.status,
            "current_game": discord_user.game,
            "is_bot": discord_user.is_bot
        }
        
        self.users.update_one(
            {"user_id": discord_user.user_id},
            {"$set": user_data},
            upsert=True
        )

    def save_group(self, group: GameGroup):
        """Salva/atualiza grupo no MongoDB"""
        group_data = {
            "group_id": group.group_id,
            "name": group.name,
            "owner_id": group.owner_id,
            "description": group.description,
            "max_members": group.max_members,
            "is_public": group.is_public,
            "members": group.members,
            "created_at": group.created_at,
            "icon": group.icon
        }
        
        self.groups.update_one(
            {"group_id": group.group_id},
            {"$set": group_data},
            upsert=True
        )

    def get_user_groups(self, user_id: str) -> List[GameGroup]:
        """Busca grupos do usuário"""
        groups_data = self.groups.find({
            "$or": [
                {"owner_id": user_id},
                {"members": user_id}
            ]
        })
        
        groups = []
        for data in groups_data:
            group = GameGroup(
                data["group_id"],
                data["name"],
                data["owner_id"],
                data.get("description", ""),
                data.get("max_members", 10),
                data.get("is_public", True)
            )
            group.members = data.get("members", [])
            group.created_at = data.get("created_at", datetime.now())
            group.icon = data.get("icon", "👥")
            groups.append(group)
        
        return groups

    def find_user_by_discord_id(self, discord_id: str) -> Optional[Dict]:
        """Encontra usuário pelo ID do Discord"""
        return self.users.find_one({"user_id": discord_id})

    def create_session(self, user_id: str, discord_token: str) -> str:
        """Cria sessão de usuário"""
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "discord_token": discord_token,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(days=7)
        }
        self.sessions.insert_one(session_data)
        return session_id

class MultiplayerView(arcade.View):
    def __init__(self, menu_view=None):
        super().__init__()
        self.menu_view = menu_view
        
        # Configurações do Discord
        self.discord_api_base = "https://discord.com/api/v10"
        self.discord_token = None
        self.discord_gateway = None
        self.current_user = None
        
        # MongoDB
        self.mongo = MongoDBManager()
        
        # Estado da UI
        self.active_section = 0  # 0: Amigos, 1: Grupos, 2: Configurações, 3: Criar Grupo
        self.sections = ["AMIGOS ONLINE", "MEUS GRUPOS", "CONFIGURAÇÕES", "CRIAR GRUPO"]
        
        # Dados
        self.friends_data = []
        self.user_groups = []
        self.available_groups = []
        
        # Elementos de UI
        self.search_text = ""
        self.typing = False
        self.typing_field = None  # 'token', 'group_name', 'group_desc'
        self.connection_status = "Desconectado"
        
        # Dados para criar grupo
        self.new_group_name = ""
        self.new_group_description = ""
        self.new_group_max_members = 8
        self.new_group_public = True
        
        # Carregar token salvo se existir
        self._load_saved_token()
        
        # Inicializar dados
        self._initialize_sample_data()

    def _load_saved_token(self):
        """Carrega token do Discord salvo anteriormente"""
        try:
            if os.path.exists("discord_token.txt"):
                with open("discord_token.txt", "r") as f:
                    self.discord_token = f.read().strip()
                    self.connection_status = "Token Carregado"
        except Exception as e:
            print(f"Erro ao carregar token: {e}")

    def _save_token(self, token: str):
        """Salva token do Discord"""
        try:
            with open("discord_token.txt", "w") as f:
                f.write(token)
            self.discord_token = token
            self.connection_status = "Token Salvo"
        except Exception as e:
            print(f"Erro ao salvar token: {e}")

    def _initialize_sample_data(self):
        """Inicializa dados de exemplo"""
        # Amigos de exemplo
        self.friends_data = [
            {
                "user_id": "123456789",
                "username": "HQIneedU",
                "discriminator": "1234",
                "status": "online",
                "game": "Jogando Red Dead Redemption 2",
                "karma": "10.9k",
                "avatar_url": "https://cdn.discordapp.com/embed/avatars/0.png"
            }
        ]

    async def connect_to_discord(self, token: str):
        """Conecta à API do Discord e inicia Gateway"""
        if not token:
            self.connection_status = "Token Inválido"
            return False
        
        try:
            headers = {"Authorization": f"Bot {token}"}
            async with aiohttp.ClientSession() as session:
                # Testar conexão básica
                async with session.get(f"{self.discord_api_base}/users/@me", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        
                        # Criar objeto DiscordUser
                        self.current_user = DiscordUser(
                            user_id=user_data['id'],
                            username=user_data['username'],
                            discriminator=user_data['discriminator'],
                            avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data.get('avatar', '')}.png",
                            status="online",
                            is_bot=user_data.get('bot', False)
                        )
                        
                        # Salvar no MongoDB
                        self.mongo.save_user(self.current_user)
                        
                        # Criar sessão
                        session_id = self.mongo.create_session(
                            self.current_user.user_id, 
                            token
                        )
                        
                        # Iniciar Gateway
                        self.discord_gateway = DiscordGateway(token)
                        gateway_connected = await self.discord_gateway.connect()
                        
                        if gateway_connected:
                            self.connection_status = "Conectado ao Gateway"
                            self._save_token(token)
                            
                            # Carregar grupos do usuário
                            self._load_user_groups()
                            
                            return True
                        else:
                            self.connection_status = "Gateway Falhou"
                            return False
                    else:
                        self.connection_status = "Falha na Autenticação"
                        return False
                        
        except Exception as e:
            print(f"Erro na conexão Discord: {e}")
            self.connection_status = f"Erro: {str(e)}"
            return False

    def _load_user_groups(self):
        """Carrega grupos do usuário do MongoDB"""
        if self.current_user:
            self.user_groups = self.mongo.get_user_groups(self.current_user.user_id)

    def create_new_group(self):
        """Cria um novo grupo de jogo"""
        if not self.current_user:
            return False
        
        try:
            group_id = str(uuid.uuid4())
            new_group = GameGroup(
                group_id=group_id,
                name=self.new_group_name,
                owner_id=self.current_user.user_id,
                description=self.new_group_description,
                max_members=self.new_group_max_members,
                is_public=self.new_group_public
            )
            
            # Adicionar criador como membro
            new_group.members.append(self.current_user.user_id)
            
            # Salvar no MongoDB
            self.mongo.save_group(new_group)
            
            # Recarregar grupos
            self._load_user_groups()
            
            # Limpar formulário
            self.new_group_name = ""
            self.new_group_description = ""
            self.new_group_max_members = 8
            self.new_group_public = True
            
            return True
            
        except Exception as e:
            print(f"Erro ao criar grupo: {e}")
            return False

    def join_group(self, group_id: str):
        """Entra em um grupo existente"""
        if not self.current_user:
            return False
        
        try:
            group_data = self.mongo.groups.find_one({"group_id": group_id})
            if group_data and len(group_data.get("members", [])) < group_data.get("max_members", 10):
                self.mongo.groups.update_one(
                    {"group_id": group_id},
                    {"$addToSet": {"members": self.current_user.user_id}}
                )
                self._load_user_groups()
                return True
            return False
        except Exception as e:
            print(f"Erro ao entrar no grupo: {e}")
            return False

    def on_show(self):
        """Chamado quando a view é mostrada"""
        arcade.set_background_color((240, 240, 240))
        print("🎮 Tela Multiplayer aberta")

    def on_draw(self):
        """Renderiza a tela multiplayer"""
        self.clear()
        
        # Fundo estilo Neubrutalism
        self._draw_neubrutalism_background()
        
        # Header
        self._draw_header()
        
        # Conteúdo principal
        self._draw_main_content()
        
        # Sidebar
        self._draw_sidebar()
        
        # Footer
        self._draw_footer()

    def _draw_neubrutalism_background(self):
        """Desenha fundo no estilo Neubrutalism"""
        width, height = self.window.width, self.window.height
        
        # Fundo principal
        arcade.draw_lrbt_rectangle_filled(0, width, 0, height, (240, 240, 240))
        
        # Elementos decorativos
        arcade.draw_lrbt_rectangle_filled(0, width, height - 60, height, (255, 100, 100))
        arcade.draw_lrbt_rectangle_filled(width - 300, width, 0, height - 60, (100, 150, 255))
        
        # Bordas grossas
        arcade.draw_lrbt_rectangle_outline(10, width - 10, 10, height - 10, (0, 0, 0), 4)
        arcade.draw_lrbt_rectangle_outline(width - 290, width - 10, 10, height - 70, (0, 0, 0), 3)

    def _draw_header(self):
        """Desenha o header"""
        width, height = self.window.width, self.window.height
        
        # Logo/Title
        arcade.draw_text("MULTIPLAYER HUB", width // 2, height - 35, 
                        (255, 255, 255), 24, bold=True, 
                        anchor_x="center", anchor_y="center")
        
        # Status da conexão
        status_color = (0, 200, 0) if "Conectado" in self.connection_status else (
            (255, 200, 0) if "Carregado" in self.connection_status else (255, 50, 50)
        )
        arcade.draw_text(f"Status: {self.connection_status}", 20, height - 35,
                        status_color, 14, bold=True, anchor_y="center")
        
        # Usuário atual
        if self.current_user:
            arcade.draw_text(
                f"👤 {self.current_user.username}#{self.current_user.discriminator}", 
                width - 200, height - 35, (255, 255, 255), 12, 
                anchor_x="right", anchor_y="center"
            )

    def _draw_main_content(self):
        """Desenha o conteúdo principal"""
        width, height = self.window.width, self.window.height
        
        # Área principal
        main_width = width - 320
        main_height = height - 80
        
        # Abas de navegação
        self._draw_navigation_tabs(main_width)
        
        # Conteúdo da aba ativa
        if self.active_section == 0:  # AMIGOS
            self._draw_friends_section(main_width, main_height)
        elif self.active_section == 1:  # GRUPOS
            self._draw_groups_section(main_width, main_height)
        elif self.active_section == 2:  # CONFIGURAÇÕES
            self._draw_settings_section(main_width, main_height)
        elif self.active_section == 3:  # CRIAR GRUPO
            self._draw_create_group_section(main_width, main_height)

    def _draw_navigation_tabs(self, main_width: int):
        """Desenha as abas de navegação"""
        height = self.window.height
        tab_width = main_width / len(self.sections)
        
        for i, section in enumerate(self.sections):
            tab_x = i * tab_width + tab_width / 2
            tab_y = height - 90
            
            # Fundo da aba
            bg_color = (255, 100, 100) if i == self.active_section else (200, 200, 200)
            arcade.draw_lrbt_rectangle_filled(
                i * tab_width + 5, (i + 1) * tab_width - 5,
                height - 100, height - 70,
                bg_color
            )
            
            # Borda
            arcade.draw_lrbt_rectangle_outline(
                i * tab_width + 5, (i + 1) * tab_width - 5,
                height - 100, height - 70,
                (0, 0, 0), 2
            )
            
            # Texto
            text_color = (255, 255, 255) if i == self.active_section else (0, 0, 0)
            arcade.draw_text(section, tab_x, tab_y, text_color, 14, 
                           bold=True, anchor_x="center", anchor_y="center")

    def _draw_friends_section(self, width: int, height: int):
        """Desenha seção de amigos online"""
        start_x = 20
        start_y = self.window.height - 120
        
        # Barra de pesquisa
        self._draw_search_bar(start_x, start_y, width - 40)
        
        # Lista de amigos
        friends_start_y = start_y - 50
        for i, friend in enumerate(self.friends_data):
            friend_y = friends_start_y - (i * 120)
            if friend_y > 100:
                self._draw_friend_card(start_x + 10, friend_y, width - 60, 100, friend)

    def _draw_friend_card(self, x: int, y: int, width: int, height: int, friend: Dict):
        """Desenha card de amigo"""
        # Fundo do card
        arcade.draw_lrbt_rectangle_filled(x, x + width, y - height, y, (255, 255, 255))
        arcade.draw_lrbt_rectangle_outline(x, x + width, y - height, y, (0, 0, 0), 2)
        
        # Status indicator
        status_colors = {
            "online": (0, 200, 0),
            "idle": (255, 200, 0),
            "dnd": (255, 50, 50),
            "offline": (100, 100, 100)
        }
        status_color = status_colors.get(friend["status"], (100, 100, 100))
        
        arcade.draw_circle_filled(x + 20, y - 20, 8, status_color)
        arcade.draw_circle_outline(x + 20, y - 20, 8, (0, 0, 0), 1)
        
        # Avatar
        arcade.draw_circle_filled(x + 20, y - 50, 25, (200, 200, 200))
        arcade.draw_circle_outline(x + 20, y - 50, 25, (0, 0, 0), 2)
        arcade.draw_text("👤", x + 20, y - 50, (100, 100, 100), 20, 
                        anchor_x="center", anchor_y="center")
        
        # Informações do usuário
        arcade.draw_text(f"{friend['username']}#{friend['discriminator']}", 
                        x + 60, y - 20, (0, 0, 0), 16, bold=True)
        
        arcade.draw_text(f"Karma: {friend['karma']}", 
                        x + 60, y - 40, (100, 100, 100), 12)
        
        # Status do jogo
        if friend["game"]:
            arcade.draw_text(f"🎮 {friend['game']}", 
                           x + 60, y - 60, (0, 100, 200), 12)
        
        # Botão de ação
        arcade.draw_lrbt_rectangle_filled(x + width - 100, x + width - 20, y - 30, y - 10, 
                                        (100, 200, 100))
        arcade.draw_lrbt_rectangle_outline(x + width - 100, x + width - 20, y - 30, y - 10, 
                                         (0, 0, 0), 1)
        arcade.draw_text("JOGAR", x + width - 60, y - 20, (0, 0, 0), 12, 
                        anchor_x="center", anchor_y="center", bold=True)

    def _draw_groups_section(self, width: int, height: int):
        """Desenha seção de grupos"""
        start_x = 20
        start_y = self.window.height - 120
        
        arcade.draw_text("MEUS GRUPOS DE JOGO", start_x, start_y, 
                        (0, 0, 0), 20, bold=True)
        
        # Lista de grupos do usuário
        groups_start_y = start_y - 40
        for i, group in enumerate(self.user_groups):
            group_y = groups_start_y - (i * 180)
            if group_y > 100:
                self._draw_group_card(start_x + 10, group_y, width - 60, 160, group, True)

    def _draw_group_card(self, x: int, y: int, width: int, height: int, group: GameGroup, is_my_group: bool = False):
        """Desenha card de grupo"""
        # Fundo do card
        arcade.draw_lrbt_rectangle_filled(x, x + width, y - height, y, (255, 255, 255))
        arcade.draw_lrbt_rectangle_outline(x, x + width, y - height, y, (0, 0, 0), 2)
        
        # Ícone do grupo
        arcade.draw_text(group.icon, x + 30, y - 30, (0, 0, 0), 32,
                        anchor_x="center", anchor_y="center")
        
        # Nome e estatísticas
        arcade.draw_text(group.name, x + 70, y - 20, (0, 0, 0), 18, bold=True)
        arcade.draw_text(f"👥 {len(group.members)}/{group.max_members} membros • {'Público' if group.is_public else 'Privado'}", 
                        x + 70, y - 45, (100, 100, 100), 12)
        
        # Descrição
        arcade.draw_text(group.description, x + 70, y - 65, (0, 0, 0), 12)
        
        # Botões de ação
        button_width = 80
        if is_my_group:
            # Botão para gerenciar grupo
            arcade.draw_lrbt_rectangle_filled(x + width - button_width - 20, x + width - 20, 
                                            y - 140, y - 120, (100, 150, 255))
            arcade.draw_lrbt_rectangle_outline(x + width - button_width - 20, x + width - 20, 
                                             y - 140, y - 120, (0, 0, 0), 1)
            arcade.draw_text("GERENCIAR", x + width - button_width/2 - 20, y - 130, 
                            (255, 255, 255), 10, anchor_x="center", anchor_y="center", bold=True)
        else:
            # Botão para entrar no grupo
            arcade.draw_lrbt_rectangle_filled(x + width - button_width - 20, x + width - 20, 
                                            y - 140, y - 120, (100, 200, 100))
            arcade.draw_lrbt_rectangle_outline(x + width - button_width - 20, x + width - 20, 
                                             y - 140, y - 120, (0, 0, 0), 1)
            arcade.draw_text("ENTRAR", x + width - button_width/2 - 20, y - 130, 
                            (0, 0, 0), 11, anchor_x="center", anchor_y="center", bold=True)

    def _draw_create_group_section(self, width: int, height: int):
        """Desenha seção de criação de grupo"""
        start_x = 20
        start_y = self.window.height - 120
        
        arcade.draw_text("CRIAR NOVO GRUPO", start_x, start_y, 
                        (0, 0, 0), 20, bold=True)
        
        # Campo: Nome do Grupo
        arcade.draw_text("Nome do Grupo:", start_x + 20, start_y - 50, 
                        (0, 0, 0), 16, bold=True)
        self._draw_input_field(start_x + 20, start_y - 80, width - 60, 30, 
                              self.new_group_name, "group_name", "Digite o nome do grupo...")
        
        # Campo: Descrição
        arcade.draw_text("Descrição:", start_x + 20, start_y - 130, 
                        (0, 0, 0), 16, bold=True)
        self._draw_input_field(start_x + 20, start_y - 160, width - 60, 30, 
                              self.new_group_description, "group_desc", "Descrição opcional...")
        
        # Campo: Máximo de Membros
        arcade.draw_text(f"Máximo de Membros: {self.new_group_max_members}", 
                        start_x + 20, start_y - 210, (0, 0, 0), 16, bold=True)
        
        # Botões +/- para membros
        arcade.draw_lrbt_rectangle_filled(start_x + 250, start_x + 280, start_y - 225, start_y - 205, 
                                        (200, 200, 200))
        arcade.draw_text("-", start_x + 265, start_y - 215, (0, 0, 0), 16, 
                        anchor_x="center", anchor_y="center", bold=True)
        
        arcade.draw_lrbt_rectangle_filled(start_x + 290, start_x + 320, start_y - 225, start_y - 205, 
                                        (200, 200, 200))
        arcade.draw_text("+", start_x + 305, start_y - 215, (0, 0, 0), 16, 
                        anchor_x="center", anchor_y="center", bold=True)
        
        # Checkbox: Grupo Público
        checkbox_color = (100, 200, 100) if self.new_group_public else (200, 200, 200)
        arcade.draw_lrbt_rectangle_filled(start_x + 20, start_x + 40, start_y - 260, start_y - 240, 
                                        checkbox_color)
        arcade.draw_lrbt_rectangle_outline(start_x + 20, start_x + 40, start_y - 260, start_y - 240, 
                                         (0, 0, 0), 2)
        arcade.draw_text("Grupo Público", start_x + 50, start_y - 250, (0, 0, 0), 14)
        
        # Botão Criar Grupo
        arcade.draw_lrbt_rectangle_filled(start_x + 20, start_x + 200, start_y - 300, start_y - 270, 
                                        (100, 200, 100))
        arcade.draw_lrbt_rectangle_outline(start_x + 20, start_x + 200, start_y - 300, start_y - 270, 
                                         (0, 0, 0), 2)
        arcade.draw_text("CRIAR GRUPO", start_x + 110, start_y - 285, (0, 0, 0), 14, 
                        anchor_x="center", anchor_y="center", bold=True)

    def _draw_input_field(self, x: int, y: int, width: int, height: int, 
                         text: str, field_type: str, placeholder: str):
        """Desenha campo de entrada genérico"""
        # Fundo
        bg_color = (220, 220, 255) if self.typing and self.typing_field == field_type else (255, 255, 255)
        arcade.draw_lrbt_rectangle_filled(x, x + width, y - height, y, bg_color)
        arcade.draw_lrbt_rectangle_outline(x, x + width, y - height, y, (0, 0, 0), 2)
        
        # Texto
        display_text = text if text else placeholder
        text_color = (0, 0, 0) if text else (150, 150, 150)
        arcade.draw_text(display_text, x + 10, y - height/2, text_color, 14, anchor_y="center")

    def _draw_settings_section(self, width: int, height: int):
        """Desenha seção de configurações"""
        start_x = 20
        start_y = self.window.height - 120
        
        arcade.draw_text("CONFIGURAÇÕES DO DISCORD", start_x, start_y, 
                        (0, 0, 0), 20, bold=True)
        
        # Área de configuração do token
        token_y = start_y - 50
        arcade.draw_text("Token do Discord Bot:", start_x + 20, token_y, 
                        (0, 0, 0), 16, bold=True)
        
        # Campo de entrada do token
        self._draw_input_field(start_x + 20, token_y - 30, 400, 30, 
                              self.search_text if self.typing and self.typing_field == 'token' else ("*" * len(self.discord_token) if self.discord_token else ""), 
                              "token", "Clique para inserir token...")
        
        # Botão de conectar
        connect_button_color = (100, 200, 100) if self.discord_token else (200, 200, 200)
        arcade.draw_lrbt_rectangle_filled(start_x + 440, start_x + 540, token_y - 30, token_y, 
                                        connect_button_color)
        arcade.draw_lrbt_rectangle_outline(start_x + 440, start_x + 540, token_y - 30, token_y, 
                                         (0, 0, 0), 2)
        arcade.draw_text("CONECTAR", start_x + 490, token_y - 15, (0, 0, 0), 12, 
                        anchor_x="center", anchor_y="center", bold=True)
        
        # Informações do MongoDB
        mongo_y = token_y - 80
        arcade.draw_text("STATUS DO BANCO DE DADOS:", start_x + 20, mongo_y, 
                        (0, 0, 0), 16, bold=True)
        
        try:
            # Testar conexão com MongoDB
            server_info = self.mongo.client.server_info()
            arcade.draw_text("✅ MongoDB Conectado", start_x + 40, mongo_y - 30, (0, 150, 0), 14)
            arcade.draw_text(f"📊 Grupos salvos: {self.mongo.groups.count_documents({})}", 
                           start_x + 40, mongo_y - 55, (0, 0, 0), 12)
            arcade.draw_text(f"👥 Usuários registrados: {self.mongo.users.count_documents({})}", 
                           start_x + 40, mongo_y - 80, (0, 0, 0), 12)
        except Exception as e:
            arcade.draw_text("❌ MongoDB Desconectado", start_x + 40, mongo_y - 30, (255, 0, 0), 14)

    def _draw_search_bar(self, x: int, y: int, width: int):
        """Desenha barra de pesquisa"""
        # Fundo da barra
        arcade.draw_lrbt_rectangle_filled(x, x + width, y - 35, y - 5, (255, 255, 255))
        arcade.draw_lrbt_rectangle_outline(x, x + width, y - 35, y - 5, (0, 0, 0), 2)
        
        # Ícone de pesquisa
        arcade.draw_text("🔍", x + 15, y - 20, (100, 100, 100), 16, 
                        anchor_x="center", anchor_y="center")
        
        # Texto
        search_text = self.search_text if self.search_text else "Pesquisar amigos..."
        text_color = (0, 0, 0) if self.search_text else (150, 150, 150)
        arcade.draw_text(search_text, x + 40, y - 20, text_color, 14)

    def _draw_sidebar(self):
        """Desenha a sidebar"""
        width, height = self.window.width, self.window.height
        sidebar_x = width - 290
        sidebar_width = 280
        
        # Título da sidebar
        arcade.draw_text("ATIVIDADES RECENTES", sidebar_x + 20, height - 100, 
                        (255, 255, 255), 16, bold=True)
        
        # Lista de atividades
        activities = [
            {"user": "HQIneedU", "action": "entrou no jogo", "time": "2 min"},
            {"user": "lousnman_dvo", "action": "completou uma missão", "time": "5 min"}
        ]
        
        activity_y = height - 130
        for activity in activities:
            arcade.draw_text(f"• {activity['user']} {activity['action']}", 
                           sidebar_x + 20, activity_y, (255, 255, 255), 12)
            arcade.draw_text(activity["time"], sidebar_x + sidebar_width - 30, activity_y, 
                           (200, 200, 200), 10, anchor_x="right")
            activity_y -= 25

    def _draw_footer(self):
        """Desenha o footer"""
        width, height = self.window.width, self.window.height
        
        arcade.draw_lrbt_rectangle_filled(0, width, 0, 40, (50, 50, 50))
        arcade.draw_text("Multiplayer Hub • Conecte-se com amigos e jogue together!", 
                        20, 20, (200, 200, 200), 12, anchor_y="center")
        
        # Botão voltar
        arcade.draw_lrbt_rectangle_filled(width - 120, width - 20, 10, 30, (255, 100, 100))
        arcade.draw_lrbt_rectangle_outline(width - 120, width - 20, 10, 30, (255, 255, 255), 2)
        arcade.draw_text("VOLTAR", width - 70, 20, (255, 255, 255), 12, 
                        anchor_x="center", anchor_y="center", bold=True)

    def on_key_press(self, key, modifiers):
        """Lida com pressionamento de teclas"""
        if self.typing:
            if key == arcade.key.ENTER:
                self.typing = False
                self.typing_field = None
                if self.search_text and self.typing_field == 'token':
                    self.discord_token = self.search_text
                    self.search_text = ""
                    asyncio.create_task(self.connect_to_discord(self.discord_token))
            elif key == arcade.key.BACKSPACE:
                if self.typing_field == 'token':
                    self.search_text = self.search_text[:-1]
                elif self.typing_field == 'group_name':
                    self.new_group_name = self.new_group_name[:-1]
                elif self.typing_field == 'group_desc':
                    self.new_group_description = self.new_group_description[:-1]
            elif key == arcade.key.ESCAPE:
                self.typing = False
                self.typing_field = None
                self.search_text = ""
        else:
            if key == arcade.key.LEFT:
                self.active_section = (self.active_section - 1) % len(self.sections)
            elif key == arcade.key.RIGHT:
                self.active_section = (self.active_section + 1) % len(self.sections)
            elif key == arcade.key.ESCAPE:
                self._return_to_menu()

    def on_text(self, text: str):
        """Lida com entrada de texto quando está digitando"""
        if self.typing:
            if self.typing_field == 'token':
                self.search_text += text
            elif self.typing_field == 'group_name':
                self.new_group_name += text
            elif self.typing_field == 'group_desc':
                self.new_group_description += text

    def on_mouse_press(self, x, y, button, modifiers):
        """Lida com cliques do mouse"""
        # Verificar clique nas abas
        self._handle_tab_click(x, y)
        
        # Verificar clique nos campos de entrada
        self._handle_input_field_click(x, y)
        
        # Verificar clique nos botões
        self._handle_button_clicks(x, y)
        
        # Verificar clique no botão voltar
        self._handle_back_button_click(x, y)

    def _handle_tab_click(self, x, y):
        """Verifica clique nas abas"""
        width = self.window.width - 320
        height = self.window.height
        tab_width = width / len(self.sections)
        
        for i in range(len(self.sections)):
            tab_x1 = i * tab_width + 5
            tab_x2 = (i + 1) * tab_width - 5
            
            if (tab_x1 <= x <= tab_x2 and 
                height - 100 <= y <= height - 70):
                self.active_section = i
                break

    def _handle_input_field_click(self, x, y):
        """Verifica clique nos campos de entrada"""
        start_x = 20
        start_y = self.window.height - 120
        
        # Campo do token
        if (start_x + 20 <= x <= start_x + 420 and 
            start_y - 60 <= y <= start_y - 30):
            self.typing = True
            self.typing_field = 'token'
            self.search_text = self.discord_token if self.discord_token else ""
        
        # Campo nome do grupo (na aba criar grupo)
        elif (self.active_section == 3 and 
              start_x + 20 <= x <= start_x + (self.window.width - 320) - 40 and 
              start_y - 110 <= y <= start_y - 80):
            self.typing = True
            self.typing_field = 'group_name'
        
        # Campo descrição do grupo
        elif (self.active_section == 3 and 
              start_x + 20 <= x <= start_x + (self.window.width - 320) - 40 and 
              start_y - 190 <= y <= start_y - 160):
            self.typing = True
            self.typing_field = 'group_desc'

    def _handle_button_clicks(self, x, y):
        """Verifica clique nos botões"""
        start_x = 20
        start_y = self.window.height - 120
        
        # Botão conectar Discord
        if (self.active_section == 2 and 
            start_x + 440 <= x <= start_x + 540 and 
            start_y - 60 <= y <= start_y - 30):
            if self.discord_token:
                asyncio.create_task(self.connect_to_discord(self.discord_token))
        
        # Botão criar grupo
        elif (self.active_section == 3 and 
              start_x + 20 <= x <= start_x + 200 and 
              start_y - 330 <= y <= start_y - 300):
            if self.new_group_name.strip():
                success = self.create_new_group()
                if success:
                    print("✅ Grupo criado com sucesso!")
                else:
                    print("❌ Erro ao criar grupo")
        
        # Botões +/- para membros
        elif (self.active_section == 3 and 
              start_x + 250 <= x <= start_x + 280 and 
              start_y - 255 <= y <= start_y - 235):
            if self.new_group_max_members > 2:
                self.new_group_max_members -= 1
        elif (self.active_section == 3 and 
              start_x + 290 <= x <= start_x + 320 and 
              start_y - 255 <= y <= start_y - 235):
            if self.new_group_max_members < 20:
                self.new_group_max_members += 1
        
        # Checkbox grupo público
        elif (self.active_section == 3 and 
              start_x + 20 <= x <= start_x + 40 and 
              start_y - 290 <= y <= start_y - 270):
            self.new_group_public = not self.new_group_public

    def _handle_back_button_click(self, x, y):
        """Verifica clique no botão voltar"""
        width = self.window.width
        if (width - 120 <= x <= width - 20 and 
            10 <= y <= 30):
            self._return_to_menu()

    def _return_to_menu(self):
        """Volta para o menu principal"""
        try:
            # Fechar conexão do Gateway se existir
            if self.discord_gateway:
                asyncio.create_task(self.discord_gateway.close())
            
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

    def on_hide_view(self):
        """Chamado quando a view é escondida"""
        # Fechar conexões
        if self.discord_gateway:
            asyncio.create_task(self.discord_gateway.close())