from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from dotenv import load_dotenv
from openai import OpenAI
import sqlite3
import os
import json

# ======================
# Configurações iniciais
# ======================
load_dotenv()
app = Flask(__name__)
app.secret_key = "sua_chave_secreta"
DATABASE = "banco.db"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ======================
# Banco de dados
# ======================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ======================
# Usuário logado
# ======================
def get_usuario_logado():
    if "usuario_id" in session:
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE id = ?", (session["usuario_id"],)).fetchone()
        conn.close()
        return user
    return None

# ======================
# Rotas básicas
# ======================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
            conn.commit()
            msg = None
        except sqlite3.IntegrityError:
            msg = "Email já cadastrado!"
        finally:
            conn.close()

        if msg:
            return render_template("cadastro.html", erro=msg)
        else:
            return redirect(url_for("login"))
    return render_template("cadastro.html", erro=None)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha)).fetchone()
        conn.close()

        if user:
            session["usuario_id"] = user["id"]
            return redirect(url_for("trilhas"))
        else:
            return render_template("login.html", erro="Usuário ou senha incorretos")
    return render_template("login.html", erro=None)

@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    return redirect(url_for("index"))

# ======================
# Perfil
# ======================
@app.route("/perfil")
def perfil():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    usuario = conn.execute("SELECT * FROM usuarios WHERE id=?", (session["usuario_id"],)).fetchone()
    concluidos = conn.execute(
        "SELECT COUNT(*) FROM progresso WHERE usuario_id=? AND concluido=1", (session["usuario_id"],)
    ).fetchone()[0]
    conn.close()
    return render_template("perfil.html", usuario=usuario, concluidos=concluidos)

# ======================
# Trilhas
# ======================
@app.route("/trilhas")
def trilhas():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    trilhas = conn.execute("SELECT * FROM trilhas").fetchall()
    conn.close()
    usuario = get_usuario_logado()
    return render_template("trilhas.html", trilhas=trilhas, usuario=usuario)

