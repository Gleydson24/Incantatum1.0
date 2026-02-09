import pygame
import random
import os
from scripts.settings import *
from scripts.utils import TextoFlutuante, fatiar_spritesheet_horizontal

# =====================================================
# CONFIGURAÇÃO DOS PERSONAGENS (DATABASE)
# =====================================================
DB_ANIMACAO = {
    "P1": "LEGACY", 

    # Evil Wizard 1
    "P2": {
        "escala": 2.5,
        "ajuste_y": 116,
        "mapa": {
            "Idle": "Idle.png",
            "walk": "move.png",
            "movfire": "Attack.png",
            "dead": "Death.png"
        }
    },
    # Evil Wizard 2
    "P3": {
        "escala": 2.5,
        "ajuste_y": 205,
        "mapa": {
            "Idle": "Idle.png",
            "walk": "move.png",
            "movfire": "Attack1.png",
            "dead": "Death.png"
        }
    },
    # Evil Wizard 3
    "P4": {
        "escala": 2.5,
        "ajuste_y": 110,
        "mapa": {
            "Idle": "Idle.png",
            "walk": "Walk.png",
            "movfire": "Attack.png",
            "dead": "Death.png"
        }
    },
    # P5 FOI REMOVIDO DAQUI
    
    # Goose (O Pato Boss)
    "Goose": {
        "escala": 3.0,
        "ajuste_y": 120, 
        "mapa": {
            "Idle": "Idle.png",
            "walk": "Walk.png", 
            "movfire": "Flap.png", 
            "dead": "Idle.png" 
        }
    }
}

