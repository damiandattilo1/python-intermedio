import re
import modelo


class Materia:
    @staticmethod
    def validar_profesor(nombre):
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ]+(\s[A-Za-zÁÉÍÓÚáéíóúÑñ]+)*$"
        return re.match(patron, nombre) is not None

    @staticmethod
    def validar_horas(valor):
        return valor.isdigit() and int(valor) > 0

    @staticmethod
    def agregar(datos):
        if not Materia.validar_profesor(datos[2]):
            return False, "Profesor invalido"
        if not Materia.validar_horas(datos[3]):
            return False, "Horas debe ser un numero entero"
        con = modelo.crear_base()
        try:
            modelo.insertar(con, datos)
        finally:
            con.close()
        return True, ""

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
    def modificar(mi_id, nivel, nombre, docente, horas):
        con = modelo.crear_base()
        try:
            modelo.actualizar_materia(con, nivel, nombre, docente, horas, mi_id)
        finally:
            con.close()
