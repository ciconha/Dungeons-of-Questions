# verificacao.py

import importlib.util
import sys
import subprocess
import os

def verificar_versao_python():
    """Verifica se a versão do Python é compatível"""
    print("🐍 Verificando versão do Python...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, "Python 3.8 ou superior necessário"
    return True, "✅ Versão compatível"

def verificar_pip():
    """Verifica se o pip está disponível"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "✅ Pip disponível"
    except:
        return False, "❌ Pip não encontrado"

def verificar_pacote(nome_import, nome_pacote):
    """Verifica se um pacote específico está instalado"""
    try:
        spec = importlib.util.find_spec(nome_import)
        if spec is None:
            return False, f"❌ {nome_pacote}"
        
        try:
            modulo = importlib.import_module(nome_import)
            versao = getattr(modulo, '__version__', '?')
            return True, f"✅ {nome_pacote} (v{versao})"
        except:
            return True, f"✅ {nome_pacote}"
            
    except ImportError:
        return False, f"❌ {nome_pacote}"
    except Exception as e:
        return False, f"❌ {nome_pacote} - Erro: {e}"

def verificar_arquivos_necessarios():
    """Verifica se os arquivos essenciais do projeto existem"""
    arquivos_necessarios = [
        "main.py",
        "auth/simple_auth.py",
        "views/menu_view.py", 
        "views/quiz_view.py",
        "views/shop_view.py",
        "assets/characters/Emillywhite_front.png"
    ]
    
    print("\n📁 Verificando arquivos do projeto...")
    faltantes = []
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo}")
            faltantes.append(arquivo)
    
    return len(faltantes) == 0, faltantes

def main():
    """Função principal de verificação"""
    print("🎮 VERIFICADOR DE INSTALAÇÃO - RPG QUIZ GAME")
    print("=" * 60)
    
    # Lista de dependências
    DEPENDENCIAS = {
        "altgraph": "altgraph",
        "annotated_types": "annotated-types", 
        "anyio": "anyio",
        "arcade": "arcade",
        "attrs": "attrs",
        "certifi": "certifi",
        "cffi": "cffi",
        "charset_normalizer": "charset-normalizer",
        "click": "click",
        "dns": "dnspython",
        "fastapi": "fastapi",
        "h11": "h11",
        "httptools": "httptools",
        "idna": "idna",
        "packaging": "packaging",
        "PIL": "pillow",
        "pycparser": "pycparser",
        "pydantic": "pydantic",
        "pydantic_core": "pydantic_core",
        "pyglet": "pyglet",
        "PyInstaller": "pyinstaller",
        "pyinstaller_hooks_contrib": "pyinstaller-hooks-contrib",
        "pymongo": "pymongo",
        "pymunk": "pymunk",
        "pyperclip": "pyperclip",
        "dotenv": "python-dotenv",
        "pytiled_parser": "pytiled_parser",
        "yaml": "PyYAML",
        "requests": "requests",
        "setuptools": "setuptools",
        "sniffio": "sniffio",
        "starlette": "starlette",
        "typing_inspection": "typing-inspection",
        "typing_extensions": "typing_extensions",
        "urllib3": "urllib3",
        "uvicorn": "uvicorn",
        "uvloop": "uvloop",
        "watchfiles": "watchfiles",
        "websockets": "websockets"
    }
    
    # Verifica Python
    python_ok, python_msg = verificar_versao_python()
    print(python_msg)
    
    # Verifica pip
    pip_ok, pip_msg = verificar_pip()
    print(pip_msg)
    
    print("\n📦 Verificando pacotes...")
    print("-" * 50)
    
    pacotes_ok = []
    pacotes_faltantes = []
    
    for nome_import, nome_pacote in DEPENDENCIAS.items():
        ok, mensagem = verificar_pacote(nome_import, nome_pacote)
        print(f"   {mensagem}")
        
        if ok:
            pacotes_ok.append(nome_pacote)
        else:
            pacotes_faltantes.append(nome_pacote)
    
    # Verifica arquivos
    arquivos_ok, arquivos_faltantes = verificar_arquivos_necessarios()
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL:")
    print(f"✅ Pacotes instalados: {len(pacotes_ok)}/{len(DEPENDENCIAS)}")
    print(f"❌ Pacotes faltantes: {len(pacotes_faltantes)}")
    
    if pacotes_faltantes:
        print("\n📋 PACOTES FALTANTES:")
        for pacote in pacotes_faltantes:
            print(f"   • {pacote}")
    
    if arquivos_faltantes:
        print("\n📁 ARQUIVOS FALTANTES:")
        for arquivo in arquivos_faltantes:
            print(f"   • {arquivo}")
    
    # Status geral
    tudo_ok = python_ok and pip_ok and (len(pacotes_faltantes) == 0) and arquivos_ok
    
    if tudo_ok:
        print("\n🎉 TUDO OK! O jogo está pronto para executar!")
        print("🚀 Execute: python main.py")
    else:
        print(f"\n⚠️  Problemas encontrados: {len(pacotes_faltantes)} pacotes faltantes")
        print("\n💡 SOLUÇÕES:")
        print("• Execute: python instalador.py para instalar tudo automaticamente")
        print("• Ou instale manualmente: pip install NOME_DO_PACOTE")
        
        if not python_ok:
            print("• Instale Python 3.8+: https://www.python.org/downloads/")
        
        if not pip_ok:
            print("• Reinstale o Python para corrigir o pip")
    
    # Pausa no Windows
    if os.name == 'nt':
        input("\nPressione Enter para sair...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Verificação cancelada")
    except Exception as e:
        print(f"\n❌ Erro: {e}")