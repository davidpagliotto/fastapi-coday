from typing import List

import aiosqlite
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


async def criar_db():
    try:
        conn = await aiosqlite.connect(DB_NAME)
        cursor = await conn.cursor()
        await cursor.execute("""
            CREATE TABLE newsletter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                email TEXT
            );
        """)
        await conn.close()
    except Exception as e:
        print(e)


async def gravar_inscrito(nome: str, email: str):
    conn = await aiosqlite.connect(DB_NAME)
    cursor = await conn.cursor()
    await cursor.execute(f"""
        INSERT INTO newsletter (nome, email)
        VALUES (?, ?);
    """, (nome, email))
    await conn.commit()
    id = cursor.lastrowid
    await conn.close()

    return id


async def get_total_inscritos_db():
    conn = await aiosqlite.connect(DB_NAME)
    cursor = await conn.cursor()
    await cursor.execute("""
        SELECT count(1) FROM newsletter
    """)
    linha = await cursor.fetchone()
    await conn.close()
    return linha[0]


async def get_inscritos_db():
    conn = await aiosqlite.connect(DB_NAME)
    cursor = await conn.cursor()
    await cursor.execute("""
        SELECT
            id, nome, email
        FROM
            newsletter
    """)
    inscritos = []
    for linha in await cursor.fetchall():
        inscritos.append(InscritoDB(
            id=linha[0],
            nome=linha[1],
            email=linha[2]
        ))

    return inscritos


@app.post("/inscrever", response_model=InscritoDB)
async def post_inscrever(inscrito: Inscrito):
    id = await gravar_inscrito(inscrito.nome, inscrito.email)
    inscrito_db = InscritoDB(id=id, nome=inscrito.nome, email=inscrito.email)
    return inscrito_db


@app.get("/total-inscritos")
async def get_total_inscritos():
    total = await get_total_inscritos_db()
    return dict(total=total)


@app.get("/inscritos", response_model=List[InscritoDB])
async def get_inscritos():
    inscritos = await get_inscritos_db()
    return inscritos


if __name__ == '__main__':
    criar_db()
    uvicorn.run(app, host="localhost", port=8001)
