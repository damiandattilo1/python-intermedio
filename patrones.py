import os
import sqlite3

_DIRECTORIO = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# PATRÓN SINGLETON
# Asegura una única instancia de MateriaDB
# ============================================================

class MateriaDB(object):
    class __MateriaDB:
        def __init__(self, db_path):
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
            from modelo import Materia
            con = self._conexion()
            try:
                filas = con.execute("SELECT * FROM materias").fetchall()
                return [Materia.desde_fila(f) for f in filas]
            finally:
                con.close()

        def obtener_por_id(self, mi_id):
            from modelo import Materia
            con = self._conexion()
            try:
                fila = con.execute("SELECT * FROM materias WHERE id=?", (mi_id,)).fetchone()
                return Materia.desde_fila(fila) if fila else None
            finally:
                con.close()

    instancia = None

    def __new__(cls, db_path=None):
        if not MateriaDB.instancia:
            if db_path is None:
                db_path = os.path.join(_DIRECTORIO, "materias.db")
            MateriaDB.instancia = MateriaDB.__MateriaDB(db_path)
        return MateriaDB.instancia

    def __getattr__(self, nombre):
        return getattr(self.instancia, nombre)


# ============================================================
# PATRÓN FACTORY
# Crea objetos Materia según el tipo de nivel
# ============================================================

class MateriaFactory:
    """Factory para crear materiales según su nivel."""

    _clases = {}

    @classmethod
    def registrar(cls, nivel, clase_materia):
        cls._clases[nivel] = clase_materia

    @classmethod
    def crear(cls, nivel, **kwargs):
        clase = cls._clases.get(nivel, MateriaBasica)
        return clase(nivel=nivel, **kwargs)


class MateriaBasica:
    """Materia de nivel básico (1-2)."""

    def __init__(self, nivel="1", nombre="", docente="", horas=4):
        self.nivel = nivel
        self.nombre = nombre
        self.docente = docente
        self.horas = int(horas)
        self.tipo = "Basica"

    def descripcion(self):
        return f"[{self.tipo}] {self.nombre} - Nivel {self.nivel}"


class MateriaIntermedia:
    """Materia de nivel intermedio (3)."""

    def __init__(self, nivel="3", nombre="", docente="", horas=4):
        self.nivel = nivel
        self.nombre = nombre
        self.docente = docente
        self.horas = int(horas)
        self.tipo = "Intermedia"

    def descripcion(self):
        return f"[{self.tipo}] {self.nombre} - Nivel {self.nivel} ({self.horas}hs)"


class MateriaAvanzada:
    """Materia de nivel avanzado (4-5)."""

    def __init__(self, nivel="5", nombre="", docente="", horas=4):
        self.nivel = nivel
        self.nombre = nombre
        self.docente = docente
        self.horas = int(horas)
        self.tipo = "Avanzada"

    def descripcion(self):
        return f"[{self.tipo}] {self.nombre} - Nivel {self.nivel} ({self.horas}hs)"


# Registro de tipos de materia
MateriaFactory.registrar("1", MateriaBasica)
MateriaFactory.registrar("2", MateriaBasica)
MateriaFactory.registrar("3", MateriaIntermedia)
MateriaFactory.registrar("4", MateriaAvanzada)
MateriaFactory.registrar("5", MateriaAvanzada)


# ============================================================
# PATRÓN ADAPTER
# Adapta la interfaz de un sistema externo de calendario
# para que sea compatible con el sistema de materias
# ============================================================

class CalendarioExterno:
    """Interfaz de un sistema externo de calendario (Adaptee)."""

    def obtener_eventos(self):
        return [
            {"titulo": "Clase de Matematica", "fecha": "2026-07-28", "duracion_min": 90},
            {"titulo": "Clase de Fisica", "fecha": "2026-07-30", "duracion_min": 60},
        ]


class FormatoMaterias:
    """Interfaz que espera el sistema de materias (Target)."""

    def listar_materias_formateadas(self):
        raise NotImplementedError


class CalendarioAdapter(FormatoMaterias):
    """Adapta CalendarioExterno al formato de materias."""

    def __init__(self, calendario):
        self._calendario = calendario

    def listar_materias_formateadas(self):
        eventos = self._calendario.obtener_eventos()
        resultado = []
        for e in eventos:
            horas = e["duracion_min"] // 60
            resultado.append({
                "nombre": e["titulo"],
                "fecha": e["fecha"],
                "horas": max(horas, 1),
            })
        return resultado


class FormatoMateriasDirecto(FormatoMaterias):
    """Formato directo de materias sin adaptación."""

    def __init__(self, materias):
        self._materias = materias

    def listar_materias_formateadas(self):
        return [{"nombre": m.nombre, "nivel": m.nivel, "horas": m.horas}
                for m in self._materias]
