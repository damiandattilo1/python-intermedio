import re
import modelo

# conexión global del controlador
con = modelo.crear_base()
modelo.crear_tabla(con)

def validar_profesor(nombre):
    patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ]+(\s[A-Za-zÁÉÍÓÚáéíóúÑñ]+)*$"
    return re.match(patron, nombre) is not None


def agregar(datos):
    if not validar_profesor(datos[2]):
        print("Profesor inválido")
        return
    modelo.insertar(con, datos)


def listar():
    return modelo.obtener_todos(con)


def eliminar(mi_id):
    modelo.borrar(con, mi_id)


def modificar_docente(mi_id, docente):
    modelo.actualizar_docente(con, docente, mi_id)