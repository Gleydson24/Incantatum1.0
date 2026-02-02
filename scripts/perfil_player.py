import pygame
import random
import os
import tkinter as tk
from tkinter import filedialog
from scripts.settings import *
from scripts.utils import Botao
from scripts.save_system import salvar_dados
from scripts.ai_service import ChatIA
from scripts.network import CLIENTE_ONLINE

# Cores dos Elos
CORES_TIER = {
    "Bronze": (205, 127, 50),
    "Prata": (192, 192, 192),
    "Ouro": (255, 215, 0),
    "Platina": (0, 255, 200),
    "Diamante": (185, 242, 255),
    "Mestre": (255, 100, 255),
    "Desafiante": (255, 50, 50)
}

class PerfilJogador:
    def __init__(self, jogo):
        self.jogo = jogo
        self.tela = jogo.tela
        
        self.largura_painel = 1000; self.altura_painel = 680
        self.x = (LARGURA - self.largura_painel) // 2
        self.y = (ALTURA - self.altura_painel) // 2
        self.rect_painel = pygame.Rect(self.x, self.y, self.largura_painel, self.altura_painel)
        
        self.COR_FUNDO_PAINEL = (20, 20, 25); self.COR_MOLDURA = (60, 50, 40); self.COR_CHAT_BG = (15, 15, 20)
        
        try:
            self.fonte_nome = pygame.font.SysFont("Garamond", 55, bold=True)
            self.fonte_titulo = pygame.font.SysFont("Garamond", 22, italic=True)
            self.fonte_secao = pygame.font.SysFont("Arial", 18, bold=True)
            self.fonte_texto = pygame.font.SysFont("Arial", 16)
            self.fonte_mini = pygame.font.SysFont("Arial", 12, bold=True)
            self.fonte_rank = pygame.font.SysFont("Impact", 40)
            self.fonte_icone = pygame.font.SysFont("Segoe UI Symbol", 25) 
        except: self.fonte_nome = pygame.font.SysFont(None, 60)
        
        self.btn_fechar = Botao(self.x + self.largura_painel - 50, self.y + 10, 40, 40, "X", cor_fundo=(80, 20, 20))

        y_abas = self.y + 160; w_aba = 180
        self.aba_ativa = "stats"
        self.botoes_aba = {
            "stats": Botao(self.x + 30, y_abas, w_aba, 35, "ESTATÍSTICAS", tamanho_fonte=16),
            "social": Botao(self.x + 30 + w_aba + 10, y_abas, w_aba, 35, "SOCIAL", tamanho_fonte=16),
            "chat": Botao(self.x + 30 + (w_aba + 10)*2, y_abas, w_aba, 35, "CHAT", tamanho_fonte=16),
            "conta": Botao(self.x + 30 + (w_aba + 10)*3, y_abas, w_aba, 35, "RANKING / CONTA", tamanho_fonte=16)
        }

        self.digitando_nome = False; self.temp_nome = ""
        self.rect_nome = pygame.Rect(self.x + 160, self.y + 50, 400, 60)
        self.rect_avatar = pygame.Rect(self.x + 50, self.y + 40, 100, 100)
        self.avatar_img_custom = None; self.carregar_avatar_customizado() 
        self.tipos_avatar = ["bruxo", "caveira", "pocao", "coruja"]
        self.seletor_aberto = False
        self.rect_seletor = pygame.Rect(self.x + 40, self.y + 150, 320, 80)
        self.botoes_avatar = []
        for i, t in enumerate(self.tipos_avatar): self.botoes_avatar.append({"tipo":"interno", "id":i, "rect":pygame.Rect(self.rect_seletor.x+10+(i*60), self.rect_seletor.y+10, 50, 60), "nome":t})
        self.botoes_avatar.append({"tipo":"custom", "rect":pygame.Rect(self.rect_seletor.x+10+(4*60), self.rect_seletor.y+10, 50, 60), "nome":"+"})

        # --- CHAT ---
        self.chat_ai_service = ChatIA(); self.modo_chat = "menu"; self.chat_session_logs = {}
        self.btn_chat_amigos = Botao(0,0,300,200,"FALAR COM AMIGOS",cor_fundo=(50,50,80))
        self.btn_chat_ia = Botao(0,0,300,200,"PERSONAGENS (IA)",cor_fundo=(80,50,50), tamanho_fonte=24)
        self.btn_voltar_chat = Botao(0,0,80,30,"Voltar",cor_fundo=(50,50,50),tamanho_fonte=14)
        
        self.personagens_ia = [
            {"nome": "Harry Potter", "cor": (255,100,100)}, 
            {"nome": "Hermione Granger", "cor": (200,100,200)},
            {"nome": "Rony Weasley", "cor": (200,150,100)},
            {"nome": "Dumbledore", "cor": (150,150,255)}
        ]
        if self.jogo.dados_globais.get("jojo_desbloqueado", False):
            self.personagens_ia.append({"nome": "Jojo", "cor": (100, 100, 100)})

        self.selecionado_idx = 0; self.ia_selecionada_idx = 0; self.input_chat = ""; self.digitando_chat = False

        # --- CONTA / RANK (Posições Ajustadas) ---
        self.input_user = ""; self.input_pass = ""; self.foco_input = None
        self.msg_erro_login = ""
        # Botões reposicionados para baixo (y + 350) e alargados (170px)
        self.btn_login = Botao(self.x + 300, self.y + 350, 170, 45, "ENTRAR", cor_fundo=(0, 100, 0))
        self.btn_registrar = Botao(self.x + 500, self.y + 350, 170, 45, "CADASTRAR", cor_fundo=(0, 0, 100))
        self.btn_refresh = Botao(self.x + 750, self.y + 230, 100, 30, "Atualizar", cor_fundo=(50,50,50), tamanho_fonte=14)
        self.btn_add_friend = []

        self.particulas = []
        for _ in range(20): self.particulas.append([random.randint(self.x, self.x+1000), random.randint(self.y, self.y+680), random.uniform(0.5,2), random.randint(2,5)])
        self.notificacao_msg = ""; self.notificacao_timer = 0
        self.scroll_y_conquistas = 0

    def carregar_avatar_customizado(self):
        try:
            path = self.jogo.dados_globais.get("avatar_path", "")
            if path and os.path.exists(path): self.avatar_img_custom = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (80,80))
        except: pass

    def importar_imagem_pc(self):
        try:
            root = tk.Tk(); root.withdraw() 
            file_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg")])
            root.destroy()
            if file_path:
                self.jogo.dados_globais["avatar_path"] = file_path; self.jogo.dados_globais["avatar_id"] = -1
                salvar_dados(self.jogo.dados_globais); self.carregar_avatar_customizado()
        except: pass

    def quebrar_texto(self, texto, largura_max):
        palavras = texto.split(' '); linhas = []; linha_atual = ""
        for p in palavras:
            t = linha_atual + p + " "
            if self.fonte_texto.size(t)[0] < largura_max: linha_atual = t
            else: linhas.append(linha_atual); linha_atual = p + " "
        linhas.append(linha_atual)
        return linhas

    def desenhar_avatar_interno(self, cx, cy, tipo):
        if tipo == "bruxo": pygame.draw.circle(self.tela, (200, 180, 50), (cx, cy), 40)
        elif tipo == "caveira": pygame.draw.circle(self.tela, (30, 30, 30), (cx, cy), 40)
        elif tipo == "pocao": pygame.draw.circle(self.tela, (40, 0, 40), (cx, cy), 40)
        elif tipo == "coruja": pygame.draw.circle(self.tela, (60, 40, 20), (cx, cy), 40)
        pygame.draw.circle(self.tela, OURO, (cx, cy), 40, 2)

    def desenhar_icone_simples(self, cx, cy, tipo):
        if tipo == "bruxo": pygame.draw.circle(self.tela, (200, 180, 50), (cx, cy), 15)
        elif tipo == "+": 
            pygame.draw.line(self.tela, BRANCO, (cx-10, cy), (cx+10, cy), 3); pygame.draw.line(self.tela, BRANCO, (cx, cy-10), (cx, cy+10), 3)
        else: pygame.draw.circle(self.tela, CINZA, (cx, cy), 15)

    def desenhar_barra_xp(self):
        dados = self.jogo.dados_globais
        xp, xp_prox = dados.get("xp_atual", 0), dados.get("xp_proximo_nivel", 1000)
        nivel = dados.get("nivel_jogador", 1)
        bx, by = self.x + self.largura_painel - 350, self.y + 60
        bw, bh = 300, 20
        self.tela.blit(self.fonte_secao.render(f"NÍVEL {nivel}", True, OURO), (bx, by - 25))
        pygame.draw.rect(self.tela, (30, 30, 30), (bx, by, bw, bh), border_radius=10)
        if xp_prox > 0: pygame.draw.rect(self.tela, (0, 200, 255), (bx, by, bw * min(1, xp/xp_prox), bh), border_radius=10)
        pygame.draw.rect(self.tela, BRANCO, (bx, by, bw, bh), 1, border_radius=10)
        t = self.fonte_mini.render(f"{int(xp)} / {int(xp_prox)} XP", True, BRANCO)
        self.tela.blit(t, (bx + bw//2 - t.get_width()//2, by + 3))

    def desenhar_aba_stats(self):
        dados = self.jogo.dados_globais
        x, y = self.x + 50, self.y + 250
        stats = [("Partidas", dados.get("partidas_totais", 0)), ("Vitórias", dados.get("vitorias_p1", 0)), ("Derrotas", dados.get("partidas_totais", 0) - dados.get("vitorias_p1", 0))]
        for i, (l, v) in enumerate(stats):
            bx = x + i * 160
            pygame.draw.rect(self.tela, (35,35,45), (bx, y, 140, 50), border_radius=5)
            self.tela.blit(self.fonte_secao.render(str(v), True, OURO), (bx + 10, y + 5))
            self.tela.blit(self.fonte_mini.render(l.upper(), True, CINZA_TEXTO), (bx + 10, y + 30))
        y_bar = y + 80
        for k, n, c in [("incendio", "Incendio", (255, 100, 0)), ("protego", "Protego", (50, 100, 255)), ("avada kedavra", "Avada", (0, 255, 0))]:
            usos = dados.get("maestria", {}).get(k, 0)
            self.tela.blit(self.fonte_texto.render(n, True, CINZA_CLARO), (x, y_bar))
            pygame.draw.rect(self.tela, (20,20,20), (x+150, y_bar+2, 400, 15), border_radius=4)
            if usos > 0: pygame.draw.rect(self.tela, c, (x+150, y_bar+2, int(400 * min(1, usos/50)), 15), border_radius=4)
            self.tela.blit(self.fonte_mini.render(f"{usos} usos", True, c), (x+570, y_bar))
            y_bar += 35

    def desenhar_aba_social(self):
        x, y = self.x + 50, self.y + 250
        self.btn_add_friend = []
        
        if not CLIENTE_ONLINE.conectado:
            self.tela.blit(self.fonte_titulo.render("Faça Login para encontrar bruxos!", True, CINZA), (x, y))
            return

        self.tela.blit(self.fonte_secao.render("BRUXOS SUGERIDOS PARA DUELO", True, OURO), (x, y - 30))
        
        if not CLIENTE_ONLINE.sugestoes:
            self.tela.blit(self.fonte_texto.render("Carregando sugestões ou sem jogadores...", True, CINZA), (x, y + 20))
        
        for i, p in enumerate(CLIENTE_ONLINE.sugestoes):
            yy = y + (i * 70)
            pygame.draw.rect(self.tela, (40, 40, 45), (x, yy, 900, 60), border_radius=8)
            cor_tier = CORES_TIER.get(p.get("tier"), BRANCO)
            pygame.draw.circle(self.tela, cor_tier, (x + 40, yy + 30), 20)
            
            self.tela.blit(self.fonte_secao.render(p['nome'], True, BRANCO), (x + 80, yy + 10))
            self.tela.blit(self.fonte_mini.render(f"{p['tier']} - {p['elo']} ELO", True, cor_tier), (x + 80, yy + 35))

            if p['nome'] not in CLIENTE_ONLINE.friends:
                btn = pygame.Rect(x + 750, yy + 15, 40, 30)
                self.btn_add_friend.append({"rect": btn, "nome": p['nome']})
                c_btn = (0, 100, 0) if btn.collidepoint(pygame.mouse.get_pos()) else (0, 80, 0)
                pygame.draw.rect(self.tela, c_btn, btn, border_radius=5)
                lbl = self.fonte_secao.render("+", True, BRANCO)
                self.tela.blit(lbl, (btn.centerx - lbl.get_width()//2, btn.centery - lbl.get_height()//2))
            else:
                self.tela.blit(self.fonte_mini.render("AMIGO", True, (0,255,0)), (x+750, yy+20))

    def desenhar_aba_chat(self):
        x_base, y_base = self.x + 30, self.y + 210
        w_chat, h_chat = 940, 420
        
        if self.modo_chat == "menu":
            self.btn_chat_amigos.rect.center = (self.x + 300, self.y + 400); self.btn_chat_amigos.desenhar(self.tela)
            self.btn_chat_ia.rect.center = (self.x + 700, self.y + 400); self.btn_chat_ia.desenhar(self.tela)
            self.tela.blit(self.fonte_secao.render("Escolha com quem conversar:", True, CINZA_CLARO), (self.x + 500 - 100, self.y + 250))
            return

        w_lista, w_msgs = 250, w_chat - 250
        pygame.draw.rect(self.tela, (30, 30, 35), (x_base, y_base, w_lista, h_chat), border_top_left_radius=8, border_bottom_left_radius=8)
        
        lista_display = []
        if self.modo_chat == "amigos":
            for f in CLIENTE_ONLINE.friends: lista_display.append({"nome": f, "cor": (100, 200, 100)})
            if not lista_display: self.tela.blit(self.fonte_mini.render("Adicione amigos no Social!", True, CINZA), (x_base+10, y_base+20))
        else:
            lista_display = self.personagens_ia

        idx_sel = self.selecionado_idx if self.modo_chat == "amigos" else self.ia_selecionada_idx
        
        for i, item in enumerate(lista_display):
            cor_bg = (50, 50, 60) if i == idx_sel else (30, 30, 35)
            r = pygame.Rect(x_base, y_base + (i*60), w_lista, 60)
            if r.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                if self.modo_chat == "amigos": self.selecionado_idx = i
                else: self.ia_selecionada_idx = i
            pygame.draw.rect(self.tela, cor_bg, r)
            pygame.draw.circle(self.tela, item["cor"], (x_base + 30, y_base + (i*60) + 30), 20)
            self.tela.blit(self.fonte_secao.render(item["nome"], True, BRANCO), (x_base + 60, y_base + (i*60) + 20))

        chat_rect = pygame.Rect(x_base + w_lista, y_base, w_msgs, h_chat - 50)
        pygame.draw.rect(self.tela, self.COR_CHAT_BG, chat_rect, border_top_right_radius=8)
        
        target_name = lista_display[idx_sel]["nome"] if lista_display else "Ninguém"
        
        pygame.draw.rect(self.tela, (25, 25, 30), (chat_rect.x, chat_rect.y, chat_rect.width, 40))
        self.tela.blit(self.fonte_secao.render(f"Chat: {target_name}", True, OURO), (chat_rect.x + 20, chat_rect.y + 10))
        self.btn_voltar_chat.rect.topright = (chat_rect.right - 10, chat_rect.y + 5); self.btn_voltar_chat.desenhar(self.tela)
        
        if target_name != "Ninguém":
            logs_key = f"chat_{self.modo_chat}_{target_name}"
            logs = self.chat_session_logs.get(logs_key, [])
            if self.modo_chat == "ia":
                resp = self.chat_ai_service.checar_resposta()
                if resp: 
                    logs.append({"sender": "them", "text": resp}); self.chat_session_logs[logs_key] = logs

            area_mensagens = pygame.Rect(chat_rect.x, chat_rect.y + 40, chat_rect.width, chat_rect.height - 40)
            self.tela.set_clip(area_mensagens)
            msg_y = chat_rect.bottom - 20; w_max = w_msgs - 60
            for msg in reversed(logs):
                lines = self.quebrar_texto(msg["text"], w_max)
                h_box = (len(lines) * 20) + 10
                is_me = msg["sender"] == "me"
                w_real = max([self.fonte_texto.size(l)[0] for l in lines]) + 20
                x_msg = chat_rect.right - w_real - 20 if is_me else chat_rect.left + 20
                c_box = (0, 100, 0) if is_me else ((60, 60, 60) if self.modo_chat == "amigos" else (80, 40, 80))
                
                pygame.draw.rect(self.tela, c_box, (x_msg, msg_y - h_box, w_real, h_box), border_radius=10)
                off = 0
                for l in lines:
                    self.tela.blit(self.fonte_texto.render(l, True, BRANCO), (x_msg + 10, msg_y - h_box + 5 + off)); off += 20
                msg_y -= (h_box + 10)
                if msg_y < chat_rect.top: break
            self.tela.set_clip(None)

            ir = pygame.Rect(x_base + w_lista, y_base + h_chat - 50, w_msgs, 50)
            pygame.draw.rect(self.tela, (40, 40, 50), ir, border_bottom_right_radius=8)
            t = self.input_chat + ("|" if self.digitando_chat and (pygame.time.get_ticks()//500)%2==0 else "")
            self.tela.blit(self.fonte_texto.render(t, True, BRANCO), (ir.x+10, ir.y+15))

    def desenhar_aba_conta(self):
        x, y = self.x + 50, self.y + 230
        if not CLIENTE_ONLINE.conectado:
            self.tela.blit(self.fonte_secao.render("LOGIN / CADASTRO", True, OURO), (x + 350, y - 20))
            
            # Ajuste de Layout: Labels e Placeholders
            c_u = OURO if self.foco_input == "user" else CINZA; c_p = OURO if self.foco_input == "pass" else CINZA
            
            # Label Usuário
            self.tela.blit(self.fonte_texto.render("Usuário:", True, CINZA_CLARO), (x+250, y+40))
            pygame.draw.rect(self.tela, (30,30,40), (x+250, y+65, 400, 40), border_radius=5)
            pygame.draw.rect(self.tela, c_u, (x+250, y+65, 400, 40), 2, border_radius=5)
            
            if self.input_user:
                self.tela.blit(self.fonte_texto.render(self.input_user, True, BRANCO), (x+260, y+75))
            elif self.foco_input != "user":
                self.tela.blit(self.fonte_texto.render("Digite aqui...", True, (100,100,100)), (x+260, y+75))

            # Label Senha
            self.tela.blit(self.fonte_texto.render("Senha:", True, CINZA_CLARO), (x+250, y+115))
            pygame.draw.rect(self.tela, (30,30,40), (x+250, y+140, 400, 40), border_radius=5)
            pygame.draw.rect(self.tela, c_p, (x+250, y+140, 400, 40), 2, border_radius=5)
            
            if self.input_pass:
                self.tela.blit(self.fonte_texto.render("*"*len(self.input_pass), True, BRANCO), (x+260, y+150))
            elif self.foco_input != "pass":
                self.tela.blit(self.fonte_texto.render("Digite aqui...", True, (100,100,100)), (x+260, y+150))
            
            self.btn_login.desenhar(self.tela)
            self.btn_registrar.desenhar(self.tela)
            
            if self.msg_erro_login: 
                self.tela.blit(self.fonte_mini.render(self.msg_erro_login, True, (255,100,100)), (x+250, y+270))
        else:
            elo = CLIENTE_ONLINE.elo; tier = CLIENTE_ONLINE.tier; cor_tier = CORES_TIER.get(tier, BRANCO)
            pygame.draw.circle(self.tela, (30, 30, 40), (x + 100, y + 80), 70); pygame.draw.circle(self.tela, cor_tier, (x + 100, y + 80), 70, 5)
            lb_tier = self.fonte_secao.render(tier.upper(), True, cor_tier); self.tela.blit(lb_tier, (x + 100 - lb_tier.get_width()//2, y + 60))
            lb_elo = self.fonte_titulo.render(str(elo), True, BRANCO); self.tela.blit(lb_elo, (x + 100 - lb_elo.get_width()//2, y + 90))
            self.tela.blit(self.fonte_secao.render(f"Bem-vindo, {CLIENTE_ONLINE.username}", True, BRANCO), (x + 200, y + 20))
            self.btn_refresh.desenhar(self.tela)
            pygame.draw.line(self.tela, CINZA, (x + 200, y + 60), (x + 900, y + 60))
            self.tela.blit(self.fonte_mini.render("RANK GLOBAL (TOP JOGADORES)", True, CINZA_CLARO), (x + 200, y + 45))
            y_list = y + 70
            for i, p in enumerate(CLIENTE_ONLINE.top_rank):
                c = OURO if i == 0 else (BRANCO if i < 3 else CINZA); t_tier = CORES_TIER.get(p.get('tier'), BRANCO)
                pygame.draw.rect(self.tela, (35, 35, 40), (x+200, y_list, 700, 25))
                self.tela.blit(self.fonte_mini.render(f"#{i+1}", True, c), (x+210, y_list+5))
                self.tela.blit(self.fonte_mini.render(p['nome'], True, c), (x+250, y_list+5))
                self.tela.blit(self.fonte_mini.render(f"{p['elo']} PDL", True, OURO), (x+500, y_list+5))
                self.tela.blit(self.fonte_mini.render(p.get('tier', 'Unranked'), True, t_tier), (x+600, y_list+5))
                y_list += 28
                if i >= 8: break

    def desenhar(self):
        dados = self.jogo.dados_globais
        mouse_pos = pygame.mouse.get_pos()
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA); overlay.fill((0, 0, 0, 220)); self.tela.blit(overlay, (0, 0))
        pygame.draw.rect(self.tela, self.COR_FUNDO_PAINEL, self.rect_painel, border_radius=10)
        pygame.draw.rect(self.tela, self.COR_MOLDURA, self.rect_painel, 2, border_radius=10)
        idx = dados.get("avatar_id", 0)
        if idx == -1 and self.avatar_img_custom: self.tela.blit(self.avatar_img_custom, (self.x+60, self.y+50))
        else: self.desenhar_avatar_interno(self.x+100, self.y+90, self.tipos_avatar[idx] if idx < 4 else "bruxo")
        self.tela.blit(self.fonte_nome.render(self.temp_nome if self.digitando_nome else dados.get("nome_jogador"), True, BRANCO), (self.x+160, self.y+50))
        if not self.digitando_nome: 
             try: self.tela.blit(self.fonte_icone.render("✎", True, BRANCO), (self.x+450, self.y+60))
             except: pass
        self.tela.blit(self.fonte_titulo.render(dados.get("titulo_jogador"), True, CINZA_CLARO), (self.x+160, self.y+115))
        self.desenhar_barra_xp()
        for k, b in self.botoes_aba.items(): 
            b.cor_fundo = (80,80,100) if self.aba_ativa == k else (40,40,40); b.desenhar(self.tela)
        if self.aba_ativa == "stats": self.desenhar_aba_stats()
        elif self.aba_ativa == "social": self.desenhar_aba_social()
        elif self.aba_ativa == "chat": self.desenhar_aba_chat()
        elif self.aba_ativa == "conta": self.desenhar_aba_conta()
        elif self.aba_ativa == "history": self.desenhar_aba_history()
        self.btn_fechar.desenhar(self.tela)
        if self.seletor_aberto:
            pygame.draw.rect(self.tela, (30,30,40), self.rect_seletor); 
            for b in self.botoes_avatar: pygame.draw.rect(self.tela, (60,60,70), b["rect"], 1)
        if self.notificacao_timer > 0:
            self.notificacao_timer -= 1; t = self.fonte_texto.render(self.notificacao_msg, True, (100,255,100)); self.tela.blit(t, (LARGURA//2 - t.get_width()//2, ALTURA-50))

    def processar_eventos(self, event):
        dados = self.jogo.dados_globais
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_fechar.desenhar(self.tela): self.jogo.mudar_estado(MENU)
            for k, b in self.botoes_aba.items(): 
                if b.rect.collidepoint(event.pos): 
                    self.aba_ativa = k
                    if k == "conta" and CLIENTE_ONLINE.conectado: CLIENTE_ONLINE.atualizar_dados()
                    if k == "social" and CLIENTE_ONLINE.conectado: CLIENTE_ONLINE.atualizar_dados()

            if self.aba_ativa == "conta" and not CLIENTE_ONLINE.conectado:
                x, y = self.x + 50, self.y + 250
                # Ajuste de coordenadas de clique para as novas caixas
                r_u = pygame.Rect(x+250, y+65, 400, 40)
                r_p = pygame.Rect(x+250, y+140, 400, 40)
                
                if r_u.collidepoint(event.pos): self.foco_input = "user"
                elif r_p.collidepoint(event.pos): self.foco_input = "pass"
                else: self.foco_input = None
                
                if self.btn_login.desenhar(self.tela):
                    if not self.input_user.strip(): self.msg_erro_login = "Digite um usuário!"
                    else:
                        resp = CLIENTE_ONLINE.login(self.input_user, self.input_pass)
                        if resp["status"] == "error": self.msg_erro_login = resp["msg"]
                        else:
                            dados["nome_jogador"] = self.input_user
                            if "vitorias" in resp: dados["vitorias_p1"] = resp["vitorias"]
                            salvar_dados(dados)
                            CLIENTE_ONLINE.atualizar_dados()
                            
                if self.btn_registrar.desenhar(self.tela):
                    if not self.input_user.strip(): self.msg_erro_login = "Digite um usuário!"
                    else:
                        resp = CLIENTE_ONLINE.registrar(self.input_user, self.input_pass)
                        self.msg_erro_login = resp["msg"]
                        
            elif self.aba_ativa == "conta" and CLIENTE_ONLINE.conectado:
                if self.btn_refresh.desenhar(self.tela): CLIENTE_ONLINE.atualizar_dados()

            if self.aba_ativa == "social":
                for item in self.btn_add_friend:
                    if item["rect"].collidepoint(event.pos):
                        msg = CLIENTE_ONLINE.adicionar_amigo(item["nome"])
                        self.notificacao_msg = msg; self.notificacao_timer = 120

            if self.aba_ativa == "chat":
                if self.modo_chat == "menu":
                    if self.btn_chat_amigos.desenhar(self.tela): self.modo_chat = "amigos"
                    if self.btn_chat_ia.desenhar(self.tela): self.modo_chat = "ia"
                else:
                    if self.btn_voltar_chat.desenhar(self.tela): self.modo_chat = "menu"
                    if event.pos[1] > self.y+600: self.digitando_chat = True

        if event.type == pygame.KEYDOWN:
            if self.aba_ativa == "conta" and self.foco_input:
                t = self.input_user if self.foco_input == "user" else self.input_pass
                if event.key == pygame.K_BACKSPACE: t = t[:-1]
                elif event.unicode.isprintable(): t += event.unicode
                if self.foco_input == "user": self.input_user = t
                else: self.input_pass = t
            
            if self.aba_ativa == "chat" and self.digitando_chat:
                if event.key == pygame.K_RETURN and self.input_chat:
                    lista = CLIENTE_ONLINE.friends if self.modo_chat == "amigos" else self.personagens_ia
                    idx = self.selecionado_idx if self.modo_chat == "amigos" else self.ia_selecionada_idx
                    if lista:
                        name = lista[idx] if self.modo_chat == "amigos" else lista[idx]["nome"]
                        k = f"chat_{self.modo_chat}_{name}"
                        if k not in self.chat_session_logs: self.chat_session_logs[k] = []
                        self.chat_session_logs[k].append({"sender": "me", "text": self.input_chat})
                        
                        if self.modo_chat == "ia" and "joaildo" in self.input_chat.lower():
                            if not dados.get("jojo_desbloqueado"):
                                dados["jojo_desbloqueado"] = True; salvar_dados(dados)
                                self.personagens_ia.append({"nome": "Jojo", "cor": (100, 100, 100)})
                                self.chat_session_logs[k].append({"sender": "them", "text": "👀 Uma presença estranha se aproxima..."})

                        if self.modo_chat == "ia": self.chat_ai_service.enviar_mensagem(name, self.chat_session_logs[k])
                        self.input_chat = ""
                elif event.key == pygame.K_BACKSPACE: self.input_chat = self.input_chat[:-1]
                elif len(self.input_chat) < 100: self.input_chat += event.unicode