import pygame

# --- TELA & GERAL ---
LARGURA = 1280
ALTURA = 720
FPS = 60
TITULO = "INCANTATUM"

# --- GAMEPLAY ---
CHAO_Y = 600
USAR_CAMERA = True  # Define se o jogo tenta carregar o módulo de câmera
GRAVIDADE = 1
VELOCIDADE_MOVIMENTO = 5

# --- CORES GERAIS ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
PRETO_FUNDO = (20, 20, 30)
CINZA = (100, 100, 100)
CINZA_CLARO = (200, 200, 200)
CINZA_TEXTO = (200, 200, 200)

# --- CORES TEMÁTICAS E UI ---
OURO = (218, 165, 32)
OURO_ANTIGO = (200, 170, 50)
AZUL_MANA = (50, 50, 200)
SANGUE_ESCURO = (100, 0, 0)
VERDE_SLYTHERIN = (30, 100, 30)
VERMELHO_GRYFFINDOR = (116, 0, 1)

# --- CORES DOS FEITIÇOS ---
COR_INCENDIO_CENTRO = (255, 255, 0)
COR_INCENDIO_BORDA = (255, 100, 0)
COR_STUPEFY = (200, 0, 0)
COR_EXPELLIARMUS = (255, 50, 50)
COR_SECTUMSEMPRA = (200, 200, 255)
COR_PROTEGO = (100, 200, 255)
COR_AVADA = (0, 255, 0) # Verde brilhante
AZUL_CHOQUE = (150, 255, 255) # Para o efeito de colisão (clash)
VERMELHO_EXP = (255, 50, 50)  # Para barra de disputa
VERDE_CLASH = (50, 255, 100)  # Para barra de disputa

# --- ESTADOS DO JOGO ---
# Usamos constantes numéricas para facilitar a máquina de estados
INTRO = 100
MENU = 101
JOGO = 102
VITORIA = 103
DERROTA = 104
CONFIG = 105
DISPUTA = 106
CENA_MORTE = 107
CUTSCENE = 108
PROGRESSO = 109
GRIMORIO = 111
PERFIL = 112
DESAFIOS = 113
CREDITOS = 114 
PROCURANDO = 115

FEITICOS = {
    "incendio": {
        "dano": 10,
        "custo": 15,
        "vel": 10,
        "efeito": "queimar",
        "shape": "fogo",
        "cor": (255, 120, 0)
    },
    "expelliarmus": {
        "dano": 8,
        "custo": 20,
        "vel": 12,
        "efeito": "empurrão",
        "shape": "anel",
        "cor": (255, 0, 0)
    },
    "stupefy": {
        "dano": 12,
        "custo": 18,
        "vel": 11,
        "efeito": "stun",
        "shape": "esfera",
        "cor": (255, 255, 0)
    },
    "sectumsempra": {
        "dano": 25,
        "custo": 35,
        "vel": 14,
        "efeito": "sangramento",
        "shape": "lamina",
        "cor": (200, 200, 200)
    },
    "avada kedavra": {
        "dano": 100,
        "custo": 80,
        "vel": 18,
        "efeito": None,
        "shape": "raio",
        "cor": (0, 255, 0)
    },
    "protego": {
        "dano": 0,
        "custo": 25,
        "vel": 0,
        "efeito": None,
        "shape": None,
        "cor": (100, 200, 255)
    }
}


# --- CONFIGURAÇÃO DE CONTROLES ---

# 1. CONTROLES SOLO (Player vs IA)
CONTROLES_SOLO = {
    "esquerda": pygame.K_a,     # WASD padrão para facilitar
    "direita": pygame.K_d,
    "dash": pygame.K_LSHIFT,
    "incendio": pygame.K_1,
    "protego": pygame.K_2,
    "expelliarmus": pygame.K_3,
    "stupefy": pygame.K_4,
    "sectumsempra": pygame.K_5,
    "avada": pygame.K_x,
    "disputa": pygame.K_SPACE
}

# 2. CONTROLES PVP - PLAYER 1 (Esquerda do Teclado)
CONTROLES_P1_PVP = {
    "esquerda": pygame.K_a,
    "direita": pygame.K_d,
    "dash": pygame.K_LSHIFT,
    "incendio": pygame.K_1,
    "protego": pygame.K_2,
    "expelliarmus": pygame.K_3,
    "stupefy": pygame.K_4,
    "sectumsempra": pygame.K_5,
    "avada": pygame.K_x,
    "disputa": pygame.K_SPACE
}

# 3. CONTROLES PVP - PLAYER 2 (Direita do Teclado/Setas/Numpad)
CONTROLES_P2_PVP = {
    "esquerda": pygame.K_LEFT, 
    "direita": pygame.K_RIGHT, 
    "dash": pygame.K_RSHIFT,
    "incendio": pygame.K_KP1, 
    "protego": pygame.K_KP2, 
    "expelliarmus": pygame.K_KP3,
    "stupefy": pygame.K_KP4, 
    "sectumsempra": pygame.K_KP5, 
    "avada": pygame.K_KP0,
    "disputa": pygame.K_KP_ENTER
}