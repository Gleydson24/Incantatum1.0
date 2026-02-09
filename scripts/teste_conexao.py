from google import genai
import os

# --- COLOQUE SUA CHAVE AQUI ---
API_KEY = "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" 

print("--- INICIANDO DIAGNÓSTICO DETALHADO ---")

try:
    client = genai.Client(api_key=API_KEY)
    
    print("1. Tentando listar modelos disponíveis para sua chave...")
    try:
        # Tenta listar tudo o que sua chave pode ver
        modelos = client.models.list()
        count = 0
        for m in modelos:
            print(f"   - Encontrado: {m.name}")
            count += 1
        
        if count == 0:
            print("   [ALERTA] A lista retornou vazia. Sua chave pode não ter permissão para acessar modelos.")
        else:
            print(f"   [SUCESSO] Total de {count} modelos encontrados.")
            
    except Exception as e:
        print(f"   [FALHA NA LISTAGEM] Erro: {e}")

    print("\n2. Tentando teste de envio (Força Bruta)...")
    candidatos = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-pro",
        "gemini-2.0-flash-exp",
        "models/gemini-1.5-flash"
    ]
    
    for modelo in candidatos:
        print(f"   Tentando modelo: {modelo}...", end=" ")
        try:
            response = client.models.generate_content(
                model=modelo,
                contents="Teste"
            )
            print("OK! (Funcionou)")
            print(f"   -> Resposta: {response.text.strip()}")
            break # Se funcionou, para
        except Exception as e:
            print("FALHOU.")
            # Pega o erro específico para entendermos
            erro_str = str(e)
            if "404" in erro_str: print("      Motivo: Modelo não encontrado (404)")
            elif "429" in erro_str: print("      Motivo: Limite de cota excedido (429 - Sem crédito)")
            elif "400" in erro_str: print(f"      Motivo: Requisição inválida (400) - {erro_str}")
            elif "403" in erro_str: print("      Motivo: Permissão negada (403 - Chave inválida ou bloqueada)")
            else: print(f"      Motivo: {erro_str}")

except Exception as e:
    print(f"\n[ERRO CRÍTICO] Não foi possível nem iniciar o cliente: {e}")

input("\nPressione ENTER para sair...")