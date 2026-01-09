import pygame
import random
from scripts.settings import *
from scripts.utils import Botao

# Cores do Livro
COR_PERGAMINHO = (245, 235, 205)
COR_PERGAMINHO_ESC = (210, 195, 160)
COR_TINTA = (40, 30, 20)
COR_TINTA_FRACA = (100, 90, 80)
COR_DESTAQUE = (180, 50, 50) 

class Grimorio:
    def __init__(self, jogo):
        self.jogo = jogo
        self.aberto = False
        self.pagina_atual = "feiticos"
        self.feitico_selecionado = None 
        
        self.registro_num = random.randint(1000, 9999)
        
        self.largura = 900
        self.altura = 600
        self.x = (LARGURA - self.largura) // 2
        self.y = (ALTURA - self.altura) // 2
        
        # --- CORREÇÃO: FONTES MENORES ---
        font_name = "Garamond" if "Garamond" in pygame.font.get_fonts() else "Arial"
        self.fonte_titulo = pygame.font.SysFont(font_name, 35, bold=True) # Reduzido de 50 para 35
        self.fonte_texto = pygame.font.SysFont(font_name, 22)
        self.fonte_misterio = pygame.font.SysFont(font_name, 22, italic=True)
        
        # Botão Fechar (X)
        self.btn_fechar = Botao(self.x + self.largura - 40, self.y - 20, 40, 40, "X", cor_fundo=(150, 50, 50))
        
        # Abas Laterais
        aba_x = self.x + self.largura - 10
        self.abas = {
            "feiticos": Botao(aba_x, self.y + 50, 50, 80, "F", cor_fundo=COR_PERGAMINHO_ESC, cor_texto=COR_TINTA),
            "varinha": Botao(aba_x, self.y + 140, 50, 80, "V", cor_fundo=COR_PERGAMINHO_ESC, cor_texto=COR_TINTA),
            "perfil": Botao(aba_x, self.y + 230, 50, 80, "P", cor_fundo=COR_PERGAMINHO_ESC, cor_texto=COR_TINTA),
        }
        
        self.rects_feiticos = {} 
        self.descricoes = {
            "incendio": "Conjura uma bola de fogo básica.\nDano: Médio\nCusto: 20 Mana",
            "protego": "Cria um escudo mágico temporário.\nBloqueia 1 feitiço.\nCusto: 30 Mana",
            "sectumsempra": "Lâmina invisível e rápida.\nDano: Alto (Veloz)\nCusto: 40 Mana",
            "expelliarmus": "Desarma e empurra o oponente.\nDano: Baixo + Controle\nCusto: 25 Mana",
            "avada kedavra": "Maldição imperdoável.\nDano: FATAL (Mata Instataneamente)\nCusto: 100 Mana"
        }

    def desenhar_fundo_livro(self, tela):
        # Capa
        pygame.draw.rect(tela, (30, 20, 10), (self.x - 20, self.y - 20, self.largura + 40, self.altura + 40), border_radius=10)
        metade = self.largura // 2
        
        # Pagina Esquerda
        pygame.draw.rect(tela, COR_PERGAMINHO, (self.x, self.y, metade, self.altura), border_top_left_radius=5, border_bottom_left_radius=5)
        
        # Pagina Direita
        pygame.draw.rect(tela, COR_PERGAMINHO, (self.x + metade, self.y, metade, self.altura), border_top_right_radius=5, border_bottom_right_radius=5)
        
        # Lombada Central (Sombra)
        sombra = pygame.Surface((40, self.altura), pygame.SRCALPHA)
        sombra.fill((0,0,0,0))
        pygame.draw.rect(sombra, (0,0,0,50), (15, 0, 10, self.altura)) 
        pygame.draw.rect(sombra, (0,0,0,30), (5, 0, 30, self.altura))
        tela.blit(sombra, (self.x + metade - 20, self.y))
        
        self.btn_fechar.desenhar(tela)

    def desenhar_pagina_feiticos(self, tela):
        cx, cy = self.x + 50, self.y + 50
        tela.blit(self.fonte_titulo.render("Estudos Arcanos", True, COR_TINTA), (cx, cy))
        
        feiticos_lista = ["incendio", "protego", "sectumsempra", "expelliarmus", "avada kedavra"]
        y_off = 80 # Ajustado
        self.rects_feiticos = {} 
        
        dados = self.jogo.dados_globais.get("maestria", {})
        
        # Lista na esquerda
        for f in feiticos_lista:
            uso = dados.get(f, 0)
            nivel = min(5, int(uso / 5)) 
            
            nome_display = f.capitalize()
            cor = (150, 0, 0) if f == "avada kedavra" else COR_TINTA
            
            if self.feitico_selecionado == f:
                cor = COR_DESTAQUE
                pygame.draw.rect(tela, (230, 220, 190), (cx - 10, cy + y_off - 5, 380, 35))

            txt = self.fonte_texto.render(f"• {nome_display}", True, cor)
            rect = txt.get_rect(topleft=(cx, cy + y_off))
            tela.blit(txt, rect)
            self.rects_feiticos[f] = rect
            
            estrelas = "★" * nivel + "☆" * (5 - nivel)
            txt_star = self.fonte_texto.render(estrelas, True, (200, 150, 0))
            tela.blit(txt_star, (cx + 250, cy + y_off))
            
            y_off += 50

        # Detalhes na direita
        cx_dir = self.x + self.largura//2 + 40
        
        if self.feitico_selecionado:
            pygame.draw.rect(tela, COR_PERGAMINHO_ESC, (cx_dir, cy, 350, 400), border_radius=5)
            pygame.draw.rect(tela, COR_TINTA, (cx_dir, cy, 350, 400), 2, border_radius=5)
            
            texto_desc = self.descricoes.get(self.feitico_selecionado, "Sem dados.")
            linhas = texto_desc.split("\n")
            dy = 20
            
            t_detalhe = self.fonte_titulo.render(self.feitico_selecionado.capitalize(), True, COR_TINTA)
            if t_detalhe.get_width() > 300:
                t_detalhe = pygame.transform.scale(t_detalhe, (300, 40))
            
            tela.blit(t_detalhe, (cx_dir + 20, cy + dy))
            dy += 70
            
            for linha in linhas:
                l_surf = self.fonte_texto.render(linha, True, COR_TINTA)
                tela.blit(l_surf, (cx_dir + 20, cy + dy))
                dy += 35
        else:
            info = self.fonte_misterio.render("Selecione um feitiço...", True, COR_TINTA_FRACA)
            tela.blit(info, (cx_dir + 20, cy + 180))

    def desenhar_pagina_varinha(self, tela):
        cx = self.x + 50
        tela.blit(self.fonte_titulo.render("Sua Varinha", True, COR_TINTA), (cx, self.y + 50))
        
        desc = self.fonte_texto.render("O catalisador da sua magia.", True, COR_TINTA_FRACA)
        tela.blit(desc, (cx, self.y + 100))
        
        opcoes = [("Núcleo", "Pena de Fênix"), ("Madeira", "Carvalho"), ("Flexibilidade", "Rígida")]
        y_off = 160
        for k, v in opcoes:
            t = self.fonte_texto.render(f"{k}: {v}", True, COR_TINTA)
            tela.blit(t, (cx, self.y + y_off))
            y_off += 40
            
        cx_dir = self.x + self.largura//2 + 100
        pygame.draw.line(tela, (100, 70, 20), (cx_dir + 50, self.y + 100), (cx_dir + 200, self.y + 400), 8)
        pygame.draw.circle(tela, (200, 255, 255), (cx_dir + 50, self.y + 100), 5)
            
        nota = self.fonte_misterio.render("(Representação Visual)", True, COR_TINTA_FRACA)
        tela.blit(nota, (cx_dir, self.y + 420))

    def desenhar_pagina_perfil(self, tela):
        cx = self.x + 50
        tela.blit(self.fonte_titulo.render("Registro do Bruxo", True, COR_TINTA), (cx, self.y + 50))
        
        vitorias = self.jogo.dados_globais.get("vitorias_p1", 0)
        total = self.jogo.dados_globais.get("partidas_totais", 0)
        derrotas = total - vitorias
        
        linhas = [
            f"ID do Ministério: {self.registro_num}", 
            "",
            f"Duelos Totais: {total}",
            f"Vitórias: {vitorias}",
            f"Derrotas: {derrotas}",
            "",
            "Classificação: " + ("Auror" if vitorias > 20 else "Estudante")
        ]
        
        y_off = 120
        for l in linhas:
            t = self.fonte_texto.render(l, True, COR_TINTA)
            tela.blit(t, (cx, self.y + y_off))
            y_off += 30

    def processar_eventos(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.btn_fechar.rect.collidepoint(pos):
                self.jogo.mudar_estado(MENU)
                return

            if self.abas["feiticos"].desenhar(self.jogo.tela): self.pagina_atual = "feiticos"
            if self.abas["varinha"].desenhar(self.jogo.tela): self.pagina_atual = "varinha"
            if self.abas["perfil"].desenhar(self.jogo.tela): self.pagina_atual = "perfil"
            
            if self.pagina_atual == "feiticos":
                for nome, rect in self.rects_feiticos.items():
                    if rect.collidepoint(pos):
                        self.feitico_selecionado = nome

    def desenhar(self, tela):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        tela.blit(overlay, (0, 0))
        self.desenhar_fundo_livro(tela)
        for k, aba in self.abas.items():
            if k == self.pagina_atual: 
                aba.rect.x = self.x + self.largura - 15
            else: 
                aba.rect.x = self.x + self.largura - 5
            aba.desenhar(tela)

        if self.pagina_atual == "feiticos": self.desenhar_pagina_feiticos(tela)
        elif self.pagina_atual == "varinha": self.desenhar_pagina_varinha(tela)
        elif self.pagina_atual == "perfil": self.desenhar_pagina_perfil(tela)