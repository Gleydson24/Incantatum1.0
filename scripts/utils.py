import pygame
import random
import os

# CORES GERAIS
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA_HOVER = (60, 60, 80)
AZUL_ESCURO = (30, 30, 45)
BORDA = (100, 100, 150)
AMARELO = (255, 215, 0)

class Botao:
    def __init__(self, x, y, w, h, texto, cor_texto=(255,255,255), cor_bg=AZUL_ESCURO, ao_clicar=None, cor_fundo=None, **kwargs):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        
        # Correção de segurança: Se passar função no lugar da cor
        if callable(cor_texto): 
            self.ao_clicar = cor_texto
            self.cor_texto = (255, 255, 255)
        elif cor_texto is None:
            self.cor_texto = (255, 255, 255)
        else:
            self.cor_texto = cor_texto

        # Compatibilidade com nomes antigos (cor_fundo ou cor_bg)
        if cor_fundo is not None:
            self.cor_bg = cor_fundo
        else:
            self.cor_bg = cor_bg
        
        if ao_clicar is not None:
            self.ao_clicar = ao_clicar
            
        self.font = pygame.font.Font(None, 36)
        self.hovered = False

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        cor_fundo = CINZA_HOVER if self.hovered else self.cor_bg
        cor_borda = BORDA
        
        pygame.draw.rect(surface, cor_fundo, self.rect, border_radius=12)
        pygame.draw.rect(surface, cor_borda, self.rect, 2, border_radius=12)
        
        try:
            txt_surf = self.font.render(self.texto, True, self.cor_texto)
        except TypeError:
            txt_surf = self.font.render(self.texto, True, (255, 255, 255))
            
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def checar_clique(self, event):
        if hasattr(event, 'type'):
             if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos) and self.ao_clicar:
                    self.ao_clicar()
        else:
             if self.rect.collidepoint(event) and self.ao_clicar:
                 self.ao_clicar()
    
    def desenhar(self, surface):
        self.draw(surface)
        return self.hovered and pygame.mouse.get_pressed()[0]

class Slider:
    def __init__(self, x, y, w, min_val, max_val, inicial):
        self.rect = pygame.Rect(x, y, w, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.valor = inicial
        self.circle_x = x + (inicial - min_val) / (max_val - min_val) * w
        self.dragging = False

    def desenhar(self, surf):
        pygame.draw.line(surf, (200,200,200), (self.rect.left, self.rect.centery), (self.rect.right, self.rect.centery), 4)
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
            if rect_tooltip.right > 1280: rect_tooltip.x -= 220
            if rect_tooltip.bottom > 720: rect_tooltip.y -= altura_box + 20
            pygame.draw.rect(surf, (30, 30, 40), rect_tooltip)
            pygame.draw.rect(surf, BRANCO, rect_tooltip, 1)
            tit_surf = self.font.render(self.titulo, True, AMARELO)
            surf.blit(tit_surf, (rect_tooltip.x + 10, rect_tooltip.y + 10))
            for i, linha in enumerate(self.texto):
                txt_surf = self.font_texto.render(linha, True, (220, 220, 220))
                surf.blit(txt_surf, (rect_tooltip.x + 10, rect_tooltip.y + 35 + (i * 20)))

class TextoFlutuante:
    def __init__(self, x, y, texto, cor=(255,0,0)):
        self.x = x; self.y = y; self.texto = texto; self.cor = cor; self.timer = 60
        self.font = pygame.font.Font(None, 24)
    def update(self): self.y -= 1; self.timer -= 1
    def draw(self, surf):
        if self.timer > 0:
            t = self.font.render(self.texto, True, self.cor)
            surf.blit(t, (self.x, self.y))

class ParticulaMagica:
    def __init__(self, x, y, cor, tipo=None):
        self.x = x; self.y = y; self.cor = cor; 
        self.vida = random.randint(20, 40)
        self.vx = random.uniform(-2, 2); self.vy = random.uniform(-2, 2)
        if tipo == "explosao":
             self.vx *= 2
             self.vy *= 2

    def update(self): self.x += self.vx; self.y += self.vy; self.vida -= 1
    def draw(self, surf):
        if self.vida > 0:
            try:
                surf.set_at((int(self.x), int(self.y)), self.cor)
            except:
                pass

def fatiar_spritesheet_horizontal(caminho, escala=1.0, qtd_frames_manual=None):
    # LÓGICA DE SPRITE FALTANTE:
    # Se a imagem não existe ou der erro, cria um bloco 100% TRANSPARENTE.
    # Antes era roxo, agora é (0,0,0,0) -> Invisível.
    if not os.path.exists(caminho):
        surf = pygame.Surface((50, 80), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0)) # Transparente
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
    except Exception as e:
        print(f"Erro ao carregar sprite {caminho}: {e}")
        surf = pygame.Surface((50, 80), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0)) # Transparente
        return [surf]

def gerar_cenario_procedural():
    fundo = pygame.Surface((1280, 720))
    for y in range(720):
        r = max(0, 20 - y // 20)
        g = max(0, 20 - y // 20)
        b = max(50, 100 - y // 10)
        pygame.draw.line(fundo, (r, g, b), (0, y), (1280, y))
    for _ in range(100):
        x = random.randint(0, 1280); y = random.randint(0, 400)
        fundo.set_at((x, y), (255, 255, 255))
    pygame.draw.rect(fundo, (30, 20, 10), (0, 600, 1280, 120))
    pygame.draw.line(fundo, (50, 200, 50), (0, 600), (1280, 600), 5)
    return fundo