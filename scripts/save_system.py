import json
import os
import random
import datetime

ARQUIVO_SAVE = "save_game.json"

# Listas para gerar varinha aleatória
MADEIRAS = ["Carvalho", "Azevinho", "Teixo", "Salgueiro", "Videira", "Sabugueiro"]
NUCLEOS = ["Pena de Fênix", "Fibra de Coração de Dragão", "Pelo de Unicórnio"]
FLEXIBILIDADE = ["Rígida", "Flexível", "Vibrante", "Quebradiça"]

def carregar_dados():
    hoje_str = str(datetime.date.today())

    varinha_padrao = {
        "madeira": random.choice(MADEIRAS),
        "nucleo": random.choice(NUCLEOS),
        "flex": random.choice(FLEXIBILIDADE)
    }

    dados_padrao = {
        "nome_jogador": f"Guest-{random.randint(1000, 9999)}",
        "nome_alterado": False,
        "titulo_jogador": "Bruxo Iniciante",
        "avatar_id": 0,
        "avatar_path": "",
        "partidas_totais": 0,
        "vitorias_p1": 0,
        "vitorias_p2": 0,
        "vitorias_ia": 0,
        "nivel_jogador": 1,
        "xp_atual": 0,
        "xp_proximo_nivel": 1000,
        "data_ultima_missao": hoje_str, 
        "missoes_diarias": [],  
        "historico_conquistas": [],
        "chat_logs": {},
        
        "jojo_desbloqueado": False,
        
        # --- NOVOS EASTER EGGS ---
        "modo_crianca": False, # Muda o sprite do P1
        "modo_critico": False, # Muda os textos do Grimório
        # -------------------------
        
        "varinha": varinha_padrao,
        "maestria": {
            "incendio": 0, "protego": 0, "sectumsempra": 0, 
            "expelliarmus": 0, "avada kedavra": 0
        }
    }
    
    if not os.path.exists(ARQUIVO_SAVE):
        salvar_dados(dados_padrao)
        return dados_padrao
    
    try:
        with open(ARQUIVO_SAVE, "r") as f:
            dados = json.load(f)
            for k, v in dados_padrao.items():
                if k not in dados: dados[k] = v
            if "varinha" not in dados: dados["varinha"] = varinha_padrao
            return dados
    except Exception as e:
        print(f"Erro ao carregar save: {e}")
        return dados_padrao

def salvar_dados(dados):
    # Atualiza o título automaticamente antes de salvar
    vitorias = dados.get("vitorias_p1", 0)
    total = dados.get("partidas_totais", 0)
    maestria = dados.get("maestria", {})
    
    tit = "Bruxo Iniciante"
    if maestria.get("avada kedavra", 0) > 5: tit = "Portador da Maldição"
    elif maestria.get("incendio", 0) > 50: tit = "Discípulo das Chamas"
    elif vitorias > 50: tit = "Mestre Duelista"
    elif total > 20: tit = "Bruxo Experiente"
    elif vitorias > 10: tit = "Auror em Treinamento"
    
    dados["titulo_jogador"] = tit

    try:
        with open(ARQUIVO_SAVE, "w") as f:
            json.dump(dados, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar: {e}")
