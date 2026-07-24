import datetime


# ============================================================
# PATRÓN OBSERVER
# Según la notación del curso: Tema / Observador
# ============================================================

class Tema:
    """Sujeto observable (Tema) - interfaz base del patrón Observer."""

    def agregar(self, obj):
        raise NotImplementedError

    def quitar(self, obj):
        raise NotImplementedError

    def notificar(self):
        raise NotImplementedError


class TemaConcreto(Tema):
    """Tema concreto que maneja el estado de materias."""

    def __init__(self):
        self.estado = None
        self._observadores = []

    def set_estado(self, value):
        self.estado = value
        self.notificar()

    def get_estado(self):
        return self.estado

    def agregar(self, obj):
        self._observadores.append(obj)

    def quitar(self, obj):
        self._observadores.remove(obj)

    def notificar(self):
        for observador in self._observadores:
            observador.update()


class Observador:
    """Interfaz base del patrón Observer."""

    def update(self):
        raise NotImplementedError


class ConcreteObserverA(Observador):
    """Observador concreto A: registra logs en consola."""

    def __init__(self, obj):
        self.observador_a = obj
        self.observador_a.agregar(self)
        self.estado = None

    def update(self):
        momento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.estado = self.observador_a.get_estado()
        if isinstance(self.estado, dict):
            evento = self.estado.get("evento", "")
            if evento == "agregar":
                nombre = self.estado.get("nombre", "?")
                print(f"[{momento}] [Observer A] INGRESO: Nueva materia '{nombre}'")
            elif evento == "eliminar":
                mi_id = self.estado.get("id", "?")
                print(f"[{momento}] [Observer A] ELIMINACION: Materia ID {mi_id}")
            elif evento == "modificar":
                nombre = self.estado.get("nombre", "?")
                print(f"[{momento}] [Observer A] ACTUALIZACION: Materia '{nombre}'")
            elif evento == "listar":
                cantidad = self.estado.get("cantidad", 0)
                print(f"[{momento}] [Observer A] CONSULTA: {cantidad} materias")


class ConcreteObserverB(Observador):
    """Observador concreto B: acumula historial en memoria."""

    def __init__(self, obj):
        self.observador_b = obj
        self.observador_b.agregar(self)
        self.historial = []

    def update(self):
        momento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        estado = self.observador_b.get_estado()
        self.historial.append({"momento": momento, "estado": estado})

    def obtener_historial(self):
        return list(self.historial)

    def limpiar(self):
        self.historial.clear()


# ============================================================
# Wrapper legacy: Subject/Observer para uso en controlador
# ============================================================

class Subject:
    """Wrapper que adapta TemaConcreto al uso del controlador."""

    def __init__(self):
        self._tema = TemaConcreto()
        self._observadores_legacy = []

    def agregar_observador(self, observador):
        if hasattr(observador, "actualizar"):
            self._observadores_legacy.append(observador)
        else:
            self._tema.agregar(observador)

    def eliminar_observador(self, observador):
        if observador in self._observadores_legacy:
            self._observadores_legacy.remove(observador)
        else:
            self._tema.quitar(observador)

    def notificar(self, evento, datos=None):
        for obs in self._observadores_legacy:
            obs.actualizar(evento, datos)
        estado = {"evento": evento}
        if isinstance(datos, dict):
            estado.update(datos)
        elif hasattr(datos, "nombre"):
            estado["nombre"] = datos.nombre
            estado["datos"] = datos
        self._tema.set_estado(estado)


class Observer:
    """Interfaz base para observadores legacy."""
    pass

class LogObserver(Observer):
    """Observador que registra eventos CRUD en consola."""

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

    def update(self):
        pass


class HistorialObserver(Observer):
    """Observador que acumula un historial de eventos en memoria."""

    def __init__(self):
        self.historial = []

    def actualizar(self, evento, datos=None):
        momento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.historial.append({"momento": momento, "evento": evento, "datos": datos})

    def update(self):
        pass

    def obtener_historial(self):
        return list(self.historial)

    def limpiar(self):
        self.historial.clear()
