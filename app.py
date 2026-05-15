import os
import pyodbc
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

DB_CONFIG = {
    "server": os.getenv("DB_SERVER", "serverdindin.database.windows.net"),
    "database": os.getenv("DB_NAME", "dbdindin"),
    "username": os.getenv("DB_USER", "vini123"),
    "password": os.getenv("DB_PASSWORD", "viniadm123!"),
    "driver": "{ODBC Driver 18 for SQL Server}",
}

def get_connection():
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='clientes' AND xtype='U')
            CREATE TABLE clientes (
                id INT IDENTITY(1,1) PRIMARY KEY,
                nome NVARCHAR(100) NOT NULL,
                email NVARCHAR(100) NOT NULL,
                telefone NVARCHAR(20),
                criado_em DATETIME DEFAULT GETDATE()
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>DinDin — Clientes</title>
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #0a0a0f;
      --surface: #12121a;
      --border: #1e1e2e;
      --accent: #7fff6e;
      --accent2: #4fffde;
      --text: #e8e8f0;
      --muted: #5a5a7a;
      --danger: #ff5e5e;
    }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Syne', sans-serif;
      min-height: 100vh;
      padding: 2rem;
      background-image:
        radial-gradient(ellipse 60% 40% at 80% 10%, rgba(127,255,110,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 50% 50% at 10% 90%, rgba(79,255,222,0.05) 0%, transparent 60%);
    }

    header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 3rem;
      animation: fadeDown 0.6s ease both;
    }

    .logo {
      width: 44px; height: 44px;
      background: var(--accent);
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.3rem; font-weight: 800; color: #0a0a0f;
    }

    h1 { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.03em; }
    h1 span { color: var(--accent); }

    .layout {
      display: grid;
      grid-template-columns: 380px 1fr;
      gap: 2rem;
      max-width: 1100px;
    }

    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 2rem;
      animation: fadeUp 0.6s ease both;
    }

    .card h2 {
      font-size: 1rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--muted);
      margin-bottom: 1.5rem;
    }

    .field { margin-bottom: 1.2rem; }

    label {
      display: block;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin-bottom: 0.4rem;
    }

    input {
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text);
      font-family: 'DM Mono', monospace;
      font-size: 0.9rem;
      padding: 0.7rem 1rem;
      transition: border-color 0.2s, box-shadow 0.2s;
      outline: none;
    }

    input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(127,255,110,0.1);
    }

    button[type="submit"] {
      width: 100%;
      margin-top: 0.5rem;
      background: var(--accent);
      color: #0a0a0f;
      border: none;
      border-radius: 8px;
      font-family: 'Syne', sans-serif;
      font-weight: 800;
      font-size: 0.95rem;
      padding: 0.85rem;
      cursor: pointer;
      letter-spacing: 0.03em;
      transition: transform 0.15s, opacity 0.15s;
    }

    button[type="submit"]:hover { opacity: 0.85; transform: translateY(-1px); }
    button[type="submit"]:active { transform: translateY(0); }

    .toast {
      display: none;
      margin-top: 1rem;
      padding: 0.75rem 1rem;
      border-radius: 8px;
      font-size: 0.85rem;
      font-family: 'DM Mono', monospace;
      animation: fadeUp 0.3s ease both;
    }
    .toast.success { background: rgba(127,255,110,0.1); border: 1px solid var(--accent); color: var(--accent); }
    .toast.error   { background: rgba(255,94,94,0.1);   border: 1px solid var(--danger);  color: var(--danger); }

    .table-wrap { overflow-x: auto; }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
    }

    thead tr { border-bottom: 1px solid var(--border); }

    th {
      text-align: left;
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--muted);
      padding: 0 1rem 0.75rem;
    }

    td {
      padding: 0.85rem 1rem;
      border-bottom: 1px solid var(--border);
      font-family: 'DM Mono', monospace;
      color: var(--text);
    }

    tr:last-child td { border-bottom: none; }
    tr:hover td { background: rgba(255,255,255,0.02); }

    .badge {
      display: inline-block;
      background: rgba(79,255,222,0.1);
      color: var(--accent2);
      border: 1px solid rgba(79,255,222,0.2);
      border-radius: 999px;
      font-size: 0.7rem;
      padding: 0.15rem 0.6rem;
      font-family: 'DM Mono', monospace;
    }

    .empty {
      text-align: center;
      padding: 3rem;
      color: var(--muted);
      font-size: 0.9rem;
    }

    .btn-del {
      background: none;
      border: 1px solid var(--border);
      color: var(--muted);
      border-radius: 6px;
      padding: 0.3rem 0.6rem;
      font-size: 0.75rem;
      cursor: pointer;
      transition: border-color 0.2s, color 0.2s;
    }
    .btn-del:hover { border-color: var(--danger); color: var(--danger); }

    @keyframes fadeUp   { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:none; } }
    @keyframes fadeDown { from { opacity:0; transform:translateY(-12px); } to { opacity:1; transform:none; } }
  </style>
