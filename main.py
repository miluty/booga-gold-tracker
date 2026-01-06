from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Almacena cuentas: username -> {gold, lastSeen}
accounts = {}

@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.json
        username = data.get('username')
        gold = data.get('gold')
        if username is not None and gold is not None:
            accounts[username] = {'gold': gold, 'lastSeen': time.time()}
            print(f"✅ {username} -> {gold} Gold")
            return jsonify({"status": "ok"}), 200
        return jsonify({"error": "bad data"}), 400
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "server error"}), 500

@app.route('/active', methods=['GET'])
def active():
    now = time.time()
    # Cuentas activas en los últimos 2 minutos
    active = {user: info['gold'] for user, info in accounts.items() if now - info['lastSeen'] < 120}
    return jsonify(active)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BOOGA GOLD LEADERBOARD</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap" rel="stylesheet">
        <style>
            body { margin:0; padding:0; background:linear-gradient(135deg,#0f0c29,#302b63,#24243e); color:#fff; font-family:'Orbitron',Arial,sans-serif; min-height:100vh; }
            .header { text-align:center; padding:50px 20px; background:rgba(0,0,0,0.5); border-bottom:3px solid #00ffff; }
            h1 { font-size:4em; margin:0; text-shadow:0 0 30px #00ffff; letter-spacing:5px; }
            .subtitle { font-size:1.5em; color:#00ffff; margin-top:15px; }
            .container { display:flex; flex-wrap:wrap; justify-content:center; gap:30px; padding:50px 20px; }
            .card { background:rgba(15,15,40,0.9); border:2px solid #00ffff; border-radius:20px; width:320px; padding:30px; text-align:center; box-shadow:0 0 30px rgba(0,255,255,0.4); transition:0.5s; opacity:0; transform:translateY(50px); animation:fadeUp 0.8s forwards; }
            .card:hover { transform:translateY(-20px) scale(1.08); box-shadow:0 0 50px rgba(0,255,255,0.8); border-color:#00ffea; }
            @keyframes fadeUp { to { opacity:1; transform:translateY(0); } }
            .rank { font-size:2.5em; color:#ffd700; text-shadow:0 0 15px #ffd700; }
            .username { font-size:1.8em; margin:20px 0; color:#00ffff; }
            .gold { font-size:3em; font-weight:bold; color:#ffd700; text-shadow:0 0 20px #ffd700; }
            .status { margin-top:20px; color:#00ff88; font-size:1.2em; }
            .spinner { text-align:center; margin:40px; font-size:1.4em; color:#00ffff; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>BOOGA GOLD LEADERBOARD</h1>
            <p class="subtitle">Cuentas activas en tiempo real</p>
        </div>
        <div class="container" id="cards"></div>
        <div class="spinner">🔄 Actualizando cada 5 segundos...</div>

        <script>
            async function load() {
                try {
                    const res = await fetch('/active');
                    const data = await res.json();
                    const container = document.getElementById('cards');
                    container.innerHTML = '';
                    const sorted = Object.entries(data)
                        .sort((a, b) => b[1] - a[1])
                        .map((e, i) => ({user: e[0], gold: e[1], rank: i + 1}));

                    sorted.forEach((acc, i) => {
                        const card = document.createElement('div');
                        card.className = 'card';
                        card.style.animationDelay = `${i * 0.15}s`;
                        card.innerHTML = `
                            <div class="rank">#${acc.rank}</div>
                            <div class="username">${acc.user}</div>
                            <div class="gold">${acc.gold.toLocaleString()}</div>
                            <div class="status">🟢 Online</div>
                        `;
                        container.appendChild(card);
                    });
                } catch(e) { console.error(e); }
            }
            load();
            setInterval(load, 5000);
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
