import pygame
import random
import datetime
from scripts.settings import *
from scripts.utils import Botao
from scripts.save_system import salvar_dados

# --- MANTENHA A LISTA "MODELOS" IGUAL ESTAVA ANTES ---
MODELOS = [
    {"titulo": "Duelista Nato", "desc_template": "Vença {meta} partidas (P1).", "tipo_dado": "vitorias_p1", "chave_maestria": None, "min_meta": 1, "max_meta": 3, "xp_por_unidade": 150},
    {"titulo": "Treino Constante", "desc_template": "Jogue {meta} partidas completas.", "tipo_dado": "partidas_totais", "chave_maestria": None, "min_meta": 2, "max_meta": 5, "xp_por_unidade": 100},
    {"titulo": "Mestre do Fogo", "desc_template": "Use Incendio {meta} vezes.", "tipo_dado": "incendio", "chave_maestria": "incendio", "min_meta": 5, "max_meta": 15, "xp_por_unidade": 30},
    {"titulo": "Defesa Impenetrável", "desc_template": "Use Protego {meta} vezes.", "tipo_dado": "protego", "chave_maestria": "protego", "min_meta": 5, "max_meta": 12, "xp_por_unidade": 40},
    {"titulo": "Desarme Tático", "desc_template": "Use Expelliarmus {meta} vezes.", "tipo_dado": "expelliarmus", "chave_maestria": "expelliarmus", "min_meta": 5, "max_meta": 15, "xp_por_unidade": 35},
    {"titulo": "Artes das Trevas", "desc_template": "Use Avada Kedavra {meta} vezes.", "tipo_dado": "avada kedavra", "chave_maestria": "avada kedavra", "min_meta": 1, "max_meta": 3, "xp_por_unidade": 300}
]