</head>
<body>
  <header>
    <div class="logo">D$</div>
    <h1>Din<span>Din</span> — Clientes</h1>
  </header>

  <div class="layout">
    <div class="card" style="animation-delay:0.1s">
      <h2>Novo Cliente</h2>
      <form id="form">
        <div class="field">
          <label>Nome</label>
          <input type="text" id="nome" placeholder="João Silva" required />
        </div>
        <div class="field">
          <label>Email</label>
          <input type="email" id="email" placeholder="joao@email.com" required />
        </div>
        <div class="field">
          <label>Telefone</label>
          <input type="text" id="telefone" placeholder="(11) 99999-9999" />
        </div>
        <button type="submit">Cadastrar Cliente</button>
        <div class="toast" id="toast"></div>
      </form>
    </div>

    <div class="card" style="animation-delay:0.2s">
      <h2>Clientes Cadastrados</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Nome</th>
              <th>Email</th>
              <th>Telefone</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody id="tbody">
            <tr><td colspan="6" class="empty">Carregando...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <script>
    const toast = document.getElementById('toast');

    function showToast(msg, type) {
      toast.textContent = msg;
      toast.className = 'toast ' + type;
      toast.style.display = 'block';
      setTimeout(() => toast.style.display = 'none', 4000);
    }

    async function loadClientes() {
      const res = await fetch('/clientes');
      const data = await res.json();
      const tbody = document.getElementById('tbody');
      if (!data.clientes || data.clientes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty">Nenhum cliente cadastrado ainda.</td></tr>';
        return;
      }
      tbody.innerHTML = data.clientes.map(c => `
        <tr>
          <td>${c.id}</td>
          <td>${c.nome}</td>
          <td>${c.email}</td>
          <td>${c.telefone || '—'}</td>
          <td><span class="badge">ativo</span></td>
          <td><button class="btn-del" onclick="deletar(${c.id})">remover</button></td>
        </tr>
      `).join('');
    }

    document.getElementById('form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const body = {
        nome: document.getElementById('nome').value,
        email: document.getElementById('email').value,
        telefone: document.getElementById('telefone').value,
      };
      const res = await fetch('/clientes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      if (res.ok) {
        showToast('✓ Cliente cadastrado com sucesso!', 'success');
        e.target.reset();
        loadClientes();
      } else {
        showToast('✗ Erro: ' + data.error, 'error');
      }
    });

    async function deletar(id) {
      if (!confirm('Remover este cliente?')) return;
      const res = await fetch('/clientes/' + id, { method: 'DELETE' });
      if (res.ok) { showToast('Cliente removido.', 'success'); loadClientes(); }
    }

    loadClientes();
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    init_db()
    return render_template_string(HTML)

@app.route("/clientes", methods=["GET"])
def listar_clientes():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, telefone FROM clientes ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        clientes = [{"id": r[0], "nome": r[1], "email": r[2], "telefone": r[3]} for r in rows]
        return jsonify({"clientes": clientes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clientes", methods=["POST"])
def criar_cliente():
    try:
        data = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)",
            data["nome"], data["email"], data.get("telefone", "")
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Cliente criado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clientes/<int:id>", methods=["DELETE"])
def deletar_cliente(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id = ?", id)
        conn.commit()
        conn.close()
        return jsonify({"message": "Cliente removido"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)