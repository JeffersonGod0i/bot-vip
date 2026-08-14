import sqlite3, datetime, os

DB_PATH = "bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        username TEXT,
        plano TEXT,
        expira_em TEXT,
        payment_id TEXT,
        status TEXT,
        created_at TEXT
    )""")
    conn.commit()
    conn.close()

def salvar_pagamento_pendente(telegram_id, username, plano, payment_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT OR REPLACE INTO users (telegram_id, username, plano, payment_id, status, created_at) VALUES (?,?,?,?,?,?)",
                 (telegram_id, username, plano, str(payment_id), "pendente", datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def liberar_acesso(telegram_id, plano_dias):
    expira = datetime.datetime.now() + datetime.timedelta(days=plano_dias)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE users SET expira_em=?, status='ativo' WHERE telegram_id=?",
                 (expira.isoformat(), telegram_id))
    conn.commit()
    conn.close()
    return expira

def buscar_user(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
