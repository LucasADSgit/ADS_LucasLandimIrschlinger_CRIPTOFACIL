from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"  # troque por algo mais seguro

DATABASE = "banco.db"

# Conexão com o banco
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ======================
# PÁGINA INICIAL
# ======================
@app.route("/")
def index():
    return render_template("index.html")

# ======================
# CADASTRO DE USUÁRIO
# ======================
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
            (nome, email, senha)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    
    return render_template("cadastro.html")

# ======================
# LOGIN DE USUÁRIO
# ======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM usuarios WHERE email = ? AND senha = ?",
            (email, senha)
        ).fetchone()
        conn.close()

        if user:
            session["usuario_id"] = user["id"]
            return redirect(url_for("trilhas"))
        else:
            return "Usuário ou senha incorretos"

    return render_template("login.html")

# ======================
# LOGOUT
# ======================
@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    return redirect(url_for("index"))

# ======================
# LISTA DE TRILHAS
# ======================
@app.route("/trilhas")
def trilhas():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    trilhas = conn.execute("SELECT * FROM trilhas").fetchall()
    conn.close()
    return render_template("trilhas.html", trilhas=trilhas)

# ======================
# QUIZ
# ======================
@app.route("/quiz/<int:conteudo_id>", methods=["GET", "POST"])
def quiz(conteudo_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    quiz = conn.execute(
        "SELECT * FROM quizzes WHERE conteudo_id = ?",
        (conteudo_id,)
    ).fetchall()
    conn.close()

    if request.method == "POST":
        respostas = request.form
        acertos = 0
        for q in quiz:
            if respostas.get(str(q["id"])) == q["resposta_correta"]:
                acertos += 1
        return f"Você acertou {acertos} de {len(quiz)} perguntas!"

    return render_template("quiz.html", quiz=quiz)

# ======================
# EXECUÇÃO DO APP
# ======================
if __name__ == "__main__":
    app.run(debug=True)
