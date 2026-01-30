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
        
        # --- AUTO-START SERVIDOR RANKED ---
        caminho_server = os.path.join("scripts", "server_rank.py")
        self.processo_server = None
        if os.path.exists(caminho_server):
            try:
                # Inicia o servidor em segundo plano sem abrir janela extra
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                self.processo_server = subprocess.Popen(
                    [sys.executable, caminho_server], 
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
                )
                print("Servidor Rankeado Iniciado Automaticamente.")
            except Exception as e:
                print(f"Aviso: Não foi possível iniciar o servidor automaticamente. Erro: {e}")
        # ----------------------------------

        try:
            self.tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN | pygame.SCALED)
        except:
            self.tela = pygame.display.set_mode((LARGURA, ALTURA))
            
        pygame.display.set_caption(TITULO)
        pygame.mouse.set_visible(False)
        
        self.relogio = pygame.time.Clock()
        self.dados_globais = carregar_dados()

        if TEM_MOBILE: start_remote()

        self.carregar_assets()

        # >>> ADICIONADO: iniciar música de fundo <<<
        if os.path.exists(self.musica_fundo_path):
            pygame.mixer.music.load(self.musica_fundo_path)
            pygame.mixer.music.set_volume(self.slider_musica.valor if hasattr(self, "slider_musica") else 0.3)
            pygame.mixer.music.play(-1)

                    # >>> ADICIONADO: caminho da música da batalha <<<
        self.musica_batalha_path = "data/sons/tela-de-luta.mp3"


        self.fonte_titulo = pygame.font.SysFont("Garamond", 60, bold=True)
        self.fonte_ui = pygame.font.SysFont("Garamond", 22)
        self.fonte_aviso = pygame.font.SysFont("Arial", 40, bold=True)
        self.fonte_fps = pygame.font.SysFont("Arial", 18, bold=True)
        
        self.criar_botoes_menu()
        self.criar_elementos_config()
        
        # --- INICIALIZAÇÃO DAS TELAS ---
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
        
        # Matchmaking
        self.timer_matchmaking = 0
        
        self.usar_camera = False
        self.usar_voz = False
        self.usar_mobile = True
        self.mostrar_fps = False
        
        self.confirmando_reset = False

        self.player = None
        self.inimigo = None
        self.todos_sprites = pygame.sprite.Group()
        self.magias_player = pygame.sprite.Group()
        self.magias_inimigo = pygame.sprite.Group()
        self.fantasmas = pygame.sprite.Group()
        self.particulas = []
        self.textos_flutuantes = []

        if TEM_VOZ:
            try:
                self.reconhecedor = sr.Recognizer()
                self.microfone = sr.Microphone()
                # Tenta iniciar a thread. Se o PyAudio faltar, o erro acontece aqui dentro
                threading.Thread(target=self.ouvir_voz, daemon=True).start()
            except Exception as e:
                print(f"[AVISO] Controle de voz desativado (PyAudio não encontrado): {e}")
                self.usar_voz = False
                # Removemos a linha "TEM_VOZ = False" que causava o erro

    def criar_sprite_varinha(self):
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.line(surf, (100, 50, 0), (28, 28), (10, 10), 4)
        pygame.draw.circle(surf, (200, 255, 255), (8, 8), 4)
        return surf

    def carregar_assets(self):
        self.cursor_img = self.criar_sprite_varinha()
        self.bg_jogo = self.carregar_imagem("data/cenario.png", fallback_func=lambda: gerar_cenario_procedural(LARGURA, ALTURA, CHAO_Y))
        self.bg_menu = self.carregar_imagem("data/telas/menu.png", fallback_cor=(20, 20, 40))
        self.bg_intro = self.carregar_imagem("data/telas/intro.png", fallback_cor=(0, 0, 0))
        self.bg_vitoria = self.carregar_imagem("data/telas/vitoria.png", fallback_cor=(0, 50, 0))
        self.bg_derrota = self.carregar_imagem("data/telas/derrota.png", fallback_cor=(50, 0, 0))
        self.snd_cast = None
        if os.path.exists("data/sounds/cast.wav"): self.snd_cast = pygame.mixer.Sound("data/sounds/cast.wav")

        # >>> ADICIONADO: caminho da música de fundo <<<
        self.musica_fundo_path = "data/sons/tela-inicial.mp3"

    # >>> ADICIONADO: função para trocar música de fundo <<<
    def tocar_musica(self, caminho):
        if os.path.exists(caminho):
            pygame.mixer.music.stop()
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(self.slider_musica.valor)
            pygame.mixer.music.play(-1)


    def carregar_imagem(self, path, fallback_cor=None, fallback_func=None):
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert()
                return pygame.transform.scale(img, (LARGURA, ALTURA))
            except: pass
        if fallback_func: return fallback_func()
        s = pygame.Surface((LARGURA, ALTURA))
        s.fill(fallback_cor if fallback_cor else (0,0,0))
        return s

    def criar_botoes_menu(self):
        self.botoes_menu = {
            "jogar": Botao(119, 100, 205, 50, texto="", cor_fundo=None), 
            "treino": Botao(114, 164, 269, 50, texto="", cor_fundo=None),
            "perfil": Botao(109, 233, 247, 50, texto="", cor_fundo=None),
            "grimorio": Botao(104, 301, 240, 50, texto="", cor_fundo=None),
            "desafios": Botao(104, 367, 239, 50, texto="", cor_fundo=None),
            "config": Botao(103, 434, 307, 50, texto="", cor_fundo=None),
            "creditos": Botao(104, 501, 238, 50, texto="", cor_fundo=None),
            "sair": Botao(105, 574, 244, 50, texto="", cor_fundo=None) 
        }
        
        cx, cy = LARGURA // 2, ALTURA // 2
        self.botoes_modos = {
            "ia": Botao(cx - 150, cy - 80, 300, 55, texto="CONTRA IA", cor_fundo=(50, 50, 80)),
            "p2": Botao(cx - 150, cy - 10, 300, 55, texto="CONTRA P2", cor_fundo=(50, 50, 80)),
            "rank": Botao(cx - 150, cy + 60, 300, 55, texto="RANKEADA", cor_fundo=(50, 50, 80)),
            "voltar": Botao(cx - 150, cy + 150, 300, 55, texto="VOLTAR", cor_fundo=(80, 20, 20))
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
        
        self.chk_mobile = Checkbox(cx - 100, cy, "Mobile", ativo=True)
        self.chk_voz = Checkbox(cx - 100, cy + 30, "Voz", ativo=False)
        self.chk_camera = Checkbox(cx - 100, cy + 60, "Câmera", ativo=False)
        self.chk_fps = Checkbox(cx - 100, cy + 90, "FPS", ativo=False)
        
        y_btns = cy + 150
        
        self.btn_reset = Botao(cx - 210, y_btns, 130, 40, "Resetar", cor_fundo=(100, 20, 20), tamanho_fonte=18)
        self.btn_calibrar = Botao(cx - 65, y_btns, 130, 40, "Calibrar", cor_fundo=(30, 30, 60), tamanho_fonte=18)
        self.btn_voltar_conf = Botao(cx + 80, y_btns, 130, 40, "Voltar", cor_fundo=(50, 50, 50), tamanho_fonte=18)
        
        # --- INICIALIZAÇÃO CORRETA DOS TOOLTIPS ---
        self.tip_musica = BotaoAjuda(cx + 130, cy - 120, "Música", ["Volume da trilha sonora."])
        self.tip_sfx = BotaoAjuda(cx + 130, cy - 60, "Efeitos", ["Volume dos feitiços e impactos."])
        
        try: ip = socket.gethostbyname(socket.gethostname())
        except: ip = "127.0.0.1"
        
        self.tip_mobile = BotaoAjuda(cx + 200, cy, "Mobile", [f"WiFi: {ip}:5000"])
        self.tip_voz = BotaoAjuda(cx + 170, cy + 30, "Voz", ["Fale os feitiços no microfone."])
        self.tip_camera = BotaoAjuda(cx + 170, cy + 60, "Câmera", ["Use um objeto colorido como varinha."])
        self.tip_fps = BotaoAjuda(cx + 170, cy + 90, "FPS", ["Mostra quadros por segundo."])
        
        self.btn_confirma_sim = Botao(cx - 80, cy + 20, 70, 40, "SIM", cor_fundo=(100, 0, 0))
        self.btn_confirma_nao = Botao(cx + 10, cy + 20, 70, 40, "NÃO", cor_fundo=(0, 100, 0))

    def ouvir_voz(self):
        with self.microfone as source:
            self.reconhecedor.adjust_for_ambient_noise(source)
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
        self.todos_sprites.empty()
        self.magias_player.empty()
        self.magias_inimigo.empty()
        self.fantasmas.empty()
        self.particulas = []
        self.textos_flutuantes = []
        
        ctrl_p1 = CONTROLES_SOLO if modo != 2 else CONTROLES_P1_PVP
        ctrl_p2 = CONTROLES_P2_PVP if modo == 2 else {}
        is_p2_human = (modo == 2)
        
        if modo == 3: nome_p2 = "Guardião (Ranked)"
        elif modo == 1: nome_p2 = "Draco (IA)"
        else: nome_p2 = "Player 2"
        
        self.player = Mago(200, CHAO_Y, "Harry", self, ctrl_p1, "data/P1", is_human=True, lado_inicial_dir=True)
        self.inimigo = Mago(LARGURA - 200, CHAO_Y, nome_p2, self, ctrl_p2, "data/P1", is_human=is_p2_human, lado_inicial_dir=False)
        
        self.player.magias_player = self.magias_player
        self.player.magias_inimigo = self.magias_inimigo
        self.inimigo.magias_player = self.magias_player
        self.inimigo.magias_inimigo = self.magias_inimigo
        self.player.fantasmas = self.fantasmas
        self.inimigo.fantasmas = self.fantasmas
        
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

        # >>> ADICIONADO: troca automática de música por estado <<<
        if novo == JOGO:
            self.tocar_musica(self.musica_batalha_path)
        elif novo in [MENU, INTRO, CONFIG, GRIMORIO, PERFIL, DESAFIOS, CREDITOS, VITORIA, DERROTA]:
            self.tocar_musica(self.musica_fundo_path)

    def iniciar_disputa(self):
        self.mudar_estado(DISPUTA)
        self.clash_progress = 50 
        self.timer_aviso = 0

    def update_jogo(self):
        self.player.update()
        self.inimigo.update()
        self.magias_player.update()
        self.magias_inimigo.update()
        self.fantasmas.update()
        
        hits_magia = pygame.sprite.groupcollide(self.magias_player, self.magias_inimigo, True, True)
        if hits_magia:
            self.iniciar_disputa()
            return
            
        hits1 = pygame.sprite.spritecollide(self.inimigo, self.magias_player, True)
        for m in hits1:
            self.inimigo.receber_dano(m)
            self.criar_efeito_impacto(m.rect.center)
            
        hits2 = pygame.sprite.spritecollide(self.player, self.magias_inimigo, True)
        for m in hits2:
            self.player.receber_dano(m)
            self.criar_efeito_impacto(m.rect.center)

        self.processar_inputs_externos()

    def processar_inputs_externos(self):
        if TEM_MOBILE and self.usar_mobile and not self.player.morto:
            if CONTROLE_REMOTO.get("esquerda"): self.player.rect.x -= 5
            elif CONTROLE_REMOTO.get("direita"): self.player.rect.x += 5
            if CONTROLE_REMOTO.get("dash"): 
                self.player.ativar_dash(); CONTROLE_REMOTO["dash"] = False
            for f in ["incendio", "protego", "expelliarmus", "avada"]:
                if CONTROLE_REMOTO.get(f):
                    nome = "avada kedavra" if f == "avada" else f
                    self.player.castar_feitico(nome)
                    CONTROLE_REMOTO[f] = False

        if TEM_CAMERA and self.usar_camera and CONTROLE_CAMERA.get("ativo"):
            if CONTROLE_CAMERA.get("clique"):
                self.player.castar_feitico("incendio") 
                CONTROLE_CAMERA["clique"] = False

    def update_disputa(self):
        # Lógica da IA apenas (Inputs estão no loop)
        if self.modo_jogo != 2: # Se IA
            # Chance de pressionar
            if random.randint(0, 100) < 15: 
                self.clash_progress -= 15

        if self.clash_progress >= 100:
            self.mudar_estado(JOGO)
            self.inimigo.receber_dano(None, 50) 
        elif self.clash_progress <= 0:
            self.mudar_estado(JOGO)
            self.player.receber_dano(None, 50) 

    def criar_efeito_impacto(self, pos):
        if self.snd_cast: self.snd_cast.play()
        self.textos_flutuantes.append(TextoFlutuante(pos[0], pos[1]-20, "HIT!", (255,200,0)))
        for _ in range(10):
            self.particulas.append(ParticulaMagica(pos[0], pos[1], (255, 100, 0), "explosao"))

    def desenhar_hud(self):
        pygame.draw.rect(self.tela, SANGUE_ESCURO, (50, 50, 200 * (self.player.vida/100), 20))
        pygame.draw.rect(self.tela, AZUL_MANA, (50, 75, 200 * (self.player.mana/100), 10))
        pygame.draw.rect(self.tela, BRANCO, (50, 50, 200, 20), 2)
        
        offset = LARGURA - 250
        pygame.draw.rect(self.tela, SANGUE_ESCURO, (offset, 50, 200 * (self.inimigo.vida/100), 20))
        pygame.draw.rect(self.tela, BRANCO, (offset, 50, 200, 20), 2)
        pygame.draw.rect(self.tela, AZUL_MANA, (offset, 75, 200 * (self.inimigo.mana/100), 10))

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

                # --- INPUT DA DISPUTA (CLASH) ---
                if event.type == pygame.KEYDOWN and self.estado == DISPUTA:
                    if event.key == pygame.K_SPACE: self.clash_progress += 15
                    if self.modo_jogo == 2 and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
                        self.clash_progress -= 15
                # --------------------------------

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.estado == INTRO: 
                        self.mudar_estado(MENU)
                    
                    elif self.estado == MENU:
                        if self.mostrando_modos:
                            if self.botoes_modos["ia"].desenhar(self.tela): self.iniciar_batalha(1); self.mostrando_modos = False
                            elif self.botoes_modos["p2"].desenhar(self.tela): self.iniciar_batalha(2); self.mostrando_modos = False
                            elif self.botoes_modos["voltar"].desenhar(self.tela): self.mostrando_modos = False
                            elif self.botoes_modos["rank"].desenhar(self.tela): 
                                if not CLIENTE_ONLINE.conectado:
                                    self.aviso_temp = "FAÇA LOGIN NO PERFIL!"; self.timer_aviso = 120
                                else:
                                    self.mudar_estado(PROCURANDO)
                                    self.timer_matchmaking = 120
                                    self.mostrando_modos = False
                        else:
                            if self.botoes_menu["jogar"].desenhar(self.tela): self.mostrando_modos = True
                            elif self.botoes_menu["treino"].desenhar(self.tela): ModoTreinamento(self).rodar(); self.mudar_estado(MENU)
                            elif self.botoes_menu["perfil"].desenhar(self.tela): self.mudar_estado(PERFIL)
                            elif self.botoes_menu["grimorio"].desenhar(self.tela): self.mudar_estado(GRIMORIO)
                            elif self.botoes_menu["desafios"].desenhar(self.tela): self.mudar_estado(DESAFIOS)
                            elif self.botoes_menu["config"].desenhar(self.tela): self.mudar_estado(CONFIG)
                            elif self.botoes_menu["creditos"].desenhar(self.tela): 
                                self.tela_creditos.resetar()
                                self.mudar_estado(CREDITOS)
                            elif self.botoes_menu["sair"].desenhar(self.tela): self.rodando = False

                    elif self.estado == CONFIG:
                        if self.confirmando_reset:
                            if self.btn_confirma_sim.desenhar(self.tela):
                                self.dados_globais = {"partidas_totais":0, "vitorias_p1":0, "vitorias_p2":0, "vitorias_ia":0, "maestria":{}}
                                salvar_dados(self.dados_globais)
                                self.aviso_temp = "DADOS RESETADOS!"
                                self.timer_aviso = 60
                                self.confirmando_reset = False
                            elif self.btn_confirma_nao.desenhar(self.tela):
                                self.confirmando_reset = False
                        else:
                            if self.btn_voltar_conf.desenhar(self.tela): self.mudar_estado(MENU)
                            
                            if self.chk_mobile.checar_clique(event.pos): self.usar_mobile = self.chk_mobile.ativo
                            if self.chk_voz.checar_clique(event.pos): self.usar_voz = self.chk_voz.ativo
                            if self.chk_camera.checar_clique(event.pos): self.usar_camera = self.chk_camera.ativo
                            if self.chk_fps.checar_clique(event.pos): self.mostrar_fps = self.chk_fps.ativo
                            
                            if self.btn_calibrar.desenhar(self.tela):
                                if TEM_CAMERA: start_camera()

                            if self.btn_reset.desenhar(self.tela):
                                self.confirmando_reset = True

                    elif self.estado in [VITORIA, DERROTA]:
                        if self.botoes_vitoria["menu"].desenhar(self.tela): 
                            self.botoes_vitoria["menu"].clicado = False
                            self.mudar_estado(MENU)
                        
                        if self.estado == VITORIA:
                             if self.botoes_vitoria["continuar"].desenhar(self.tela):
                                 self.botoes_vitoria["continuar"].clicado = False
                                 self.iniciar_batalha(self.modo_jogo)
                        else:
                             if self.botoes_derrota["revanche"].desenhar(self.tela):
                                 self.botoes_derrota["revanche"].clicado = False
                                 self.iniciar_batalha(self.modo_jogo)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.estado in [JOGO, GRIMORIO, CONFIG, PERFIL, DESAFIOS, CREDITOS]: self.mudar_estado(MENU)

            self.tela.fill(PRETO)
            
            if self.estado == INTRO:
                self.tela.blit(self.bg_intro, (0,0))
                
            elif self.estado == MENU:
                self.tela.blit(self.bg_menu, (0,0))
                if self.mostrando_modos:
                    self.botoes_modos["ia"].desenhar(self.tela)
                    self.botoes_modos["p2"].desenhar(self.tela)
                    self.botoes_modos["rank"].desenhar(self.tela)
                    self.botoes_modos["voltar"].desenhar(self.tela)
                else:
                    for k, btn in self.botoes_menu.items(): btn.desenhar(self.tela)

            elif self.estado == GRIMORIO:
                self.tela.blit(self.bg_menu, (0,0))
                self.grimorio.desenhar(self.tela)

            elif self.estado == PERFIL:
                self.tela.blit(self.bg_menu, (0,0)) 
                self.perfil_jogador.desenhar()

            elif self.estado == DESAFIOS:
                self.tela.blit(self.bg_menu, (0,0))
                self.tela_desafios.desenhar()

            elif self.estado == CREDITOS:
                self.tela_creditos.desenhar()
            
            elif self.estado == PROCURANDO:
                self.tela.blit(self.bg_menu, (0,0))
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA); overlay.fill((0,0,0,200)); self.tela.blit(overlay, (0,0))
                dots = "." * (int(pygame.time.get_ticks() / 500) % 4)
                txt = self.fonte_titulo.render(f"Procurando Oponente{dots}", True, OURO)
                self.tela.blit(txt, (LARGURA//2 - txt.get_width()//2, ALTURA//2))
                self.timer_matchmaking -= 1
                if self.timer_matchmaking <= 0: self.iniciar_batalha(3)

            elif self.estado == CONFIG:
                self.tela.blit(self.bg_menu, (0,0))
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                overlay.fill((0,0,0,220))
                self.tela.blit(overlay, (0,0))
                
                pygame.draw.rect(self.tela, (30, 30, 30), self.rect_painel_config, border_radius=10)
                pygame.draw.rect(self.tela, OURO_ANTIGO, self.rect_painel_config, 3, border_radius=10)
                
                tit = self.fonte_titulo.render("CONFIGURAÇÕES", True, OURO_ANTIGO)
                self.tela.blit(tit, (LARGURA//2 - tit.get_width()//2, self.rect_painel_config.y + 30))
                
                lbl_mus = self.fonte_ui.render(f"Música: {int(self.slider_musica.valor*100)}%", True, BRANCO)
                self.tela.blit(lbl_mus, (self.slider_musica.rect.x, self.slider_musica.rect.y - 25))
                self.slider_musica.desenhar(self.tela)
                self.tip_musica.desenhar(self.tela)
                
                lbl_sfx = self.fonte_ui.render(f"Efeitos: {int(self.slider_sfx.valor*100)}%", True, BRANCO)
                self.tela.blit(lbl_sfx, (self.slider_sfx.rect.x, self.slider_sfx.rect.y - 25))
                self.slider_sfx.desenhar(self.tela)
                self.tip_sfx.desenhar(self.tela)
                
                self.chk_mobile.desenhar(self.tela); self.tip_mobile.desenhar(self.tela)
                self.chk_voz.desenhar(self.tela); self.tip_voz.desenhar(self.tela)
                self.chk_camera.desenhar(self.tela); self.tip_camera.desenhar(self.tela)
                self.chk_fps.desenhar(self.tela); self.tip_fps.desenhar(self.tela)

                self.btn_reset.desenhar(self.tela)
                self.btn_calibrar.desenhar(self.tela)
                self.btn_voltar_conf.desenhar(self.tela)
                
                if not self.confirmando_reset:
                    vol_mus = self.slider_musica.update()
                    vol_sfx = self.slider_sfx.update()
                    pygame.mixer.music.set_volume(vol_mus)
                    if self.snd_cast: self.snd_cast.set_volume(vol_sfx)
                
                self.tip_musica.desenhar_tooltip(self.tela)
                self.tip_sfx.desenhar_tooltip(self.tela)
                self.tip_mobile.desenhar_tooltip(self.tela)
                self.tip_voz.desenhar_tooltip(self.tela)
                self.tip_camera.desenhar_tooltip(self.tela)
                self.tip_fps.desenhar_tooltip(self.tela)
                
                if self.confirmando_reset:
                    cx, cy = LARGURA//2, ALTURA//2
                    rect_pop = pygame.Rect(cx - 150, cy - 80, 300, 160)
                    pygame.draw.rect(self.tela, (10, 10, 10), rect_pop)
                    pygame.draw.rect(self.tela, (255, 0, 0), rect_pop, 2)
                    msg = self.fonte_ui.render("Tem certeza?", True, BRANCO)
                    self.tela.blit(msg, (cx - msg.get_width()//2, cy - 50))
                    self.btn_confirma_sim.desenhar(self.tela)
                    self.btn_confirma_nao.desenhar(self.tela)
                
                if self.timer_aviso > 0:
                    self.timer_aviso -= 1
                    av = self.fonte_aviso.render(self.aviso_temp, True, BRANCO)
                    self.tela.blit(av, (LARGURA//2 - av.get_width()//2, ALTURA - 100))

            elif self.estado == JOGO:
                self.tela.blit(self.bg_jogo, (0,0))
                self.update_jogo()
                
                self.fantasmas.draw(self.tela)
                self.tela.blit(self.player.image, self.player.rect)
                self.tela.blit(self.inimigo.image, self.inimigo.rect)
                
                if self.player.escudo_ativo: pygame.draw.circle(self.tela, COR_PROTEGO, self.player.rect.center, 50, 2)
                if self.inimigo.escudo_ativo: pygame.draw.circle(self.tela, COR_PROTEGO, self.inimigo.rect.center, 50, 2)
                
                for m in self.magias_player: self.tela.blit(m.image, m.rect)
                for m in self.magias_inimigo: self.tela.blit(m.image, m.rect)
                
                for p in self.particulas[:]: 
                    p.update()
                    p.draw(self.tela)
                    if p.timer <= 0: self.particulas.remove(p)
                
                for t in self.textos_flutuantes[:]: t.update(); t.draw(self.tela)

                self.desenhar_hud()
                
                if self.mostrar_fps:
                     fps = int(self.relogio.get_fps())
                     self.tela.blit(self.fonte_fps.render(f"FPS: {fps}", True, (0,255,0)), (LARGURA-80, 50))

            elif self.estado == DISPUTA:
                self.tela.blit(self.bg_jogo, (0,0))
                self.tela.blit(self.player.image, self.player.rect)
                self.tela.blit(self.inimigo.image, self.inimigo.rect)
                self.update_disputa()
                
                largura_b = 400
                pygame.draw.rect(self.tela, PRETO_FUNDO, (LARGURA//2 - 200, ALTURA//2 - 50, largura_b, 40))
                fill = (self.clash_progress / 100) * largura_b
                pygame.draw.rect(self.tela, VERDE_CLASH, (LARGURA//2 - 200, ALTURA//2 - 50, fill, 40))
                
                txt = "ESMAGUE ESPAÇO!" if self.modo_jogo == 1 else "P1: ESPAÇO | P2: ENTER(NUM)"
                msg = self.fonte_fps.render(txt, True, OURO)
                self.tela.blit(msg, (LARGURA//2 - msg.get_width()//2, ALTURA//2 - 100))

            elif self.estado == CENA_MORTE:
                self.tela.blit(self.bg_jogo, (0,0))
                
                self.player.update()
                self.inimigo.update()
                
                self.tela.blit(self.player.image, self.player.rect)
                self.tela.blit(self.inimigo.image, self.inimigo.rect)
                
                self.timer_morte -= 1
                if self.timer_morte <= 0:
                    vitoria_player = not self.player.morto
                    
                    if self.modo_jogo == 3 and CLIENTE_ONLINE.conectado:
                        CLIENTE_ONLINE.enviar_partida("win" if vitoria_player else "loss")
                        if vitoria_player: self.aviso_temp = "ELO ATUALIZADO!"
                    
                    self.dados_globais["partidas_totais"] += 1
                    if vitoria_player: 
                        self.dados_globais["vitorias_p1"] += 1
                        self.mudar_estado(VITORIA)
                    else: 
                        self.mudar_estado(DERROTA)
                    salvar_dados(self.dados_globais)

            elif self.estado in [VITORIA, DERROTA]:
                bg = self.bg_vitoria if self.estado == VITORIA else self.bg_derrota
                self.tela.blit(bg, (0,0))

            if self.estado != INTRO and self.estado != DISPUTA:
                self.tela.blit(self.cursor_img, (mx-16, my-16))
                
            pygame.display.flip()
        
        # Encerra servidor ao fechar
        if self.processo_server:
            self.processo_server.terminate()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Jogo().loop()