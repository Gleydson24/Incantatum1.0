import pygame
import random
# Importa as configurações para garantir acesso às cores
from scripts.settings import *

class Botao:
    def __init__(self, x, y, largura, altura, texto, cor_texto=BRANCO, cor_fundo=None, cor_hover=(100, 100, 100), tamanho_fonte=30, fonte_nome="Garamond"):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor_texto = cor_texto
        self.cor_fundo = cor_fundo 
        self.cor_hover = cor_hover
        self.fonte = pygame.font.SysFont(fonte_nome, tamanho_fonte, bold=True)
        self.hovered = False
        self.clicado = False 
        self.bloqueado = False # Para evitar spam de clique

    def desenhar(self, superficie):
        acao = False
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        self.hovered = self.rect.collidepoint(mouse_pos)

        # Fundo (só desenha se tiver cor definida)
        if self.cor_fundo:
            cor = self.cor_hover if self.hovered else self.cor_fundo
            pygame.draw.rect(superficie, cor, self.rect, border_radius=5)
            # Borda dourada
            pygame.draw.rect(superficie, OURO, self.rect, 2, border_radius=5)
        
        # Texto
        if self.texto:
            # Se for botão "invisível" (sem fundo), o texto brilha ao passar o mouse
            cor_atual = OURO if (self.hovered and not self.cor_fundo) else self.cor_texto
            surf_texto = self.fonte.render(self.texto, True, cor_atual)
            rect_texto = surf_texto.get_rect(center=self.rect.center)
            superficie.blit(surf_texto, rect_texto)

        # Lógica de Clique (apenas um clique por vez)
        if self.hovered and mouse_pressed:
            if not self.clicado:
                self.clicado = True
                acao = True
        
        if not mouse_pressed:
            self.clicado = False

        return acao

