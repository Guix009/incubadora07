from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# =====================
# BANCO DE DADOS
# =====================

DATABASE_URL = os.environ.get("DATABASE_URL")

def conectar_db():
    return psycopg2.connect(DATABASE_URL)

def criar_tabela():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ideias (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            matricula TEXT NOT NULL,
            area TEXT NOT NULL,
            supervisor TEXT NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT DEFAULT 'Submetida',
            pontuacao INTEGER DEFAULT 0,
            avaliador TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

criar_tabela()

# =====================
# ROTAS
# =====================

@app.route("/api/ideias", methods=["POST"])
def enviar_ideia():
    dados = request.json

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ideias (nome, matricula, area, supervisor, descricao)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        dados["nome"],
        dados["matricula"],
        dados["area"],
        dados["supervisor"],
        dados["descricao"]
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensagem": "Ideia enviada com sucesso"}), 201

# =====================
# LISTAR IDEIAS (OPERADORES / RANKING)
# =====================

@app.route("/api/ideias", methods=["GET"])
def listar_ideias():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, area, descricao, status, pontuacao
        FROM ideias
        ORDER BY data_criacao DESC
    """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    ideias = []
    for r in rows:
        ideias.append({
            "id": r[0],
            "nome": r[1],
            "area": r[2],
            "descricao": r[3],
            "status": r[4],
            "pontuacao": r[5]
        })

    return jsonify(ideias)

# =====================
# LISTAR IDEIAS (PERFORMANCE)
# =====================

@app.route("/api/performance/ideias", methods=["GET"])
def ideias_performance():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, matricula, area, supervisor,
               descricao, status, pontuacao, avaliador
        FROM ideias
        ORDER BY data_criacao DESC
    """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    ideias = []
    for r in rows:
        ideias.append({
            "id": r[0],
            "nome": r[1],
            "matricula": r[2],
            "area": r[3],
            "supervisor": r[4],
            "descricao": r[5],
            "status": r[6],
            "pontuacao": r[7],
            "avaliador": r[8]
        })

    return jsonify(ideias)

# =====================
# AVALIAR IDEIA
# =====================

@app.route("/api/performance/avaliar", methods=["POST"])
def avaliar_ideia():
    dados = request.json

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ideias
        SET status = %s,
            pontuacao = %s,
            avaliador = %s
        WHERE id = %s
    """, (
        dados["status"],
        dados["pontuacao"],
        dados["avaliador"],
        dados["id"]
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensagem": "Ideia avaliada com sucesso"}), 200

# =====================
# EXCLUIR IDEIA
# =====================

@app.route("/api/performance/excluir/<int:ideia_id>", methods=["DELETE"])
def excluir_ideia(ideia_id):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM ideias WHERE id = %s",
        (ideia_id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensagem": "Ideia excluída"}), 200

# =====================
# START (RENDER)
# =====================

if __name__ == "__main__":
    app.run()
