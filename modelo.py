import os
import sqlite3

_DIRECTORIO = os.path.dirname(os.path.abspath(__file__))

def crear_base():
    return sqlite3.connect(os.path.join(_DIRECTORIO, "materias.db"))

def crear_tabla(con):
    cursor = con.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nivel TEXT,
        nombre TEXT,
        docente TEXT,
        horas TEXT
    )
    """)
    con.commit()

def insertar(con, data):
    cursor = con.cursor()
    cursor.execute("""
    INSERT INTO materias 
    (nivel, nombre, docente, horas)
    VALUES (?, ?, ?, ?)
    """, data)
    con.commit()

def borrar(con, mi_id):
    con.cursor().execute("DELETE FROM materias WHERE id=?", (mi_id,))
    con.commit()

def actualizar_docente(con, docente, mi_id):
    con.cursor().execute("UPDATE materias SET docente=? WHERE id=?", (docente, mi_id))
    con.commit()

def obtener_todos(con):
    return con.cursor().execute("SELECT * FROM materias").fetchall()