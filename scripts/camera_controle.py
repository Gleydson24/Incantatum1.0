import threading
import numpy as np
import time
import os

# Tenta importar CV2. Se não tiver, o jogo não quebra, apenas avisa.
try:
    import cv2
    OPENCV_DISPONIVEL = True
except ImportError:
    OPENCV_DISPONIVEL = False

# Importação segura das settings
try:
    from scripts.settings import LARGURA, ALTURA
except ModuleNotFoundError:
    LARGURA = 1280
    ALTURA = 720

# Arquivo para salvar a cor calibrada
ARQUIVO_CALIBRACAO = "dados_calibracao.npy"

# --- CONFIGURAÇÕES DE SENSIBILIDADE ---
SUAVIZACAO = 0.2         
LIMITE_AREA_CLIQUE = 1.3 
MIN_AREA = 100           

# Dicionário compartilhado com o Main
CONTROLE_CAMERA = {
    "ativo": False,
    "frame_buffer": None,
    "largura": 0,
    "altura": 0,
    "gesto_nome": "Aguardando...",
    "cursor_x": 0,
    "cursor_y": 0,
    "clique": False
}

class CameraThread:
    def __init__(self):
        self.cap = None
        self.rodando = False
        self.clicando = False
        self.pos_x, self.pos_y = 0, 0
        self.area_base = 1000 
        
        # Cor padrão (se não calibrar, é preto e não detecta nada)
        self.lower_color = np.array([0, 0, 0], dtype=np.uint8)
        self.upper_color = np.array([0, 0, 0], dtype=np.uint8)
        self.calibrado = False
        
        self.carregar_calibracao()

    def carregar_calibracao(self):
        if os.path.exists(ARQUIVO_CALIBRACAO):
            try:
                dados = np.load(ARQUIVO_CALIBRACAO, allow_pickle=True)
                self.lower_color = np.array(dados[0], dtype=np.uint8)
                self.upper_color = np.array(dados[1], dtype=np.uint8)
                self.area_base = float(dados[2])
                self.calibrado = True
                print("Calibração carregada do arquivo.")
            except Exception as e:
                print(f"Erro ao carregar calibração: {e}")

    def abrir_camera_segura(self):
        """Tenta abrir indice 0, se falhar tenta 1, backend DSHOW no Windows é mais rápido"""
        print("--- ABRINDO CÂMERA ---")
        if not OPENCV_DISPONIVEL:
            print("OpenCV não instalado.")
            return None

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("Tentando câmera secundária...")
            cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            if not cap.isOpened():
                # Tenta sem DSHOW como fallback
                cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            return cap
        else:
            print("ERRO: Nenhuma câmera encontrada.")
            return None

    def calibrar_agora(self):
        if not OPENCV_DISPONIVEL: return

        print("\n=== CALIBRAÇÃO ===")
        print("Clique na cor do objeto (varinha) e aperte Q para salvar.")
        
        cap = self.abrir_camera_segura()
        if not cap: return

        def pegar_cor(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                frame = param
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                pixel = hsv[y, x]
                
                # Margem de tolerância para a cor
                h_margin = 15
                s_margin = 60
                v_margin = 60
                
                l_h = max(0, int(pixel[0]) - h_margin)
                l_s = max(40, int(pixel[1]) - s_margin)
                l_v = max(40, int(pixel[2]) - v_margin)
                
                u_h = min(180, int(pixel[0]) + h_margin)
                u_s = 255
                u_v = 255
                
                self.lower_color = np.array([l_h, l_s, l_v], dtype=np.uint8)
                self.upper_color = np.array([u_h, u_s, u_v], dtype=np.uint8)
                print(f"Cor definida! HSV: {pixel}")

        cv2.namedWindow("CALIBRACAO")
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            
            cv2.setMouseCallback("CALIBRACAO", pegar_cor, frame)
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
            resultado = cv2.bitwise_and(frame, frame, mask=mask)
            
            # Texto explicativo
            cv2.putText(frame, "CLIQUE NA COR -> APERTE Q", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            imagem_final = np.hstack([frame, resultado])
            cv2.imshow("CALIBRACAO", imagem_final)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # Calcula a área base do objeto
                contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contornos:
                    maior = max(contornos, key=cv2.contourArea)
                    self.area_base = cv2.contourArea(maior)
                    if self.area_base < MIN_AREA: self.area_base = 500
                
                # Salva
                try:
                    dados_salvar = [
                        self.lower_color.tolist(), 
                        self.upper_color.tolist(), 
                        self.area_base
                    ]
                    np.save(ARQUIVO_CALIBRACAO, np.array(dados_salvar, dtype=object))
                except Exception as e:
                    print(f"Erro ao salvar calibração: {e}")
                
                self.calibrado = True
                break
        
        cap.release()
        cv2.destroyAllWindows()

    def iniciar(self):
        # Se não estiver calibrado, força calibração. Se estiver, usa o arquivo.
        if not self.calibrado:
            self.calibrar_agora()
            
        if self.calibrado and OPENCV_DISPONIVEL:
            self.rodando = True
            threading.Thread(target=self.loop, daemon=True).start()
        else:
            print("AVISO: Câmera não iniciada (falta calibração ou biblioteca).")

    def loop(self):
        self.cap = self.abrir_camera_segura()
        if not self.cap: return

        kernel = np.ones((5,5), np.uint8)

        while self.rodando:
            ret, frame = self.cap.read()
            if not ret: 
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Processamento de Imagem
            mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
            mask = cv2.erode(mask, kernel, iterations=1)
            mask = cv2.dilate(mask, kernel, iterations=2)
            
            contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            gesto = "..."
            
            if contornos:
                maior_c = max(contornos, key=cv2.contourArea)
                area = cv2.contourArea(maior_c)
                
                if area > MIN_AREA:
                    M = cv2.moments(maior_c)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])

                        # Mapeia coordenadas da câmera (640x480) para a tela do jogo
                        target_x = np.interp(cx, (0, 640), (0, LARGURA))
                        target_y = np.interp(cy, (0, 480), (0, ALTURA))
                        
                        # Suavização do movimento
                        self.pos_x += (target_x - self.pos_x) * SUAVIZACAO
                        self.pos_y += (target_y - self.pos_y) * SUAVIZACAO
                        
                        # Desenha na visão da câmera (debug)
                        cv2.circle(frame, (cx, cy), 10, (0, 255, 255), 2)

                        # Detecção de "Clique" (aproximar a varinha da câmera aumenta a área)
                        if area > self.area_base * LIMITE_AREA_CLIQUE:
                            gesto = "DISPARO!"
                            cv2.circle(frame, (cx, cy), 20, (0, 255, 0), -1) 
                            CONTROLE_CAMERA["clique"] = True
                            self.clicando = True
                        else:
                            gesto = "Mira"
                            CONTROLE_CAMERA["clique"] = False
                            
                            # Atualiza a área base dinamicamente para se adaptar à luz
                            if abs(area - self.area_base) < 1000:
                                self.area_base = self.area_base * 0.98 + area * 0.02

                        CONTROLE_CAMERA["cursor_x"] = int(self.pos_x)
                        CONTROLE_CAMERA["cursor_y"] = int(self.pos_y)

            # Prepara frame para enviar ao Pygame (Miniatura)
            frame_mini = cv2.resize(frame, (160, 120))
            # Converte BGR para RGB para o Pygame
            frame_mini = cv2.cvtColor(frame_mini, cv2.COLOR_BGR2RGB)
            
            CONTROLE_CAMERA["frame_buffer"] = frame_mini.tobytes()
            CONTROLE_CAMERA["ativo"] = True
            CONTROLE_CAMERA["largura"] = 160
            CONTROLE_CAMERA["altura"] = 120
            CONTROLE_CAMERA["gesto_nome"] = gesto
            
            time.sleep(0.01)

def start_camera():
    c = CameraThread()
    c.iniciar()