class TelaDesafios:
    def __init__(self, jogo):
        self.jogo = jogo
        self.tela = jogo.tela
        
        self.largura_painel = 900
        self.altura_painel = 600
        self.x = (LARGURA - self.largura_painel) // 2
        self.y = (ALTURA - self.altura_painel) // 2
        self.rect_painel = pygame.Rect(self.x, self.y, self.largura_painel, self.altura_painel)
        
        self.btn_voltar = Botao(self.x + self.largura_painel - 140, self.y + self.altura_painel - 60, 120, 40, "Voltar", cor_fundo=(100, 30, 30))
        
        try:
            # --- CORREÇÃO: FONTES MENORES ---
            self.fonte_titulo = pygame.font.SysFont("Garamond", 35, bold=True)
            self.fonte_item = pygame.font.SysFont("Garamond", 22, bold=True)
            self.fonte_desc = pygame.font.SysFont("Arial", 16)
            self.fonte_progresso = pygame.font.SysFont("Arial", 14, bold=True)
            self.fonte_btn = pygame.font.SysFont("Arial", 12, bold=True)
        except:
            self.fonte_titulo = pygame.font.SysFont(None, 40)
            self.fonte_item = pygame.font.SysFont(None, 22)

        self.scroll_y = 0
        self.botoes_resgate = []
        self.verificar_virada_do_dia()

    def obter_valor_stat(self, tipo_dado, chave_maestria):
        dados = self.jogo.dados_globais
        if chave_maestria:
            return dados.get("maestria", {}).get(chave_maestria, 0)
        return dados.get(tipo_dado, 0)

    def verificar_virada_do_dia(self):
        dados = self.jogo.dados_globais
        hoje = str(datetime.date.today())
        
        if dados.get("data_ultima_missao") != hoje or not dados.get("missoes_diarias"):
            novas_missoes = []
            escolhidos = random.sample(MODELOS, 3)
            for i, modelo in enumerate(escolhidos):
                meta_random = random.randint(modelo["min_meta"], modelo["max_meta"])
                valor_inicial = self.obter_valor_stat(modelo["tipo_dado"], modelo["chave_maestria"])
                
                nova = {
                    "id": f"daily_{hoje}_{i}",
                    "titulo": modelo["titulo"],
                    "desc": modelo["desc_template"].format(meta=meta_random),
                    "meta": meta_random,
                    "xp": meta_random * modelo["xp_por_unidade"],
                    "valor_inicial": valor_inicial,
                    "tipo_dado": modelo["tipo_dado"],
                    "chave_maestria": modelo["chave_maestria"],
                    "resgatado": False,
                    "data": hoje # Salva a data para exibir no histórico depois
                }
                novas_missoes.append(nova)
            
            dados["missoes_diarias"] = novas_missoes
            dados["data_ultima_missao"] = hoje
            salvar_dados(dados)

    def obter_progresso(self, missao):
        valor_total_atual = self.obter_valor_stat(missao["tipo_dado"], missao["chave_maestria"])
        progresso_hoje = valor_total_atual - missao["valor_inicial"]
        if progresso_hoje < 0: progresso_hoje = 0
        pct = min(1.0, progresso_hoje / missao["meta"])
        concluido = progresso_hoje >= missao["meta"]
        return progresso_hoje, pct, concluido

    def resgatar_xp(self, missao_idx):
        dados = self.jogo.dados_globais
        missao = dados["missoes_diarias"][missao_idx]
        
        if missao["resgatado"]: return

        # XP e Level Up
        xp_ganho = missao["xp"]
        dados["xp_atual"] = dados.get("xp_atual", 0) + xp_ganho
        missao["resgatado"] = True
        
        xp_prox = dados.get("xp_proximo_nivel", 1000)
        while dados["xp_atual"] >= xp_prox:
            dados["xp_atual"] -= xp_prox
            dados["nivel_jogador"] = dados.get("nivel_jogador", 1) + 1
            dados["xp_proximo_nivel"] = int(xp_prox * 1.2)
        
        # --- NOVO: SALVA NO HISTÓRICO PERMANENTE ---
        if "historico_conquistas" not in dados: dados["historico_conquistas"] = []
        # Adiciona no inicio da lista (mais recente primeiro)
        dados["historico_conquistas"].insert(0, {
            "titulo": missao["titulo"],
            "desc": missao["desc"],
            "data": missao.get("data", str(datetime.date.today()))
        })
        # Limita histórico a 50 itens para não pesar
        if len(dados["historico_conquistas"]) > 50:
             dados["historico_conquistas"].pop()
        # -------------------------------------------

        salvar_dados(dados)

    def desenhar_barra(self, x, y, w, h, pct, concluido):
        pygame.draw.rect(self.tela, (30, 30, 30), (x, y, w, h), border_radius=5)
        cor_fill = (50, 200, 50) if concluido else (200, 150, 0)
        fill_w = int(w * pct)
        if fill_w > 0:
            pygame.draw.rect(self.tela, cor_fill, (x, y, fill_w, h), border_radius=5)
        pygame.draw.rect(self.tela, (100, 100, 100), (x, y, w, h), 1, border_radius=5)

    def desenhar(self):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.tela.blit(overlay, (0, 0))
        
        pygame.draw.rect(self.tela, (25, 25, 30), self.rect_painel, border_radius=10)
        pygame.draw.rect(self.tela, OURO_ANTIGO, self.rect_painel, 3, border_radius=10)
        
        dados = self.jogo.dados_globais
        nivel = dados.get("nivel_jogador", 1)
        hoje_formatado = datetime.date.today().strftime("%d/%m")
        
        # --- CORREÇÃO: Título menor e sem display de XP numérico ---
        txt_tit = self.fonte_titulo.render(f"MISSÕES DIÁRIAS ({hoje_formatado})", True, OURO)
        self.tela.blit(txt_tit, (self.x + 30, self.y + 20))
        
        txt_lvl = self.fonte_item.render(f"Nível {nivel}", True, BRANCO) # Só o nível
        self.tela.blit(txt_lvl, (self.x + self.largura_painel - txt_lvl.get_width() - 30, self.y + 30))

        # Lista
        missoes = dados.get("missoes_diarias", [])
        area_lista_y = self.y + 80
        item_h = 80
        padding = 10
        self.botoes_resgate = [] 
        
        for i, missao in enumerate(missoes):
            item_y = area_lista_y + i * (item_h + padding) + self.scroll_y
            if item_y < area_lista_y or item_y + item_h > self.y + self.altura_painel - 70: continue
            
            item_x = self.x + 30
            item_w = self.largura_painel - 60
            
            atual, pct, concluido_fisico = self.obter_progresso(missao)
            ja_resgatou = missao["resgatado"]
            
            cor_bg = (30, 40, 30) if ja_resgatou else ((40, 50, 40) if concluido_fisico else (40, 40, 45))
            rect_item = pygame.Rect(item_x, item_y, item_w, item_h)
            pygame.draw.rect(self.tela, cor_bg, rect_item, border_radius=8)
            pygame.draw.rect(self.tela, (60, 60, 60), rect_item, 1, border_radius=8)

            nome = self.fonte_item.render(missao["titulo"], True, OURO if ja_resgatou else BRANCO)
            self.tela.blit(nome, (item_x + 20, item_y + 10))
            
            desc = self.fonte_desc.render(missao["desc"], True, CINZA_CLARO)
            self.tela.blit(desc, (item_x + 20, item_y + 40))
            
            rect_btn = pygame.Rect(item_x + item_w - 140, item_y + 20, 120, 40)
            
            if ja_resgatou:
                lbl = self.fonte_progresso.render("CONCLUÍDO", True, (100, 255, 100))
                self.tela.blit(lbl, (rect_btn.centerx - lbl.get_width()//2, rect_btn.centery - lbl.get_height()//2))
            
            elif concluido_fisico:
                mouse_pos = pygame.mouse.get_pos()
                hover = rect_btn.collidepoint(mouse_pos)
                cor_btn = (0, 150, 0) if not hover else (0, 200, 0)
                pygame.draw.rect(self.tela, cor_btn, rect_btn, border_radius=5)
                pygame.draw.rect(self.tela, BRANCO, rect_btn, 1, border_radius=5)
                lbl = self.fonte_btn.render(f"RESGATAR", True, BRANCO)
                self.tela.blit(lbl, (rect_btn.centerx - lbl.get_width()//2, rect_btn.centery - lbl.get_height()//2))
                self.botoes_resgate.append((rect_btn, i))
            
            else:
                self.desenhar_barra(item_x + item_w - 220, item_y + 35, 200, 15, pct, False)
                prog_txt = self.fonte_progresso.render(f"{int(atual)}/{missao['meta']}", True, BRANCO)
                self.tela.blit(prog_txt, (item_x + item_w - 220, item_y + 15))

        self.btn_voltar.desenhar(self.tela)
        
    def processar_eventos(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_voltar.rect.collidepoint(event.pos):
                self.jogo.mudar_estado(MENU)
            
            for rect, indice in self.botoes_resgate:
                if rect.collidepoint(event.pos):
                    self.resgatar_xp(indice)
            
            if event.button == 4: self.scroll_y = min(0, self.scroll_y + 20)
            if event.button == 5: 
                max_scroll = -(len(self.jogo.dados_globais.get("missoes_diarias", [])) * 90 - 450)
                self.scroll_y = max(max_scroll, self.scroll_y - 20)