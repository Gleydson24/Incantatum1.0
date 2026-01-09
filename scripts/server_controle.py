import logging
import threading
import socket
from flask import Flask, request, render_template_string

# Desativa logs padrão do Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# Estado dos botões (Compartilhado com o jogo)
CONTROLE_REMOTO = {
    "cima": False, "baixo": False, "esquerda": False, "direita": False,
    "incendio": False, "protego": False, "expelliarmus": False, 
    "stupefy": False, "sectumsempra": False, "avada": False,
    "dash": False, "modo_jogo": "normal"
}

# HTML embutido para não precisar de pasta templates extra
HTML_CONTROLE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Varinha Mobile</title>
    <style>
        body { 
            background-color: #1a1a1a; color: white; 
            font-family: Arial, sans-serif; text-align: center;
            overflow: hidden; user-select: none; touch-action: manipulation;
            margin: 0; padding: 0;
        }
        
        /* Layout Grid */
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            height: 100vh;
            gap: 5px;
            padding: 5px;
            box-sizing: border-box;
        }

        button {
            border: 2px solid #444; border-radius: 10px;
            font-weight: bold; font-size: 18px; color: white;
            outline: none; touch-action: manipulation;
            background-color: #333;
        }
        button:active { transform: scale(0.95); opacity: 0.8; background-color: #555; }

        /* Direcionais */
        .d-pad {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            grid-template-rows: 1fr 1fr 1fr;
            gap: 2px;
        }
        .btn-dir { background-color: #222; font-size: 24px; }
        .up { grid-column: 2; grid-row: 1; }
        .left { grid-column: 1; grid-row: 2; }
        .right { grid-column: 3; grid-row: 2; }
        .down { grid-column: 2; grid-row: 3; }
        #dash { grid-column: 2; grid-row: 2; background-color: #008080; font-size: 12px; }

        /* Magias */
        .spells {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 5px;
        }
        .atk { background-color: #8b0000; }
        .def { background-color: #00008b; }
        .big { grid-column: span 2; background-color: #4b0082; }
        .ult { grid-column: span 2; background-color: #006400; color: #0f0; border: 1px solid #0f0; }

        /* MODO DISPUTA */
        #tela-disputa {
            display: none; position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: #ff3333; z-index: 2000;
            flex-direction: column; justify-content: center; align-items: center;
        }
        #btn-esmagar {
            width: 80%; height: 60%;
            background-color: #800000; color: white;
            font-size: 30px; border: 5px solid white;
            border-radius: 20px; box-shadow: 0 0 20px white;
        }
    </style>
</head>
<body>

    <div id="tela-disputa">
        <h1 style="color:yellow">DISPUTA MÁGICA!</h1>
        <button id="btn-esmagar" ontouchstart="spamAttack(event)">
            TOQUE RÁPIDO!<br>(Vários dedos)
        </button>
    </div>

    <div class="container" id="controle-normal">
        <div class="d-pad">
            <button class="btn-dir up" ontouchstart="startMove('cima')" ontouchend="stopMove('cima')">▲</button>
            <button class="btn-dir left" ontouchstart="startMove('esquerda')" ontouchend="stopMove('esquerda')">◄</button>
            <button id="dash" onclick="sendPulse('dash')">DASH</button>
            <button class="btn-dir right" ontouchstart="startMove('direita')" ontouchend="stopMove('direita')">►</button>
            <button class="btn-dir down" ontouchstart="startMove('baixo')" ontouchend="stopMove('baixo')">▼</button>
        </div>

        <div class="spells">
            <button class="atk" onclick="sendPulse('incendio')">FOGO</button>
            <button class="def" onclick="sendPulse('protego')">ESCUDO</button>
            <button class="atk" onclick="sendPulse('expelliarmus')">EXPEL.</button>
            <button class="atk" onclick="sendPulse('stupefy')">ESTUP.</button>
            <button class="big" onclick="sendPulse('sectumsempra')">SECTUMSEMPRA</button>
            <button class="ult" onclick="sendPulse('avada')">AVADA KEDAVRA</button>
        </div>
    </div>

    <script>
        // Atualiza a tela baseado no estado do jogo (Disputa ou Normal)
        setInterval(() => {
            fetch('/status')
                .then(r => r.json())
                .then(data => {
                    const disputeDiv = document.getElementById('tela-disputa');
                    const normalDiv = document.getElementById('controle-normal');
                    if (data.modo === 106) { // 106 é o código de DISPUTA
                        disputeDiv.style.display = 'flex';
                        normalDiv.style.display = 'none';
                    } else {
                        disputeDiv.style.display = 'none';
                        normalDiv.style.display = 'grid';
                    }
                });
        }, 1000);

        function sendPulse(acao) {
            fetch('/update', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: acao, status: true})
            });
            setTimeout(() => {
                fetch('/update', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({key: acao, status: false})
                });
            }, 100);
        }

        // Multitouch para disputa
        function spamAttack(e) {
            e.preventDefault();
            for (let i = 0; i < e.changedTouches.length; i++) {
                sendPulse('incendio'); // Envia sinal de ataque
            }
        }

        let intervalIds = {};
        function startMove(direction) {
            if (intervalIds[direction]) return;
            fetch('/update', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: direction, status: true})
            });
            intervalIds[direction] = setInterval(() => {
                fetch('/update', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({key: direction, status: true})
                });
            }, 200);
        }

        function stopMove(direction) {
            clearInterval(intervalIds[direction]);
            delete intervalIds[direction];
            fetch('/update', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: direction, status: false})
            });
        }
    </script>
</body>
</html>
"""

estado_jogo_atual = 0

@app.route('/')
def index():
    return render_template_string(HTML_CONTROLE)

@app.route('/update', methods=['POST'])
def update():
    data = request.json
    key = data.get('key')
    status = data.get('status')
    if key in CONTROLE_REMOTO:
        CONTROLE_REMOTO[key] = status
    return "OK", 200

@app.route('/status')
def status():
    return {"modo": estado_jogo_atual}

def atualizar_estado_jogo(estado):
    global estado_jogo_atual
    estado_jogo_atual = estado

def run_server():
    # Tenta pegar IP local
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = '127.0.0.1'
    
    print(f"\n[SERVER] Controle Mobile em: http://{local_ip}:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def start_remote():
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()