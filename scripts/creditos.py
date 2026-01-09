import pygame
from scripts.settings import *
from scripts.utils import Botao

class TelaCreditos:
    def __init__(self, jogo):
        self.jogo = jogo
        self.tela = jogo.tela
        
        # Fontes
        try:
            self.fonte_titulo = pygame.font.SysFont("Garamond", 60, bold=True)
            self.fonte_cargo = pygame.font.SysFont("Garamond", 24, italic=True)
            self.fonte_nome = pygame.font.SysFont("Arial", 28, bold=True)
            self.fonte_footer = pygame.font.SysFont("Arial", 16)
        except:
            self.fonte_titulo = pygame.font.SysFont(None, 60)
            self.fonte_cargo = pygame.font.SysFont(None, 24)
            self.fonte_nome = pygame.font.SysFont(None, 28)

        # Botão Voltar
        self.btn_voltar = Botao(50, ALTURA - 80, 150, 50, "VOLTAR", cor_fundo=(100, 30, 30))
        
        # --- LISTA DE CRÉDITOS ---
        # Formato: (Tipo, Texto) -> Tipo: "titulo", "cargo", "nome", "espaco"
        self.lista_creditos = [
            ("titulo", "HOGWARTS DUEL"),
            ("titulo", "ARCADE EDITION"),
            ("espaco", ""),
            ("espaco", ""),
            
            ("cargo", "Criação e Desenvolvimento"),
            ("nome", "Gleydson"),
            ("nome", "Eduardo"),
            ("espaco", ""),
            
            ("cargo", "Game Design & Mecânicas"),
            ("nome", "Gleydson"),
            ("nome", "Eduardo"),
            ("espaco", ""),
            
            ("cargo", "Inteligência Artificial (Chat)"),
            ("nome", "Powered by Groq & Llama 3"),
            ("espaco", ""),
            
            ("cargo", "Visão Computacional (Varinha)"),
            ("nome", "OpenCV Integration"),
            ("espaco", ""),
            
            ("cargo", "Bibliotecas Utilizadas"),
            ("nome", "Pygame Community"),
            ("nome", "Google GenAI"),
            ("espaco", ""),
            
            ("cargo", "Agradecimentos Especiais"),
            ("nome", "Aos Jogadores"),
            ("nome", "J.K. Rowling (Universo Original)"),
            ("espaco", ""),
            ("espaco", ""),
            ("espaco", ""),
            ("titulo", "Feito com Python"),
            ("titulo", "e Magia"),
        ]
        
        self.scroll_y = ALTURA  # Começa embaixo da tela

    def resetar(self):
        """Reinicia a animação de subida"""
        self.scroll_y = ALTURA + 50

    def desenhar(self):
        # Fundo escuro transparente
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230)) # Bem escuro para ler o texto
        self.tela.blit(self.jogo.bg_menu, (0,0))
        self.tela.blit(overlay, (0,0))
        
        # Lógica de Scroll e Desenho
        y_atual = self.scroll_y
        centro_x = LARGURA // 2
        
        for tipo, texto in self.lista_creditos:
            # Só desenha se estiver visível na tela
            if -50 < y_atual < ALTURA + 50:
                if tipo == "titulo":
                    surf = self.fonte_titulo.render(texto, True, OURO)
                    rect = surf.get_rect(center=(centro_x, y_atual))
                    self.tela.blit(surf, rect)
                    y_atual += 70
                    
                elif tipo == "cargo":
                    surf = self.fonte_cargo.render(texto, True, CINZA_CLARO)
                    rect = surf.get_rect(center=(centro_x, y_atual))
                    self.tela.blit(surf, rect)
                    y_atual += 35
                    
                elif tipo == "nome":
                    surf = self.fonte_nome.render(texto, True, BRANCO)
                    rect = surf.get_rect(center=(centro_x, y_atual))
                    self.tela.blit(surf, rect)
                    y_atual += 40
                    
                elif tipo == "espaco":
                    y_atual += 40
            else:
                # Se não estiver visível, só soma a altura para calcular o próximo
                if tipo == "titulo": y_atual += 70
                elif tipo == "cargo": y_atual += 35
                elif tipo == "nome": y_atual += 40
                elif tipo == "espaco": y_atual += 40

        # Atualiza a posição (Sobe devagar)
        self.scroll_y -= 1.0  # Velocidade do scroll
        
        # Loop infinito dos créditos (se subir tudo, recomeça)
        altura_total = y_atual - self.scroll_y
        if self.scroll_y < -altura_total - 50:
            self.resetar()

        # Botão Voltar (Fixo)
        self.btn_voltar.desenhar(self.tela)

    def processar_eventos(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_voltar.rect.collidepoint(event.pos):
                self.jogo.mudar_estado(MENU)
            
            # Clique na tela acelera ou reseta
            if event.button == 1 and not self.btn_voltar.rect.collidepoint(event.pos):
                self.scroll_y -= 50 # Pula um pouco
                
        # Scroll com mouse ou setas
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * 20
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN: self.scroll_y -= 10
            if event.key == pygame.K_UP: self.scroll_y += 10