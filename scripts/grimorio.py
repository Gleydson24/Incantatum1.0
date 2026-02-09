import pygame
import random
from scripts.settings import *
from scripts.utils import Botao
from scripts.save_system import salvar_dados

COR_PERGAMINHO = (245, 235, 205)
COR_TINTA = (40, 30, 20)
COR_DESENHO = (50, 50, 180) # Cor de caneta azul/lápis

class Grimorio:
    def __init__(self, jogo):
        self.jogo = jogo
        self.pagina_atual = "feiticos"
        self.feitico_selecionado = None 
        
        self.largura = 900; self.altura = 600
        self.x = (LARGURA - self.largura) // 2; self.y = (ALTURA - self.altura) // 2
        
        try: self.fonte_titulo = pygame.font.SysFont("Garamond", 35, bold=True)
        except: self.fonte_titulo = pygame.font.SysFont(None, 35)
        self.fonte_texto = pygame.font.SysFont("Garamond", 22)
        
        # Fonte "Infantil" (Comic Sans ou similar se tiver, senão default)
        try: self.fonte_crianca = pygame.font.SysFont("Comic Sans MS", 20, bold=True)
        except: self.fonte_crianca = pygame.font.SysFont("Arial", 20, bold=True)
        
        self.btn_fechar = Botao(self.x + self.largura - 40, self.y - 20, 40, 40, "X", cor_fundo=(150, 50, 50))
        
        aba_x = self.x + self.largura - 10
        self.abas = {
            "feiticos": Botao(aba_x, self.y + 50, 50, 80, "F", cor_fundo=COR_PERGAMINHO, cor_texto=COR_TINTA),
            "varinha": Botao(aba_x, self.y + 140, 50, 80, "V", cor_fundo=COR_PERGAMINHO, cor_texto=COR_TINTA),
            "perfil": Botao(aba_x, self.y + 230, 50, 80, "P", cor_fundo=COR_PERGAMINHO, cor_texto=COR_TINTA),
        }
        
        # Área do desenho secreto (Varinha Torta)
        self.rect_desenho_secreto = pygame.Rect(self.x + 60, self.y + 500, 60, 60)
        self.cliques_secreto = 0
        
        self.rects_feiticos = {} 
        
        # Descrições Normais
        self.desc_normal = {
            "incendio": "Bola de fogo concentrada.\nDano: Médio\nCusto: 15 Mana",
            "protego": "Escudo mágico de proteção.\nBloqueia todo dano.\nCusto: 25 Mana",
            "sectumsempra": "Feitiço cortante das trevas.\nDano: Alto e Rápido\nCusto: 35 Mana",
            "expelliarmus": "Feitiço de desarmamento.\nDano: Baixo (Empurrão)\nCusto: 20 Mana",
            "avada kedavra": "A Maldição da Morte.\nDano: INSTAKILL (Fatal)\nCusto: 80 Mana"
        }

        # Descrições "Críticos Mirins"
        self.desc_crianca = {
            "incendio": "Faz 'FWOOSH' e esquenta\nmarshmallow! Cuidado pra\nnão queimar o dedo.",
            "protego": "O escudo anti-monstro\ndo quarto. Nada passa!",
            "sectumsempra": "Corta papel igual tesoura\nsem ponta (mentira, tem ponta sim).",
            "expelliarmus": "Derruba o brinquedo\ndo irmão longe!",
            "avada kedavra": "O papai disse que é\nPROIBIDO usar esse.\nFica de castigo!"
        }

    def desenhar(self, tela):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA); overlay.fill((0,0,0,180)); tela.blit(overlay, (0,0))
        
        # Livro
        pygame.draw.rect(tela, (30, 20, 10), (self.x-20, self.y-20, self.largura+40, self.altura+40), border_radius=10)
        pygame.draw.rect(tela, COR_PERGAMINHO, (self.x, self.y, self.largura//2, self.altura), border_top_left_radius=5, border_bottom_left_radius=5)
        pygame.draw.rect(tela, COR_PERGAMINHO, (self.x+self.largura//2, self.y, self.largura//2, self.altura), border_top_right_radius=5, border_bottom_right_radius=5)
        pygame.draw.line(tela, (150,140,120), (self.x+self.largura//2, self.y), (self.x+self.largura//2, self.y+self.altura), 3)
        
        self.btn_fechar.desenhar(tela)
        for k, aba in self.abas.items(): aba.desenhar(tela)

        if self.pagina_atual == "feiticos": self.pag_feiticos(tela)
        elif self.pagina_atual == "varinha": self.pag_varinha(tela)
        elif self.pagina_atual == "perfil": self.pag_perfil(tela)

    def pag_feiticos(self, tela):
        cx, cy = self.x + 50, self.y + 50
        tela.blit(self.fonte_titulo.render("Feitiços", True, COR_TINTA), (cx, cy))
        
        # --- DESENHO SECRETO (VARINHA TORTA) ---
        # Desenha um "rabisco" simulando desenho de criança
        ox, oy = self.rect_desenho_secreto.x, self.rect_desenho_secreto.y
        # Cabo torto
        pygame.draw.line(tela, COR_DESENHO, (ox, oy+50), (ox+25, oy+25), 3)
        pygame.draw.line(tela, COR_DESENHO, (ox+25, oy+25), (ox+50, oy), 3)
        # Estrela na ponta
        pygame.draw.circle(tela, (255, 200, 0), (ox+50, oy), 6) 
        
        # Feedback visual ao passar o mouse
        if self.rect_desenho_secreto.collidepoint(pygame.mouse.get_pos()):
             pygame.draw.rect(tela, (200, 200, 0), self.rect_desenho_secreto, 1)
        # ---------------------------------------

        dados = self.jogo.dados_globais
        modo_critico = dados.get("modo_critico", False)
        
        # Escolhe qual dicionário e fonte usar
        dicionario_atual = self.desc_crianca if modo_critico else self.desc_normal
        fonte_desc_atual = self.fonte_crianca if modo_critico else self.fonte_texto
        cor_desc_atual = COR_DESENHO if modo_critico else COR_TINTA

        y_off = 80
        self.rects_feiticos = {}
        
        for f in ["incendio", "protego", "sectumsempra", "expelliarmus", "avada kedavra"]:
            cor = (150,0,0) if f == "avada kedavra" else COR_TINTA
            txt = self.fonte_texto.render(f"• {f.capitalize()}", True, cor)
            rect = txt.get_rect(topleft=(cx, cy + y_off))
            
            if self.feitico_selecionado == f: pygame.draw.rect(tela, (220, 210, 180), rect.inflate(10,5))
            
            tela.blit(txt, rect)
            self.rects_feiticos[f] = rect
            
            nv = min(5, int(dados.get("maestria", {}).get(f, 0)/10))
            tela.blit(self.fonte_texto.render("★"*nv, True, (200,150,0)), (cx + 250, cy + y_off))
            y_off += 40

        # Detalhes (Direita)
        cx2 = self.x + self.largura//2 + 40
        if self.feitico_selecionado:
            nome_display = self.feitico_selecionado.capitalize()
            # Título muda se for modo crítico
            if modo_critico and self.feitico_selecionado == "avada kedavra": 
                nome_display = "MALDIÇÃO PROIBIDA"
                
            tela.blit(self.fonte_titulo.render(nome_display, True, cor_desc_atual), (cx2, cy))
            
            desc = dicionario_atual.get(self.feitico_selecionado, "").split('\n')
            dy = 60
            for l in desc:
                tela.blit(fonte_desc_atual.render(l, True, cor_desc_atual), (cx2, cy+dy)); dy+=30

    def pag_varinha(self, tela):
        cx = self.x + 50
        tela.blit(self.fonte_titulo.render("Sua Varinha", True, COR_TINTA), (cx, self.y + 50))
        varinha = self.jogo.dados_globais.get("varinha", {"madeira":"Freixo", "nucleo":"Unicórnio", "flex":"Rígida"})
        y_off = 100
        tela.blit(self.fonte_texto.render(f"Madeira: {varinha['madeira']}", True, COR_TINTA), (cx, self.y + y_off)); y_off+=40
        tela.blit(self.fonte_texto.render(f"Núcleo: {varinha['nucleo']}", True, COR_TINTA), (cx, self.y + y_off)); y_off+=40
        tela.blit(self.fonte_texto.render(f"Flexibilidade: {varinha['flex']}", True, COR_TINTA), (cx, self.y + y_off))
        cx2 = self.x + self.largura//2 + 100
        pygame.draw.line(tela, (100, 70, 20), (cx2, self.y + 100), (cx2 + 150, self.y + 400), 8)
        pygame.draw.circle(tela, (200, 255, 255), (cx2, self.y + 100), 5)

    def pag_perfil(self, tela):
        cx = self.x + 50
        tela.blit(self.fonte_titulo.render("Registro do Bruxo", True, COR_TINTA), (cx, self.y + 50))
        dados = self.jogo.dados_globais
        titulo = dados.get("titulo_jogador", "Bruxo Iniciante")
        linhas = [f"Nome: {dados.get('nome_jogador')}", f"Título: {titulo}", "", f"Vitórias: {dados.get('vitorias_p1', 0)}", f"Partidas: {dados.get('partidas_totais', 0)}"]
        y_off = 100
        for l in linhas:
            tela.blit(self.fonte_texto.render(l, True, COR_TINTA), (cx, self.y + y_off))
            y_off += 30

    def processar_eventos(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.btn_fechar.rect.collidepoint(pos): self.jogo.mudar_estado(MENU)
            for k, b in self.abas.items(): 
                if b.rect.collidepoint(pos): self.pagina_atual = k
            
            if self.pagina_atual == "feiticos":
                # --- LÓGICA DO EASTER EGG (CLIQUE NO DESENHO) ---
                if self.rect_desenho_secreto.collidepoint(pos):
                    self.cliques_secreto += 1
                    if self.cliques_secreto >= 20: # 5 Cliques ativa/desativa
                        dados = self.jogo.dados_globais
                        dados["modo_critico"] = not dados.get("modo_critico", False)
                        salvar_dados(dados)
                        self.cliques_secreto = 0
                # -----------------------------------------------

                for nome, rect in self.rects_feiticos.items():
                    if rect.collidepoint(pos): self.feitico_selecionado = nome
