import pygame
from scripts.settings import *
from scripts.utils import Botao

class TelaCreditos:
    def __init__(self, jogo):
        self.jogo = jogo
        self.tela = jogo.tela
        
        self.btn_voltar = Botao(50, ALTURA - 80, 150, 50, "VOLTAR", cor_fundo=(100, 30, 30))
        
        try:
            self.fonte_titulo = pygame.font.SysFont("Garamond", 60, bold=True)
            self.fonte_cargo = pygame.font.SysFont("Garamond", 24, italic=True)
            self.fonte_nome = pygame.font.SysFont("Arial", 28, bold=True)
        except:
            self.fonte_titulo = pygame.font.SysFont(None, 60)
            self.fonte_cargo = pygame.font.SysFont(None, 24)
            self.fonte_nome = pygame.font.SysFont(None, 28)

        self.lista_creditos = [
            ("titulo", "INCANTATUM"), ("espaco", ""), ("cargo", "Criado Por"), ("nome", "Gleydson & Eduardo"),
            ("espaco", ""), ("cargo", "Design"), ("nome", "Gleydson & Eduardo"),
            ("espaco", ""), ("cargo", "Tecnologia IA"), ("nome", "Groq & Llama 3"),
            ("espaco", ""), ("titulo", "Feito com Python")
        ]
        self.scroll_y = ALTURA

    def resetar(self):
        self.scroll_y = ALTURA + 50

    def desenhar(self):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA); overlay.fill((0, 0, 0, 230))
        self.tela.blit(self.jogo.bg_menu, (0,0)); self.tela.blit(overlay, (0,0))
        
        y = self.scroll_y
        cx = LARGURA // 2
        
        for tipo, txt in self.lista_creditos:
            if -50 < y < ALTURA + 50:
                font = self.fonte_titulo if tipo == "titulo" else (self.fonte_cargo if tipo == "cargo" else self.fonte_nome)
                col = OURO if tipo == "titulo" else (CINZA_CLARO if tipo == "cargo" else BRANCO)
                if tipo != "espaco":
                    surf = font.render(txt, True, col)
                    self.tela.blit(surf, surf.get_rect(center=(cx, y)))
            
            y += 70 if tipo == "titulo" else (35 if tipo == "cargo" else 40)

        self.scroll_y -= 1.0
        if self.scroll_y < - (y - self.scroll_y): self.resetar()
        
        self.btn_voltar.desenhar(self.tela)

    def processar_eventos(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_voltar.rect.collidepoint(event.pos):
                self.jogo.mudar_estado(MENU)