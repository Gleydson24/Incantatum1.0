import json
import os
import random
import datetime

ARQUIVO_SAVE = "save_game.json"

def carregar_dados():
    hoje_str = str(datetime.date.today())

    dados_padrao = {
        "nome_jogador": f"Guest-{random.randint(1000, 9999)}",
        "nome_alterado": False,
        "avatar_id": 0,
        "avatar_path": "",
        "partidas_totais": 0,
        "vitorias_p1": 0,
        "vitorias_p2": 0,
        "vitorias_ia": 0,
        
        # Nível
        "nivel_jogador": 1,
        "xp_atual": 0,
        "xp_proximo_nivel": 1000,
        
        # Missões Diárias
        "data_ultima_missao": hoje_str, 
        "missoes_diarias": [],  
        
        # --- NOVO: Histórico e Chat ---
        "historico_conquistas": [], # Lista de missões antigas já feitas
        "chat_logs": {},            # Histórico de conversas com amigos
        # ------------------------------

        "maestria": {
            "incendio": 0,
            "protego": 0,
            "sectumsempra": 0,
            "expelliarmus": 0,
            "avada kedavra": 0
        }
    }
    
    if not os.path.exists(ARQUIVO_SAVE):
        salvar_dados(dados_padrao)
        return dados_padrao
    
    try:
        with open(ARQUIVO_SAVE, "r") as f:
            dados = json.load(f)
            # Mescla chaves novas para não quebrar saves antigos
            for k, v in dados_padrao.items():
                if k not in dados:
                    dados[k] = v
            return dados
    except Exception as e:
        print(f"Erro ao carregar save: {e}")
        return dados_padrao

def salvar_dados(dados):
    try:
        with open(ARQUIVO_SAVE, "w") as f:
            json.dump(dados, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar: {e}")