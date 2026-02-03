import pygame
import random
import os

# --- CORES GERAIS ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA_HOVER = (60, 60, 80)
AZUL_ESCURO = (30, 30, 45) # Cor padrão
BORDA = (100, 100, 150)
AMARELO = (255, 215, 0)
CINZA_CLARO = (200, 200, 200)

# Importa configurações para ter LARGURA/ALTURA se necessário
try:
    from scripts.settings import *
except:
    pass

class Botao:
    def __init__(self, x, y, w, h, texto, cor_texto=BRANCO, cor_fundo=AZUL_ESCURO, tamanho_fonte=30, fonte_nome="Garamond", **kwargs):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.cor_texto = cor_texto
        
        # Se cor_fundo for None, o botão será invisível
        self.cor_bg = cor_fundo 
        
        # Previne erro se cor_bg for roxo "mágico", muda para azul
        if self.cor_bg == (255, 0, 255): 
            self.cor_bg = AZUL_ESCURO

        try:
            self.font = pygame.font.SysFont(fonte_nome, tamanho_fonte, bold=True)
        except:
            self.font = pygame.font.Font(None, tamanho_fonte)
            
        self.hovered = False
        self.clicado = False

    def desenhar(self, surface):
        acao = False
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        self.hovered = self.rect.collidepoint(mouse_pos)

        # --- CORREÇÃO DOS BOTÕES ROXOS/VISÍVEIS ---
        # Só desenha o retângulo se tiver uma cor definida.
        # Se self.cor_bg for None, ele pula isso e desenha só o texto (se houver)
        if self.cor_bg is not None:
            cor_atual = CINZA_HOVER if self.hovered else self.cor_bg
            pygame.draw.rect(surface, cor_atual, self.rect, border_radius=12)
            pygame.draw.rect(surface, BORDA, self.rect, 2, border_radius=12)
        # ------------------------------------------
        
        # Desenha o texto
        if self.texto:
            # Se for botão invisível, o texto brilha no hover
            cor_txt = AMARELO if (self.hovered and self.cor_bg is None) else self.cor_texto
            
            txt_surf = self.font.render(self.texto, True, cor_txt)
            txt_rect = txt_surf.get_rect(center=self.rect.center)
            surface.blit(txt_surf, txt_rect)

        # Lógica de Clique
        if self.hovered and mouse_pressed:
            if not self.clicado:
                self.clicado = True
                acao = True
        
        if not mouse_pressed:
            self.clicado = False

        return acao

