import pygame
import sys
import os
import threading
import socket
import random
import subprocess
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from scripts.settings import *
    from scripts.utils import Botao, Slider, Checkbox, BotaoAjuda, TextoFlutuante, ParticulaMagica, gerar_cenario_procedural
    from scripts.entities import Mago
    from scripts.save_system import carregar_dados, salvar_dados
    from scripts.grimorio import Grimorio
    from scripts.perfil_player import PerfilJogador 
    from scripts.training_mode import ModoTreinamento
    from scripts.desafios import TelaDesafios
    from scripts.creditos import TelaCreditos
    from scripts.network import CLIENTE_ONLINE
    
    try:
        from scripts.camera_controle import start_camera, CONTROLE_CAMERA
        TEM_CAMERA = True
    except ImportError:
        TEM_CAMERA = False
        CONTROLE_CAMERA = {}

    try:
        from scripts.server_controle import start_remote, CONTROLE_REMOTO, atualizar_estado_jogo
        TEM_MOBILE = True
    except ImportError:
        TEM_MOBILE = False
        CONTROLE_REMOTO = {}
        def atualizar_estado_jogo(e): pass

except ImportError as e:
    print(f"ERRO CRÍTICO DE IMPORTAÇÃO: {e}")
    sys.exit(1)

try:
    import speech_recognition as sr
    TEM_VOZ = True
except ImportError:
    TEM_VOZ = False

class Jogo:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # --- PROGRESSÃO ARCADE ---
        self.indice_arcade = 0
        # Lista de oponentes na ordem: P2 -> P3 -> P4 -> P5 -> Goose
        self.oponentes_arcade = ["data/P2", "data/P3", "data/P4", "data/Goose"]
        # -------------------------

        caminho_server = os.path.join("scripts", "server_rank.py")
        self.processo_server = None
        if os.path.exists(caminho_server):
            try:
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                self.processo_server = subprocess.Popen(
                    [sys.executable, caminho_server], 
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
                )
                print("Servidor Rankeado Iniciado.")
            except: pass

        try: self.tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN | pygame.SCALED)
        except: self.tela = pygame.display.set_mode((LARGURA, ALTURA))
            
        pygame.display.set_caption(TITULO)
        pygame.mouse.set_visible(False)
        self.relogio = pygame.time.Clock()
        self.dados_globais = carregar_dados()
        if TEM_MOBILE: start_remote()
        self.carregar_assets()

        self.musica_atual = None
        self.musica_fundo_path = "data/sons/tela-inicial.mp3"
        self.musica_batalha_path = "data/sons/tela-de-luta.mp3"
        if os.path.exists(self.musica_fundo_path): self.tocar_musica(self.musica_fundo_path)

        self.fonte_titulo = pygame.font.SysFont("Garamond", 60, bold=True)
        self.fonte_ui = pygame.font.SysFont("Garamond", 22)
        self.fonte_aviso = pygame.font.SysFont("Arial", 40, bold=True)
        self.fonte_fps = pygame.font.SysFont("Arial", 18, bold=True)
        self.criar_botoes_menu()
        self.criar_elementos_config()
        self.grimorio = Grimorio(self)
        self.perfil_jogador = PerfilJogador(self)
        self.tela_desafios = TelaDesafios(self)
        self.tela_creditos = TelaCreditos(self)

        self.rodando = True
        self.estado = INTRO
        self.modo_jogo = 1 
        self.aviso_temp = ""
        self.timer_aviso = 0
        self.mostrando_modos = False
        self.timer_matchmaking = 0
        self.timer_cutscene = 0 # Timer para a tela preta do pato
        
        self.usar_camera = False; self.usar_voz = False; self.usar_mobile = True; self.mostrar_fps = False
        self.confirmando_reset = False
        self.player = None; self.inimigo = None
        self.todos_sprites = pygame.sprite.Group(); self.magias_player = pygame.sprite.Group()
        self.magias_inimigo = pygame.sprite.Group(); self.fantasmas = pygame.sprite.Group()
        self.particulas = []; self.textos_flutuantes = []

        if TEM_VOZ:
            try:
                self.reconhecedor = sr.Recognizer(); self.microfone = sr.Microphone()
                threading.Thread(target=self.ouvir_voz, daemon=True).start()
            except: self.usar_voz = False

    def tocar_musica(self, caminho):
        if self.musica_atual == caminho: return 
        if os.path.exists(caminho):
            self.musica_atual = caminho
            pygame.mixer.music.stop()
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(self.slider_musica.valor if hasattr(self, "slider_musica") else 0.3)
            pygame.mixer.music.play(-1)

    def criar_sprite_varinha(self):
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.line(s, (100, 50, 0), (28, 28), (10, 10), 4)
        pygame.draw.circle(s, (200, 255, 255), (8, 8), 4)
        return s

    def carregar_assets(self):
        self.cursor_img = self.criar_sprite_varinha()
        self.bg_jogo = self.carregar_imagem("data/cenario.png", fallback_func=lambda: gerar_cenario_procedural(LARGURA, ALTURA, CHAO_Y))
        self.bg_menu = self.carregar_imagem("data/telas/menu.png", fallback_cor=(20, 20, 40))
        self.bg_intro = self.carregar_imagem("data/telas/intro.png", fallback_cor=(0, 0, 0))
        self.bg_vitoria = self.carregar_imagem("data/telas/vitoria.png", fallback_cor=(0, 50, 0))
        self.bg_derrota = self.carregar_imagem("data/telas/derrota.png", fallback_cor=(50, 0, 0))
        self.snd_cast = None
        if os.path.exists("data/sounds/cast.wav"): self.snd_cast = pygame.mixer.Sound("data/sounds/cast.wav")

    def carregar_imagem(self, path, fallback_cor=None, fallback_func=None):
        if os.path.exists(path):
            try: return pygame.transform.scale(pygame.image.load(path).convert(), (LARGURA, ALTURA))
            except: pass
        if fallback_func: return fallback_func()
        s = pygame.Surface((LARGURA, ALTURA)); s.fill(fallback_cor if fallback_cor else (0,0,0))
        return s
