import sqlite3
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "chave_secreta_segura_terra_viva"


def init_db():
  """Inicializa a base de dados SQLite com a tabela de lotes de estoque."""
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS lotes_estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_item TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            unidade TEXT NOT NULL,
            data_entrada TEXT NOT NULL,
            data_validade TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


@app.route("/")
def index():
  """Tela 1: Menu Inicial / Entrada Principal."""
  return render_template("index.html")


@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
  """Tela 2: Formulário de Registo e Entrada de Lotes."""
  if request.method == "POST":
    nome_item = request.form["nome_item"]
    quantidade = request.form["quantidade"]
    unidade = request.form["unidade"]
    data_entrada = request.form["data_entrada"]
    data_validade = request.form["data_validade"]

    # Validação básica de regras e OWASP (proteção contra entradas vazias)
    if not nome_item or not quantidade or not data_validade:
      flash("Todos os campos obrigatórios devem ser preenchidos!", "danger")
      return redirect(url_for("cadastrar"))

    # Lógica simples de definição de status baseada na validade
    status = "Ativo (Verde)"
    if data_validade <= "2026-11-01":
      status = "Crítico (Vencerá em breve)"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        """
            INSERT INTO lotes_estoque (nome_item, quantidade, unidade, data_entrada, data_validade, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        (nome_item, quantidade, unidade, data_entrada, data_validade, status),
    )
    conn.commit()
    conn.close()

    flash("Lote registado com sucesso!", "success")
    return redirect(url_for("painel"))

  return render_template("cadastrar.html")


@app.route("/painel")
def painel():
  """Tela 3: Painel Geral de Stock e Alertas de Validade."""
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM lotes_estoque ORDER BY data_validade ASC")
  lotes = cursor.fetchall()
  conn.close()
  return render_template("painel.html", lotes=lotes)


if __name__ == "__main__":
  init_db()
  app.run(debug=True)