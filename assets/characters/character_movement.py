# assets/characters/character_movement.py

import arcade
import os
from typing import Dict, Optional

class CharacterMovement:
    """
    Sistema centralizado de movimentação para TODOS os personagens
    CORRIGE automaticamente usuários com animações quebradas
    """
    
    # 🔥 CONFIGURAÇÕES PADRÃO ABSOLUTAS - CAMINHOS GARANTIDOS
    DEFAULT_ANIMATIONS = {
        "up": "assets/characters/Emillywhite_down.png",
        "down": "assets/characters/Emillywhite_front.png", 
        "left": "assets/characters/Emillywhite_left.png",
        "right": "assets/characters/Emillywhite_right.png"
    }
    
    DEFAULT_SPEED = 180
    DEFAULT_SCALE = 0.95
    DEFAULT_POSITION = {"x": 128, "y": 128}

    @staticmethod
    def _has_broken_animations(animations: Dict) -> bool:
        """DETECTA se as animações estão quebradas (todas iguais)"""
        if not animations:
            return True
            
        # Se tem menos de 4 animações, está quebrado
        if len(animations) < 4:
            return True
            
        # Se todas as animações apontam para o mesmo arquivo, está quebrado
        unique_paths = set(animations.values())
        if len(unique_paths) == 1:
            print(f"🚨 ANIMAÇÕES QUEBRADAS: Todas apontam para {list(unique_paths)[0]}")
            return True
            
        return False

    @staticmethod
    def _validate_image_path(image_path: str) -> bool:
        """VALIDA se o caminho da imagem existe"""
        if not image_path:
            return False
        
        # Tenta caminhos diferentes
        paths_to_try = [
            image_path,
            os.path.join(os.getcwd(), image_path),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), image_path)
        ]
        
        for path in paths_to_try:
            if os.path.exists(path):
                return True
                
        return False

    @staticmethod
    def _get_valid_image_path(image_path: str, fallback_path: str) -> str:
        """Retorna caminho válido ou fallback"""
        if CharacterMovement._validate_image_path(image_path):
            return image_path
        else:
            return fallback_path

    @staticmethod
    def create_character_sprite(character_data: Dict) -> arcade.Sprite:
        """Cria sprite CORRIGINDO animações quebradas"""
        try:
            print("🎭 Criando sprite da Emily...")
            
            # 🔥 CORREÇÃO CRÍTICA: Verifica e corrige animações quebradas
            animations = character_data.get("animations", {})
            
            if CharacterMovement._has_broken_animations(animations):
                print("🚨 CORRIGINDO animações quebradas automaticamente!")
                animations = CharacterMovement.DEFAULT_ANIMATIONS.copy()
            else:
                animations = CharacterMovement._ensure_complete_and_valid_animations(animations)
            
            # Carrega sprite com animações garantidas
            initial_texture_path = CharacterMovement._get_valid_image_path(
                animations.get("down"), 
                CharacterMovement.DEFAULT_ANIMATIONS["down"]
            )
            
            if CharacterMovement._validate_image_path(initial_texture_path):
                sprite = arcade.Sprite(
                    initial_texture_path,
                    scale=CharacterMovement.DEFAULT_SCALE,
                    hit_box_algorithm="Simple"
                )
                
                # 🔥 CARREGA TEXTURAS COM CORREÇÃO
                sprite.textures = {}
                for direction, texture_path in animations.items():
                    valid_path = CharacterMovement._get_valid_image_path(
                        texture_path, 
                        CharacterMovement.DEFAULT_ANIMATIONS[direction]
                    )
                    
                    try:
                        texture = arcade.load_texture(valid_path)
                        sprite.textures[direction] = texture
                        print(f"   ✅ {direction}: {os.path.basename(valid_path)}")
                    except Exception as e:
                        print(f"   ❌ Erro em {direction}: {e}")
                        # Fallback para direção padrão
                        try:
                            fallback_texture = arcade.load_texture(CharacterMovement.DEFAULT_ANIMATIONS[direction])
                            sprite.textures[direction] = fallback_texture
                            print(f"   🔄 Fallback para {direction}")
                        except:
                            # Último recurso
                            sprite.textures[direction] = arcade.SpriteSolidColor(40, 60, arcade.color.BLUE).texture
                
                # Define textura inicial
                if "down" in sprite.textures:
                    sprite.texture = sprite.textures["down"]
                
                print(f"✅ Sprite criado com {len(sprite.textures)} animações")
                return sprite
            else:
                raise FileNotFoundError("Nenhuma textura válida")
                
        except Exception as e:
            print(f"❌ Erro crítico: {e}")
            # Fallback de emergência
            try:
                sprite = arcade.Sprite(
                    CharacterMovement.DEFAULT_ANIMATIONS["down"],
                    scale=CharacterMovement.DEFAULT_SCALE
                )
                # Cria texturas básicas
                sprite.textures = {}
                for direction in ["up", "down", "left", "right"]:
                    sprite.textures[direction] = sprite.texture
                print("🆘 Sprite de emergência criado")
                return sprite
            except:
                emergency_sprite = arcade.SpriteSolidColor(40, 60, arcade.color.BLUE)
                emergency_sprite.textures = {dir: emergency_sprite.texture for dir in ["up", "down", "left", "right"]}
                return emergency_sprite

    @staticmethod
    def _ensure_complete_and_valid_animations(animations: Dict) -> Dict:
        """GARANTE animações completas e válidas"""
        complete_animations = {}
        
        for direction, default_path in CharacterMovement.DEFAULT_ANIMATIONS.items():
            user_path = animations.get(direction)
            
            if user_path and CharacterMovement._validate_image_path(user_path):
                complete_animations[direction] = user_path
            else:
                complete_animations[direction] = default_path
                if user_path:
                    print(f"🔄 {direction} inválido, usando padrão")
                else:
                    print(f"🔄 {direction} faltando, usando padrão")
        
        return complete_animations

    @staticmethod
    def get_initial_position(character_data: Dict) -> tuple:
        """Obtém posição inicial do personagem"""
        position = character_data.get("position", CharacterMovement.DEFAULT_POSITION)
        x = position.get("x", CharacterMovement.DEFAULT_POSITION["x"])
        y = position.get("y", CharacterMovement.DEFAULT_POSITION["y"])
        print(f"📍 Posição inicial: ({x}, {y})")
        return x, y
    
    @staticmethod
    def update_movement(
        sprite: arcade.Sprite,
        keys: Dict,
        delta_time: float,
        map_width: float,
        map_height: float
    ) -> tuple:
        """
        Atualiza movimento do personagem
        Retorna: (new_x, new_y, facing_direction, is_moving)
        """
        if not sprite:
            return 0, 0, "down", False
        
        speed = CharacterMovement.DEFAULT_SPEED * delta_time
        
        # 🔥 CONTROLES WASD PADRONIZADOS PARA TODOS
        dx = dy = 0
        if keys.get(arcade.key.W, False):
            dy += speed
        if keys.get(arcade.key.S, False):
            dy -= speed
        if keys.get(arcade.key.A, False):
            dx -= speed
        if keys.get(arcade.key.D, False):
            dx += speed
        
        # Normaliza movimento diagonal
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        
        # Calcula nova posição
        new_x = sprite.center_x + dx
        new_y = sprite.center_y + dy
        
        # Limita ao mapa
        new_x = max(sprite.width / 2, min(new_x, map_width - sprite.width / 2))
        new_y = max(sprite.height / 2, min(new_y, map_height - sprite.height / 2))
        
        # Determina direção
        facing_direction = "down"  # padrão
        is_moving = dx != 0 or dy != 0
        
        if is_moving:
            if abs(dx) > abs(dy):
                facing_direction = "right" if dx > 0 else "left"
            else:
                facing_direction = "up" if dy > 0 else "down"
        
        return new_x, new_y, facing_direction, is_moving
    
    @staticmethod
    def update_sprite_texture(sprite: arcade.Sprite, facing_direction: str):
        """Atualiza textura do sprite baseado na direção - COM FALLBACK ROBUSTO"""
        if not sprite:
            return
        
        # 🔥 VERIFICA SE TEM SISTEMA DE TEXTURAS
        if not hasattr(sprite, 'textures'):
            print("❌ Sprite não tem sistema de texturas")
            # Tenta criar texturas básicas
            sprite.textures = {
                "up": sprite.texture,
                "down": sprite.texture, 
                "left": sprite.texture,
                "right": sprite.texture
            }
            return
        
        # 🔥 TENTA USAR A TEXTURA DA DIREÇÃO ESPECIFICADA
        if facing_direction in sprite.textures:
            sprite.texture = sprite.textures[facing_direction]
        else:
            # 🔥 FALLBACK INTELIGENTE - Tenta outras direções
            fallback_attempts = ["down", "up", "left", "right"]
            for fallback_dir in fallback_attempts:
                if fallback_dir in sprite.textures:
                    sprite.texture = sprite.textures[fallback_dir]
                    return
    
    @staticmethod
    def validate_character_data(character_data: Dict) -> Dict:
        """VALIDA e CORRIGE dados do personagem - FORÇA ANIMAÇÕES CORRETAS"""
        validated_data = character_data.copy() if character_data else {}
        
        print("🔧 Validando personagem...")
        
        # Garante nome
        validated_data["name"] = "Emily"
        
        # 🔥 CORREÇÃO CRÍTICA: Verifica e corrige animações quebradas
        current_animations = validated_data.get("animations", {})
        
        if CharacterMovement._has_broken_animations(current_animations):
            print("🚨 CORRIGINDO: Animações quebradas detectadas, usando padrões!")
            validated_data["animations"] = CharacterMovement.DEFAULT_ANIMATIONS.copy()
        else:
            validated_data["animations"] = CharacterMovement._ensure_complete_and_valid_animations(current_animations)
        
        # Garante posição
        if "position" not in validated_data:
            validated_data["position"] = CharacterMovement.DEFAULT_POSITION.copy()
        
        print("✅ Personagem validado e corrigido")
        return validated_data

    @staticmethod
    def create_default_character() -> Dict:
        """Cria personagem padrão com animações CORRETAS"""
        return {
            "name": "Emily",
            "animations": CharacterMovement.DEFAULT_ANIMATIONS.copy(),
            "position": CharacterMovement.DEFAULT_POSITION.copy()
        }

    @staticmethod
    def force_correct_animations_for_all_users():
        """CORREÇÃO GLOBAL: Força animações corretas para TODOS os usuários"""
        print("🔥 APLICANDO CORREÇÃO GLOBAL PARA TODOS OS USUÁRIOS...")
        
        try:
            from auth.simple_auth import auth_system
            
            for username in list(auth_system.users.keys()):
                user_data = auth_system.users[username]
                
                if "character" in user_data:
                    # Aplica correção
                    user_data["character"] = CharacterMovement.validate_character_data(user_data["character"])
                    print(f"   ✅ {username}: Animações corrigidas")
                else:
                    # Cria personagem padrão
                    user_data["character"] = CharacterMovement.create_default_character()
                    print(f"   ✅ {username}: Personagem criado")
            
            # Salva as correções
            auth_system.save_users()
            print("💾 Correções salvas permanentemente!")
            
        except Exception as e:
            print(f"❌ Erro na correção global: {e}")

    @staticmethod
    def debug_character_data(character_data: Dict, username: str):
        """DEBUG: Mostra informações detalhadas do personagem"""
        print(f"\n🔍 DEBUG Personagem - {username}:")
        print(f"   Nome: {character_data.get('name', 'N/A')}")
        print(f"   Posição: {character_data.get('position', {})}")
        
        animations = character_data.get("animations", {})
        print(f"   Animações ({len(animations)}):")
        for direction in ["up", "down", "left", "right"]:
            path = animations.get(direction, "N/A")
            exists = CharacterMovement._validate_image_path(path) if path != "N/A" else False
            status = "✅" if exists else "❌"
            print(f"     {direction}: {status} {path}")
        
        # Verifica se está quebrado
        if CharacterMovement._has_broken_animations(animations):
            print("   🚨 STATUS: ANIMAÇÕES QUEBRADAS!")
        else:
            print("   ✅ STATUS: Animações OK")
        
        print("--- FIM DEBUG ---\n")