# Dentro de main.py:

    def criar_botoes_menu(self):
        # Usamos cor_fundo=None para deixar invisível
        self.botoes_menu = {
            "jogar": Botao(98, 139, 214, 51, texto="", cor_fundo=None), 
            "treino": Botao(98, 192, 280, 53, texto="", cor_fundo=None),
            "perfil": Botao(97, 248, 227, 56, texto="", cor_fundo=None),
            "grimorio": Botao(97, 305, 258, 57, texto="", cor_fundo=None),
            "desafios": Botao(96, 363, 235, 59, texto="", cor_fundo=None),
            "config": Botao(99, 424, 320, 52, texto="", cor_fundo=None),
            "creditos": Botao(96, 480, 244, 56, texto="", cor_fundo=None),
            "sair": Botao(97, 538, 223, 53, texto="", cor_fundo=None) 
        }
        
        cx, cy = LARGURA // 2, ALTURA // 2
        # Estes continuam com cor pois são submenus
        self.botoes_modos = {
            "ia": Botao(cx - 150, cy - 80, 300, 55, "MODO ARCADE (IA)", (50, 50, 80)),
            "p2": Botao(cx - 150, cy - 10, 300, 55, "CONTRA P2", (50, 50, 80)),
            "rank": Botao(cx - 150, cy + 60, 300, 55, "RANKEADA", (50, 50, 80)),
            "voltar": Botao(cx - 150, cy + 150, 300, 55, "VOLTAR", (80, 20, 20))
        }
        
        self.botoes_vitoria = {
            "continuar": Botao(386, 640, 225, 60, texto="", cor_fundo=None), 
            "menu": Botao(659, 638, 221, 60, texto="", cor_fundo=None)
        }
        self.botoes_derrota = {
            "revanche": Botao(391, 635, 224, 60, texto="", cor_fundo=None), 
            "menu": Botao(659, 635, 222, 60, texto="", cor_fundo=None)
        }
    def criar_elementos_config(self):
        cx, cy = LARGURA // 2, ALTURA // 2
        self.rect_painel_config = pygame.Rect(cx - 300, cy - 250, 600, 500)
        self.slider_musica = Slider(cx - 100, cy - 120, 200, 0, 1, 0.3)
        self.slider_sfx = Slider(cx - 100, cy - 60, 200, 0, 1, 1.0)
        self.chk_mobile = Checkbox(cx - 100, cy, "Mobile", ativo=True); self.chk_voz = Checkbox(cx - 100, cy + 30, "Voz", ativo=False)
        self.chk_camera = Checkbox(cx - 100, cy + 60, "Câmera", ativo=False); self.chk_fps = Checkbox(cx - 100, cy + 90, "FPS", ativo=False)
        y_btns = cy + 150
        self.btn_reset = Botao(cx - 210, y_btns, 130, 40, "Resetar", (100,20,20), 18); self.btn_calibrar = Botao(cx - 65, y_btns, 130, 40, "Calibrar", (30,30,60), 18); self.btn_voltar_conf = Botao(cx + 80, y_btns, 130, 40, "Voltar", (50,50,50), 18)
        self.tip_musica = BotaoAjuda(cx+130, cy-120, "Música", ["Volume."]); self.tip_sfx = BotaoAjuda(cx+130, cy-60, "Efeitos", ["Sons."])
        try: ip = socket.gethostbyname(socket.gethostname())
        except: ip = "127.0.0.1"
        self.tip_mobile = BotaoAjuda(cx+200, cy, "Mobile", [f"WiFi: {ip}:5000"]); self.tip_voz = BotaoAjuda(cx+170, cy+30, "Voz", ["Fale feitiços."]); self.tip_camera = BotaoAjuda(cx+170, cy+60, "Câmera", ["Cor."]); self.tip_fps = BotaoAjuda(cx+170, cy+90, "FPS", ["Frames."])
        self.btn_confirma_sim = Botao(cx-80, cy+20, 70, 40, "SIM", (100,0,0)); self.btn_confirma_nao = Botao(cx+10, cy+20, 70, 40, "NÃO", (0,100,0))

    def ouvir_voz(self):
        with self.microfone as source:
            try: self.reconhecedor.adjust_for_ambient_noise(source)
            except: return
            while self.rodando:
                if self.estado == JOGO and self.usar_voz and self.modo_jogo == 1:
                    try:
                        audio = self.reconhecedor.listen(source, timeout=1, phrase_time_limit=2)
                        texto = self.reconhecedor.recognize_google(audio, language='pt-BR').lower()
                        self.processar_comando_voz(texto)
                    except: pass

    def processar_comando_voz(self, texto):
        if not self.player or self.player.morto: return
        if "fogo" in texto or "incendio" in texto: self.player.castar_feitico("incendio")
        elif "escudo" in texto or "protego" in texto: self.player.castar_feitico("protego")
        elif "expelliarmus" in texto: self.player.castar_feitico("expelliarmus")
        elif "avada" in texto: self.player.castar_feitico("avada kedavra")

    def iniciar_batalha(self, modo):
        self.modo_jogo = modo
        self.todos_sprites.empty(); self.magias_player.empty(); self.magias_inimigo.empty(); self.fantasmas.empty()
        self.particulas = []; self.textos_flutuantes = []
        
        ctrl_p1 = CONTROLES_SOLO if modo != 2 else CONTROLES_P1_PVP
        ctrl_p2 = CONTROLES_P2_PVP if modo == 2 else {}
        is_p2_human = (modo == 2)
        
        # --- DEFINIÇÃO DO OPONENTE ARCADE ---
        pasta_oponente = "data/P1" # Padrão
        nome_p2 = "Oponente"
        dificuldade = 1.0
        
        if modo == 1: # ARCADE
            pasta_oponente = self.oponentes_arcade[self.indice_arcade]
            # Extrai nome da pasta (ex: "data/Goose" -> "Goose")
            nome_p2 = os.path.basename(pasta_oponente)
            
            # Dificuldade aumenta conforme avança
            dificuldade = 1.0 + (self.indice_arcade * 0.5) 
            
        elif modo == 3: # RANKED
            nome_p2 = "Guardião (Ranked)"
            pasta_oponente = "data/P5" # Ranked sempre difícil
            dificuldade = 2.0
        else: # P2
            nome_p2 = "Player 2"
        # ------------------------------------
        
        self.player = Mago(200, CHAO_Y, "Harry", self, ctrl_p1, "data/P1", True, True)
        # Cria inimigo com a pasta e dificuldade calculada
        self.inimigo = Mago(LARGURA - 200, CHAO_Y, nome_p2, self, ctrl_p2, pasta_oponente, is_p2_human, False, dificuldade)
        
        self.player.magias_player = self.magias_player; self.player.magias_inimigo = self.magias_inimigo
        self.inimigo.magias_player = self.magias_player; self.inimigo.magias_inimigo = self.magias_inimigo
        self.player.fantasmas = self.fantasmas; self.inimigo.fantasmas = self.fantasmas
        
        self.todos_sprites.add(self.player, self.inimigo)
        self.mudar_estado(JOGO)

    def iniciar_cena_morte(self, quem):
        if self.estado != JOGO: return
        self.fim_de_jogo = True
        self.mudar_estado(CENA_MORTE)
        self.timer_morte = 60

    def mudar_estado(self, novo):
        self.estado = novo
        if TEM_MOBILE: atualizar_estado_jogo(novo)
        pygame.event.clear()
        if novo == JOGO: self.tocar_musica(self.musica_batalha_path)
        elif novo in [MENU, INTRO, CONFIG, GRIMORIO, PERFIL, DESAFIOS, CREDITOS, VITORIA, DERROTA, CUTSCENE_BOSS]:
            self.tocar_musica(self.musica_fundo_path)

    def iniciar_disputa(self):
        self.mudar_estado(DISPUTA); self.clash_progress = 50 

    def update_jogo(self):
        self.player.update(); self.inimigo.update()
        self.magias_player.update(); self.magias_inimigo.update(); self.fantasmas.update()
        
        # DISPUTA (Se magias colidirem)
        hits_magia = pygame.sprite.groupcollide(self.magias_player, self.magias_inimigo, True, True, pygame.sprite.collide_mask)
        if hits_magia: self.iniciar_disputa(); return
            
        # DANO NO INIMIGO (Usando Máscara/Pixel Perfect)
        hits1 = pygame.sprite.spritecollide(self.inimigo, self.magias_player, True, pygame.sprite.collide_mask)
        for m in hits1: 
            self.inimigo.receber_dano(m); self.criar_efeito_impacto(m.rect.center)
            
        # DANO NO PLAYER (Usando Máscara/Pixel Perfect)
        hits2 = pygame.sprite.spritecollide(self.player, self.magias_inimigo, True, pygame.sprite.collide_mask)
        for m in hits2: 
            self.player.receber_dano(m); self.criar_efeito_impacto(m.rect.center)

        # DANO FÍSICO DO PATO (Colisão com Máscara)
        if "Goose" in self.inimigo.pasta:
            if pygame.sprite.collide_mask(self.player, self.inimigo):
                self.player.receber_dano(None, 2)
                self.player.rect.x -= 10 

        self.processar_inputs_externos()

    def processar_inputs_externos(self):
        if TEM_MOBILE and self.usar_mobile and not self.player.morto:
            if CONTROLE_REMOTO.get("esquerda"): self.player.rect.x -= 5
            elif CONTROLE_REMOTO.get("direita"): self.player.rect.x += 5
            if CONTROLE_REMOTO.get("dash"): 
                self.player.ativar_dash(); CONTROLE_REMOTO["dash"] = False
            for f in ["incendio", "protego", "expelliarmus", "avada"]:
                if CONTROLE_REMOTO.get(f):
                    self.player.castar_feitico("avada kedavra" if f == "avada" else f)
                    CONTROLE_REMOTO[f] = False
        if TEM_CAMERA and self.usar_camera and CONTROLE_CAMERA.get("ativo"):
            if CONTROLE_CAMERA.get("clique"): self.player.castar_feitico("incendio"); CONTROLE_CAMERA["clique"] = False

    def update_disputa(self):
        if self.modo_jogo != 2:
            dificuldade = 4 
            forca = 10
            if self.modo_jogo == 3: dificuldade = 8; forca = 12
            if random.randint(0, 100) < dificuldade: self.clash_progress -= forca
        
        if self.clash_progress >= 100:
            self.mudar_estado(JOGO); self.inimigo.receber_dano(None, 20); self.criar_efeito_impacto(self.inimigo.rect.center); self.clash_progress = 50
        elif self.clash_progress <= 0:
            self.mudar_estado(JOGO); self.player.receber_dano(None, 20); self.criar_efeito_impacto(self.player.rect.center); self.clash_progress = 50

    def criar_efeito_impacto(self, pos):
        if self.snd_cast: self.snd_cast.play()
        self.textos_flutuantes.append(TextoFlutuante(pos[0], pos[1]-20, "HIT!", (255,200,0)))
        for _ in range(10): self.particulas.append(ParticulaMagica(pos[0], pos[1], (255, 100, 0), "explosao"))

    def desenhar_hud(self):
        # --- HUD DO PLAYER ---
        pygame.draw.rect(self.tela, SANGUE_ESCURO, (50, 50, 200 * (self.player.vida/self.player.vida_max), 20))
        pygame.draw.rect(self.tela, AZUL_MANA, (50, 75, 200 * (self.player.mana/self.player.mana_max), 10)) # <--- Ajustei aqui também para garantir
        pygame.draw.rect(self.tela, BRANCO, (50, 50, 200, 20), 2)
        
        # --- HUD DO INIMIGO ---
        offset = LARGURA - 250
        pygame.draw.rect(self.tela, SANGUE_ESCURO, (offset, 50, 200 * (self.inimigo.vida/self.inimigo.vida_max), 20))
        pygame.draw.rect(self.tela, BRANCO, (offset, 50, 200, 20), 2)
        
        if "Goose" not in self.inimigo.pasta: # Pato não tem mana
            # AQUI ESTAVA O ERRO: Mudei de 100 para self.inimigo.mana_max
            pygame.draw.rect(self.tela, AZUL_MANA, (offset, 75, 200 * (self.inimigo.mana / self.inimigo.mana_max), 10))

    def loop(self):
        while self.rodando:
            self.relogio.tick(60)
            mx, my = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.rodando = False
                if self.estado == GRIMORIO: self.grimorio.processar_eventos(event)
                if self.estado == PERFIL: self.perfil_jogador.processar_eventos(event)
                if self.estado == DESAFIOS: self.tela_desafios.processar_eventos(event)
                if self.estado == CREDITOS: self.tela_creditos.processar_eventos(event)

                if event.type == pygame.KEYDOWN and self.estado == DISPUTA:
                    if event.key == pygame.K_SPACE: self.clash_progress += 15
                    if self.modo_jogo == 2 and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER): self.clash_progress -= 15

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.estado == INTRO: self.mudar_estado(MENU)
                    elif self.estado == MENU:
                        if self.mostrando_modos:
                            # --- MODO ARCADE (1) ---
                            if self.botoes_modos["ia"].desenhar(self.tela): 
                                self.indice_arcade = 0 # Começa do zero
                                self.iniciar_batalha(1)
                                self.mostrando_modos=False
                            # -----------------------
                            elif self.botoes_modos["p2"].desenhar(self.tela): self.iniciar_batalha(2); self.mostrando_modos=False
                            elif self.botoes_modos["voltar"].desenhar(self.tela): self.mostrando_modos=False
                            elif self.botoes_modos["rank"].desenhar(self.tela): 
                                if not CLIENTE_ONLINE.conectado:
                                    self.aviso_temp = "FAÇA LOGIN NO PERFIL!"; self.timer_aviso = 120
                                else:
                                    self.mudar_estado(PROCURANDO); self.timer_matchmaking = 120; self.mostrando_modos = False
                        else:
                            if self.botoes_menu["jogar"].desenhar(self.tela): self.mostrando_modos = True
                            elif self.botoes_menu["treino"].desenhar(self.tela): 
                                self.tocar_musica(self.musica_batalha_path)
                                ModoTreinamento(self).rodar()
                                self.tocar_musica(self.musica_fundo_path)
                                self.mudar_estado(MENU)
                            elif self.botoes_menu["perfil"].desenhar(self.tela): self.mudar_estado(PERFIL)
                            elif self.botoes_menu["grimorio"].desenhar(self.tela): self.mudar_estado(GRIMORIO)
                            elif self.botoes_menu["desafios"].desenhar(self.tela): self.mudar_estado(DESAFIOS)
                            elif self.botoes_menu["config"].desenhar(self.tela): self.mudar_estado(CONFIG)
                            elif self.botoes_menu["creditos"].desenhar(self.tela): self.tela_creditos.resetar(); self.mudar_estado(CREDITOS)
                            elif self.botoes_menu["sair"].desenhar(self.tela): self.rodando = False

                    elif self.estado == CONFIG:
                        if self.confirmando_reset:
                            if self.btn_confirma_sim.desenhar(self.tela): self.dados_globais={"partidas_totais":0,"vitorias_p1":0,"vitorias_p2":0,"vitorias_ia":0,"maestria":{}}; salvar_dados(self.dados_globais); self.aviso_temp="RESETADO!"; self.timer_aviso=60; self.confirmando_reset=False
                            elif self.btn_confirma_nao.desenhar(self.tela): self.confirmando_reset=False
                        else:
                            if self.btn_voltar_conf.desenhar(self.tela): self.mudar_estado(MENU)
                            if self.chk_mobile.checar_clique(event.pos): self.usar_mobile = self.chk_mobile.ativo
                            if self.chk_voz.checar_clique(event.pos): self.usar_voz = self.chk_voz.ativo
                            if self.chk_camera.checar_clique(event.pos): self.usar_camera = self.chk_camera.ativo
                            if self.chk_fps.checar_clique(event.pos): self.mostrar_fps = self.chk_fps.ativo
                            if self.btn_calibrar.desenhar(self.tela): 
                                if TEM_CAMERA: start_camera()
                            if self.btn_reset.desenhar(self.tela): self.confirmando_reset = True

                    elif self.estado in [VITORIA, DERROTA]:
                        if self.botoes_vitoria["menu"].desenhar(self.tela): 
                            self.botoes_vitoria["menu"].clicado = False; self.mudar_estado(MENU)
                        
                        if self.estado == VITORIA and self.botoes_vitoria["continuar"].desenhar(self.tela):
                             self.botoes_vitoria["continuar"].clicado = False
                             
                             # --- LÓGICA DE PROGRESSÃO ARCADE ---
                             if self.modo_jogo == 1: # Arcade
                                 self.indice_arcade += 1
                                 
                                 # Se chegou no final (Pato)
                                 if self.indice_arcade >= len(self.oponentes_arcade):
                                     self.aviso_temp = "VOCÊ ZEROU O ARCADE!"; self.timer_aviso = 120
                                     self.mudar_estado(MENU)
                                 elif "Goose" in self.oponentes_arcade[self.indice_arcade]:
                                     # Tela Preta do Pato
                                     self.mudar_estado(CUTSCENE_BOSS)
                                     self.timer_cutscene = 240 # 4 segundos
                                 else:
                                     # Próximo mago normal
                                     self.iniciar_batalha(1)
                             else:
                                 # Outros modos (P2/Rank) apenas reiniciam
                                 self.iniciar_batalha(self.modo_jogo)
                             # -----------------------------------

                        if self.estado == DERROTA and self.botoes_derrota["revanche"].desenhar(self.tela):
                             self.botoes_derrota["revanche"].clicado = False; self.iniciar_batalha(self.modo_jogo)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.estado in [JOGO, GRIMORIO, CONFIG, PERFIL, DESAFIOS, CREDITOS]: self.mudar_estado(MENU)

            self.tela.fill(PRETO)
            if self.estado == INTRO: self.tela.blit(self.bg_intro, (0,0))
            elif self.estado == MENU:
                self.tela.blit(self.bg_menu, (0,0))
                if self.mostrando_modos:
                    for k,b in self.botoes_modos.items(): b.desenhar(self.tela)
                else:
                    for k,b in self.botoes_menu.items(): b.desenhar(self.tela)
            
            elif self.estado == PROCURANDO:
                self.tela.blit(self.bg_menu, (0,0))
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA); overlay.fill((0,0,0,200)); self.tela.blit(overlay, (0,0))
                dots = "." * (int(pygame.time.get_ticks() / 500) % 4)
                txt = self.fonte_titulo.render(f"Procurando Oponente{dots}", True, OURO)
                self.tela.blit(txt, (LARGURA//2 - txt.get_width()//2, ALTURA//2))
                self.timer_matchmaking -= 1
                if self.timer_matchmaking <= 0: self.iniciar_batalha(3)

            # --- CUTSCENE DO BOSS ---
            elif self.estado == CUTSCENE_BOSS:
                self.tela.fill(PRETO)
                txt = self.fonte_titulo.render("Você derrotaria um pato?", True, (255, 0, 0))
                self.tela.blit(txt, (LARGURA//2 - txt.get_width()//2, ALTURA//2))
                self.timer_cutscene -= 1
                if self.timer_cutscene <= 0:
                    self.iniciar_batalha(1) # Inicia a luta contra o Pato
            # ------------------------

            elif self.estado == GRIMORIO: self.tela.blit(self.bg_menu, (0,0)); self.grimorio.desenhar(self.tela)
            elif self.estado == PERFIL: self.tela.blit(self.bg_menu, (0,0)); self.perfil_jogador.desenhar()
            elif self.estado == DESAFIOS: self.tela.blit(self.bg_menu, (0,0)); self.tela_desafios.desenhar()
            elif self.estado == CREDITOS: self.tela_creditos.desenhar()
            elif self.estado == CONFIG:
                self.tela.blit(self.bg_menu, (0,0))
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA); overlay.fill((0,0,0,220)); self.tela.blit(overlay, (0,0))
                pygame.draw.rect(self.tela, (30, 30, 30), self.rect_painel_config, border_radius=10)
                pygame.draw.rect(self.tela, OURO_ANTIGO, self.rect_painel_config, 3, border_radius=10)
                tit = self.fonte_titulo.render("CONFIGURAÇÕES", True, OURO_ANTIGO)
                self.tela.blit(tit, (LARGURA//2 - tit.get_width()//2, self.rect_painel_config.y + 30))
                lbl_mus = self.fonte_ui.render(f"Música: {int(self.slider_musica.valor*100)}%", True, BRANCO)
                self.tela.blit(lbl_mus, (self.slider_musica.rect.x, self.slider_musica.rect.y - 25)); self.slider_musica.desenhar(self.tela)
                self.tip_musica.desenhar(self.tela)
                lbl_sfx = self.fonte_ui.render(f"Efeitos: {int(self.slider_sfx.valor*100)}%", True, BRANCO)
                self.tela.blit(lbl_sfx, (self.slider_sfx.rect.x, self.slider_sfx.rect.y - 25)); self.slider_sfx.desenhar(self.tela)
                self.tip_sfx.desenhar(self.tela)
                self.chk_mobile.desenhar(self.tela); self.tip_mobile.desenhar(self.tela)
                self.chk_voz.desenhar(self.tela); self.tip_voz.desenhar(self.tela)
                self.chk_camera.desenhar(self.tela); self.tip_camera.desenhar(self.tela)
                self.chk_fps.desenhar(self.tela); self.tip_fps.desenhar(self.tela)
                self.btn_reset.desenhar(self.tela); self.btn_calibrar.desenhar(self.tela); self.btn_voltar_conf.desenhar(self.tela)
                if not self.confirmando_reset:
                    vol_mus = self.slider_musica.update(); vol_sfx = self.slider_sfx.update()
                    pygame.mixer.music.set_volume(vol_mus)
                    if self.snd_cast: self.snd_cast.set_volume(vol_sfx)
                self.tip_musica.desenhar_tooltip(self.tela); self.tip_sfx.desenhar_tooltip(self.tela); self.tip_mobile.desenhar_tooltip(self.tela); self.tip_voz.desenhar_tooltip(self.tela); self.tip_camera.desenhar_tooltip(self.tela); self.tip_fps.desenhar_tooltip(self.tela)
                if self.confirmando_reset:
                    cx, cy = LARGURA//2, ALTURA//2; rect_pop = pygame.Rect(cx - 150, cy - 80, 300, 160)
                    pygame.draw.rect(self.tela, (10, 10, 10), rect_pop); pygame.draw.rect(self.tela, (255, 0, 0), rect_pop, 2)
                    msg = self.fonte_ui.render("Tem certeza?", True, BRANCO); self.tela.blit(msg, (cx - msg.get_width()//2, cy - 50))
                    self.btn_confirma_sim.desenhar(self.tela); self.btn_confirma_nao.desenhar(self.tela)
                if self.timer_aviso > 0: self.timer_aviso -= 1; av = self.fonte_aviso.render(self.aviso_temp, True, BRANCO); self.tela.blit(av, (LARGURA//2 - av.get_width()//2, ALTURA - 100))

            elif self.estado == JOGO:
                self.tela.blit(self.bg_jogo, (0,0))
                self.update_jogo()
                self.fantasmas.draw(self.tela)
                self.tela.blit(self.player.image, self.player.rect); self.tela.blit(self.inimigo.image, self.inimigo.rect)
                if self.player.escudo_ativo: pygame.draw.circle(self.tela, COR_PROTEGO, self.player.rect.center, 50, 2)
                if self.inimigo.escudo_ativo: pygame.draw.circle(self.tela, COR_PROTEGO, self.inimigo.rect.center, 50, 2)
                self.magias_player.draw(self.tela); self.magias_inimigo.draw(self.tela)
                for p in self.particulas: p.update(); p.draw(self.tela)
                for t in self.textos_flutuantes: t.update(); t.draw(self.tela)
                self.desenhar_hud()
                if self.mostrar_fps: fps = int(self.relogio.get_fps()); self.tela.blit(self.fonte_fps.render(f"FPS: {fps}", True, (0,255,0)), (LARGURA-80, 50))

            elif self.estado == DISPUTA:
                self.tela.blit(self.bg_jogo, (0,0))
                self.tela.blit(self.player.image, self.player.rect); self.tela.blit(self.inimigo.image, self.inimigo.rect)
                self.update_disputa()
                lar = 400; pygame.draw.rect(self.tela, PRETO_FUNDO, (LARGURA//2-200, ALTURA//2-50, lar, 40))
                pygame.draw.rect(self.tela, VERDE_CLASH, (LARGURA//2-200, ALTURA//2-50, (self.clash_progress/100)*lar, 40))
                t = "P1: ESPAÇO" if self.modo_jogo != 2 else "P1: ESPAÇO | P2: ENTER"
                m = self.fonte_fps.render(t, True, OURO); self.tela.blit(m, (LARGURA//2 - m.get_width()//2, ALTURA//2 - 100))

            elif self.estado == CENA_MORTE:
                self.tela.blit(self.bg_jogo, (0,0))
                self.player.update(); self.inimigo.update()
                self.tela.blit(self.player.image, self.player.rect); self.tela.blit(self.inimigo.image, self.inimigo.rect)
                
                self.timer_morte -= 1
                if self.timer_morte <= 0:
                    vitoria_player = not self.player.morto
                    
                    if self.modo_jogo == 3 and CLIENTE_ONLINE.conectado:
                        CLIENTE_ONLINE.enviar_partida("win" if vitoria_player else "loss")
                        if vitoria_player: self.aviso_temp = "ELO ATUALIZADO!"
                    
                    self.dados_globais["partidas_totais"] += 1
                    
                    if vitoria_player: 
                        self.dados_globais["vitorias_p1"] += 1; self.mudar_estado(VITORIA)
                    else: 
                        # --- MODIFICAÇÃO AQUI: Lógica do Pato ---
                        if "Goose" in self.inimigo.pasta:
                            # Tela preta secreta
                            self.tela.fill((0, 0, 0))
                            
                            # Textos
                            txt1 = self.fonte_titulo.render("Não, você não consegue.", True, (255, 0, 0))
                            txt2 = self.fonte_titulo.render("Não bata em animais.", True, (255, 255, 255))
                            
                            # Centraliza e desenha
                            self.tela.blit(txt1, (LARGURA//2 - txt1.get_width()//2, ALTURA//2 - 40))
                            self.tela.blit(txt2, (LARGURA//2 - txt2.get_width()//2, ALTURA//2 + 40))
                            
                            pygame.display.flip()
                            pygame.time.delay(4000) # Espera 4 segundos lendo a mensagem
                            
                            self.mudar_estado(MENU) # Volta direto pro menu
                        else:
                            self.mudar_estado(DERROTA) # Derrota normal
                        # ----------------------------------------

                    salvar_dados(self.dados_globais)

            elif self.estado in [VITORIA, DERROTA]:
                bg = self.bg_vitoria if self.estado == VITORIA else self.bg_derrota
                self.tela.blit(bg, (0,0))

            if self.estado != INTRO and self.estado != DISPUTA: self.tela.blit(self.cursor_img, (mx-16, my-16))
            if self.timer_aviso > 0: self.timer_aviso -= 1; t = self.fonte_aviso.render(self.aviso_temp, True, BRANCO); self.tela.blit(t, (LARGURA//2-t.get_width()//2, ALTURA-100))
            
            pygame.display.flip()
        
        if self.processo_server: self.processo_server.terminate()
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    Jogo().loop()