class Slider:
    def __init__(self, x, y, largura, min_val, max_val, inicial):
        self.rect = pygame.Rect(x, y, largura, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.valor = inicial
        self.arrastando = False
        # Calcula posição inicial do círculo
        ratio = (inicial - min_val) / (max_val - min_val)
        self.circle_x = x + (largura * ratio)

    def desenhar(self, tela):
        # Linha
        pygame.draw.line(tela, CINZA_CLARO, (self.rect.x, self.rect.centery), (self.rect.right, self.rect.centery), 4)
        # Círculo
        pygame.draw.circle(tela, OURO, (int(self.circle_x), self.rect.centery), 10)
        
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        dist = ((mouse_pos[0] - self.circle_x)**2 + (mouse_pos[1] - self.rect.centery)**2)**0.5
        
        if dist < 15 and mouse_click: 
            self.arrastando = True
        
        if not mouse_click: 
            self.arrastando = False

        if self.arrastando:
            self.circle_x = max(self.rect.x, min(mouse_pos[0], self.rect.right))
            ratio = (self.circle_x - self.rect.x) / self.rect.width
            self.valor = self.min_val + (ratio * (self.max_val - self.min_val))
            
        return self.valor

class Checkbox:
    def __init__(self, x, y, texto, ativo=False):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.texto = texto
        self.ativo = ativo
        self.fonte = pygame.font.SysFont("Garamond", 24, bold=True)
        self.clicado_anteriormente = False

    def desenhar(self, tela):
        # Caixa
        pygame.draw.rect(tela, OURO, self.rect, 2)
        if self.ativo:
            pygame.draw.rect(tela, OURO, (self.rect.x + 5, self.rect.y + 5, 15, 15))
        # Texto
        txt = self.fonte.render(self.texto, True, BRANCO)
        tela.blit(txt, (self.rect.right + 10, self.rect.y))

    def checar_clique(self, pos):
        if self.rect.collidepoint(pos):
            self.ativo = not self.ativo
            return True
        return False

class BotaoAjuda:
    def __init__(self, x, y, titulo, linhas_texto):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.titulo = titulo
        self.linhas = linhas_texto
        self.fonte = pygame.font.SysFont("Arial", 18, bold=True)
        self.fonte_desc = pygame.font.SysFont("Arial", 16)
        self.hover = False

    def desenhar(self, tela):
        mouse_pos = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(mouse_pos)
        cor = OURO if self.hover else CINZA
        pygame.draw.circle(tela, cor, self.rect.center, 12)
        txt = self.fonte.render("?", True, PRETO)
        rect_txt = txt.get_rect(center=self.rect.center)
        tela.blit(txt, rect_txt)

    def desenhar_tooltip(self, tela):
        if self.hover:
            largura_box = 250
            altura_box = 40 + (len(self.linhas) * 20)
            x = self.rect.right + 10
            y = self.rect.y - 10
            
            # Se sair da tela pela direita, joga para a esquerda
            if x + largura_box > LARGURA: 
                x = self.rect.left - largura_box - 10
                
            bg_rect = pygame.Rect(x, y, largura_box, altura_box)
            pygame.draw.rect(tela, PRETO_FUNDO, bg_rect)
            pygame.draw.rect(tela, OURO, bg_rect, 1)
            
            tit = self.fonte.render(self.titulo, True, OURO)
            tela.blit(tit, (x + 10, y + 10))
            
            for i, linha in enumerate(self.linhas):
                l = self.fonte_desc.render(linha, True, CINZA_CLARO)
                tela.blit(l, (x + 10, y + 35 + (i * 20)))

class TextoFlutuante(pygame.sprite.Sprite):
    def __init__(self, x, y, texto, cor, tamanho=30):
        super().__init__()
        x += random.randint(-25, 25)
        y += random.randint(-10, 10)
        self.fonte = pygame.font.SysFont("Impact", tamanho)
        self.image = self.fonte.render(texto, True, cor)
        self.sombra = self.fonte.render(texto, True, PRETO)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = -4
        self.timer = 30 # Dura meio segundo
        
    def update(self):
        self.rect.y += self.vel_y
        self.timer -= 1
        if self.timer <= 0: self.kill()
            
    def draw(self, tela):
        tela.blit(self.sombra, (self.rect.x + 2, self.rect.y + 2))
        tela.blit(self.image, self.rect)

class ParticulaMagica(pygame.sprite.Sprite):
    def __init__(self, x, y, cor, tipo="faísca"):
        super().__init__()
        self.tipo = tipo
        tamanho = random.randint(3, 8)
        self.image = pygame.Surface((tamanho, tamanho))
        self.image.fill(cor)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Velocidade aleatória para explosão
        vx = random.uniform(-5, 5)
        vy = random.uniform(-5, 5)
        self.vel = [vx, vy]
        self.timer = random.randint(20, 40)
        
    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        
        # Gravidade leve para partículas
        if self.tipo == "explosao": 
            self.vel[1] += 0.2
            
        self.timer -= 1
        if self.timer <= 0: self.kill()
    
    def draw(self, tela):
        tela.blit(self.image, self.rect)

def gerar_cenario_procedural(largura, altura, chao_y):
    """Gera um background simples caso não exista imagem"""
    surf = pygame.Surface((largura, altura))
    
    # Céu degradê
    cor_topo = (10, 10, 30)
    cor_base = (40, 30, 60)
    for y in range(altura):
        r = cor_topo[0] + (cor_base[0] - cor_topo[0]) * y // altura
        g = cor_topo[1] + (cor_base[1] - cor_topo[1]) * y // altura
        b = cor_topo[2] + (cor_base[2] - cor_topo[2]) * y // altura
        pygame.draw.line(surf, (r, g, b), (0, y), (largura, y))
    
    # Lua
    pygame.draw.circle(surf, (220, 220, 200), (largura - 100, 100), 50)
    
    # Montanhas
    pontos_montanha = [(0, chao_y)]
    for x in range(0, largura + 50, 50):
        alt_mont = random.randint(50, 250)
        pontos_montanha.append((x, chao_y - alt_mont))
    pontos_montanha.append((largura, chao_y))
    pontos_montanha.append((largura, altura)) # Fechar embaixo
    pontos_montanha.append((0, altura))
    
    pygame.draw.polygon(surf, (20, 20, 40), pontos_montanha)
    
    return surf