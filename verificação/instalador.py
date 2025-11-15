# instalador.py

import subprocess
import sys
import os

def verificar_python():
    """Verifica a versão do Python"""
    print("🐍 Verificando Python...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ necessário!")
        return False
    print("✅ Python compatível")
    return True

def instalar_pacote(pacote):
    """Instala um pacote específico"""
    try:
        print(f"📦 Instalando {pacote}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pacote],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {pacote} instalado")
            return True
        else:
            print(f"❌ Falha: {pacote}")
            print(f"   Erro: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout: {pacote}")
        return False
    except Exception as e:
        print(f"❌ Erro: {pacote} - {e}")
        return False

def atualizar_pip():
    """Tenta atualizar o pip"""
    print("🔄 Tentando atualizar pip...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            timeout=120
        )
        print("✅ Pip atualizado")
        return True
    except:
        print("⚠️  Não foi possível atualizar o pip")
        return True  # Continua mesmo se falhar

def main():
    """Função principal do instalador"""
    print("🎮 INSTALADOR AUTOMÁTICO - RPG QUIZ GAME")
    print("=" * 50)
    
    if not verificar_python():
        print("❌ Instalação cancelada")
        return
    
    # Lista completa de dependências
    DEPENDENCIAS = [
        "altgraph==0.17.4",
        "annotated-types==0.7.0",
        "anyio==4.10.0",
        "arcade==3.3.3",
        "attrs==25.3.0",
        "certifi==2025.8.3",
        "cffi==1.17.1",
        "charset-normalizer==3.4.3",
        "click==8.2.1",
        "dnspython==2.8.0",
        "fastapi==0.116.1",
        "h11==0.16.0",
        "httptools==0.6.4",
        "idna==3.10",
        "packaging==25.0",
        "pillow==11.3.0",
        "pycparser==2.22",
        "pydantic==2.11.7",
        "pydantic_core==2.33.2",
        "pyglet==2.1.8",
        "pyinstaller==6.16.0",
        "pyinstaller-hooks-contrib==2025.9",
        "pymongo==4.15.3",
        "pymunk==6.9.0",
        "pyperclip==1.11.0",
        "python-dotenv==1.1.1",
        "pytiled_parser==2.2.9",
        "PyYAML==6.0.2",
        "requests==2.32.5",
        "setuptools==80.9.0",
        "sniffio==1.3.1",
        "starlette==0.47.3",
        "typing-inspection==0.4.1",
        "typing_extensions==4.15.0",
        "urllib3==2.5.0",
        "uvicorn==0.35.0",
        "uvloop==0.21.0",
        "watchfiles==1.1.0",
        "websockets==15.0.1"
    ]
    
    # Confirmação do usuário
    print(f"\n📋 Serão instalados {len(DEPENDENCIAS)} pacotes")
    resposta = input("🤔 Continuar? (s/N): ").strip().lower()
    
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("❌ Instalação cancelada")
        return
    
    # Atualiza pip primeiro
    atualizar_pip()
    
    print(f"\n🚀 Instalando {len(DEPENDENCIAS)} pacotes...")
    print("-" * 50)
    
    sucessos = 0
    falhas = 0
    falhas_lista = []
    
    # Instala cada pacote
    for i, pacote in enumerate(DEPENDENCIAS, 1):
        print(f"\n[{i}/{len(DEPENDENCIAS)}] ", end="")
        if instalar_pacote(pacote):
            sucessos += 1
        else:
            falhas += 1
            falhas_lista.append(pacote)
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO DA INSTALAÇÃO:")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {falhas}")
    
    if falhas == 0:
        print("\n🎉 TODOS OS PACOTES FORAM INSTALADOS!")
        print("✨ O jogo está pronto para usar!")
        print("🚀 Execute: python main.py")
    else:
        print(f"\n⚠️  {falhas} pacotes falharam:")
        for falha in falhas_lista:
            print(f"   • {falha}")
        
        print("\n💡 Tente instalar manualmente:")
        for falha in falhas_lista:
            print(f"   pip install {falha}")
    
    # Cria requirements.txt
    print("\n📄 Criando arquivo requirements.txt...")
    try:
        with open("requirements.txt", "w") as f:
            for pacote in DEPENDENCIAS:
                f.write(pacote + "\n")
        print("✅ requirements.txt criado!")
    except Exception as e:
        print(f"❌ Erro ao criar requirements.txt: {e}")
    
    # Verificação final
    print("\n🔍 Verificando instalação...")
    try:
        # Tenta importar arcade para testar
        import arcade
        print("✅ Arcade funcionando corretamente!")
    except ImportError as e:
        print(f"❌ Problema com arcade: {e}")
    except Exception as e:
        print(f"⚠️  Aviso: {e}")
    
    # Pausa no Windows
    if os.name == 'nt':
        input("\nPressione Enter para sair...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Instalação interrompida pelo usuário")
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO: {e}")
        if os.name == 'nt':
            input("Pressione Enter para sair...")