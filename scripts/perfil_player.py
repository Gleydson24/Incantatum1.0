import pygame
import random
import os
import tkinter as tk
from tkinter import filedialog
from scripts.settings import *
from scripts.utils import Botao
from scripts.save_system import salvar_dados
from scripts.ai_service import ChatIA

class PerfilJogador:
    def __init__(self, jogo):
        self.jogo = jogo
        self.tela = jogo.tela
        
        # --- Layout ---
        self.largura_painel = 1000
        self.altura_painel = 680
        self.x = (LARGURA - self.largura_painel) // 2
        self.y = (ALTURA - self.altura_painel) // 2
        self.rect_painel = pygame.Rect(self.x, self.y, self.largura_painel, self.altura_painel)
        
        # Cores
        self.COR_FUNDO_PAINEL = (20, 20, 25)
        self.COR_MOLDURA = (60, 50, 40)
        self.COR_CHAT_BG = (15, 15, 20)
        
        # --- Fontes ---
        try:
            self.fonte_nome = pygame.font.SysFont("Garamond", 55, bold=True)
            self.fonte_titulo = pygame.font.SysFont("Garamond", 22, italic=True)
            self.fonte_secao = pygame.font.SysFont("Arial", 18, bold=True)
            self.fonte_texto = pygame.font.SysFont("Arial", 16)
            self.fonte_mini = pygame.font.SysFont("Arial", 12, bold=True)
            self.fonte_icone = pygame.font.SysFont("Segoe UI Symbol", 25) 
        except:
            self.fonte_nome = pygame.font.SysFont(None, 60)
            self.fonte_texto = pygame.font.SysFont(None, 16)
            self.fonte_icone = pygame.font.SysFont(None, 25)
        
        self.btn_fechar = Botao(self.x + self.largura_painel - 50, self.y + 10, 40, 40, "X", cor_fundo=(80, 20, 20))

        # --- NAVEGAÇÃO ---
        y_abas = self.y + 160 
        w_aba = 180
        self.aba_ativa = "stats"
        self.botoes_aba = {
            "stats": Botao(self.x + 30, y_abas, w_aba, 35, "ESTATÍSTICAS", tamanho_fonte=16),
            "social": Botao(self.x + 30 + w_aba + 10, y_abas, w_aba, 35, "SOCIAL", tamanho_fonte=16),
            "chat": Botao(self.x + 30 + (w_aba + 10)*2, y_abas, w_aba, 35, "CHAT", tamanho_fonte=16),
            "history": Botao(self.x + 30 + (w_aba + 10)*3, y_abas, w_aba, 35, "CONQUISTAS", tamanho_fonte=16)
        }

        # --- Edição de Perfil ---
        self.digitando_nome = False
        self.temp_nome = ""
        self.rect_nome = pygame.Rect(self.x + 160, self.y + 50, 400, 60)
        
        # --- Avatar ---
        self.rect_avatar = pygame.Rect(self.x + 50, self.y + 40, 100, 100)
        self.avatar_img_custom = None
        self.carregar_avatar_customizado() 
        self.tipos_avatar = ["bruxo", "caveira", "pocao", "coruja"]
        self.seletor_aberto = False
        self.rect_seletor = pygame.Rect(self.x + 40, self.y + 150, 320, 80)
        self.botoes_avatar = []
        for i, tipo in enumerate(self.tipos_avatar):
            r = pygame.Rect(self.rect_seletor.x + 10 + (i*60), self.rect_seletor.y + 10, 50, 60)
            self.botoes_avatar.append({"tipo": "interno", "id": i, "rect": r, "nome": tipo})
        r_plus = pygame.Rect(self.rect_seletor.x + 10 + (len(self.tipos_avatar)*60), self.rect_seletor.y + 10, 50, 60)
        self.botoes_avatar.append({"tipo": "custom", "rect": r_plus, "nome": "+"})

        # --- SISTEMA DE CHAT ---
        self.chat_ai_service = ChatIA()
        self.modo_chat = "menu"
        self.btn_chat_amigos = Botao(0, 0, 300, 200, "FALAR COM AMIGOS", cor_fundo=(50, 50, 80))
        
        # --- CORREÇÃO 1: Texto menor e ajustado ---
        self.btn_chat_ia = Botao(0, 0, 300, 200, "PERSONAGENS (IA)", cor_fundo=(80, 50, 50), tamanho_fonte=24)
        
        self.btn_voltar_chat = Botao(0, 0, 80, 30, "Voltar", cor_fundo=(50, 50, 50), tamanho_fonte=14)
        
        self.amigos = [
            {"nome": "Hermione G.", "status": "online", "cor": (200, 100, 100)},
            {"nome": "Rony W.", "status": "jogando", "cor": (200, 150, 100)},
            {"nome": "Draco M.", "status": "online", "cor": (200, 255, 200)},
            {"nome": "Neville L.", "status": "offline", "cor": (150, 150, 150)},
        ]
        self.selecionado_idx = 0
        
        self.personagens_ia = [
            {"nome": "Harry Potter", "cor": (255, 100, 100)},
            {"nome": "Hermione Granger", "cor": (200, 100, 200)},
            {"nome": "Rony Weasley", "cor": (200, 150, 100)},
            {"nome": "Dumbledore", "cor": (150, 150, 255)}
        ]
        self.ia_selecionada_idx = 0
        
        # ARMAZENAMENTO TEMPORÁRIO (Não salva no JSON)
        self.chat_session_logs = {} 
        
        self.input_chat = ""
        self.digitando_chat = False
        
        # --- Visual Geral ---
        self.particulas = []
        for _ in range(20):
            self.particulas.append([random.randint(self.x, self.x+self.largura_painel), random.randint(self.y, self.y+self.altura_painel), random.uniform(0.5, 2), random.randint(2, 5)])
        self.notificacao_msg = ""
        self.notificacao_timer = 0
        self.scroll_y_conquistas = 0

    def carregar_avatar_customizado(self):
        path = self.jogo.dados_globais.get("avatar_path", "")
        if path and os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                self.avatar_img_custom = pygame.transform.scale(img, (80, 80))
            except: self.avatar_img_custom = None

    def importar_imagem_pc(self):
        try:
            root = tk.Tk(); root.withdraw() 
            file_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.bmp")])
            root.destroy()
            if file_path:
                self.jogo.dados_globais["avatar_path"] = file_path
                self.jogo.dados_globais["avatar_id"] = -1
                salvar_dados(self.jogo.dados_globais)
                self.carregar_avatar_customizado()
        except: pass

    def quebrar_texto(self, texto, largura_max):
        """Função auxiliar para quebrar texto em várias linhas"""
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ""
        
        for palavra in palavras:
            teste = linha_atual + palavra + " "
            largura_teste = self.fonte_texto.size(teste)[0]
            if largura_teste < largura_max:
                linha_atual = teste
            else:
                linhas.append(linha_atual)
                linha_atual = palavra + " "
        linhas.append(linha_atual)
        return linhas

    # --- DESENHO DE ELEMENTOS GRÁFICOS ---
    def desenhar_icone_simples(self, cx, cy, tipo):
        if tipo == "bruxo": pygame.draw.circle(self.tela, (200, 180, 50), (cx, cy), 15)
        elif tipo == "+": 
            pygame.draw.line(self.tela, BRANCO, (cx-10, cy), (cx+10, cy), 3)
            pygame.draw.line(self.tela, BRANCO, (cx, cy-10), (cx, cy+10), 3)
        else: pygame.draw.circle(self.tela, CINZA, (cx, cy), 15)

    def desenhar_avatar_interno(self, cx, cy, tipo):
        if tipo == "bruxo": pygame.draw.circle(self.tela, (20, 20, 40), (cx, cy), 40)
        elif tipo == "caveira": pygame.draw.circle(self.tela, (30, 30, 30), (cx, cy), 40)
        elif tipo == "pocao": pygame.draw.circle(self.tela, (40, 0, 40), (cx, cy), 40)
        elif tipo == "coruja": pygame.draw.circle(self.tela, (60, 40, 20), (cx, cy), 40)
        pygame.draw.circle(self.tela, OURO, (cx, cy), 40, 2)

    def desenhar_barra_xp(self):
        dados = self.jogo.dados_globais
        xp, xp_prox = dados.get("xp_atual", 0), dados.get("xp_proximo_nivel", 1000)
        nivel = dados.get("nivel_jogador", 1)
        bx, by = self.x + self.largura_painel - 350, self.y + 60
        bw, bh = 300, 20
        txt_lvl = self.fonte_secao.render(f"NÍVEL {nivel}", True, OURO)
        self.tela.blit(txt_lvl, (bx, by - 25))
        pygame.draw.rect(self.tela, (30, 30, 30), (bx, by, bw, bh), border_radius=10)
        if xp_prox > 0: pygame.draw.rect(self.tela, (0, 200, 255), (bx, by, bw * min(1, xp/xp_prox), bh), border_radius=10)
        pygame.draw.rect(self.tela, BRANCO, (bx, by, bw, bh), 1, border_radius=10)
        txt_xp = self.fonte_mini.render(f"{int(xp)} / {int(xp_prox)} XP", True, BRANCO)
        self.tela.blit(txt_xp, (bx + bw//2 - txt_xp.get_width()//2, by + 3))

    # --- ABAS ---
    def desenhar_aba_stats(self):
        dados = self.jogo.dados_globais
        x_col1, y_topo = self.x + 50, self.y + 230
        stats = [("Partidas", dados.get("partidas_totais", 0)), ("Vitórias", dados.get("vitorias_p1", 0)), ("Derrotas", dados.get("partidas_totais", 0) - dados.get("vitorias_p1", 0))]
        for i, (l, v) in enumerate(stats):
            bx = x_col1 + i * 160
            pygame.draw.rect(self.tela, (35,35,45), (bx, y_topo, 140, 50), border_radius=5)
            self.tela.blit(self.fonte_secao.render(str(v), True, OURO), (bx + 10, y_topo + 5))
            self.tela.blit(self.fonte_mini.render(l.upper(), True, CINZA_TEXTO), (bx + 10, y_topo + 30))
        y_bar = y_topo + 80
        for k, n, c in [("incendio", "Incendio", (255, 100, 0)), ("protego", "Protego", (50, 100, 255)), ("avada kedavra", "Avada", (0, 255, 0))]:
            usos = dados.get("maestria", {}).get(k, 0)
            self.tela.blit(self.fonte_texto.render(n, True, CINZA_CLARO), (x_col1, y_bar))
            w = int(400 * min(1, usos/50))
            pygame.draw.rect(self.tela, (20,20,20), (x_col1 + 150, y_bar+2, 400, 15), border_radius=4)
            if w > 0: pygame.draw.rect(self.tela, c, (x_col1 + 150, y_bar+2, w, 15), border_radius=4)
            self.tela.blit(self.fonte_mini.render(f"{usos} usos", True, c), (x_col1 + 570, y_bar))
            y_bar += 35

    def desenhar_aba_social(self):
        x, y = self.x + 50, self.y + 230
        for i, amigo in enumerate(self.amigos):
            yy = y + (i * 70)
            pygame.draw.rect(self.tela, (40, 40, 45), (x, yy, 900, 60), border_radius=8)
            pygame.draw.circle(self.tela, amigo["cor"], (x + 40, yy + 30), 20)
            self.tela.blit(self.fonte_secao.render(amigo["nome"], True, BRANCO), (x + 80, yy + 10))
            st = amigo["status"]
            txt_st = "Online em Hogwarts" if st == "online" else ("Duelando" if st == "jogando" else "Offline")
            cor_st = (0, 255, 0) if st == "online" else ((255, 165, 0) if st == "jogando" else CINZA)
            self.tela.blit(self.fonte_mini.render(txt_st, True, cor_st), (x + 80, yy + 35))
            btn = pygame.Rect(x + 750, yy + 15, 130, 30)
            c_btn = (80, 20, 20) if st != "offline" else (60,60,60)
            pygame.draw.rect(self.tela, c_btn, btn, border_radius=5)
            lbl = self.fonte_mini.render("CONVIDAR", True, BRANCO)
            self.tela.blit(lbl, (btn.centerx - lbl.get_width()//2, btn.centery - lbl.get_height()//2))

    def desenhar_aba_chat(self):
        x_base, y_base = self.x + 30, self.y + 210
        w_chat, h_chat = 940, 420
        
        if self.modo_chat == "menu":
            self.btn_chat_amigos.rect.center = (self.x + 300, self.y + 400)
            self.btn_chat_ia.rect.center = (self.x + 700, self.y + 400)
            self.btn_chat_amigos.desenhar(self.tela)
            self.btn_chat_ia.desenhar(self.tela)
            lbl = self.fonte_secao.render("Escolha com quem conversar:", True, CINZA_CLARO)
            self.tela.blit(lbl, (self.x + 500 - lbl.get_width()//2, self.y + 250))
            return

        w_lista, w_msgs = 250, w_chat - 250
        
        # LISTA ESQUERDA
        pygame.draw.rect(self.tela, (30, 30, 35), (x_base, y_base, w_lista, h_chat), border_top_left_radius=8, border_bottom_left_radius=8)
        lista_atual = self.amigos if self.modo_chat == "amigos" else self.personagens_ia
        idx_selecionado = self.selecionado_idx if self.modo_chat == "amigos" else self.ia_selecionada_idx
        
        for i, item in enumerate(lista_atual):
            cor_bg = (50, 50, 60) if i == idx_selecionado else (30, 30, 35)
            rect_item = pygame.Rect(x_base, y_base + (i*60), w_lista, 60)
            if rect_item.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                if self.modo_chat == "amigos": self.selecionado_idx = i
                else: self.ia_selecionada_idx = i
            pygame.draw.rect(self.tela, cor_bg, rect_item)
            pygame.draw.circle(self.tela, item["cor"], (x_base + 30, y_base + (i*60) + 30), 20)
            self.tela.blit(self.fonte_secao.render(item["nome"], True, BRANCO), (x_base + 60, y_base + (i*60) + 20))

        # ÁREA DE CHAT (DIREITA)
        chat_rect = pygame.Rect(x_base + w_lista, y_base, w_msgs, h_chat - 50)
        pygame.draw.rect(self.tela, self.COR_CHAT_BG, chat_rect, border_top_right_radius=8)
        
        nome_atual = lista_atual[idx_selecionado]["nome"]
        pygame.draw.rect(self.tela, (25, 25, 30), (chat_rect.x, chat_rect.y, chat_rect.width, 40))
        self.tela.blit(self.fonte_secao.render(f"Chat: {nome_atual}", True, OURO), (chat_rect.x + 20, chat_rect.y + 10))
        
        self.btn_voltar_chat.rect.topright = (chat_rect.right - 10, chat_rect.y + 5)
        self.btn_voltar_chat.desenhar(self.tela)
        
        # LOGS E RESPOSTA IA
        logs_key = f"chat_{self.modo_chat}_{nome_atual}"
        logs = self.chat_session_logs.get(logs_key, []) 
        
        if self.modo_chat == "ia":
            resp_ia = self.chat_ai_service.checar_resposta()
            if resp_ia:
                logs.append({"sender": "them", "text": resp_ia})
                self.chat_session_logs[logs_key] = logs 

        # --- CORREÇÃO 2: CLIPPING AREA (Impede vazar mensagem) ---
        area_mensagens = pygame.Rect(chat_rect.x, chat_rect.y + 40, chat_rect.width, chat_rect.height - 40)
        self.tela.set_clip(area_mensagens)
        # ---------------------------------------------------------

        # RENDERIZAÇÃO DAS MENSAGENS COM QUEBRA DE LINHA
        msg_y = chat_rect.bottom - 20
        largura_maxima_msg = w_msgs - 60 

        for msg in reversed(logs):
            txt, is_me = msg["text"], msg["sender"] == "me"
            
            linhas_texto = self.quebrar_texto(txt, largura_maxima_msg)
            altura_caixa = (len(linhas_texto) * 20) + 10
            cor_box = (0, 100, 0) if is_me else ((60, 60, 60) if self.modo_chat == "amigos" else (80, 40, 80))
            
            largura_real_box = 0
            for l in linhas_texto:
                w = self.fonte_texto.size(l)[0]
                if w > largura_real_box: largura_real_box = w
            largura_real_box += 20 
            
            x_msg = chat_rect.right - largura_real_box - 20 if is_me else chat_rect.left + 20
            
            pygame.draw.rect(self.tela, cor_box, (x_msg, msg_y - altura_caixa, largura_real_box, altura_caixa), border_radius=10)
            
            offset_linha = 0
            for l in linhas_texto:
                surf = self.fonte_texto.render(l, True, BRANCO)
                self.tela.blit(surf, (x_msg + 10, msg_y - altura_caixa + 5 + offset_linha))
                offset_linha += 20
            
            msg_y -= (altura_caixa + 10) 
            
            if msg_y < chat_rect.top: break

        # --- RESET CLIPPING ---
        self.tela.set_clip(None)
        # ----------------------

        # INPUT BOX
        input_rect = pygame.Rect(x_base + w_lista, y_base + h_chat - 50, w_msgs, 50)
        pygame.draw.rect(self.tela, (40, 40, 50), input_rect, border_bottom_right_radius=8)
        txt_display = self.input_chat + ("|" if self.digitando_chat and (pygame.time.get_ticks()//500)%2==0 else "")
        self.tela.blit(self.fonte_texto.render(txt_display, True, BRANCO), (input_rect.x + 10, input_rect.y + 15))
        if not self.digitando_chat and not self.input_chat:
            status_txt = "Digitando..." if (self.modo_chat == "ia" and self.chat_ai_service.ocupado) else "Clique para escrever..."
            self.tela.blit(self.fonte_texto.render(status_txt, True, CINZA), (input_rect.x + 10, input_rect.y + 15))

    def desenhar_aba_history(self):
        x, y = self.x + 50, self.y + 230
        h_area = 400
        hist = self.jogo.dados_globais.get("historico_conquistas", [])
        self.tela.set_clip(pygame.Rect(x, y, 900, h_area))
        yy = y + self.scroll_y_conquistas
        if not hist: self.tela.blit(self.fonte_secao.render("Nenhuma missão completada.", True, CINZA_TEXTO), (x, y))
        for item in hist:
            pygame.draw.rect(self.tela, (30, 35, 30), (x, yy, 900, 60), border_radius=8)
            pygame.draw.rect(self.tela, (50, 100, 50), (x, yy, 900, 60), 1, border_radius=8)
            self.tela.blit(self.fonte_secao.render("✓", True, (0,255,0)), (x + 20, yy + 15))
            self.tela.blit(self.fonte_secao.render(item["titulo"], True, OURO), (x + 60, yy + 10))
            self.tela.blit(self.fonte_mini.render(f"{item['desc']} - {item['data']}", True, CINZA_CLARO), (x + 60, yy + 35))
            yy += 70
        self.tela.set_clip(None)

    def desenhar(self):
        dados = self.jogo.dados_globais
        mouse_pos = pygame.mouse.get_pos()
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA); overlay.fill((0, 0, 0, 220)); self.tela.blit(overlay, (0, 0))
        pygame.draw.rect(self.tela, self.COR_FUNDO_PAINEL, self.rect_painel, border_radius=10)
        for p in self.particulas:
            p[1] -= p[2]
            if p[1] < self.y: p[1] = self.y + self.altura_painel
            pygame.draw.circle(self.tela, (255, 255, 255, 30), (int(p[0]), int(p[1])), p[3])
        pygame.draw.rect(self.tela, self.COR_MOLDURA, self.rect_painel, 2, border_radius=10)
        rect_glow = self.rect_painel.inflate(4, 4); pygame.draw.rect(self.tela, OURO_ANTIGO, rect_glow, 2, border_radius=10)
        
        idx = dados.get("avatar_id", 0)
        if idx == -1 and self.avatar_img_custom:
            mask = pygame.Surface((80, 80), pygame.SRCALPHA); pygame.draw.circle(mask, (255,255,255), (40, 40), 40)
            img_rect = self.avatar_img_custom.get_rect(center=(self.x + 100, self.y + 100))
            final = self.avatar_img_custom.copy(); final.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
            self.tela.blit(final, img_rect); pygame.draw.circle(self.tela, OURO, (self.x + 100, self.y + 100), 40, 2)
        else:
            tipo = self.tipos_avatar[idx] if idx >= 0 and idx < len(self.tipos_avatar) else "bruxo"
            self.desenhar_avatar_interno(self.x + 100, self.y + 90, tipo)
            
        nome_surf = self.fonte_nome.render(self.temp_nome if self.digitando_nome else dados.get("nome_jogador", "Guest"), True, BRANCO)
        self.tela.blit(nome_surf, (self.x + 160, self.y + 50))
        if self.rect_nome.collidepoint(mouse_pos) and not self.digitando_nome:
             try: self.tela.blit(self.fonte_icone.render("✎", True, BRANCO), (self.x + 160 + nome_surf.get_width() + 10, self.y + 60))
             except: pass
        
        txt_titulo = self.fonte_titulo.render(dados.get("titulo_jogador", "Bruxo Iniciante"), True, CINZA_CLARO)
        self.tela.blit(txt_titulo, (self.x + 160, self.y + 115))
        
        self.desenhar_barra_xp()

        for k, btn in self.botoes_aba.items():
            btn.cor_fundo = (80, 80, 100) if self.aba_ativa == k else (40, 40, 40)
            btn.desenhar(self.tela)
        pygame.draw.line(self.tela, OURO, (self.x + 30, self.botoes_aba["stats"].rect.bottom + 5), (self.x + self.largura_painel - 30, self.botoes_aba["stats"].rect.bottom + 5), 1)

        if self.aba_ativa == "stats": self.desenhar_aba_stats()
        elif self.aba_ativa == "social": self.desenhar_aba_social()
        elif self.aba_ativa == "chat": self.desenhar_aba_chat()
        elif self.aba_ativa == "history": self.desenhar_aba_history()

        self.btn_fechar.desenhar(self.tela)
        if self.seletor_aberto:
            pygame.draw.rect(self.tela, (30,30,40), self.rect_seletor, border_radius=10); pygame.draw.rect(self.tela, OURO, self.rect_seletor, 2, border_radius=10)
            for btn in self.botoes_avatar:
                r, h = btn["rect"], btn["rect"].collidepoint(mouse_pos)
                pygame.draw.rect(self.tela, (60,60,70) if h else (40,40,50), r, border_radius=5)
                self.desenhar_icone_simples(r.centerx, r.centery, btn["nome"])

        if self.notificacao_timer > 0:
            self.notificacao_timer -= 1
            st = pygame.Surface((400, 50)); st.fill((50,50,50)); pygame.draw.rect(st, OURO, (0,0,400,50), 2)
            t = self.fonte_texto.render(self.notificacao_msg, True, BRANCO)
            st.blit(t, (200-t.get_width()//2, 15)); self.tela.blit(st, ((LARGURA-400)//2, ALTURA-100))

    def processar_eventos(self, event):
        dados = self.jogo.dados_globais
        if event.type == pygame.KEYDOWN:
            if self.digitando_nome:
                if event.key == pygame.K_RETURN: dados["nome_jogador"] = self.temp_nome; salvar_dados(dados); self.digitando_nome = False
                elif event.key == pygame.K_BACKSPACE: self.temp_nome = self.temp_nome[:-1]
                elif len(self.temp_nome) < 15 and event.unicode.isprintable(): self.temp_nome += event.unicode
            
            elif self.aba_ativa == "chat" and self.digitando_chat and self.modo_chat != "menu":
                if event.key == pygame.K_RETURN and self.input_chat:
                    nome_dest = self.amigos[self.selecionado_idx]["nome"] if self.modo_chat == "amigos" else self.personagens_ia[self.ia_selecionada_idx]["nome"]
                    key_log = f"chat_{self.modo_chat}_{nome_dest}"
                    
                    if key_log not in self.chat_session_logs: self.chat_session_logs[key_log] = []
                    
                    msg_user = {"sender": "me", "text": self.input_chat}
                    self.chat_session_logs[key_log].append(msg_user)
                    
                    if self.modo_chat == "ia":
                        self.chat_ai_service.enviar_mensagem(nome_dest, self.chat_session_logs[key_log])
                    
                    self.input_chat = ""
                elif event.key == pygame.K_BACKSPACE: self.input_chat = self.input_chat[:-1]
                elif len(self.input_chat) < 100 and event.unicode.isprintable(): self.input_chat += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.seletor_aberto:
                for b in self.botoes_avatar:
                    if b["rect"].collidepoint(pos):
                        if b["tipo"]=="custom": self.importar_imagem_pc()
                        else: dados["avatar_id"]=b["id"]; dados["avatar_path"]=""; salvar_dados(dados)
                        self.seletor_aberto=False; return
                if not self.rect_seletor.collidepoint(pos): self.seletor_aberto=False
                return

            if self.btn_fechar.desenhar(self.tela): self.jogo.mudar_estado(MENU)
            if self.rect_avatar.collidepoint(pos): self.seletor_aberto = True
            if self.rect_nome.collidepoint(pos): self.digitando_nome = True; self.temp_nome = dados.get("nome_jogador", "")
            
            for k, btn in self.botoes_aba.items():
                if btn.rect.collidepoint(pos): self.aba_ativa = k
            
            if self.aba_ativa == "chat":
                if self.modo_chat == "menu":
                    if self.btn_chat_amigos.desenhar(self.tela): self.modo_chat = "amigos"
                    if self.btn_chat_ia.desenhar(self.tela): self.modo_chat = "ia"
                else:
                    if self.btn_voltar_chat.desenhar(self.tela): self.modo_chat = "menu"
                    if pos[1] > self.y + 550 and pos[0] > self.x + 300: self.digitando_chat = True
                    else: self.digitando_chat = False
            
            if self.aba_ativa == "history":
                if event.button == 4: self.scroll_y_conquistas = min(0, self.scroll_y_conquistas + 20)
                if event.button == 5: self.scroll_y_conquistas -= 20