import pygame
import random
import os
from scripts.settings import *
from scripts.utils import TextoFlutuante

# =====================================================
# RASTRO DE DASH
# =====================================================
class RastroFantasma(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image.copy()
        self.image.set_alpha(120)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.timer = 12

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.timer * 10)


# =====================================================
# MAGIA
# =====================================================
class Magia(pygame.sprite.Sprite):
    def __init__(self, x, y, nome, direcao, jogo, dono):
        super().__init__()
        self.jogo = jogo
        self.dono = dono
        self.nome = nome

        # Garante que usamos a chave correta no dicionário de configurações
        chave_feitico = nome
        if nome == "avada": chave_feitico = "avada kedavra"

        if chave_feitico in FEITICOS:
            dados = FEITICOS[chave_feitico]
            self.dano = dados["dano"]
            self.efeito = dados.get("efeito")
            self.velocidade = dados["vel"] * direcao
            self.cor = dados["cor"]
        else:
            # Fallback seguro caso haja erro de chave
            self.dano = 10
            self.velocidade = 10 * direcao
            self.cor = (255, 255, 255)

        self.image = pygame.Surface((50, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.cor, (25, 12), 9)
        pygame.draw.circle(self.image, (255, 255, 255), (22, 9), 4)

        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x += self.velocidade
        if self.rect.right < 0 or self.rect.left > LARGURA:
            self.kill()


# =====================================================
# MAGO
# =====================================================
class Mago(pygame.sprite.Sprite):
    def __init__(
        self, x, y, nome, jogo, controles, pasta_sprites,
        is_human=True, lado_inicial_dir=True
    ):
        super().__init__()

        self.jogo = jogo
        self.nome = nome
        self.controles = controles
        self.is_human = is_human
        self.facing_right = lado_inicial_dir

        # ---------------- STATUS ----------------
        self.vida_max = 100
        self.mana_max = 100
        self.vida = self.vida_max
        self.mana = self.mana_max

        self.escudo_ativo = False
        self.protego_timer = 0

        self.cast_cd = 0
        self.morto = False
        self.morte_iniciada = False

        # ---------------- ANIMAÇÃO ----------------
        self.estado = "Idle"
        self.frame = 0

        self.anim = {
            "Idle": [],
            "walk": [],
            "movfire": [],
            "dead": []
        }

        self._carregar_animacoes(pasta_sprites)

        self.image = self.anim["Idle"][0]
        # Aqui está o segredo do sprite não "voltar pra trás": midbottom
        self.rect = self.image.get_rect(midbottom=(x, y))

    # =================================================
    # CARREGAMENTO DE SPRITES
    # =================================================
    def _carregar_animacoes(self, pasta):
        escala = 2.2
        estados = {"Idle": 7, "walk": 6, "movfire": 4, "dead": 6}

        for estado, qtd in estados.items():
            for i in range(qtd):
                path = os.path.join(pasta, f"{estado}_{i}.png")
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(
                        img,
                        (int(img.get_width() * escala),
                         int(img.get_height() * escala))
                    )
                else:
                    img = pygame.Surface((50, 80), pygame.SRCALPHA)
                    img.fill((255, 0, 255))
                self.anim[estado].append(img)

    # =================================================
    # FEITIÇOS
    # =================================================
    def castar_feitico(self, nome):
        # Correção de chave: "avada" (tecla) vira "avada kedavra" (dados)
        nome_real = nome
        if nome == "avada":
            nome_real = "avada kedavra"

        if self.morto or self.cast_cd > 0:
            return

        if self.mana < FEITICOS[nome_real]["custo"]:
            return

        # Desconta Mana e inicia Cooldown
        self.mana -= FEITICOS[nome_real]["custo"]
        self.cast_cd = 40 # AUMENTADO DE 25 PARA 40 (Evita spam)
        self.estado = "movfire"
        self.frame = 0
        
        # --- ATUALIZAÇÃO DO SAVE (MAESTRIA) ---
        if self.is_human and hasattr(self.jogo, 'dados_globais'):
            dados = self.jogo.dados_globais
            if "maestria" not in dados: dados["maestria"] = {}
            if nome_real not in dados["maestria"]: dados["maestria"][nome_real] = 0
            dados["maestria"][nome_real] += 1
            from scripts.save_system import salvar_dados
            salvar_dados(dados)
        # ----------------------------------------

        if nome_real == "protego":
            self.escudo_ativo = True
            self.protego_timer = 90
            return

        direcao = 1 if self.facing_right else -1

        magia = Magia(
            self.rect.centerx + 40 * direcao,
            self.rect.centery - 30,
            nome_real, direcao, self.jogo, self
        )

        if self == self.jogo.player:
            self.jogo.magias_player.add(magia)
        else:
            self.jogo.magias_inimigo.add(magia)

    # =================================================
    # DANO
    # =================================================
    def receber_dano(self, origem, dano_forcado=None):
        if self.morto: return

        # Lógica do Protego
        if self.escudo_ativo and origem:
            origem.kill()
            self.escudo_ativo = False
            return

        dano = dano_forcado if dano_forcado is not None else origem.dano
        self.vida -= dano

        if origem:
            origem.kill()

        if self.vida <= 0:
            self.vida = 0
            self.morto = True
            self.jogo.iniciar_cena_morte(self)


    # =================================================
    # UPDATE
    # =================================================
    def update(self):
        # -------- MORTE --------
        if self.morto:
            if not self.morte_iniciada:
                self.estado = "dead"
                self.frame = 0
                self.morte_iniciada = True

            self.frame += 0.15
            if self.frame >= len(self.anim["dead"]):
                self.frame = len(self.anim["dead"]) - 1

            img = self.anim["dead"][int(self.frame)]
            self.image = pygame.transform.flip(img, not self.facing_right, False)
            # IMPORTANTE: Mantém a posição fixa no chão ao morrer
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            return

        # -------- TIMERS --------
        if self.cast_cd > 0:
            self.cast_cd -= 1

        if self.protego_timer > 0:
            self.protego_timer -= 1
            if self.protego_timer <= 0:
                self.escudo_ativo = False

        # IA Regenera mais devagar para não spammar feitiço infinito
        regen = 0.15 if self.is_human else 0.08
        self.mana = min(self.mana + regen, self.mana_max)

        vx = 0

        # -------- CONTROLE HUMANO --------
        if self.is_human:
            keys = pygame.key.get_pressed()

            if keys[self.controles["esquerda"]]:
                vx = -5
                self.facing_right = False
            if keys[self.controles["direita"]]:
                vx = 5
                self.facing_right = True
            
            # Dash
            if keys[self.controles.get("dash", pygame.K_LSHIFT)]:
                 # Pequeno cooldown para não dashar infinito
                 if self.cast_cd == 0 and self.mana >= 15:
                     self.mana -= 15
                     d = 1 if self.facing_right else -1
                     self.rect.x += 150 * d
                     self.jogo.fantasmas.add(RastroFantasma(self.rect.x, self.rect.y, self.image))

            # Magias
            for magia in ["incendio", "stupefy", "expelliarmus", "sectumsempra", "avada", "protego"]:
                if magia in self.controles and keys[self.controles[magia]]:
                    self.castar_feitico(magia)

        # -------- IA (MODIFICADA PARA NÃO COLAR) --------
        else:
            player = self.jogo.player
            dx = player.rect.centerx - self.rect.centerx
            dist = abs(dx)
            
            self.facing_right = dx > 0

            # Distância de segurança aumentada de 150 para 300
            # Se tiver longe, aproxima. Se tiver perto, para.
            if dist > 350:
                vx = 3 if dx > 0 else -3
            elif dist < 150: # Se tiver muito perto, afasta (Kiting)
                vx = -3 if dx > 0 else 3

            # Chance de ataque reduzida de 3% (0.03) para 1.5% (0.015)
            # E adicionado check de distância para não atirar no vento
            if self.cast_cd == 0 and dist < 700:
                roll = random.random()
                if roll < 0.015:
                    self.castar_feitico(random.choice(["incendio", "stupefy"]))
                elif roll < 0.018: # Pequena chance de protego
                    self.castar_feitico("protego")

        self.rect.x += vx
        
        # Limites da Tela
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > LARGURA: self.rect.right = LARGURA

        # -------- ANIMAÇÃO --------
        if self.estado == "movfire":
            self.frame += 0.3
            if self.frame >= len(self.anim["movfire"]):
                self.estado = "Idle" if vx == 0 else "walk"
                self.frame = 0
        else:
            if vx != 0:
                self.estado = "walk"
            else:
                self.estado = "Idle"

            self.frame = (self.frame + 0.2) % len(self.anim[self.estado])

        # -------- SPRITE FINAL --------
        img = self.anim[self.estado][int(self.frame)]
        self.image = pygame.transform.flip(img, not self.facing_right, False)
        
        # AQUI É A CHAVE DO PROBLEMA DO SPRITE:
        # Usamos midbottom para que, se o sprite mudar de tamanho, o pé continue no mesmo pixel.
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)


# =====================================================
# EXPORTS
# =====================================================
__all__ = ["Mago", "Magia", "RastroFantasma"]