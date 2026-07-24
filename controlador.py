import re
import modelo


class Materia:
    @staticmethod
    def validar_profesor(nombre):
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ]+(\s[A-Za-zÁÉÍÓÚáéíóúÑñ]+)*$"
        return re.match(patron, nombre) is not None

    @staticmethod
    def agregar(datos):
        if not Materia.validar_profesor(datos[2]):
            print("Profesor inválido")
            return
        con = modelo.crear_base()
        try:
            modelo.insertar(con, datos)
        finally:
            con.close()

    @staticmethod
    def listar():
        con = modelo.crear_base()
        try:
            return modelo.obtener_todos(con)
        finally:
            con.close()

    @staticmethod
    def eliminar(mi_id):
        con = modelo.crear_base()
        try:
            modelo.borrar(con, mi_id)
        finally:
            con.close()

    @staticmethod
    def modificar(mi_id, nombre, docente):
        con = modelo.crear_base()
        try:
            modelo.actualizar_materia(con, nombre, docente, mi_id)
        finally:
            con.close()
