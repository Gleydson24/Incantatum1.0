import pygame
import sys
import os

# Configuração simples
LARGURA = 1280
ALTURA = 720
COR_MARCACAO = (255, 0, 0)
COR_TEXTO = (0, 255, 0)

pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("CALIBRADOR DE BOTÕES - CLIQUE NOS 4 CANTOS")
fonte = pygame.font.SysFont("Arial", 20)

# Lista de imagens para calibrar
imagens = [
    "data/telas/menu.png",
    "data/telas/vitoria.png",
    "data/telas/derrota.png",
    "data/cenario.png" # Para calibrar coisas do jogo se precisar
]

indice_img = 0
cliques = []

def carregar_bg(path):
    if os.path.exists(path):
        img = pygame.image.load(path)
        return pygame.transform.scale(img, (LARGURA, ALTURA))
    else:
        surf = pygame.Surface((LARGURA, ALTURA))
        surf.fill((50, 50, 50))
        return surf

bg_atual = carregar_bg(imagens[indice_img])

print("\n" + "="*50)
print("MODO CALIBRAÇÃO INICIADO")
print("1. Clique na ordem: Sup.Esq -> Sup.Dir -> Inf.Esq -> Inf.Dir")
print("2. O código do botão aparecerá aqui.")
print("3. Aperte ESPAÇO para trocar de imagem.")
print("="*50 + "\n")

rodando = True
while rodando:
    tela.blit(bg_atual, (0,0))
    
    # Desenha os cliques
    for i, ponto in enumerate(cliques):
        pygame.draw.circle(tela, COR_MARCACAO, ponto, 5)
        # Desenha linha entre os pontos para visualizar o retangulo
        if i > 0:
            pygame.draw.line(tela, COR_MARCACAO, cliques[i-1], ponto, 2)
    
    # Se tiver 4 cliques, desenha o retângulo final para conferência
    if len(cliques) == 4:
        x = cliques[0][0]
        y = cliques[0][1]
        w = cliques[1][0] - cliques[0][0] # Distancia X do primeiro pro segundo
        h = cliques[2][1] - cliques[0][1] # Distancia Y do primeiro pro terceiro
        
        rect_preview = pygame.Rect(x, y, w, h)
        pygame.draw.rect(tela, (0, 255, 0), rect_preview, 4)
        
        # Gera o print apenas uma vez
        print(f"\nCOORDENADA CAPTURADA:")
        print(f'Botao({x}, {y}, {w}, {h}, texto="", cor_fundo=None),')
        print("-" * 30)
        
        cliques = [] # Reseta para o próximo botão

    # Instruções na tela
    txt_img = fonte.render(f"Imagem: {imagens[indice_img]} (ESPAÇO para trocar)", True, (255, 255, 255))
    txt_click = fonte.render(f"Cliques: {len(cliques)}/4", True, (255, 255, 0))
    tela.blit(txt_img, (10, 10))
    tela.blit(txt_click, (10, 40))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                indice_img = (indice_img + 1) % len(imagens)
                bg_atual = carregar_bg(imagens[indice_img])
                cliques = []
                print(f"\n--- Mudou para: {imagens[indice_img]} ---")
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Clique esquerdo
                pos = pygame.mouse.get_pos()
                cliques.append(pos)
                nomes = ["Sup. Esq", "Sup. Dir", "Inf. Esq", "Inf. Dir"]
                if len(cliques) <= 4:
                    print(f"Clique {len(cliques)} ({nomes[len(cliques)-1]}): {pos}")

pygame.quit()
sys.exit()