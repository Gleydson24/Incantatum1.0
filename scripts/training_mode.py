import pygame
import os 
from scripts.settings import *
from scripts.entities import Mago, RastroFantasma
from scripts.utils import TextoFlutuante, ParticulaMagica

class ModoTreinamento:
    def __init__(self, jogo_principal):
        self.jogo = jogo_principal
        self.tela = jogo_principal.tela
        self.relogio = jogo_principal.relogio
        
        self.rodando = True
        self.em_disputa = False 
        
        self.todos_sprites = pygame.sprite.Group()
        self.magias_player = pygame.sprite.Group()
        self.magias_inimigo = pygame.sprite.Group() 
        self.fantasmas = pygame.sprite.Group() 
        self.textos_flutuantes = [] 
        self.particulas = []
        
        # PLAYER
        self.player = Mago(200, CHAO_Y, "Aluno", self, CONTROLES_SOLO, "data/P1", is_human=True, lado_inicial_dir=True)
        # Hack para treino (Mana infinita praticamente)
        self.player.vida = 9999
        self.player.vida_max = 9999 
        self.player.mana = 9999
        self.player.mana_max = 9999
        self.todos_sprites.add(self.player)
        
        # BONECO (Agora é uma IA funcional)
        self.inimigo = Mago(LARGURA - 200, CHAO_Y, "Boneco IA", self, {}, "data/P1", is_human=False, lado_inicial_dir=False)
        self.inimigo.vida = 5000  
        self.inimigo.vida_max = 5000 
        self.inimigo.mana = 5000
        self.inimigo.mana_max = 5000
        # Força IA a atacar logo
        self.inimigo.ia_timer_acao = 70 
        self.todos_sprites.add(self.inimigo)
        
        # Referências cruzadas (Essencial para colisões)
        self.player.magias_player = self.magias_player
        self.player.magias_inimigo = self.magias_inimigo
        self.inimigo.magias_player = self.magias_player
        self.inimigo.magias_inimigo = self.magias_inimigo
        self.player.fantasmas = self.fantasmas
        self.inimigo.fantasmas = self.fantasmas

    def iniciar_cena_morte(self, entidade):
        # Renascimento instantâneo
        if entidade == self.inimigo:
            self.textos_flutuantes.append(TextoFlutuante(entidade.rect.centerx, entidade.rect.y - 50, "RESET!", (0,255,0), 50))
            entidade.vida = 5000
            entidade.morto = False
            entidade.estado_anim = 'idle'
        elif entidade == self.player:
            entidade.vida = 9999
            entidade.morto = False
            entidade.estado_anim = 'idle'
        self.magias_player.empty()
        self.magias_inimigo.empty()

    def desenhar_hud_treino(self):
        info = self.jogo.fonte_ui.render("MODO TREINO - ESC para sair", True, BRANCO)
        self.tela.blit(info, (20, 20))
        
        largura = 400
        x = (LARGURA - largura) // 2
        ratio = max(0, self.inimigo.vida / self.inimigo.vida_max)
        pygame.draw.rect(self.tela, PRETO_FUNDO, (x, 50, largura, 20))
        pygame.draw.rect(self.tela, SANGUE_ESCURO, (x, 50, largura * ratio, 20))
        pygame.draw.rect(self.tela, BRANCO, (x, 50, largura, 20), 2)
        
        txt_dano = self.jogo.fonte_ui.render(f"Dano Acumulado: {5000 - self.inimigo.vida}", True, OURO)
        self.tela.blit(txt_dano, (x, 75))

    def rodar(self):
        pygame.mouse.set_visible(False)
        
        while self.rodando:
            self.relogio.tick(FPS)
            self.tela.blit(self.jogo.bg_jogo, (0,0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando = False
                    self.jogo.rodando = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.rodando = False
            
            # Updates
            self.player.update()
            self.inimigo.update() 
            
            self.magias_player.update()
            self.magias_inimigo.update()
            self.fantasmas.update() 
            
            # Colisões
            hits = pygame.sprite.spritecollide(self.inimigo, self.magias_player, True)
            for m in hits:
                dano = m.dano
                self.inimigo.vida -= dano
                for _ in range(5):
                    self.particulas.append(ParticulaMagica(m.rect.x, m.rect.y, m.image.get_at((m.rect.width//2, m.rect.height//2)), "explosao"))
                self.textos_flutuantes.append(TextoFlutuante(self.inimigo.rect.centerx, self.inimigo.rect.y, str(dano), (255, 100, 100)))
                if self.inimigo.vida <= 0: self.iniciar_cena_morte(self.inimigo)

            # O player no treino é imortal, mas vamos mostrar o hit
            hits_p = pygame.sprite.spritecollide(self.player, self.magias_inimigo, True)
            for m in hits_p:
                 self.textos_flutuantes.append(TextoFlutuante(self.player.rect.centerx, self.player.rect.y, "DANO!", (255, 0, 0)))

            # Desenho
            self.fantasmas.draw(self.tela)
            self.tela.blit(self.player.image, self.player.rect)
            self.tela.blit(self.inimigo.image, self.inimigo.rect)
            
            for m in self.magias_player: self.tela.blit(m.image, m.rect)
            for m in self.magias_inimigo: self.tela.blit(m.image, m.rect)
            
            for p in self.particulas[:]: 
                p.update()
                p.draw(self.tela)
                if p.timer <= 0: self.particulas.remove(p)
                
            for t in self.textos_flutuantes[:]:
                t.update()
                t.draw(self.tela)
                if t.timer <= 0: self.textos_flutuantes.remove(t)

            self.desenhar_hud_treino()
            
            mx, my = pygame.mouse.get_pos()
            if hasattr(self.jogo, 'cursor_img'):
                self.tela.blit(self.jogo.cursor_img, (mx-4, my-4))

            pygame.display.flip()
        
        pygame.mouse.set_visible(False)