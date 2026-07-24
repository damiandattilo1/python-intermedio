import os
import sqlite3

_DIRECTORIO = os.path.dirname(os.path.abspath(__file__))


class Materia:
    """Representa una materia con sus atributos."""

    def __init__(self, id=None, nivel="1", nombre="", docente="", horas=4):
        self.id = id
        self.nivel = nivel
        self.nombre = nombre
        self.docente = docente
        self.horas = int(horas)

    def __repr__(self):
        return f"Materia(id={self.id}, nivel={self.nivel}, nombre={self.nombre}, docente={self.docente}, horas={self.horas})"

    def __eq__(self, other):
        if not isinstance(other, Materia):
            return False
        return (self.nivel == other.nivel and self.nombre == other.nombre
                and self.docente == other.docente and self.horas == other.horas)

    def a_tupla(self):
        return (self.nivel, self.nombre, self.docente, self.horas)

    @classmethod
    def desde_fila(cls, fila):
        return cls(id=fila[0], nivel=fila[1], nombre=fila[2], docente=fila[3], horas=int(fila[4]))


class MateriaDB:
    """Capa de acceso a datos SQLite para materias."""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(_DIRECTORIO, "materias.db")
        self._db_path = db_path

    def _conexion(self):
        return sqlite3.connect(self._db_path)

    def crear_tabla(self):
        con = self._conexion()
        try:
            con.execute("""
                CREATE TABLE IF NOT EXISTS materias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nivel TEXT,
                    nombre TEXT,
                    docente TEXT,
                    horas INTEGER
                )
            """)
            con.commit()
        finally:
            con.close()

    def insertar(self, materia):
        con = self._conexion()
        try:
            con.execute(
                "INSERT INTO materias (nivel, nombre, docente, horas) VALUES (?, ?, ?, ?)",
                materia.a_tupla(),
            )
            con.commit()
        finally:
            con.close()

    def borrar(self, mi_id):
        con = self._conexion()
        try:
            con.execute("DELETE FROM materias WHERE id=?", (mi_id,))
            con.commit()
        finally:
            con.close()

    def actualizar(self, materia):
        con = self._conexion()
        try:
            con.execute(
                "UPDATE materias SET nivel=?, nombre=?, docente=?, horas=? WHERE id=?",
                (materia.nivel, materia.nombre, materia.docente, materia.horas, materia.id),
            )
            con.commit()
        finally:
            con.close()

    def obtener_todos(self):
        con = self._conexion()
        try:
            filas = con.execute("SELECT * FROM materias").fetchall()
            return [Materia.desde_fila(f) for f in filas]
        finally:
            con.close()

    def obtener_por_id(self, mi_id):
        con = self._conexion()
        try:
            fila = con.execute("SELECT * FROM materias WHERE id=?", (mi_id,)).fetchone()
            return Materia.desde_fila(fila) if fila else None
        finally:
            con.close()
