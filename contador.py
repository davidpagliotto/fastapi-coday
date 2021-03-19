import sqlite3

import uvicorn
from fastapi import FastAPI

app = FastAPI()


def cria_db():
    try:
        conn = sqlite3.connect("contador.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE contador (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                total INTEGER    
            );
        """)
        conn.close()

        incrementa(0)
    except Exception as e:
        print(e)


def get_total():
    conn = sqlite3.connect("contador.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT total FROM contador WHERE id = 1;
    """)
    linha = cursor.fetchone()
    conn.close()

    return linha[0]


def incrementa(total):
    conn = sqlite3.connect("contador.db")
    cursor = conn.cursor()

    cursor.execute(f"""
        REPLACE INTO contador (id, total) 
        VALUES (1, {total+1});
    """)
    conn.commit()
    conn.close()


@app.get("/contador")
def get_count():
    total = get_total()
    incrementa(total)
    return total


if __name__ == "__main__":
    cria_db()
    uvicorn.run(app, host="localhost", port=8000)