# ======================
# Conteúdos
# ======================
@app.route("/trilha/<int:trilha_id>/conteudos")
def conteudos(trilha_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    trilha = conn.execute("SELECT * FROM trilhas WHERE id=?", (trilha_id,)).fetchone()
    conteudos = conn.execute("SELECT * FROM conteudos WHERE trilha_id=?", (trilha_id,)).fetchall()
    conn.close()
    if not trilha:
        return "Trilha não encontrada!"
    usuario = get_usuario_logado()
    return render_template("conteudos.html", trilha=trilha, conteudos=conteudos, usuario=usuario)

# ======================
# Ver conteúdo detalhado
# ======================
@app.route("/conteudo/<int:conteudo_id>")
def ver_conteudo(conteudo_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    conteudo = conn.execute("SELECT * FROM conteudos WHERE id=?", (conteudo_id,)).fetchone()
    if not conteudo:
        conn.close()
        return "Conteúdo não encontrado!"

    progresso = conn.execute(
        "SELECT concluido FROM progresso WHERE usuario_id=? AND conteudo_id=?",
        (session["usuario_id"], conteudo_id)
    ).fetchone()
    usuario_concluido = progresso["concluido"] == 1 if progresso else False
    usuario = get_usuario_logado()
    conn.close()
    return render_template("conteudo.html", conteudo=conteudo, usuario=usuario, usuario_concluido=usuario_concluido)

# ======================
# Marcar como concluído (corrigido)
# ======================
@app.route("/toggle_concluido/<int:conteudo_id>", methods=["POST"])
def toggle_concluido(conteudo_id):
    if "usuario_id" not in session:
        return jsonify({"error": "Usuário não logado"}), 403

    usuario_id = session["usuario_id"]
    conn = get_db_connection()

    progresso = conn.execute(
        "SELECT concluido FROM progresso WHERE usuario_id=? AND conteudo_id=?",
        (usuario_id, conteudo_id)
    ).fetchone()

    if progresso:
        novo_status = 0 if progresso["concluido"] == 1 else 1
        conn.execute(
            "UPDATE progresso SET concluido=? WHERE usuario_id=? AND conteudo_id=?",
            (novo_status, usuario_id, conteudo_id)
        )
    else:
        novo_status = 1
        conn.execute(
            "INSERT INTO progresso (usuario_id, conteudo_id, concluido, quiz_feito) VALUES (?, ?, 1, 0)",
            (usuario_id, conteudo_id)
        )

    conn.commit()
    total_concluidos = conn.execute(
        "SELECT COUNT(*) FROM progresso WHERE usuario_id=? AND concluido=1", (usuario_id,)
    ).fetchone()[0]
    conn.close()
    return jsonify({"concluido": novo_status, "total_concluidos": total_concluidos})

# ======================
# IA: gerar quiz automaticamente
# ======================
def gerar_quiz_ia(conteudo_id):
    conn = get_db_connection()
    conteudo = conn.execute("SELECT * FROM conteudos WHERE id=?", (conteudo_id,)).fetchone()
    conn.close()
    if not conteudo:
        return None

    prompt = f"""
    Gere um quiz de 3 perguntas curtas sobre o seguinte conteúdo:
    {conteudo['texto']}
    Formato JSON:
    [
      {{
        "pergunta": "...",
        "alternativas": ["A", "B", "C", "D"],
        "resposta_correta": "A"
      }}
    ]
    """

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    try:
        quiz_json = json.loads(resposta.choices[0].message.content)
    except:
        quiz_json = []

    conn = get_db_connection()
    for q in quiz_json:
        conn.execute(
            "INSERT INTO quizzes (conteudo_id, pergunta, alternativas, resposta_correta) VALUES (?, ?, ?, ?)",
            (conteudo_id, q["pergunta"], json.dumps(q["alternativas"]), q["resposta_correta"])
        )
    conn.commit()
    conn.close()
    return quiz_json

@app.route("/gerar_quiz/<int:conteudo_id>")
def gerar_quiz(conteudo_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    quiz = gerar_quiz_ia(conteudo_id)
    if quiz:
        flash("Quiz gerado com sucesso pela IA!", "success")
    else:
        flash("Erro ao gerar quiz. Tente novamente.", "danger")
    return redirect(url_for("quiz", conteudo_id=conteudo_id))

# ======================
# Quiz
# ======================
@app.route("/quiz/<int:conteudo_id>", methods=["GET", "POST"])
def quiz(conteudo_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    quiz = conn.execute("SELECT * FROM quizzes WHERE conteudo_id=?", (conteudo_id,)).fetchall()
    trilha = conn.execute("""
        SELECT t.* FROM trilhas t
        JOIN conteudos c ON c.trilha_id = t.id
        WHERE c.id = ?
    """, (conteudo_id,)).fetchone()
    conn.close()

    perguntas = []
    for q in quiz:
        perguntas.append({
            "id": q["id"],
            "pergunta": q["pergunta"],
            "alternativas": json.loads(q["alternativas"]),
            "resposta_correta": q["resposta_correta"]
        })

    if request.method == "POST":
        respostas = request.form
        acertos = sum(1 for q in perguntas if respostas.get(str(q["id"])) == q["resposta_correta"])
        conn = get_db_connection()
        conn.execute("""
            INSERT OR REPLACE INTO progresso (usuario_id, conteudo_id, concluido, quiz_feito)
            VALUES (?, ?, 1, 1)
        """, (session["usuario_id"], conteudo_id))
        conn.commit()
        conn.close()
        return f"Você acertou {acertos} de {len(perguntas)} perguntas!"

    return render_template("quiz.html", trilha=trilha, perguntas=perguntas)

# ======================
# Rodar app
# ======================
if __name__ == "__main__":
    app.run(debug=True)
