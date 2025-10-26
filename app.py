from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from dotenv import load_dotenv
from openai import OpenAI
import sqlite3
import os
import json
import ast
import traceback
import re

# ======================
# Configurações iniciais
# ======================
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "sua_chave_secreta_local")
DATABASE = "banco.db"

# Cliente OpenAI (pode lançar erro se chave/credito inválido)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ======================
# Banco de dados
# ======================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def tabela_tem_coluna(table, column):
    """Retorna True se tabela tiver a coluna dada (SQLite pragma)."""
    conn = get_db_connection()
    cur = conn.execute(f"PRAGMA table_info({table})").fetchall()
    conn.close()
    cols = [r["name"] for r in cur]
    return column in cols

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
# Marcar como concluído
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
# IA: gerar quiz automaticamente (robusto)
# ======================
def gerar_quiz_ia_interno(conteudo_id):
    """Gera quiz via OpenAI e salva no banco adaptando-se ao schema existente."""
    conn = get_db_connection()
    conteudo = conn.execute("SELECT * FROM conteudos WHERE id=?", (conteudo_id,)).fetchone()
    conn.close()
    if not conteudo:
        return None, "Conteúdo não encontrado"

    texto_para_ia = conteudo["texto"] or conteudo["descricao"] or ""
    if not texto_para_ia.strip():
        return None, "Conteúdo sem texto suficiente para gerar perguntas."

    prompt = f"""
Gere 3 perguntas de múltipla escolha curtas e objetivas sobre o conteúdo abaixo.
Cada pergunta deve ter 4 alternativas (a, b, c, d).
Retorne APENAS um JSON válido com uma lista de objetos no formato:
[
  {{
    "pergunta": "texto da pergunta",
    "alternativas": ["texto A","texto B","texto C","texto D"],
    "resposta_correta": "a"
  }}
]
Conteúdo:
{texto_para_ia}
"""

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.5
        )
        conteudo_resposta = resposta.choices[0].message.content.strip()
        print("Resposta IA (bruta):\n", conteudo_resposta)

        # 🔹 Limpeza do JSON da IA (remove ```json ... ``` caso exista)
        conteudo_resposta = conteudo_resposta.strip()
        if conteudo_resposta.startswith("```"):
            conteudo_resposta = conteudo_resposta.strip("`")
            conteudo_resposta = conteudo_resposta.replace("json", "", 1).strip()

        try:
            quiz_json = json.loads(conteudo_resposta)
        except json.JSONDecodeError:
            match = re.search(r"\[.*\]", conteudo_resposta, re.DOTALL)
            if match:
                quiz_json = json.loads(match.group(0))
            else:
                print("⚠️ Erro: IA retornou formato inválido\n", conteudo_resposta)
                return None, "IA retornou formato inválido"

        # Valida e normaliza
        normalized = []
        for item in quiz_json:
            p = item.get("pergunta") or item.get("question") or item.get("q")
            alts = item.get("alternativas") or item.get("alternatives") or item.get("choices")
            rc = item.get("resposta_correta") or item.get("answer") or item.get("correct")
            if isinstance(rc, str) and len(rc) >= 1:
                rc = rc.strip().lower()[0]
            if not (p and isinstance(alts, (list, tuple)) and len(alts) >= 4 and rc in ("a","b","c","d")):
                continue
            normalized.append({"pergunta": str(p).strip(), "alternativas": [str(a) for a in alts[:4]], "resposta_correta": rc})

        if not normalized:
            return None, "IA gerou perguntas, mas nenhuma passou na validação"

        # Salva no banco
        conn = get_db_connection()
        conn.execute("DELETE FROM quizzes WHERE conteudo_id=?", (conteudo_id,))
        has_alternativas_col = tabela_tem_coluna("quizzes", "alternativas")
        for q in normalized:
            if has_alternativas_col:
                conn.execute(
                    "INSERT INTO quizzes (conteudo_id, pergunta, alternativas, resposta_correta, gerado_por_ia) VALUES (?, ?, ?, ?, 1)",
                    (conteudo_id, q["pergunta"], json.dumps(q["alternativas"], ensure_ascii=False), q["resposta_correta"])
                )
        conn.commit()
        conn.close()
        return normalized, None

    except Exception as e:
        traceback.print_exc()
        return None, f"Erro ao chamar API da OpenAI: {e}"

@app.route("/gerar_quiz/<int:conteudo_id>")
def gerar_quiz_ia(conteudo_id):
    quiz, erro = gerar_quiz_ia_interno(conteudo_id)
    if erro:
        return f"Erro: {erro}", 400
    return redirect(url_for("quiz", conteudo_id=conteudo_id))

# ======================
# Quiz - leitura e submissão
# ======================
@app.route("/quiz/<int:conteudo_id>", methods=["GET", "POST"])
def quiz(conteudo_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    quiz_rows = conn.execute("SELECT * FROM quizzes WHERE conteudo_id=?", (conteudo_id,)).fetchall()
    trilha = conn.execute("""
        SELECT t.* FROM trilhas t
        JOIN conteudos c ON c.trilha_id = t.id
        WHERE c.id = ?
    """, (conteudo_id,)).fetchone()
    conn.close()

    perguntas = []
    if quiz_rows:
        row0 = dict(quiz_rows[0])
        if "alternativas" in row0 and row0["alternativas"] is not None:
            for r in quiz_rows:
                try:
                    alts = json.loads(r["alternativas"])
                except Exception:
                    try:
                        alts = ast.literal_eval(r["alternativas"])
                    except Exception:
                        alts = []
                perguntas.append({
                    "id": r["id"],
                    "pergunta": r["pergunta"],
                    "alternativas": alts,
                    "resposta_correta": (r["resposta_correta"] or "").strip().lower()
                })
        elif "alternativa_a" in row0:
            for r in quiz_rows:
                alts = [r["alternativa_a"], r["alternativa_b"], r["alternativa_c"], r["alternativa_d"]]
                perguntas.append({
                    "id": r["id"],
                    "pergunta": r["pergunta"],
                    "alternativas": alts,
                    "resposta_correta": (r["resposta_correta"] or "").strip().lower()
                })

    if request.method == "GET":
        if not perguntas:
            return render_template("quiz.html", trilha=trilha, perguntas=perguntas, msg_no_questions=True)
        return render_template("quiz.html", trilha=trilha, perguntas=perguntas)

    respostas = request.form
    acertos = 0
    for p in perguntas:
        user_ans = respostas.get(str(p["id"]))
        if user_ans:
            correct_letter = p["resposta_correta"].lower()
            letter_map = {"a": 0, "b": 1, "c": 2, "d": 3}
            try:
                correct_text = p["alternativas"][letter_map[correct_letter]]
            except Exception:
                correct_text = None
            if user_ans.strip().lower() == correct_letter or (correct_text and user_ans.strip() == correct_text):
                acertos += 1

    conn = get_db_connection()
    conn.execute("""
        INSERT OR REPLACE INTO progresso (usuario_id, conteudo_id, concluido, quiz_feito)
        VALUES (?, ?, 1, 1)
    """, (session["usuario_id"], conteudo_id))
    conn.commit()
    conn.close()

    return render_template("resultado_quiz.html", acertos=acertos, total=len(perguntas))

# ======================
# Rodar app
# ======================
if __name__ == "__main__":
    app.run(debug=True)
