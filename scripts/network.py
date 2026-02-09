import requests
import threading

# GARANTA QUE ESTA LINHA ESTEJA ASSIM PARA RODAR NO SEU PC:
SERVER_URL = "http://127.0.0.1:8080" 

class NetworkClient:
    def __init__(self):
        self.username = None
        self.elo = 1000
        self.tier = "Bronze"
        self.friends = []
        self.conectado = False
        self.top_rank = []
        self.sugestoes = []

    def registrar(self, user, pwd):
        try:
            # Tenta conectar. Se falhar, vai para o 'except'
            r = requests.post(f"{SERVER_URL}/register", json={"username": user, "password": pwd}, timeout=2)
            
            # Se o servidor respondeu, retorna a resposta dele (Sucesso ou Erro)
            return r.json()
        except requests.exceptions.ConnectionError:
            return {"status": "error", "msg": "Servidor Offline (Verifique o terminal)"}
        except Exception as e:
            return {"status": "error", "msg": f"Erro: {str(e)}"}

    def login(self, user, pwd):
        try:
            r = requests.post(f"{SERVER_URL}/login", json={"username": user, "password": pwd}, timeout=2)
            data = r.json()
            if data.get("status") == "success":
                self.username = user
                self.elo = data["elo"]
                self.tier = data["tier"]
                self.friends = [f for f in data["friends"] if f]
                self.conectado = True
            return data
        except requests.exceptions.ConnectionError:
            return {"status": "error", "msg": "Servidor Offline"}
        except: 
            return {"status": "error", "msg": "Erro desconhecido"}

    def enviar_partida(self, resultado):
        if not self.conectado: return
        def _thread():
            try:
                r = requests.post(f"{SERVER_URL}/update_rank", json={"username": self.username, "resultado": resultado})
                if r.status_code == 200:
                    self.elo = r.json().get("new_elo", self.elo)
            except: pass
        threading.Thread(target=_thread).start()

    def atualizar_dados(self):
        if not self.conectado: return
        def _thread():
            try:
                r = requests.get(f"{SERVER_URL}/leaderboard", timeout=2)
                self.top_rank = r.json()
                r2 = requests.get(f"{SERVER_URL}/get_suggestions?user={self.username}", timeout=2)
                self.sugestoes = r2.json()
            except: pass
        threading.Thread(target=_thread).start()

    def adicionar_amigo(self, nome_amigo):
        if not self.conectado: return "Offline"
        try:
            r = requests.post(f"{SERVER_URL}/add_friend", json={"user": self.username, "target": nome_amigo})
            if r.status_code == 200:
                self.friends.append(nome_amigo)
                return "Adicionado!"
        except: return "Erro"
        return "Erro"

CLIENTE_ONLINE = NetworkClient()