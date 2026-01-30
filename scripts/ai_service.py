from groq import Groq
import threading

# --- CONFIGURAÇÃO ---
# COLE SUA CHAVE 'gsk_...' AQUI DENTRO
API_KEY = "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" 

# Modelo ATUALIZADO (Llama 3.3 Versatile)
# É o modelo mais inteligente e rápido disponível na Groq hoje.
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
    "Dumbledore": "Você é Albus Dumbledore. Fale de forma enigmática, sábia, calma e gentil. Use metáforas. Responda de forma curta."
}

class ChatIA:
    def __init__(self):
        self.resposta_pendente = None
        self.ocupado = False

    def enviar_mensagem(self, personagem, historico_msgs):
        """
        Inicia a thread para processar a mensagem sem travar o jogo.
        """
        if not AI_DISPONIVEL:
            self.resposta_pendente = "Erro: Chave Groq não configurada."
            return

        if self.ocupado: return
        self.ocupado = True
        
        thread = threading.Thread(target=self._conectar_api, args=(personagem, historico_msgs))
        thread.daemon = True
        thread.start()

    def _conectar_api(self, personagem, historico_msgs):
        try:
            # 1. Prepara a lista de mensagens
            mensagens_formatadas = []
            
            # System Prompt (A personalidade)
            mensagens_formatadas.append({
                "role": "system", 
                "content": PERSONAS.get(personagem, "Você é um bruxo de Hogwarts.")
            })
            
            # Histórico (Pega as últimas 4 mensagens para contexto)
            for msg in historico_msgs[-4:]:
                role = "user" if msg["sender"] == "me" else "assistant"
                mensagens_formatadas.append({
                    "role": role,
                    "content": msg["text"]
                })

            # 2. Chama a API da Groq
            chat_completion = client.chat.completions.create(
                messages=mensagens_formatadas,
                model=MODELO_USAR,
                temperature=0.7, 
                max_tokens=150
            )

            # 3. Pega a resposta
            resposta_limpa = chat_completion.choices[0].message.content
            self.resposta_pendente = resposta_limpa
            
        except Exception as e:
            print(f"Erro Groq: {e}")
            erro_str = str(e)
            
            if "404" in erro_str:
                # Fallback caso o modelo mude de novo no futuro
                try:
                    chat_completion = client.chat.completions.create(
                        messages=mensagens_formatadas,
                        model="llama-3.1-8b-instant", # Modelo de backup ultrarrápido
                        max_tokens=150
                    )
                    self.resposta_pendente = chat_completion.choices[0].message.content
                except:
                    self.resposta_pendente = "O modelo de magia mudou... (Erro 404)"
            elif "401" in erro_str:
                self.resposta_pendente = "Erro de Autenticação (Chave Inválida)."
            else:
                self.resposta_pendente = "A magia falhou... (Erro de Conexão)"
        
        finally:
            self.ocupado = False

    def checar_resposta(self):
        if self.resposta_pendente:
            r = self.resposta_pendente
            self.resposta_pendente = None
            return r
        return None