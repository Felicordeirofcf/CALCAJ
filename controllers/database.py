import os
import sqlite3
from datetime import date, timedelta

# 🗂️ Caminho seguro para salvar o banco (AppData)
pasta_dados = os.path.join(os.getenv('APPDATA'), 'AJCALC')
os.makedirs(pasta_dados, exist_ok=True)
caminho_banco = os.path.join(pasta_dados, 'banco.db')

# ✅ Cria o banco e as tabelas se não existirem
def criar_banco():
    con = sqlite3.connect(caminho_banco)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, celular TEXT, email TEXT, oab TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS calculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT, cliente_id INTEGER, area TEXT,
            valor TEXT, prazo TEXT, pago TEXT, enviado TEXT
        )
    """)
    con.commit()
    con.close()

# ✅ Salvar cliente
def salvar_cliente(nome, celular, email, oab):
    con = sqlite3.connect(caminho_banco)
    cur = con.cursor()
    cur.execute("INSERT INTO clientes (nome, celular, email, oab) VALUES (?, ?, ?, ?)",
                (nome, celular, email, oab))
    con.commit()
    con.close()

# ✅ Buscar todos os clientes
def buscar_clientes():
    con = sqlite3.connect(caminho_banco)
    cur = con.cursor()
    cur.execute("SELECT id, nome, celular, email, oab FROM clientes")
    clientes = cur.fetchall()
    con.close()
    return clientes

# ✅ Excluir cliente
def excluir_cliente(cliente_id):
    con = sqlite3.connect(caminho_banco)
    cur = con.cursor()
    cur.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    cur.execute("DELETE FROM calculos WHERE cliente_id = ?", (cliente_id,))
    con.commit()
    con.close()

# ✅ Salvar novo cálculo
def salvar_calculo(numero, cliente_id, area, valor, prazo, pago, enviado):
    con = sqlite3.connect(caminho_banco)
    cur = con.cursor()
    cur.execute("""INSERT INTO calculos (
        numero, cliente_id, area, valor, prazo, pago, enviado
    ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (numero, cliente_id, area, valor, prazo, pago, enviado))
    con.commit()
    con.close()

# ✅ Buscar cálculos (processos), com filtro por número ou nome do cliente
def buscar_processos(filtro=""):
    con = sqlite3.connect(caminho_banco)
    cur = con.cursor()
    consulta = """
        SELECT c.nome, p.numero, p.prazo, p.area, p.valor, p.pago, p.enviado
        FROM calculos p
        JOIN clientes c ON c.id = p.cliente_id
    """
    if filtro:
        consulta += " WHERE c.nome LIKE ? OR p.numero LIKE ?"
        cur.execute(consulta, (f"%{filtro}%", f"%{filtro}%"))
    else:
        cur.execute(consulta)
    resultados = cur.fetchall()
    con.close()
    return resultados

# ✅ Buscar prazos por tipo: 'vencido', 'hoje' ou 'amanha'
def buscar_prazos_por_data(tipo):
    hoje = date.today()
    if tipo == "vencido":
        data = hoje.isoformat()
        where = "p.prazo < ?"
        param = (data,)
    elif tipo == "hoje":
        data = hoje.isoformat()
        where = "p.prazo = ?"
        param = (data,)
    elif tipo == "amanha":
        data = (hoje + timedelta(days=1)).isoformat()
        where = "p.prazo = ?"
        param = (data,)
    else:
        return []

    con = sqlite3.connect(caminho_banco)
    cur = con.cursor()
    cur.execute(f"""
        SELECT c.nome, p.numero, p.prazo
        FROM calculos p
        JOIN clientes c ON c.id = p.cliente_id
        WHERE {where}
    """, param)
    resultados = cur.fetchall()
    con.close()
    return resultados

