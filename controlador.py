import re
import modelo

# conexión global del controlador
con = modelo.crear_base()
modelo.crear_tabla(con)

class Materia:
    def __init__(self, id, nombre, nivel, cargoDocente, horas):
        self.id = id
        self.nombre = nombre
        self.nivel = nivel
        self.cargoDocente = cargoDocente
        self.horas = horas

    def validar_profesor(nombre):
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ]+(\s[A-Za-zÁÉÍÓÚáéíóúÑñ]+)*$"
        return re.match(patron, nombre) is not None


    def agregar(datos):
        if not Materia.validar_profesor(datos[2]):
            print("Profesor inválido")
            return
        modelo.insertar(con, datos)


    def listar():
        return modelo.obtener_todos(con)


    def eliminar(mi_id):
        modelo.borrar(con, mi_id)


    def modificar_docente(mi_id, self):
        modelo.actualizar_docente(con, self.cargoDocente, mi_id)