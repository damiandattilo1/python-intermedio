import re
from modelo import Materia, MateriaDB
from decoradores import log_agregar, log_eliminar, log_modificar
from observador import Subject


class MateriaControlador(Subject):
    """Controlador para operaciones CRUD de materias."""

    def __init__(self):
        super().__init__()
        self._db = MateriaDB()
        self._db.crear_tabla()

    @staticmethod
    def validar_profesor(nombre):
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ]+(\s[A-Za-zÁÉÍÓÚáéíóúÑñ]+)*$"
        return re.match(patron, nombre) is not None

    @staticmethod
    def validar_horas(valor):
        return valor.isdigit() and int(valor) > 0

    @log_agregar
    def agregar(self, materia):
        ok, msg = self._validar(materia)
        if not ok:
            return False, msg
        self._db.insertar(materia)
        self.notificar("agregar", materia)
        return True, ""

    def listar(self):
        materias = self._db.obtener_todos()
        self.notificar("listar", {"cantidad": len(materias)})
        return materias

    @log_eliminar
    def eliminar(self, mi_id):
        self._db.borrar(mi_id)
        self.notificar("eliminar", {"id": mi_id})

    @log_modificar
    def modificar(self, materia):
        self._db.actualizar(materia)
        self.notificar("modificar", materia)

    def _validar(self, materia):
        if not self.validar_profesor(materia.docente):
            return False, "Profesor invalido"
        if not self.validar_horas(materia.horas):
            return False, "Horas debe ser un numero entero"
        return True, ""