class RastroFantasma(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image.copy()
        self.image.set_alpha(120)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.timer = 12
    def update(self):
        self.timer -= 1
        if self.timer <= 0: self.kill()
        else: self.image.set_alpha(self.timer * 10)

class Magia(pygame.sprite.Sprite):
    def __init__(self, x, y, nome, direcao, jogo, dono):
        super().__init__()
        self.jogo = jogo
        self.dono = dono
        self.nome = nome
        nome_real = "avada kedavra" if nome == "avada" else nome
        
        if nome_real in FEITICOS:
            dados = FEITICOS[nome_real]
            self.dano = dados["dano"]
            self.velocidade = dados["vel"] * direcao
            self.cor = dados["cor"]
        else:
            self.dano = 10; self.velocidade = 10 * direcao; self.cor = (255, 255, 255)

        self.image = pygame.Surface((50, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.cor, (25, 12), 9)
        pygame.draw.circle(self.image, (255, 255, 255), (22, 9), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.velocidade
        if self.rect.right < 0 or self.rect.left > LARGURA: self.kill()

class Mago(pygame.sprite.Sprite):
    # --- CORREÇÃO DO ERRO TYPEERROR ---
    # Adicionei 'dificuldade=1.0' no final dos argumentos
    def __init__(self, x, y, nome, jogo, controles, pasta, is_human=True, lado_inicial_dir=True, dificuldade=1.0):
        super().__init__()
        self.jogo = jogo
        self.nome = nome
        self.controles = controles
        self.is_human = is_human
        self.facing_right = lado_inicial_dir
        self.pasta = pasta 
        
        # DIFICULDADE (Multiplica vida e status)
        self.vida_max = 100 * dificuldade
        self.mana_max = 100 * dificuldade
        
        if "Goose" in self.pasta: 
            self.vida_max = 500
            self.mana_max = 0 
            
        self.vida = self.vida_max
        self.mana = self.mana_max
        
        self.escudo_ativo = False
        self.protego_timer = 0
        self.cast_cd = 0
        self.morto = False
        self.morte_iniciada = False
        
        # IA Timers
        self.ia_move_timer = 0
        self.ia_decision = 0
        self.ia_reaction_delay = 0

        self.estado = "Idle"
        self.frame = 0
        self.anim = {"Idle": [], "walk": [], "movfire": [], "dead": []}
        
        # Variável para guardar o ajuste vertical
        self.ajuste_y = 0 
        
        self._carregar_animacoes(self.pasta)
        
        # --- CORREÇÃO: Fallback Transparente (Tira o quadrado roxo) ---
        if not self.anim["Idle"]:
            s = pygame.Surface((50,80), pygame.SRCALPHA); s.fill((0,0,0,0)) # Transparente
            self.anim["Idle"] = [s]

        self.image = self.anim["Idle"][0]
        
        # APLICA O AJUSTE VERTICAL AQUI (y + self.ajuste_y)
        self.rect = self.image.get_rect(midbottom=(x, y + self.ajuste_y))
        
        # Cria a máscara para colisão precisa
        self.mask = pygame.mask.from_surface(self.image)

    def _carregar_animacoes(self, pasta):
        nome_pasta = os.path.basename(os.path.normpath(pasta))
        config = DB_ANIMACAO.get(nome_pasta)
        
        if config and config != "LEGACY":
            escala = config["escala"]
            mapa = config["mapa"]
            # Lê o ajuste de Y do banco de dados, se não tiver usa 0
            self.ajuste_y = config.get("ajuste_y", 0)
            
            for estado_jogo, nome_arquivo in mapa.items():
                caminho_completo = os.path.join(pasta, nome_arquivo)
                if os.path.exists(caminho_completo):
                    self.anim[estado_jogo] = fatiar_spritesheet_horizontal(caminho_completo, escala)
                else:
                    if estado_jogo != "Idle" and self.anim["Idle"]: 
                        self.anim[estado_jogo] = self.anim["Idle"]
        else:
            # Lógica LEGACY (P1/Harry)
            escala = 2.2
            self.ajuste_y = 0 
            estados = {"Idle": 7, "walk": 6, "movfire": 4, "dead": 6}
            for estado, qtd in estados.items():
                for i in range(qtd):
                    path = os.path.join(pasta, f"{estado}_{i}.png")
                    if os.path.exists(path):
                        img = pygame.image.load(path).convert_alpha()
                        img = pygame.transform.scale(img, (int(img.get_width()*escala), int(img.get_height()*escala)))
                    else:
                        # --- CORREÇÃO: Fallback Transparente aqui também ---
                        img = pygame.Surface((50, 80), pygame.SRCALPHA); img.fill((0, 0, 0, 0))
                    self.anim[estado].append(img)

    def castar_feitico(self, nome):
        if "Goose" in self.pasta: return

        nome_real = "avada kedavra" if nome == "avada" else nome
        if self.morto or self.cast_cd > 0: return
        if self.mana < FEITICOS[nome_real]["custo"]: return

        self.mana -= FEITICOS[nome_real]["custo"]
        self.cast_cd = 40 
        self.estado = "movfire"
        self.frame = 0
        
        if self.is_human and hasattr(self.jogo, 'dados_globais'):
            dados = self.jogo.dados_globais
            if "maestria" not in dados: dados["maestria"] = {}
            if nome_real not in dados["maestria"]: dados["maestria"][nome_real] = 0
            dados["maestria"][nome_real] += 1
            from scripts.save_system import salvar_dados
            salvar_dados(dados)

        if nome_real == "protego":
            self.escudo_ativo = True
            self.protego_timer = 60
            return

        direcao = 1 if self.facing_right else -1
        offset_tiro = 40 if "P1" not in self.pasta else 30
        magia = Magia(self.rect.centerx + 40 * direcao, self.rect.centery - offset_tiro, nome_real, direcao, self.jogo, self)
        
        if self == self.jogo.player: self.jogo.magias_player.add(magia)
        else: self.jogo.magias_inimigo.add(magia)

    def receber_dano(self, origem, dano_forcado=None):
        if self.morto: return
        if self.escudo_ativo and origem:
            origem.kill(); self.escudo_ativo = False; self.jogo.textos_flutuantes.append(TextoFlutuante(self.rect.centerx, self.rect.y, "BLOQUEADO!", (100, 200, 255))); return
        dano = dano_forcado if dano_forcado is not None else origem.dano
        self.vida -= dano
        if origem: origem.kill()
        if self.vida <= 0: self.vida = 0; self.morto = True; self.jogo.iniciar_cena_morte(self)

    def ativar_dash(self):
        if self.mana >= 15 and not self.morto:
            self.mana -= 15
            d = 1 if self.facing_right else -1
            self.rect.x += 150 * d
            if self.rect.left < 0: self.rect.left = 0
            if self.rect.right > LARGURA: self.rect.right = LARGURA
            self.jogo.fantasmas.add(RastroFantasma(self.rect.x, self.rect.y, self.image))

    def update(self):
        if self.morto:
            if not self.morte_iniciada:
                self.estado = "dead"; self.frame = 0; self.morte_iniciada = True
            
            if self.frame < len(self.anim["dead"]) - 1: self.frame += 0.15
            else: self.frame = len(self.anim["dead"]) - 1
            
            img = self.anim["dead"][int(self.frame)]
            self.image = pygame.transform.flip(img, not self.facing_right, False)
            
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            return

        if self.cast_cd > 0: self.cast_cd -= 1
        if self.protego_timer > 0: self.protego_timer -= 1; 
        if self.protego_timer <= 0: self.escudo_ativo = False

        regen = 0.1 if self.is_human else 0.05
        self.mana = min(self.mana + regen, self.mana_max)

        vx = 0
        
        if self.is_human:
            keys = pygame.key.get_pressed()
            if keys[self.controles["esquerda"]]: vx = -5; self.facing_right = False
            if keys[self.controles["direita"]]: vx = 5; self.facing_right = True
            if keys[self.controles.get("dash", pygame.K_LSHIFT)]: 
                if self.cast_cd == 0: self.ativar_dash()
            for magia in ["incendio", "stupefy", "expelliarmus", "sectumsempra", "avada", "protego"]:
                if magia in self.controles and keys[self.controles[magia]]: self.castar_feitico(magia)
        
        else:
            player = self.jogo.player
            dx = player.rect.centerx - self.rect.centerx
            dist = abs(dx)
            self.facing_right = dx > 0
            
            if "Goose" in self.pasta:
                vx = 7 if dx > 0 else -7
                if dist < 80:
                    self.estado = "movfire" 
            else:
                self.ia_move_timer += 1
                if self.ia_move_timer > 40:
                    self.ia_decision = 0
                    if dist > 500: self.ia_decision = 1
                    elif dist < 300: self.ia_decision = -1 
                    self.ia_move_timer = 0
                
                direcao_move = 1 if dx > 0 else -1
                vx = 3 * self.ia_decision * direcao_move

                if self.cast_cd == 0 and dist < 700:
                    roll = random.random()
                    if roll < 0.015 and self.mana > 20: self.castar_feitico(random.choice(["incendio", "stupefy"]))
                    elif roll < 0.018 and self.mana > 30: self.castar_feitico("protego")

        self.rect.x += vx
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > LARGURA: self.rect.right = LARGURA

        if self.estado == "movfire":
            self.frame += 0.25
            if self.frame >= len(self.anim["movfire"]):
                self.estado = "Idle"; self.frame = 0 
        else:
            self.estado = "walk" if vx != 0 else "Idle"
            self.frame = (self.frame + 0.2) % len(self.anim[self.estado])

        img_original = self.anim[self.estado][int(self.frame)]
        self.image = pygame.transform.flip(img_original, not self.facing_right, False)
        
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(midbottom=(self.rect.centerx, CHAO_Y + self.ajuste_y))
        
__all__ = ["Mago", "Magia", "RastroFantasma"]