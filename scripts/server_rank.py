from flask import Flask, request, jsonify
import sqlite3
import random

app = Flask(__name__)
DB_NAME = "incantatum_online.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tabela de Usuários com colunas extras para amigos
    # friends e requests armazenam strings separadas por vírgula (ex: "player1,player2")
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, elo INTEGER, vitorias INTEGER, 
                  friends TEXT, requests TEXT)''')
    conn.commit()
    conn.close()

def calcular_elo_badge(elo):
    if elo < 1200: return "Bronze"
    if elo < 1500: return "Prata"
    if elo < 1800: return "Ouro"
    if elo < 2100: return "Platina"
    if elo < 2400: return "Diamante"
    if elo < 2700: return "Mestre"
    return "Desafiante"

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user, pwd = data.get('username'), data.get('password')
    conn = sqlite3.connect(DB_NAME)
    try:
        conn.execute("INSERT INTO users VALUES (?, ?, 1000, 0, '', '')", (user, pwd))
        conn.commit()
        return jsonify({"status": "success", "msg": "Conta criada!"})
    except:
        return jsonify({"status": "error", "msg": "Usuário já existe!"}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.execute("SELECT elo, vitorias, friends, requests FROM users WHERE username=? AND password=?", 
                          (data.get('username'), data.get('password')))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({
            "status": "success", 
            "elo": row[0], 
            "tier": calcular_elo_badge(row[0]),
            "vitorias": row[1],
            "friends": row[2].split(',') if row[2] else [],
            "requests": row[3].split(',') if row[3] else []
        })
    return jsonify({"status": "error", "msg": "Dados incorretos"}), 401

@app.route('/update_rank', methods=['POST'])
def update_rank():
    data = request.json
    user = data.get('username')
    resultado = data.get('resultado')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.execute("SELECT elo, vitorias FROM users WHERE username=?", (user,))
    row = cursor.fetchone()
    if row:
        elo, vit = row
        novo_elo = elo + 25 if resultado == 'win' else max(0, elo - 15)
        novas_vit = vit + 1 if resultado == 'win' else vit
        conn.execute("UPDATE users SET elo=?, vitorias=? WHERE username=?", (novo_elo, novas_vit, user))
        conn.commit(); conn.close()
        return jsonify({"status": "success", "new_elo": novo_elo})
    return jsonify({"error": "User not found"}), 404

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.execute("SELECT username, elo, vitorias FROM users ORDER BY elo DESC LIMIT 20")
    data = [{"nome": r[0], "elo": r[1], "tier": calcular_elo_badge(r[1]), "vitorias": r[2]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/get_suggestions', methods=['GET'])
def get_suggestions():
    # Retorna usuários aleatórios para sugerir amizade
    exclude = request.args.get('user', '')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.execute("SELECT username, elo FROM users WHERE username != ? ORDER BY RANDOM() LIMIT 5", (exclude,))
    data = [{"nome": r[0], "elo": r[1], "tier": calcular_elo_badge(r[1])} for r in cursor.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/add_friend', methods=['POST'])
def add_friend():
    data = request.json
    me, target = data.get('user'), data.get('target')
    conn = sqlite3.connect(DB_NAME)
    
    # Adiciona na lista de amigos de ambos (simplificado: aceita direto para protótipo)
    # Num jogo real teria pedido -> aceitar. Aqui vamos direto para facilitar.
    try:
        # Pega amigos atuais
        cur = conn.execute("SELECT friends FROM users WHERE username=?", (me,))
        my_friends = cur.fetchone()[0]
        cur = conn.execute("SELECT friends FROM users WHERE username=?", (target,))
        target_friends = cur.fetchone()[0]
        
        if target not in my_friends.split(','):
            new_me = (my_friends + "," + target).strip(',')
            new_target = (target_friends + "," + me).strip(',')
            
            conn.execute("UPDATE users SET friends=? WHERE username=?", (new_me, me))
            conn.execute("UPDATE users SET friends=? WHERE username=?", (new_target, target))
            conn.commit()
            msg = "Amigo adicionado!"
        else:
            msg = "Já são amigos."
    except:
        msg = "Erro ao adicionar."
        
    conn.close()
    return jsonify({"msg": msg})

if __name__ == '__main__':
    init_db()
    # Pega a porta do ambiente (para nuvem) ou usa 8080 local
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)