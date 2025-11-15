


# Dungeons of Questions - RPG Educativo

<div align="center">

![Dungeons of Questions](https://img.shields.io/badge/🎮-Dungeons_of_Questions-purple?style=for-the-badge&logo=game-controller)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Arcade](https://img.shields.io/badge/Arcade_Engine-FF6B6B?style=for-the-badge&logo=arcade)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)

---

### [link do video](https://acadcruzeirodosul-my.sharepoint.com/:v:/g/personal/eduardo_ciconha_cs_brazcubas_edu_br/EVbVybnhDjdLrIjWltZ0AzgBNc-d_fRXg_lCE238KxePdA?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=WfKeWk)

---

<table>
  <tr>
    <td style="vertical-align: top; padding: 10px;">
      <details>
        <summary><strong>relatorio_pedagógico.md</strong></summary>
         <p>
            <br>
              📘 Relatório Pedagógico do Plugin Gamificado

## 1. Identificação do Plugin
- **Nome do jogo:** Dungeons of Questions  
- **Plugin:** Arcade  

### Área da disciplina
O jogo se encaixa nas áreas de **Fundamentos de Computação, Análise de Algoritmos e Modelos Computacionais**.  
Ele não só aborda conceitos básicos de computabilidade, complexidade e lógica de algoritmos, mas também transforma esses conteúdos em desafios práticos dentro do jogo.  
Assim, o aluno consegue **experimentar a teoria de forma interativa**, vendo como ideias como máquinas de Turing, problemas decidíveis e análise de desempenho aparecem em situações de jogo e ajudam a avançar de fase.

### Grupo
- **Grupo 2**  
- **Integrantes:**  
- Eduardo Ciconha | RGM: 33352844  
- Guilherme Ribeiro | RGM: 3860858  
- Mariana de Sousa | RGM: 34030701  

---

## 2. Objetivo Pedagógico
O jogo ajuda o aluno a praticar conceitos de **computação teórica** como:
- Máquinas de Turing  
- Problemas decidíveis e indecidíveis  
- Notação assintótica  
- P vs NP  

Ao jogar, o aluno aprende de forma prática, respondendo perguntas e usando itens que dão dicas, o que reforça o conteúdo da disciplina.

---

## 3. Descrição do Jogo
- O jogador entra em uma fase com perguntas de múltipla escolha.  
- Ele tem **vidas e mana**: errar tira vidas, usar habilidades consome mana.  
- Acertar dá **XP e moedas**, que podem ser usadas para comprar itens na loja.  
- Se acertar pelo menos **3 perguntas**, passa de fase.  
- O feedback vem em forma de mensagens na tela (acerto, erro, dicas, exemplos ilustrativos) e no resultado final (XP, moedas, aprovação ou reprovação da fase).  

---

## 4. Conteúdo Relacionado à Disciplina
Os tópicos do plano de ensino que aparecem no jogo são:
- **Máquinas de Turing** (explicação e exemplos)  
- **Problema da Parada** (decidível)  
- **Classes P e NP** (diferença entre resolver e verificar)  
- **Notação Big-O** (complexidade de algoritmos)  

O jogo ajuda porque cada pergunta vem com um **exemplo ilustrativo** que conecta a teoria com situações práticas, facilitando a compreensão.

---

## 5. Critérios de Pontuação
- Cada resposta correta dá **10 XP** (ou **20 XP** quando ativa o exemplo e acerta).  
- Passa de fase se tiver **3 acertos ou mais**.  
- Ganha **moedas extras** ao completar a fase.  

### Penalidades
- Errar tira vidas.  
- Usar habilidades consome mana.  
- Se perder todas as vidas, a fase é reprovada.  

---

## 6. Testes Realizados
Casos de teste planejados:
- Jogador acerta todas as perguntas → deve ganhar XP máximo e moedas.  
- Jogador erra todas → perde todas as vidas e reprova a fase.  
- Jogador usa habilidades sem mana → deve aparecer mensagem de erro.  
- Jogador repete a fase com o mesmo seed → perguntas devem ser consistentes.  
- Jogador acerta 3 → passa de fase.  

---

## 7. Roteiro de Demonstração
- **Cenário feliz:** mostrar o jogo rodando, o aluno respondendo corretamente, usando uma habilidade (exemplo aparece), passando de fase e recebendo XP e moedas.  
- **Cenário de erro:** mostrar o aluno errando várias vezes, perdendo vidas, usando habilidade sem mana (mensagem de erro aparece), e no final reprovando a fase.  

  </p>
      </details>
    </td>
</table>


</div>

## 🚀 Sobre o Projeto

### Objetivo Principal
Proporcionar uma experiência interativa de aprendizado dos conceitos e funcionamento de uma **Máquina de Turing** através de um RPG educativo imersivo. O jogador avança por fases temáticas, respondendo perguntas de dificuldade crescente enquanto acompanha uma história cativante.

### ✨ Destaques Exclusivos
- 🏰 **Mundo RPG Imersivo**: Explore masmorras temáticas em 2D
- 🧠 **Aprendizado Progressivo**: Conceitos de computação de forma gradual e divertida
- 🎪 **Sistema de XP Avançado**: Evolua seu personagem com conhecimento
- 👥 **Perfil Personalizado RPG**: Interface estilo medieval
- 💾 **Sistema de Salvamento**: MongoDB + Autenticação 

## 🛠️ Stack Tecnológica Completa

<div align="center">

| Camada | Tecnologia | Versão | Descrição |
|--------|------------|---------|-----------|
| 🎮 **Game Engine** | `Python Arcade` | 2.6.17+ | Motor gráfico para jogos 2D |
| 🌐 **Backend API** | `FastAPI` | 0.104+ | API REST moderna e rápida |
| 🗄️ **Banco de Dados** | `MongoDB` | 5.0+ | Banco NoSQL escalável |
| 🐍 **Linguagem** | `Python` | 3.8+ | Linguagem principal |
| 🗺️ **Mapas** | `Tiled TMX` | 1.8+ | Editor de mapas profissional |
| 🎨 **Assets** | `Pixel Art` | Custom | Sprites e tilesets exclusivos |
| 🔐 **Autenticação** | `JWT` | Custom | Sistema seguro de login |

</div>

## 🏗️ Arquitetura do Projeto

```
Dungeons-of-Questions/
├── 🎮 game/                          # Cliente Principal do Jogo
│   ├── 🗺️ assets/                    # Recursos Visuais
│   │   ├── characters/              # Sprites dos Personagens
│   │   │   ├── Emillywhite_front.png
│   │   │   ├── Emillywhite_back.png
│   │   │   ├── Emillywhite_left.png
│   │   │   └── Emillywhite_right.png
│   │   ├── maps/                    # Sistema de Mapas
│   │   │   ├── tilesets/
│   │   │   │   └── tilemap_packed.png
│   │   │   ├── map.tmx
│   │   │   └── temp_map.tmx
│   │   ├── ui/                      # Interface do Usuário
│   │   │   ├── buttons/
│   │   │   ├── icons/
│   │   │   └── backgrounds/
│   │   └── avatars/                 # Avatares do Sistema
│   ├── 👁️ views/                    # Sistema de Telas
│   │   ├── game_view.py            # Tela Principal do Jogo
│   │   ├── menu_view.py            # Menu Inicial
│   │   ├── login_view.py           # Autenticação
│   │   ├── profile_view.py         # Perfil do Jogador
│   │   ├── quiz_view.py            # Sistema de Quiz
│   │   ├── multiplayer_view.py     # Multiplayer com Discord
│   │   └── rpg_button.py           # Componentes de UI RPG
│   ├── ⚡ xp/                       # Sistema de Progressão
│   │   └── xp.py                   # Gerenciador de XP
│   ├── 🔐 auth/                     # Sistema de Autenticação
│   │   ├── simple_auth.py          # Gerenciador de Auth
│   │   └── user_manager.py         # Gerenciador de Usuários
│   ├── 🔧 config.py                # Configurações Globais
│   └── 🚀 main.py                  # Ponto de Entrada
├── 🌐 api/                          # Servidor Backend
│   ├── models/                     # Modelos de Dados
│   │   ├── user_model.py          # Modelo de Usuário
│   │   └── game_model.py          # Modelo de Jogo
│   ├── routers/                   # Rotas da API
│   │   ├── users.py               # Rotas de Usuários
│   │   ├── game.py                # Rotas do Jogo
│   │   └── multiplayer.py         # Rotas Multiplayer
│   ├── services/                  # Lógica de Negócio
│   │   ├── auth_service.py        # Serviço de Autenticação
│   │   └── game_service.py        # Serviço do Jogo
│   ├── utils/                     # Utilitários
│   │   ├── database.py            # Conexão MongoDB
│   │   └── security.py            # Segurança JWT
│   └── 🚀 main.py                 # Servidor FastAPI
├── 📁 docs/                        # Documentação
│   ├── screenshots/               # Capturas de Tela
│   ├── api/                       # Documentação da API
│   └── setup/                     # Guias de Instalação
├── 📋 requirements.txt            # Dependências Python
└── 📄 README.md                   # Este Arquivo
```

## ⚡ Instalação Rápida - Todos os Sistemas

### 🐧 Linux (Ubuntu/Debian)
```bash
# 1. Clone o repositório
git clone https://github.com/ciconha/Dungeons-of-Questions.git
cd Dungeons-of-Questions

# 2. Instale as dependências do sistema
sudo apt update && sudo apt install python3-pip python3-venv -y

# 3. Ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instale dependências Python
pip install --upgrade pip
pip install -r requirements.txt

# 5. Execute o jogo
python main.py
```

### 🪟 Windows 10/11
```powershell
# 1. Clone o repositório
git clone https://github.com/ciconha/Dungeons-of-Questions.git
cd Dungeons-of-Questions

# 2. Ambiente virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalação das dependências
pip install --upgrade pip
pip install -r requirements.txt

# 4. Executar o jogo
python main.py
```

### 🍎 macOS
```bash
# 1. Clone o repositório
git clone https://github.com/ciconha/Dungeons-of-Questions.git
cd Dungeons-of-Questions

# 2. Instale Python se necessário
brew install python

# 3. Ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalação
pip install --upgrade pip
pip install -r requirements.txt

# 5. Executar
python main.py
```

## 🎯 Funcionalidades Detalhadas

### 🏰 Sistema Principal de Jogo
| Funcionalidade | Status | Descrição |
|----------------|--------|-----------|
| **Mundo Aberto 2D** | ✅ | Exploração livre em mapa TMX |
| **Sistema de Quiz** | ✅ | 6 fases progressivas sobre Turing | 
| **Progressão de XP** | ✅ | Sistema infinito de levels | 
| **Perfil RPG** | ✅ | Interface medieval personalizável | 
| **Sistema de Fases** | ✅ | Desafios temáticos progressivos  |

### 👤 Sistema Avançado de Usuário
| Módulo | Status | Características | Tecnologia |
|--------|--------|-----------------|------------|
| **Autenticação Segura** | ✅ | JWT + MongoDB | `PyJWT` + `Motor` |
| **Progresso em Nuvem** | ✅ | Salvamento automático | `MongoDB` |
| **Personalização** | ✅ | Avatares e estatísticas | `Arcade Sprites` |
| **Multiplayer** | ✅ | Integração Discord | `Discord API` |
| **Backup** | ✅ | Fallback local/cloud | `JSON` + `MongoDB` |

### 🎨 Sistema de Interface
| Componente | Status | Detalhes |
|------------|--------|----------|
| **Menu Principal** | ✅ | Navegação estilo RPG | 
| **HUD In-Game** | ✅ | Informações em tempo real |
| **Animações** | ✅ | Transições suaves | 

## 🕹️ Como Jogar - Guia Completo

### 🎮 Controles e Navegação
| Ação | Tecla | Descrição |
|------|-------|-----------|
| **Movimento** | `WASD` | Navegação fluída pelo mapa | 
| **Interagir** | `ENTER` | Iniciar desafios e quizzes | 
| **Menu** | `ESC` | Voltar/Configurações | 
| **Perfil** | `P` | Acessar perfil do jogador |
| **Multiplayer** | `M` | Acessar sistema multiplayer |
| **Tela Cheia** | `F11` | Alternar tela cheia |

### 📚 Sistema de Progressão
1. **🎯 Explore o Mapa**
   - Navegue pelas masmorras usando `WASD`
   - Encontre pontos de desafio marcados

2. **🧠 Resolva Desafios**
   - Pressione `ENTER` nos triggers
   - Responda questões sobre Máquinas de Turing
   - Dificuldade progressiva por fase

3. **⭐ Sistema de Recompensas**
   - +10 XP por resposta correta
   - Bônus por sequências corretas
   - Level Up a cada 100 XP

4. **📈 Evolução do Personagem**
   - Desbloqueie novas áreas
   - Acesse fases mais avançadas

## 👥 Equipe 

<div align="center">

### 🎮 Desenvolvedores 

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/ciconha">
        <img src="https://avatars.githubusercontent.com/u/131923066?v=4" width="80" height="80" style="border-radius: 50%; object-fit: cover;" />
        <br><br>
        <sub><b>Ciconha</b></sub>
      </a>
      <br />
      <sub>⛩️ Back-End & Infraestrutura</sub>
      <br />
      <img src="https://img.shields.io/badge/🔧-Arquitetura_Principal-orange?style=flat-square"/>
      <br />
      <img src="https://img.shields.io/badge/🎮-Game_Engine-blue?style=flat-square"/>
      <br />
      <img src="https://img.shields.io/badge/🌐-API_Integration-green?style=flat-square"/>
      <br />
      <img src="https://img.shields.io/badge/🗄️-Database_Architect-purple?style=flat-square"/>
      <br />
      <img src="https://img.shields.io/badge/🔐-Auth_System-red?style=flat-square"/>
    </td>
    <td align="center">
      <a href="https://github.com/GuiGui1006">
         <img src="https://avatars.githubusercontent.com/u/208025802?v=4" width="80" style="border-radius: 50%;" />
        <br />
        <sub><b>Guilherme Ribeiro</b></sub>
      </a>
      <br />
      <sub>⚡ architecture processes</sub>
      <br />
      <img src="https://img.shields.io/badge/%F0%9F%97%84%EF%B8%8F-An%C3%A1lise%20e%20modelagem-purple?style=flat-square"/>
      <br />
      <img src="https://img.shields.io/badge/%F0%9F%94%90-Otimização-red?style=flat-square"/>
      <br />
      <img src="https://img.shields.io/badge/🎪-Game_Logic-yellow?style=flat-square"/>
      <br />
      <img src="https://img.shields.io/badge/%E2%9C%A8-UI%20questions-pink?style=flat-square"/>
    </td>
    <td align="center">
      <a href="https://github.com/MarianaswFreire">
        <img src="https://avatars.githubusercontent.com/u/210853748?v=4" width="80" style="border-radius: 50%;" />
        <br />
        <sub><b>Mariana Freire</b></sub>
      </a>
      <br />
      <sub>🎨 UI/UX Designer</sub>
      <br />
      <img src="https://img.shields.io/badge/✨-UI_Design-pink?style=flat-square"/>
      <br />
      <img src="https://img.shields.io/badge/🎯-UX_Experience-lightblue?style=flat-square"/>
      <br />
      <img src="https://img.shields.io/badge/🖼️-Asset_Creation-green?style=flat-square"/>
    </td>
  </tr>
</table>

### 🤝 Contribuidores

[![Contributors](https://contrib.rocks/image?repo=ciconha/Dungeons-of-Questions)](https://github.com/ciconha/Dungeons-of-Questions/graphs/contributors)

</div>

## 🌟 Roadmap de Desenvolvimento

### ✅ Concluído (v1.0)
- [x] 🎮 Engine básica do jogo com Arcade
- [x] 🔐 Sistema de autenticação seguro
- [x] 🗺️ Mapa inicial e sistema de movimentação
- [x] 👤 Interface de perfil estilo RPG
- [x] ⭐ Sistema de XP e progressão
- [x] 🧠 Sistema de quiz com 6 fases
- [x] 🌐 Integração com MongoDB
- [x] 👥 Sistema multiplayer com Discord

### 🚧 Em Desenvolvimento (v1.1)
- [ ] 🎪 Mais fases e conteúdos educativos

### 📋 Planejado (v2.0)
- [ ] 📚 Editor de níveis integrado
- [ ] 🎮 Modo história expandido

## 🤝 Como Contribuir

Quer ajudar a melhorar o Dungeons of Questions? Seguimos estes passos:

### 🐛 Reportar Bugs
1. Vá para [Issues](https://github.com/ciconha/Dungeons-of-Questions/issues)
2. Clique em `New Issue`
3. Use o template de bug report
4. Inclua screenshots e steps para reproduzir

### 💡 Sugerir Features
1. Abra uma [Discussion](https://github.com/ciconha/Dungeons-of-Questions/discussions)
2. Descreva sua ideia detalhadamente
3. Inclui mockups se possível
4. Participe das votações

### 🔧 Contribuir com Código
```bash
# 1. Fork o projeto
# 2. Clone seu fork
git clone https://github.com/SEU_USER/Dungeons-of-Questions.git

# 3. Crie uma branch
git checkout -b feature/nova-feature-incrivel

# 4. Commit suas mudanças
git commit -m "feat: adiciona nova feature incrível"

# 5. Push para a branch
git push origin feature/nova-feature-incrivel

# 6. Abra um Pull Request
```

### 📝 Padrões de Commit
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração
- `test:` Testes

## 🐛 Troubleshooting Comum

### ❌ Erro: "ModuleNotFoundError: No module named 'arcade'"
**Solução:**
```bash
pip install arcade==2.6.17
# ou
python -m pip install --upgrade pip
```

### ❌ Erro: "MongoDB connection failed"
**Solução:**
1. Verifique se MongoDB está rodando
2. Confirme string de conexão no `.env`
3. Teste com: `mongosh --eval "db.runCommand({ping:1})"`

### ❌ Erro: "Discord API rate limit"
**Solução:**
- Aguarde 1-2 minutos
- Verifique token no `.env`
- Use `DISCORD_API_BASE` correto

### ❌ Erro: "TMX map not loading"
**Solução:**
```bash
# Reinstale dependências
pip uninstall pytmx
pip install pytmx

# Verifique paths no config.py
```

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para detalhes completos.

```
MIT License

Copyright (c) 2024 Dungeons of Questions Team

Permissão é concedida, gratuitamente, a qualquer pessoa que obtenha uma cópia
deste software e arquivos de documentação associados...
```

## 🆘 Suporte e Comunidade

<div align="center">

### 🌟 Ajude o Projeto

[![GitHub stars](https://img.shields.io/github/stars/ciconha/Dungeons-of-Questions?style=social)](https://github.com/ciconha/Dungeons-of-Questions/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/ciconha/Dungeons-of-Questions?style=social)](https://github.com/ciconha/Dungeons-of-Questions/network/members)
[![GitHub issues](https://img.shields.io/github/issues/ciconha/Dungeons-of-Questions?style=social)](https://github.com/ciconha/Dungeons-of-Questions/issues)

</div>

---

<div align="center">

### 🎊 "O conhecimento é a masmorra final - explore-a com coragem e curiosidade!"

**⭐ Se este projeto te ajudou ou divertiu, considere dar uma estrela no repositório!**

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=1000&color=27AE60&center=true&vCenter=true&width=435&lines=🎮+Aprenda+com+diversão;🧠+Domine+as+Máquinas+de+Turing;🏰+Explore+o+conhecimento;⭐+Torne-se+um+mestre!" alt="Typing SVG" />

**Desenvolvido com ❤️ pela comunidade Dungeons of Questions**

</div>


## Caso queira ver alguns Templates do JOGO

<table>
  <tr>
    <td style="vertical-align: top; padding: 10px;">
      <details>
        <summary><strong>Tela de Login</strong></summary>
        <img  src="https://github.com/user-attachments/assets/2a984ba1-a868-49ac-b940-6280c053245f" width="220">
      </details>
    </td>
    <td style="vertical-align: top; padding: 10px;">
      <details>
        <summary><strong>Tela de Cadastro</strong></summary>
        <img src="https://github.com/user-attachments/assets/a2c43a59-844d-4240-8f62-d980949b54d9" width="220">
      </details>
    </td>
        <td style="vertical-align: top; padding: 10px;">
      <details>
        <summary><strong>Tela de Personagens</strong></summary>
        <img src="https://github.com/user-attachments/assets/75e39fe3-860b-4c36-8d6e-9d5d6c31b7aa" width="220">
      </details>
    </td>
</table>

<table>
  <tr>
    <td style="vertical-align: top; padding: 10px;">
      <details>
        <summary><strong>Tela do Menu</strong></summary>
        <img src="https://github.com/user-attachments/assets/9fd44d2c-03da-482b-84db-14e9d2cd3d1d" width="220">
      </details>
    </td>
    <td style="vertical-align: top; padding: 10px;">
      <details>
        <summary><strong>Tela do Perfil</strong></summary>
        <img src="https://github.com/user-attachments/assets/39baab26-890d-4530-9a66-7a15364a76f4" width="120">
      </details>
    </td>
</table>

<table>
  <tr>
    <td style="vertical-align: top; padding: 10px;">
      <details>
        <summary><strong>Tela do Mapa</strong></summary>
        <img src="https://github.com/user-attachments/assets/9550cdbb-ab99-4382-9800-411b44c0e51b">
      </details>
    </td>
    <td style="vertical-align: top; padding: 10px;">
      <details>
        <summary><strong>Tela do Quiz</strong></summary>
        <img src="https://github.com/user-attachments/assets/6583651f-1b52-4499-b65c-58d1b617e9db" width="220">
      </details>
    </td>
</table>

```
Caso querira algo mais pratico para instalar as dependencias

cd verificação

python instalador.py

para instalar todos os pacotes

python verificacao.py

para verificar se todos os pacotes foram instlados

```
