# Incantatum

Incantatum é um jogo de luta e duelo mágico 2D desenvolvido em Python com Pygame. Inspirado no universo bruxo, o projeto evoluiu de um simples duelo para uma experiência completa com elementos de RPG, múltiplos métodos de controle (incluindo visão computacional e mobile) e integração com Inteligência Artificial Generativa.

# 1. 🎮 Visão Geral

Tecnologia Principal: Python 3.10+ e Pygame 2.6.1

Gênero: Fighting Game / Arcade / RPG Light

Descrição: Participe de duelos intensos utilizando feitiços icônicos. O jogo vai além do teclado, permitindo que o jogador use o celular como varinha (via WiFi), comande feitiços por voz ou use uma varinha real detectada pela webcam.

Destaque: Sistema de Perfil persistente com XP, Níveis, Missões Diárias automáticas e um Chatbot integrado com IA (LLM) para conversar com personagens.

# 2. 🚀 Funcionalidades Principais
   
⚔️ Sistema de Combate & Gameplay

Mecânica de Duelo: 6 feitiços distintos (Incendio, Protego, Expelliarmus, Stupefy, Sectumsempra, Avada Kedavra), cada um com atributos de dano, velocidade e custo de mana.

Clash de Magias: Quando dois feitiços colidem, inicia-se uma disputa de "esmagar botões" (button mashing) para vencer o embate.

# Modos de Jogo:

Solo (vs IA): Duelar contra o computador.

PvP Local: Dois jogadores no mesmo teclado.

Rankeada (Online): Em construção

Treino: Modo livre com boneco de teste e reset instantâneo.

# 🧙‍♂️ RPG e Progressão (Save System)

Perfil de Jogador: Nome editável, título desbloqueável (ex: "Mestre Duelista") e estatísticas vitais (vitórias/derrotas).

Sistema de Avatar: Escolha entre ícones internos ou importe sua própria imagem do computador.

Nível e XP: Ganhe experiência completando desafios e suba de nível.

Maestria: O jogo rastreia quantas vezes você usou cada feitiço.

# 📅 Missões Diárias (Live Service Local)

Gerador Automático: O jogo detecta a data e gera 3 novas missões aleatórias todo dia (ex: "Vença 3 partidas", "Use Incendio 10 vezes").

Histórico: Registro permanente das conquistas desbloqueadas.

# 🤖 Inteligência Artificial & Social

Chat Híbrido:

Amigos: Interface simulada de chat.

Personagens (IA Real): Integração com a API Groq (Llama 3). Converse livremente com Harry, Rony, Hermione ou Dumbledore. Eles respondem com personalidade e contexto.

# 📱 Controles Inovadores

Teclado: Controles clássicos (WASD).

Voz: Use o microfone para conjurar feitiços falando os nomes.

Mobile (Celular): Conecte seu celular via WiFi (Flask Server) e use-o como controle touchscreen.

Webcam (Visão Computacional): Rastreamento de cores via OpenCV. Use um objeto colorido como varinha para mirar e atirar.

# 4. 🎨 Interface e UX
   
Menu Dinâmico: Botões animados, efeitos de partículas e transições.

Grimório: Livro interativo explicando cada feitiço.

Configurações: Ajuste de volume, calibração de câmera e toggles de FPS.

Créditos Cinematográficos: Tela de créditos com rolagem automática (scrolling text).

# 6. 📦 Requisitos e Instalação
   
Para rodar o jogo com todas as funcionalidades, as seguintes bibliotecas são necessárias:

# Cole este código em seu Terminal (CMD, VS CODE, PowerShell ):

# pip install pygame numpy opencv-python SpeechRecognition pyaudio flask groq

# Nota: Para o chat com IA funcionar, é necessário configurar uma API KEY gratuita da Groq no arquivo scripts/ai_service.py.
# OU USAR ESSA API: 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 "Já inclusa no código"

# 8. 🕹️ Controles Padrão (Teclado)

Ação	         Player 1           	Player 2 (PvP)
Mover       	W / A / S / D      	Setas Direcionais
Dash	         Shift Esq.	            Shift Dir.
Incendio	         1	                 Numpad 1
Protego	           2	                 Numpad 2
Expelliarmus	     3	                 Numpad 3
Stupefy	           4	                 Numpad 4
Sectumsempra	     5	                 Numpad 5
Avada Kedavra      X	                 Numpad 0
Disputa	         Espaço	                Enter

# 9. 👥 Equipe de Desenvolvimento

# Gleydson Dallyson Pimenta de Brito - Eduardo Silva Santos

# "Feito com Python e Magia."
