import sqlite3
from typing import List

import uvicorn
from fastapi import FastAPI
from pydantic.main import BaseModel

app = FastAPI()
DB_NAME = "newsletter.db"


class Inscrito(BaseModel):
    nome: str
    email: str


class InscritoDB(BaseModel):
    id: int
    nome: str
    email: str


def criar_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE newsletter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                email TEXT
            );
        """)
        conn.close()
    except Exception as e:
        print(e)


def gravar_inscrito(nome: str, email: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO newsletter (nome, email)
        VALUES (?, ?);
    """, (nome, email))
    conn.commit()
    id = cursor.lastrowid
    conn.close()

    return id


def get_total_inscritos_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT count(1) FROM newsletter
    """)
    linha = cursor.fetchone()
    conn.close()
    return linha[0]


def get_inscritos_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            id, nome, email
        FROM
            newsletter
    """)
    inscritos = []
    for linha in cursor.fetchall():
        inscritos.append(InscritoDB(
            id=linha[0],
            nome=linha[1],
            email=linha[2]
        ))

    return inscritos


@app.post("/inscrever", response_model=InscritoDB)
def post_inscrever(inscrito: Inscrito):
    id = gravar_inscrito(inscrito.nome, inscrito.email)
    inscrito_db = InscritoDB(id=id, nome=inscrito.nome, email=inscrito.email)
    return inscrito_db


@app.get("/total-inscritos")
def get_total_inscritos():
    total = get_total_inscritos_db()
    return dict(total=total)


@app.get("/inscritos", response_model=List[InscritoDB])
def get_inscritos():
    inscritos = get_inscritos_db()
    return inscritos


if __name__ == '__main__':
    criar_db()
    uvicorn.run(app, host="localhost", port=8001)
