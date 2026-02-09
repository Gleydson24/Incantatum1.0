import pygame
from scripts.settings import *
from scripts.utils import Botao

COR_PERGAMINHO = (245, 235, 205)
COR_TINTA = (40, 30, 20)

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
        
        self.btn_fechar = Botao(self.x + self.largura - 40, self.y - 20, 40, 40, "X", cor_fundo=(150, 50, 50))
        
        aba_x = self.x + self.largura - 10
        self.abas = {
            "feiticos": Botao(aba_x, self.y + 50, 50, 80, "F", cor_fundo=COR_PERGAMINHO, cor_texto=COR_TINTA),
            "varinha": Botao(aba_x, self.y + 140, 50, 80, "V", cor_fundo=COR_PERGAMINHO, cor_texto=COR_TINTA),
            "perfil": Botao(aba_x, self.y + 230, 50, 80, "P", cor_fundo=COR_PERGAMINHO, cor_texto=COR_TINTA),
        }
        
        self.rects_feiticos = {} 
        self.descricoes = {
            "incendio": "Bola de fogo.\nDano: Médio\nCusto: 15 Mana",
            "protego": "Escudo mágico.\nBloqueia dano.\nCusto: 25 Mana",
            "sectumsempra": "Lâmina cortante.\nDano: Alto\nCusto: 35 Mana",
            "expelliarmus": "Desarme.\nDano: Baixo\nCusto: 20 Mana",
            "avada kedavra": "Maldição Fatal.\nDano: INSTAKILL\nCusto: 80 Mana"
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
        
        dados = self.jogo.dados_globais.get("maestria", {})
        y_off = 80
        self.rects_feiticos = {}
        
        for f in ["incendio", "protego", "sectumsempra", "expelliarmus", "avada kedavra"]:
            cor = (150,0,0) if f == "avada kedavra" else COR_TINTA
            txt = self.fonte_texto.render(f"• {f.capitalize()}", True, cor)
            rect = txt.get_rect(topleft=(cx, cy + y_off))
            
            if self.feitico_selecionado == f: pygame.draw.rect(tela, (220, 210, 180), rect.inflate(10,5))
            
            tela.blit(txt, rect)
            self.rects_feiticos[f] = rect
            
            nv = min(5, int(dados.get(f, 0)/10))
            tela.blit(self.fonte_texto.render("★"*nv, True, (200,150,0)), (cx + 250, cy + y_off))
            y_off += 40

        # Detalhes (Direita)
        cx2 = self.x + self.largura//2 + 40
        if self.feitico_selecionado:
            tela.blit(self.fonte_titulo.render(self.feitico_selecionado.capitalize(), True, COR_TINTA), (cx2, cy))
            desc = self.descricoes.get(self.feitico_selecionado, "").split('\n')
            dy = 60
            for l in desc:
                tela.blit(self.fonte_texto.render(l, True, COR_TINTA), (cx2, cy+dy)); dy+=30

    def pag_varinha(self, tela):
        cx = self.x + 50
        tela.blit(self.fonte_titulo.render("Sua Varinha", True, COR_TINTA), (cx, self.y + 50))
        
        # Pega dados do Save
        varinha = self.jogo.dados_globais.get("varinha", {"madeira":"Freixo", "nucleo":"Unicórnio", "flex":"Rígida"})
        
        y_off = 100
        tela.blit(self.fonte_texto.render(f"Madeira: {varinha['madeira']}", True, COR_TINTA), (cx, self.y + y_off)); y_off+=40
        tela.blit(self.fonte_texto.render(f"Núcleo: {varinha['nucleo']}", True, COR_TINTA), (cx, self.y + y_off)); y_off+=40
        tela.blit(self.fonte_texto.render(f"Flexibilidade: {varinha['flex']}", True, COR_TINTA), (cx, self.y + y_off))
        
        # Desenho da Varinha
        cx2 = self.x + self.largura//2 + 100
        pygame.draw.line(tela, (100, 70, 20), (cx2, self.y + 100), (cx2 + 150, self.y + 400), 8)
        pygame.draw.circle(tela, (200, 255, 255), (cx2, self.y + 100), 5) # Ponta brilhante

    def pag_perfil(self, tela):
        cx = self.x + 50
        tela.blit(self.fonte_titulo.render("Registro do Bruxo", True, COR_TINTA), (cx, self.y + 50))
        
        dados = self.jogo.dados_globais
        # Título sincronizado
        titulo = dados.get("titulo_jogador", "Bruxo Iniciante")
        
        linhas = [
            f"Nome: {dados.get('nome_jogador')}",
            f"Título: {titulo}",
            "",
            f"Vitórias: {dados.get('vitorias_p1', 0)}",
            f"Partidas: {dados.get('partidas_totais', 0)}"
        ]
        
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
                for nome, rect in self.rects_feiticos.items():
                    if rect.collidepoint(pos): self.feitico_selecionado = nome