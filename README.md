# 🎮 Dungeons of Questions - RPG Educativo

<div align="center">

![Dungeons of Questions](https://img.shields.io/badge/🎮-Dungeons_of_Questions-purple?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Arcade](https://img.shields.io/badge/Arcade_Engine-FF6B6B?style=for-the-badge)

**Uma jornada épica através do conhecimento! Explore masmorras, resolva desafios e aprenda conceitos de Ciência da Computação em um RPG imersivo.**

[![Demo](https://img.shields.io/badge/🎬-Ver_Demo-orange?style=for-the-badge)](https://github.com/ciconha/Dungeons-of-Questions#-demonstração)
[![Instalação](https://img.shields.io/badge/⚡-Começar_Jogando-green?style=for-the-badge)](https://github.com/ciconha/Dungeons-of-Questions#-instalação-rápida)

</div>

## 🚀 Sobre o Projeto

### 🎯 Objetivo Principal
Proporcionar uma experiência interativa de aprendizado dos conceitos e funcionamento de uma **Máquina de Turing**. O jogador avança por fases temáticas, respondendo perguntas de dificuldade crescente e acompanhando uma história em estilo RPG.

### ✨ Destaques
- 🏰 **Mundo Aberto**: Explore masmorras temáticas
- 🧠 **Aprendizado Progressivo**: Conceitos de computação de forma gradual
- 🎪 **Sistema de XP**: Evolua seu personagem com conhecimento
- 👥 **Perfil Personalizado**: Acompanhe seu progresso
- 🎨 **Pixel Art**: Visual retro encantador

## 🛠️ Stack Tecnológica

<div align="center">

| Camada | Tecnologia | Descrição |
|--------|------------|-----------|
| 🎮 **Game Engine** | `Python Arcade` | Motor gráfico para jogos 2D |
| 🌐 **Backend** | `FastAPI` | API REST para gerenciamento |
| 🐍 **Linguagem** | `Python 3.13` | Linguagem principal |
| 🗺️ **Mapas** | `Tiled TMX` | Editor de mapas profissional |
| 🎨 **Assets** | `Pixel Art` | Sprites e tilesets customizados |

</div>

## 🏗️ Arquitetura do Projeto

```bash
Dungeons-of-Questions/
├── 🎮 game/                          # Cliente do Jogo
│   ├── 🗺️ assets/                    # Recursos visuais
│   │   ├── characters/              # Sprites dos personagens
│   │   ├── maps/                   # Mapas e tilesets
│   │   ├── ui/                     # Interface do usuário
│   │   └── background/             # Cenários e fundos
│   ├── 👁️ views/                    # Telas e interfaces
│   │   ├── game_view.py           # Tela principal do jogo
│   │   ├── menu_view.py           # Menu inicial
│   │   ├── profile_view.py        # Perfil do jogador
│   │   └── rpg_button.py          # Componentes de UI
│   ├── ⚡ xp/                      # Sistema de progressão

```markdown
# 🎮 Dungeons of Questions - RPG Educativo

<div align="center">

![Dungeons of Questions](https://img.shields.io/badge/🎮-Dungeons_of_Questions-purple?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Arcade](https://img.shields.io/badge/Arcade_Engine-FF6B6B?style=for-the-badge)

**Uma jornada épica através do conhecimento! Explore masmorras, resolva desafios e aprenda conceitos de Ciência da Computação em um RPG imersivo.**

[![Demo](https://img.shields.io/badge/🎬-Ver_Demo-orange?style=for-the-badge)](https://github.com/ciconha/Dungeons-of-Questions#-demonstração)
[![Instalação](https://img.shields.io/badge/⚡-Começar_Jogando-green?style=for-the-badge)](https://github.com/ciconha/Dungeons-of-Questions#-instalação-rápida)

</div>

## 🚀 Sobre o Projeto

### 🎯 Objetivo Principal
Proporcionar uma experiência interativa de aprendizado dos conceitos e funcionamento de uma **Máquina de Turing**. O jogador avança por fases temáticas, respondendo perguntas de dificuldade crescente e acompanhando uma história em estilo RPG.

### ✨ Destaques
- 🏰 **Mundo Aberto**: Explore masmorras temáticas
- 🧠 **Aprendizado Progressivo**: Conceitos de computação de forma gradual
- 🎪 **Sistema de XP**: Evolua seu personagem com conhecimento
- 👥 **Perfil Personalizado**: Acompanhe seu progresso
- 🎨 **Pixel Art**: Visual retro encantador

## 🛠️ Stack Tecnológica

<div align="center">

| Camada | Tecnologia | Descrição |
|--------|------------|-----------|
| 🎮 **Game Engine** | `Python Arcade` | Motor gráfico para jogos 2D |
| 🌐 **Backend** | `FastAPI` | API REST para gerenciamento |
| 🐍 **Linguagem** | `Python 3.13` | Linguagem principal |
| 🗺️ **Mapas** | `Tiled TMX` | Editor de mapas profissional |
| 🎨 **Assets** | `Pixel Art` | Sprites e tilesets customizados |

</div>

## 🏗️ Arquitetura do Projeto

```bash
Dungeons-of-Questions/
├── 🎮 game/                          # Cliente do Jogo
│   ├── 🗺️ assets/                    # Recursos visuais
│   │   ├── characters/              # Sprites dos personagens
│   │   ├── maps/                   # Mapas e tilesets
│   │   ├── ui/                     # Interface do usuário
│   │   └── background/             # Cenários e fundos
│   ├── 👁️ views/                    # Telas e interfaces
│   │   ├── game_view.py           # Tela principal do jogo
│   │   ├── menu_view.py           # Menu inicial
│   │   ├── profile_view.py        # Perfil do jogador
│   │   └── rpg_button.py          # Componentes de UI
│   ├── ⚡ xp/                      # Sistema de progressão
│   │   └── xp.py                  # Gerenciador de XP
│   ├── 🔧 config.py               # Configurações globais
│   └── 🚀 main.py                 # Ponto de entrada
├── 🌐 api/                         # Servidor Backend
│   ├── models/                    # Modelos de dados
│   ├── routers/                  # Rotas da API
│   ├── services/                 # Lógica de negócio
│   └── utils/                    # Utilitários
└── 📋 requirements.txt           # Dependências
```

## 🎥 Demonstração

<div align="center">

### 🏠 Menu Principal
| | |
|:-------------------------:|:-------------------------:|
| **Tela de Login** | **Menu Inicial** |
| ![Login](https://via.placeholder.com/400x250/4A90E2/FFFFFF?text=Login+Screen) | ![Menu](https://via.placeholder.com/400x250/9013FE/FFFFFF?text=Main+Menu) |

### 🎮 Gameplay
| | |
|:-------------------------:|:-------------------------:|
| **Exploração** | **Quiz** |
| ![Gameplay](https://via.placeholder.com/400x250/50E3C2/FFFFFF?text=Gameplay) | ![Quiz](https://via.placeholder.com/400x250/B8E986/FFFFFF?text=Quiz+System) |

### 👤 Perfil & Progresso
| | |
|:-------------------------:|:-------------------------:|
| **Perfil do Jogador** | **Sistema de XP** |
| ![Profile](https://via.placeholder.com/400x250/F5A623/FFFFFF?text=Player+Profile) | ![XP System](https://via.placeholder.com/400x250/7ED321/FFFFFF?text=XP+Progress) |

</div>

## ⚡ Instalação Rápida

### 🐧 Linux/macOS
```bash
# 1. Clone o repositório
git clone https://github.com/ciconha/Dungeons-of-Questions.git
cd Dungeons-of-Questions

# 2. Ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalação
pip install -r requirements.txt

# 4. Executar
python game/main.py
```

### 🪟 Windows
```powershell
# 1. Clone o repositório
git clone https://github.com/ciconha/Dungeons-of-Questions.git
cd Dungeons-of-Questions

# 2. Ambiente virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalação
pip install -r requirements.txt

# 4. Executar
python game/main.py
```

## 🎯 Funcionalidades

### 🏰 Sistema de Jogo
| Funcionalidade | Status | Descrição |
|----------------|--------|-----------|
| **Mundo Aberto** | ✅ | Explore masmorras em 2D |
| **Sistema de Quiz** | ✅ | Perguntas progressivas |
| **Progressão de XP** | ✅ | Evolua com conhecimento |
| **Perfil do Jogador** | ✅ | Acompanhe estatísticas |
| **Sistema de Fases** | ✅ | Desafios temáticos |

### 👤 Sistema de Usuário
| Módulo | Status | Características |
|--------|--------|-----------------|
| **Autenticação** | ✅ | Login seguro |
| **Progresso** | ✅ | Salvar/carregar |
| **Personalização** | 🔄 | Avatares customizados |
| **Ranking** | 🚧 | Sistema de líderes |

### 🎨 Interface
| Componente | Status | Detalhes |
|------------|--------|----------|
| **Menu Principal** | ✅ | Navegação intuitiva |
| **HUD In-Game** | ✅ | Informações em tempo real |
| **Perfil RPG** | ✅ | Estilo medieval |
| **Animações** | 🔄 | Transições suaves |

## 🕹️ Como Jogar

### 🎮 Controles
| Ação | Tecla | Descrição |
|------|-------|-----------|
| **Movimento** | `WASD` | Navegação pelo mapa |
| **Interagir** | `ENTER` | Iniciar desafios |
| **Menu** | `ESC` | Voltar/Configurações |
| **Perfil** | `P` | Acessar perfil |

### 📚 Progressão
1. **🎯 Explore** o mapa e encontre pontos de desafio
2. **🧠 Resolva** questões sobre Máquinas de Turing
3. **⭐ Ganhe XP** por respostas corretas
4. **📈 Evolua** seu personagem e desbloqueie novas áreas
5. **🏆 Complete** todas as fases para dominar o conhecimento!

## 👥 Equipe de Desenvolvimento

<div align="center">

| Desenvolvedor(a) | Função | GitHub | Contribuições |
|------------------|--------|--------|---------------|
| **Guilherme Ribeiro** | Backend & Game Logic | [@GuiGui1006](https://github.com/GuiGui1006) | API, Sistemas de Jogo |
| **Mariana Freire** | Frontend & Design | [@MarianaswFreire](https://github.com/MarianaswFreire) | UI/UX, Assets Visuais |
| **Miller Ciconi** | Full Stack | [@ciconha](https://github.com/ciconha) | Arquitetura, Integração |

</div>

## 🌟 Roadmap

### ✅ Concluído
- [x] Engine básica do jogo
- [x] Sistema de autenticação
- [x] Mapa inicial e movimentação
- [x] Interface do perfil RPG
- [x] Sistema de XP e progressão

### 🚧 Em Desenvolvimento
- [ ] Sistema completo de quiz
- [ ] Mais fases e conteúdos
- [ ] Multiplayer cooperativo
- [ ] Sistema de conquistas

### 📋 Planejado
- [ ] Versão mobile
- [ ] Modo história expandido
- [ ] Editor de níveis
- [ ] Integração com LMS

## 🤝 Contribuindo

Quer ajudar a melhorar o Dungeons of Questions? 

1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. Abra um **Pull Request**

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🐛 Reportar Bugs

Encontrou um problema? [Abra uma issue](https://github.com/ciconha/Dungeons-of-Questions/issues) e nos ajude a melhorar!

---

<div align="center">

### 🎊 "O conhecimento é a masmorra final - explore-a com coragem!"

**⭐ Não esqueça de dar uma estrela no repositório se você gostou do projeto!**

[![GitHub stars](https://img.shields.io/github/stars/ciconha/Dungeons-of-Questions?style=social)](https://github.com/ciconha/Dungeons-of-Questions/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/ciconha/Dungeons-of-Questions?style=social)](https://github.com/ciconha/Dungeons-of-Questions/network/members)

</div>
```

## 🎨 Para as imagens interativas:

Quando você tiver screenshots reais do jogo, substitua os placeholders por:

```markdown
![Tela de Login](docs/screenshots/login.png)
![Menu Principal](docs/screenshots/menu.png) 
![Gameplay](docs/screenshots/gameplay.png)
```

## ✨ Recursos Incluídos:

- **🎯 Badges interativas** no topo
- **📊 Tabelas organizadas** para stack tecnológica
- **🎮 Sistema de demonstração** com placeholders para imagens
- **⚡ Guias de instalação** para todos os sistemas
- **📈 Roadmap visual** do projeto
- **👥 Equipe** com links e contribuições
- **🎨 Design responsivo** e colorido

Este README vai fazer seu projeto se destacar muito! 🚀
│   │   └── xp.py                  # Gerenciador de XP
│   ├── 🔧 config.py               # Configurações globais
│   └── 🚀 main.py                 # Ponto de entrada
├── 🌐 api/                         # Servidor Backend
│   ├── models/                    # Modelos de dados
│   ├── routers/                  # Rotas da API
│   ├── services/                 # Lógica de negócio
│   └── utils/                    # Utilitários
└── 📋 requirements.txt           # Dependências