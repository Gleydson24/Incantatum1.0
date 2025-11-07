import pygame
import sys
import os
from tela_luta import game_loop

SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "imagens", "personagens")

# Lista de personagens (nome + caminho)
PERSONAGENS = [
    ("Harry", os.path.join(IMG_DIR, "harry_icon.png")),
    ("Hermione", os.path.join(IMG_DIR, "hermione_icon.png")),
    ("Ron", os.path.join(IMG_DIR, "ron_icon.png")),
    ("Voldemort", os.path.join(IMG_DIR, "voldemort_icon.png")),
    ("Bellatrix", os.path.join(IMG_DIR, "bellatrix_icon.png")),
    ("Umbridge", os.path.join(IMG_DIR, "umbridge_icon.png"))
]

def carregar_icon(path, size=(220,220)):
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (60,60,80), surf.get_rect(), border_radius=12)
        pygame.draw.circle(surf, (140,140,180), (size[0]//2, size[1]//2), min(size)//3)
        return surf

def desenha_moldura(surface, rect, color=(220,200,130), thickness=6):
    x,y,w,h = rect
    outer = pygame.Surface((w+thickness*2, h+thickness*2), pygame.SRCALPHA)
    pygame.draw.rect(outer, (color[0], color[1], color[2], 80), outer.get_rect(), border_radius=12)
    surface.blit(outer, (x-thickness, y-thickness))
    pygame.draw.rect(surface, color, rect, border_radius=12, width=3)

def selecionar_um(screen, titulo):
    pygame.display.set_caption(titulo)
    fonte_titulo = pygame.font.Font(None, 64)
    fonte_nome = pygame.font.Font(None, 42)

    index = 0
    clock = pygame.time.Clock()

    # Carrega os ícones e redimensiona
    icones = []
    for nome, path in PERSONAGENS:
        img = carregar_icon(path)
        icones.append((nome, img))

    # layout: 3 ícones por linha (centralizados)
    cols = 3
    spacing_x = 60
    card_w, card_h = 220, 220
    start_x = (SCREEN_WIDTH - (cols * card_w + (cols-1)*spacing_x)) // 2
    y_top = 220

    while True:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    index = (index + 1) % len(icones)
                if event.key == pygame.K_LEFT:
                    index = (index - 1) % len(icones)
                if event.key == pygame.K_RETURN:
                    return icones[index][0]
                if event.key == pygame.K_ESCAPE:
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx,my = event.pos
                for i, (nome,img) in enumerate(icones):
                    col = i % cols
                    row = i // cols
                    x = start_x + col*(card_w+spacing_x)
                    y = y_top + row*(card_h+60)
                    rect = pygame.Rect(x, y, card_w, card_h)
                    if rect.collidepoint((mx,my)):
                        index = i
                        return icones[index][0]

        screen.fill((10, 8, 20))

        # título
        texto = fonte_titulo.render(titulo, True, (230, 230, 230))
        screen.blit(texto, (SCREEN_WIDTH // 2 - texto.get_width() // 2, 40))

        # desenha ícones com moldura e glow para o selecionado
        for i, (nome,img) in enumerate(icones):
            col = i % cols
            row = i // cols
            x = start_x + col*(card_w+spacing_x)
            y = y_top + row*(card_h+60)
            rect = pygame.Rect(x, y, card_w, card_h)

            if i == index:
                desenha_moldura(screen, rect, color=(160,220,255), thickness=8)
                img_to_draw = pygame.transform.smoothscale(img, (int(card_w*1.06), int(card_h*1.06)))
                screen.blit(img_to_draw, (x - int(card_w*0.03), y - int(card_h*0.03)))
            else:
                desenha_moldura(screen, rect, color=(220,200,130), thickness=4)
                screen.blit(img, (x, y))

            nome_texto = fonte_nome.render(icones[i][0], True, (240,240,240))
            screen.blit(nome_texto, (x + (card_w - nome_texto.get_width())//2, y + card_h + 8))

        pygame.display.flip()

def iniciar_selecao(screen):
    jogador = selecionar_um(screen, "Escolha seu Bruxo")
    if jogador is None:
        return

    global PERSONAGENS
    personagens_salvos = PERSONAGENS.copy()
    try:
        PERSONAGENS = [p for p in PERSONAGENS if p[0] != jogador]
    except Exception:
        PERSONAGENS = personagens_salvos

    oponente = selecionar_um(screen, "Escolha seu Inimigo")
    if oponente is None:
        PERSONAGENS = personagens_salvos
        return

    PERSONAGENS = personagens_salvos
    game_loop(screen, jogador, oponente, SCREEN_WIDTH, SCREEN_HEIGHT)