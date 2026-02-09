import cv2
import threading
import pygame
import numpy as np

# Variável global para guardar o status da câmera (gestos)
# "nenhum", "fogo", "cura", "escudo", etc.
CONTROLE_CAMERA = {
    "gesto": "nenhum"
}

_rodando = False
_thread = None

def detectar_movimento(frame_anterior, frame_atual):
    """
    Simples detecção de movimento comparando frames.
    (Aqui você pode expandir para usar MediaPipe se quiser algo avançado)
    """
    diff = cv2.absdiff(frame_anterior, frame_atual)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contornos, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    movimento_total = 0
    for c in contornos:
        if cv2.contourArea(c) > 500: # Ignora movimentos muito pequenos
            movimento_total += cv2.contourArea(c)
            
    # Lógica simples de exemplo:
    # Se houver MUITO movimento -> "ataque"
    # Se houver pouco -> "nenhum"
    if movimento_total > 50000:
        return "ataque"
    elif movimento_total > 20000:
        return "defesa"
    else:
        return "nenhum"

def loop_camera():
    global CONTROLE_CAMERA, _rodando
    
    # Adicionando cv2.CAP_DSHOW para corrigir o erro MSMF no Windows
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    # Se não abriu com DSHOW, tenta normal
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
        
    if not cap.isOpened():
        print("[ERRO] Câmera não encontrada.")
        return

    ret, frame1 = cap.read()
    ret, frame2 = cap.read()

    while _rodando and cap.isOpened():
        if not ret:
            break
            
        gesto = detecting_logic_placeholder(frame1, frame2) # Chama lógica interna
        CONTROLE_CAMERA["gesto"] = gesto
        
        frame1 = frame2
        ret, frame2 = cap.read()
        
        # Pequeno delay para não consumir 100% da CPU
        cv2.waitKey(10)

    cap.release()
    cv2.destroyAllWindows()

def detecting_logic_placeholder(f1, f2):
    # Wrapper para a lógica de detecção
    try:
        return detectar_movimento(f1, f2)
    except Exception:
        return "nenhum"

def start_camera():
    global _rodando, _thread
    if _rodando:
        return
        
    _rodando = True
    _thread = threading.Thread(target=loop_camera, daemon=True)
    _thread.start()
    print("[SISTEMA] Câmera iniciada em thread separada.")

def stop_camera():
    global _rodando
    _rodando = False