import pygame
from scripts.settings import *
from scripts.entities import Mago, Magia
from scripts.utils import TextoFlutuante, ParticulaMagica, Botao

class LivroRegras:
    def __init__(self, tela):
        self.tela = tela
        self.aberto = True # Começa aberto
        self.pagina = 0
        self.fonte = pygame.font.SysFont("Garamond", 22)
        self.fonte_tit = pygame.font.SysFont("Garamond", 40, bold=True)
        
        self.paginas = [
            ("BÁSICO", ["Use W/A/S/D para mover.", "SHIFT para Dash (Esquiva).", "Use 1-5 para lançar feitiços.", "Gerencie sua MANA (Barra Azul)."]),
            ("FEITIÇOS", ["1: Incendio (Fogo)", "2: Protego (Escudo)", "3: Expelliarmus (Empurrão)", "X: Avada Kedavra (Fatal)"]),
            ("DISPUTA (CLASH)", ["Se duas magias colidirem,", "esmague ESPAÇO rapidamente", "para vencer o empurrão!"]),
            ("MODOS EXTRAS", ["Mobile: Conecte pelo IP no Config.", "Voz: Fale o nome do feitiço.", "Varinha: Use algo colorido na Câmera."])
        ]
        # Botão menor e texto ajustado
        self.btn_fechar = Botao(LARGURA//2 - 50, ALTURA - 80, 100, 40, "OK", cor_fundo=(50, 100, 50), tamanho_fonte=20)

    def desenhar(self):
        if not self.aberto: return
        # Fundo Escuro
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA); s.fill((0,0,0,200)); self.tela.blit(s, (0,0))
        
        # Livro
        rect = pygame.Rect(100, 50, LARGURA-200, ALTURA-100)
        pygame.draw.rect(self.tela, (240, 230, 200), rect, border_radius=10)
        pygame.draw.rect(self.tela, (50, 30, 10), rect, 5, border_radius=10)
        
        tit, linhas = self.paginas[self.pagina]
        t_surf = self.fonte_tit.render(tit, True, (50, 30, 10))
        self.tela.blit(t_surf, (rect.centerx - t_surf.get_width()//2, rect.y + 40))
        
        y = rect.y + 120
        for l in linhas:
            txt = self.fonte.render(f"- {l}", True, (0,0,0))
            self.tela.blit(txt, (rect.x + 60, y)); y += 40
            
        info = self.fonte.render(f"Página {self.pagina+1}/{len(self.paginas)} (Setas p/ Mudar | ENTER p/ Sair)", True, (100,100,100))
        self.tela.blit(info, (rect.centerx - info.get_width()//2, rect.bottom - 100))
        
        self.btn_fechar.desenhar(self.tela)

class ModoTreinamento:
    def __init__(self, jogo_principal):
        self.jogo = jogo_principal
        self.tela = jogo_principal.tela
        self.relogio = jogo_principal.relogio
        self.rodando = True
        
        self.todos_sprites = pygame.sprite.Group()
        self.magias_player = pygame.sprite.Group()
        self.magias_inimigo = pygame.sprite.Group() 
        self.fantasmas = pygame.sprite.Group() 
        self.textos_flutuantes = [] 
        self.particulas = []
        
        # Player Imortal
        self.player = Mago(200, CHAO_Y, "Aluno", self, CONTROLES_SOLO, "data/P1", True, True)
        self.player.vida = 9999; self.player.mana = 9999
        self.player.magias_player = self.magias_player; self.player.magias_inimigo = self.magias_inimigo
        self.todos_sprites.add(self.player)
        
        # Boneco
        self.inimigo = Mago(LARGURA - 200, CHAO_Y, "Boneco", self, {}, "data/P1", False, False)
        self.inimigo.vida = 5000; self.inimigo.mana = 5000
        self.inimigo.magias_player = self.magias_player; self.inimigo.magias_inimigo = self.magias_inimigo
        self.todos_sprites.add(self.inimigo)
        
        self.livro = LivroRegras(self.tela)
        self.btn_regras = Botao(LARGURA - 150, 20, 130, 30, "Ver Regras", cor_fundo=(50, 50, 80), tamanho_fonte=16)

    def iniciar_cena_morte(self, quem):
        quem.vida = 5000 if quem == self.inimigo else 9999
        quem.morto = False; quem.estado = "Idle"; quem.morte_iniciada = False
        self.textos_flutuantes.append(TextoFlutuante(quem.rect.centerx, quem.rect.y-50, "RESET", (0,255,0)))

    def update_logica(self):
        self.player.update(); self.inimigo.update()
        self.magias_player.update(); self.magias_inimigo.update(); self.fantasmas.update()
        
        # DUELO DE MAGIAS (Com Máscara)
        hits_magia = pygame.sprite.groupcollide(self.magias_player, self.magias_inimigo, True, True, pygame.sprite.collide_mask)
        for m_player, m_inimigos in hits_magia.items():
            centro = m_player.rect.center
            self.textos_flutuantes.append(TextoFlutuante(centro[0], centro[1]-20, "CLASH!", (255, 255, 0)))
            for _ in range(8): self.particulas.append(ParticulaMagica(centro[0], centro[1], (255, 200, 50), "explosao"))

        # DANO NO INIMIGO (Com Máscara)
        hits = pygame.sprite.spritecollide(self.inimigo, self.magias_player, False, pygame.sprite.collide_mask)
        for m in hits:
            if self.inimigo.escudo_ativo:
                self.textos_flutuantes.append(TextoFlutuante(self.inimigo.rect.centerx, self.inimigo.rect.y - 40, "PROTEGO!", (100,200,255)))
                m.kill(); self.inimigo.escudo_ativo = False
            else:
                self.inimigo.vida -= m.dano
                self.textos_flutuantes.append(TextoFlutuante(self.inimigo.rect.centerx, self.inimigo.rect.y, str(m.dano), (255,100,0)))
                m.kill()
                # ... (resto igual) ... # Mata a magia no corpo
                # Efeito de hit
                for _ in range(5):
                    self.particulas.append(ParticulaMagica(m.rect.centerx, m.rect.centery, m.cor, "faísca"))

                if self.inimigo.vida <= 0: self.iniciar_cena_morte(self.inimigo)

    def desenhar_hud(self):
        pygame.draw.rect(self.tela, (0,0,0,150), (0,0,LARGURA, 60))
        self.tela.blit(self.jogo.fonte_ui.render(f"Dano: {5000 - self.inimigo.vida}", True, (255, 100, 100)), (20, 20))
        self.btn_regras.desenhar(self.tela)

    def rodar(self):
        pygame.event.clear() # Limpa eventos antigos para não pular coisas
        
        while self.rodando:
            self.relogio.tick(60)
            mx, my = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.rodando = False; self.jogo.rodando = False
                
                if event.type == pygame.KEYDOWN:
                    if self.livro.aberto:
                        if event.key == pygame.K_RIGHT: self.livro.pagina = (self.livro.pagina + 1) % len(self.livro.paginas)
                        if event.key == pygame.K_LEFT: self.livro.pagina = (self.livro.pagina - 1) % len(self.livro.paginas)
                        # ATALHO PARA SAIR DO LIVRO
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN or event.key == pygame.K_SPACE: 
                            self.livro.aberto = False
                    else:
                        if event.key == pygame.K_ESCAPE: self.rodando = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.livro.aberto:
                        if self.livro.btn_fechar.rect.collidepoint(event.pos): self.livro.aberto = False
                    else:
                        if self.btn_regras.rect.collidepoint(event.pos): self.livro.aberto = True

            self.tela.blit(self.jogo.bg_jogo, (0,0))
            
            if not self.livro.aberto:
                self.update_logica()
                
            self.fantasmas.draw(self.tela)
            self.tela.blit(self.player.image, self.player.rect)
            self.tela.blit(self.inimigo.image, self.inimigo.rect)
            
            # Desenha Escudos
            if self.player.escudo_ativo: pygame.draw.circle(self.tela, (100,200,255), self.player.rect.center, 50, 2)
            if self.inimigo.escudo_ativo: pygame.draw.circle(self.tela, (100,200,255), self.inimigo.rect.center, 50, 2)
            
            self.magias_player.draw(self.tela); self.magias_inimigo.draw(self.tela)
            
            for t in self.textos_flutuantes[:]: 
                t.update(); t.draw(self.tela)
                if t.timer <= 0: self.textos_flutuantes.remove(t)
            
            for p in self.particulas[:]: 
                p.update(); p.draw(self.tela)
                if p.timer <= 0: self.particulas.remove(p)

            self.desenhar_hud()
            self.livro.desenhar()
            
            # --- CURSOR DO MOUSE NO TREINO ---
            if hasattr(self.jogo, 'cursor_img'):
                self.tela.blit(self.jogo.cursor_img, (mx-16, my-16))
            
            pygame.display.flip()