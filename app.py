from flask import Flask, render_template, request, send_file, session
from datetime import datetime, timedelta
import pandas as pd
import os
from functools import wraps


app = Flask(__name__)
app.secret_key = "floresta_secret"


ARQUIVO = "controle_horas.xlsx"
ADMIN_SENHA = "Qualidade2026/2"


MEMBROS = [
    "Adla Camilla M. da Silva",
    "Ana Beatriz de Faria do Nascimento",
    "Brendo Adriano Alves Freire",
    "Carlos Augusto Corrêa",
    "Giulliana Pivato Campos",
    "Iago de Souza Reis",
    "Iago Lopes Sereno",
    "Isabela Veiga Luchetti Gonçalves",
    "João Carlos Almeida Maciel",
    "Kamilly dos Santos Almeida",
    "Kauã De Oliveira Da Silva",
    "Leonardo Antônio Luiz",
    "Liriel Sales Diniz",
    "Luiz Felipe dos Reis Bonatti",
    "Luiz Otávio de Souza Pereira",
    "Luiz Otávio Fernandes de Oliveira",
    "Marcos Vinícius de Sousa",
    "Marta Helena Pereira",
    "Mateus Gabriel de Souza",
    "Mateus Hebert Dias Pereira",
    "Matheus Moraes",
    "Michelly Maira Fernandes",
    "Nhaumy Laysa S. Januario",
    "Pedro Henrique Onofri Gomes",
    "Rita Helena Ribeiro de Souza",
    "Ronnie Von Luis Júnior",
    "Tiago Freire Elias"
]


# cria arquivo se não existir
if not os.path.exists(ARQUIVO):
    df = pd.DataFrame(columns=["Nome", "Data", "Entrada", "Saída", "Total/Dia"])
    df.to_excel(ARQUIVO, index=False)




def ler():
    return pd.read_excel(ARQUIVO).fillna("")




def salvar(df):
    df.to_excel(ARQUIVO, index=False)




# ---------------- ADMIN ----------------
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return "Acesso negado"
        return f(*args, **kwargs)
    return wrapper




# ---------------- HORAS ----------------
def calcular_horas(entrada, saida):
    try:
        t1 = datetime.strptime(entrada, "%H:%M")
        t2 = datetime.strptime(saida, "%H:%M")


        diff = t2 - t1
        minutos = int(diff.total_seconds() // 60)


        return f"{minutos // 60:02d}:{minutos % 60:02d}"
    except:
        return "00:00"




# ---------------- TOTAL SEMANAL ----------------
def total_semanal():
    df = ler()


    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")


    inicio = datetime.now() - timedelta(days=7)
    df = df[df["Data"] >= inicio]


    def to_min(x):
        try:
            h, m = x.split(":")
            return int(h) * 60 + int(m)
        except:
            return 0


    df["min"] = df["Total/Dia"].apply(to_min)


    grupo = df.groupby("Nome")["min"].sum().reset_index()


    result = []


    for _, row in grupo.iterrows():
        h = row["min"] // 60
        m = row["min"] % 60


        result.append({
            "nome": row["Nome"],
            "total": f"{h:02d}:{m:02d}"
        })


    return result




# ---------------- RANKING TOP 3 ----------------
def ranking_top3():
    dados = total_semanal()


    def conv(t):
        h, m = map(int, t.split(":"))
        return h * 60 + m


    ordenado = sorted(dados, key=lambda x: conv(x["total"]), reverse=True)


    medalhas = ["🥇", "🥈", "🥉"]


    top3 = ordenado[:3]


    ranking = []


    for i, item in enumerate(top3):
        ranking.append({
            "pos": medalhas[i],
            "nome": item["nome"],
            "total": item["total"]
        })


    return ranking




# ---------------- HOME ----------------
@app.route("/")
def home():
    df = ler()


    return render_template(
        "index.html",
        membros=MEMBROS,
        registros=df.tail(30).to_dict(orient="records"),
        semanal=total_semanal(),
        ranking=ranking_top3(),
        admin=session.get("admin", False)
    )




# ---------------- ENTRADA ----------------
@app.route("/entrada", methods=["POST"])
def entrada():
    nome = request.form["nome"]
    hora = request.form.get("hora") or datetime.now().strftime("%H:%M")


    df = ler()


    novo = {
        "Nome": nome,
        "Data": datetime.now().strftime("%Y-%m-%d"),
        "Entrada": hora,
        "Saída": "",
        "Total/Dia": ""
    }


    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
    salvar(df)


    return "Entrada registrada!"




# ---------------- SAÍDA ----------------
@app.route("/saida", methods=["POST"])
def saida():
    nome = request.form["nome"]
    hora = request.form.get("hora") or datetime.now().strftime("%H:%M")


    df = ler()


    for i in range(len(df)-1, -1, -1):
        if str(df.loc[i, "Nome"]).strip() == nome and df.loc[i, "Saída"] == "":
            df.loc[i, "Saída"] = hora
            df.loc[i, "Total/Dia"] = calcular_horas(df.loc[i, "Entrada"], hora)
            break


    salvar(df)
    return "Saída registrada!"




# ---------------- ADMIN ----------------
@app.route("/admin-login", methods=["POST"])
def admin_login():
    if request.form.get("senha") == ADMIN_SENHA:
        session["admin"] = True
        return "Admin logado"
    return "Senha incorreta"




@app.route("/logout")
def logout():
    session.clear()
    return "Deslogado"




@app.route("/limpar", methods=["POST"])
@admin_required
def limpar():
    df = pd.DataFrame(columns=["Nome", "Data", "Entrada", "Saída", "Total/Dia"])
    df.to_excel(ARQUIVO, index=False)
    return "Registros apagados"




# ---------------- DOWNLOAD ----------------
@app.route("/download")
def download():
    return send_file(ARQUIVO, as_attachment=True)




if __name__ == "__main__":
    app.run(debug=True)
