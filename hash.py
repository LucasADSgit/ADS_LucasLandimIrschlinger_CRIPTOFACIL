from werkzeug.security import generate_password_hash
import sqlite3

# Conectar ao banco
conn = sqlite3.connect("banco.db")
conn.row_factory = sqlite3.Row

# Buscar todos os usuários
usuarios = conn.execute("SELECT id, senha FROM usuarios").fetchall()

for u in usuarios:
    senha_antiga = u["senha"]
    # Só gera hash se ainda não estiver em hash
    if not senha_antiga.startswith("pbkdf2:"):
        senha_hash = generate_password_hash(senha_antiga)
        conn.execute("UPDATE usuarios SET senha=? WHERE id=?", (senha_hash, u["id"]))

conn.commit()
conn.close()
print("Todas as senhas foram atualizadas para hash!")
