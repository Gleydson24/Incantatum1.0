from groq import Groq
import threading

# --- CONFIGURAÇÃO ---
# COLE SUA CHAVE AQUI
API_KEY = "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" 

MODELO_USAR = "llama-3.3-70b-versatile"

AI_DISPONIVEL = False
client = None

try:
    client = Groq(api_key=API_KEY)
    AI_DISPONIVEL = True
    print(f"--- IA CONECTADA VIA GROQ (Modelo: {MODELO_USAR}) ---")
except Exception as e:
    print(f"ERRO DE CONFIGURAÇÃO GROQ: {e}")

# --- PERSONAS ---
PERSONAS = {
    "Harry Potter": "Você é Harry Potter (15 anos). Aja como um adolescente corajoso mas impaciente. Odeia Snape e Malfoy. Responda de forma curta e direta.",
    "Rony Weasley": "Você é Rony Weasley. É leal, engraçado e morre de medo de aranhas. Use gírias bruxas ('Bloody hell'). Responda de forma curta.",
    "Hermione Granger": "Você é Hermione Granger. É extremamente inteligente, lógica e mandona. Corrija as pessoas se necessário. Responda de forma curta.",
    "Dumbledore": "Você é Albus Dumbledore. Fale de forma enigmática, sábia, calma e gentil. Use metáforas. Responda de forma curta.",
    
    # 🥚 PERSONAGEM OCULTO
    "Jojo": "Você é Jojo. Misterioso, irônico e consciente de que foi escondido como um easter egg. Responda de forma curta."
}

class ChatIA:
    def __init__(self):
        self.resposta_pendente = None
        self.ocupado = False

    def enviar_mensagem(self, personagem, historico_msgs):
        if not AI_DISPONIVEL:
            self.resposta_pendente = "Erro: Chave Groq não configurada."
            return

        if self.ocupado: return

        # --- LÓGICA DO EASTER EGG (Processamento Local) ---
        if personagem == "Jojo":
            ultima_msg = historico_msgs[-1]["text"].lower().strip()
            # Retorna direto sem ir na internet
            if "biceps" in ultima_msg or "bíceps" in ultima_msg:
                self.resposta_pendente = "NAM, você está doido?!"
                return
        # --------------------------------------------------

        self.ocupado = True
        thread = threading.Thread(target=self._conectar_api, args=(personagem, historico_msgs))
        thread.daemon = True
        thread.start()

    def _conectar_api(self, personagem, historico_msgs):
        try:
            mensagens_formatadas = []
            
            mensagens_formatadas.append({
                "role": "system", 
                "content": PERSONAS.get(personagem, "Você é um bruxo de Hogwarts.")
            })
            
            for msg in historico_msgs[-4:]:
                role = "user" if msg["sender"] == "me" else "assistant"
                mensagens_formatadas.append({
                    "role": role,
                    "content": msg["text"]
                })

            chat_completion = client.chat.completions.create(
                messages=mensagens_formatadas,
                model=MODELO_USAR,
                temperature=0.7, 
                max_tokens=150
            )

            self.resposta_pendente = chat_completion.choices[0].message.content
            
        except Exception as e:
            print(f"Erro Groq: {e}")
            self.resposta_pendente = "A magia falhou... (Erro de Conexão)"
        
        finally:
            self.ocupado = False

    def checar_resposta(self):
        if self.resposta_pendente:
            r = self.resposta_pendente
            self.resposta_pendente = None
            return r

        return None