class Slider:
    def __init__(self, x, y, w, min_val, max_val, inicial):
        self.rect = pygame.Rect(x, y, w, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.valor = inicial
        self.circle_x = x + (inicial - min_val) / (max_val - min_val) * w
        self.dragging = False

    def desenhar(self, surf):
        pygame.draw.line(surf, CINZA_CLARO, (self.rect.left, self.rect.centery), (self.rect.right, self.rect.centery), 4)
        pygame.draw.circle(surf, (50,150,255), (int(self.circle_x), self.rect.centery), 10)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        if click:
            if self.rect.collidepoint(mouse_pos) or self.dragging:
                self.dragging = True
                self.circle_x = max(self.rect.left, min(mouse_pos[0], self.rect.right))
                ratio = (self.circle_x - self.rect.left) / self.rect.width
                self.valor = self.min_val + ratio * (self.max_val - self.min_val)
        else:
            self.dragging = False
        return self.valor

class Checkbox:
    def __init__(self, x, y, texto, ativo=False):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.texto = texto
        self.ativo = ativo
        self.font = pygame.font.Font(None, 24)
        self.clicado_anteriormente = False

    def desenhar(self, surf):
        pygame.draw.rect(surf, BRANCO, self.rect, 2)
        if self.ativo: 
            pygame.draw.rect(surf, (0,255,0), (self.rect.x+4, self.rect.y+4, 12, 12))
        t = self.font.render(self.texto, True, BRANCO)
        surf.blit(t, (self.rect.right + 10, self.rect.y))

    def checar_clique(self, pos):
        if self.rect.collidepoint(pos):
            self.ativo = not self.ativo
            return self.ativo
        return False

class BotaoAjuda:
    def __init__(self, x, y, titulo, texto):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.titulo = titulo
        self.texto = texto
        self.font = pygame.font.Font(None, 30)
        self.font_texto = pygame.font.Font(None, 24)
        self.hovered = False

    def desenhar(self, surf):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        cor = AMARELO if self.hovered else (200, 200, 200)
        pygame.draw.circle(surf, cor, self.rect.center, 15)
        pygame.draw.circle(surf, PRETO, self.rect.center, 15, 2)
        txt = self.font.render("?", True, PRETO)
        txt_rect = txt.get_rect(center=self.rect.center)
        surf.blit(txt, txt_rect)

    def desenhar_tooltip(self, surf):
        if self.hovered:
            mx, my = pygame.mouse.get_pos()
            altura_box = 40 + (len(self.texto) * 20)
            rect_tooltip = pygame.Rect(mx + 15, my + 15, 200, altura_box)
            # Evita sair da tela
            try:
                if rect_tooltip.right > LARGURA: rect_tooltip.x -= 220
                if rect_tooltip.bottom > ALTURA: rect_tooltip.y -= altura_box + 20
            except: pass # Se LARGURA não estiver definida
            
            pygame.draw.rect(surf, (30, 30, 40), rect_tooltip)
            pygame.draw.rect(surf, BRANCO, rect_tooltip, 1)
            tit_surf = self.font.render(self.titulo, True, AMARELO)
            surf.blit(tit_surf, (rect_tooltip.x + 10, rect_tooltip.y + 10))
            for i, linha in enumerate(self.texto):
                txt_surf = self.font_texto.render(linha, True, (220, 220, 220))
                surf.blit(txt_surf, (rect_tooltip.x + 10, rect_tooltip.y + 35 + (i * 20)))

# --- CORREÇÃO DO ERRO 'AttributeError: rect' ---
# A classe TextoFlutuante foi limpa e agora usa Sprite corretamente
class TextoFlutuante(pygame.sprite.Sprite):
    def __init__(self, x, y, texto, cor=(255,0,0), tamanho=30):
        super().__init__()
        self.x = x
        self.y = y
        self.texto = texto
        self.cor = cor
        self.timer = 60
        try:
            self.font = pygame.font.SysFont("Impact", tamanho)
        except:
            self.font = pygame.font.Font(None, tamanho)
            
        self.image = self.font.render(texto, True, cor)
        self.rect = self.image.get_rect(center=(x, y)) # O atributo 'rect' agora existe!

    def update(self):
        self.rect.y -= 1
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            
    # O método draw não é necessário se usarmos Group.draw(), mas mantemos para compatibilidade
    def draw(self, surf):
        surf.blit(self.image, self.rect)

class ParticulaMagica(pygame.sprite.Sprite):
    def __init__(self, x, y, cor, tipo=None):
        super().__init__() # Adicionado super init
        self.x = x
        self.y = y
        self.cor = cor
        self.vida = random.randint(20, 40)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        if tipo == "explosao":
             self.vx *= 2
             self.vy *= 2
        
        self.image = pygame.Surface((4, 4))
        self.image.fill(cor)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        self.vida -= 1
        if self.vida <= 0:
            self.kill()
            
    def draw(self, surf):
        surf.blit(self.image, self.rect)

def fatiar_spritesheet_horizontal(caminho, escala=1.0, qtd_frames_manual=None):
    if not os.path.exists(caminho):
        surf = pygame.Surface((50, 80), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0)) 
        return [surf]
        
    try:
        sheet = pygame.image.load(caminho).convert_alpha()
        sheet_w = sheet.get_width(); sheet_h = sheet.get_height()
        
        if qtd_frames_manual is None:
            if sheet_h > 0: qtd_frames = max(1, sheet_w // sheet_h)
            else: qtd_frames = 1
        else: qtd_frames = qtd_frames_manual
        
        largura_frame = sheet_w // qtd_frames; altura_frame = sheet_h
        frames = []
        for i in range(qtd_frames):
            corte = pygame.Rect(i * largura_frame, 0, largura_frame, altura_frame)
            imagem = sheet.subsurface(corte)
            novo_w = int(largura_frame * escala); novo_h = int(altura_frame * escala)
            frames.append(pygame.transform.scale(imagem, (novo_w, novo_h)))
        return frames
    except Exception:
        surf = pygame.Surface((50, 80), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        return [surf]

def gerar_cenario_procedural(largura, altura, chao_y):
    fundo = pygame.Surface((largura, altura))
    for y in range(altura):
        r = max(0, 20 - y // 20)
        g = max(0, 20 - y // 20)
        b = max(50, 100 - y // 10)
        pygame.draw.line(fundo, (r, g, b), (0, y), (largura, y))
    for _ in range(100):
        x = random.randint(0, largura); y = random.randint(0, 400)
        fundo.set_at((x, y), (255, 255, 255))
    pygame.draw.rect(fundo, (30, 20, 10), (0, chao_y, largura, altura-chao_y))
    pygame.draw.line(fundo, (50, 200, 50), (0, chao_y), (largura, chao_y), 5)
    return fundo
