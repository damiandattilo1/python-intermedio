import datetime


class Subject:
    """Sujeto observable que notifica a sus observadores."""

    def __init__(self):
        self._observadores = []

    def agregar_observador(self, observador):
        self._observadores.append(observador)

    def eliminar_observador(self, observador):
        self._observadores.remove(observador)

    def notificar(self, evento, datos=None):
        for obs in self._observadores:
            obs.actualizar(evento, datos)


class Observer:
    """Interfaz base para observadores."""

    def actualizar(self, evento, datos=None):
        raise NotImplementedError


class LogObserver(Observer):
    """Observador que registra todos los eventos CRUD en consola."""

    def actualizar(self, evento, datos=None):
        momento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if evento == "agregar":
            nombre = datos.nombre if datos else "?"
            print(f"[{momento}] [OBSERVER] INGRESO: Nueva materia '{nombre}' registrada")
        elif evento == "eliminar":
            mi_id = datos.get("id", "?") if datos else "?"
            print(f"[{momento}] [OBSERVER] ELIMINACION: Materia ID {mi_id} eliminada")
        elif evento == "modificar":
            nombre = datos.nombre if datos else "?"
            print(f"[{momento}] [OBSERVER] ACTUALIZACION: Materia '{nombre}' modificada")
        elif evento == "listar":
            cantidad = datos.get("cantidad", 0) if datos else 0
            print(f"[{momento}] [OBSERVER] CONSULTA: Listado de {cantidad} materias")


class HistorialObserver(Observer):
    """Observador que acumula un historial de eventos en memoria."""

    def __init__(self):
        self.historial = []

    def actualizar(self, evento, datos=None):
        momento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.historial.append({"momento": momento, "evento": evento, "datos": datos})

    def obtener_historial(self):
        return list(self.historial)

    def limpiar(self):
        self.historial.clear()
