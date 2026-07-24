import logging

logger = logging.getLogger(__name__)


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


class LogObserver(Observador):
    """Observador concreto: registra eventos CRUD via logging."""

    def __init__(self, tema=None):
        self._tema = tema
        self.estado = None
        if tema:
            tema.agregar(self)

    def update(self):
        self.estado = self._tema.get_estado()
        if isinstance(self.estado, dict):
            evento = self.estado.get("evento", "")
            if evento == "agregar":
                logger.info("[Observer] INGRESO: Nueva materia '%s'",
                            self.estado.get("nombre", "?"))
            elif evento == "eliminar":
                logger.info("[Observer] ELIMINACION: Materia ID %s",
                            self.estado.get("id", "?"))
            elif evento == "modificar":
                logger.info("[Observer] ACTUALIZACION: Materia '%s'",
                            self.estado.get("nombre", "?"))
            elif evento == "listar":
                logger.info("[Observer] CONSULTA: %s materias",
                            self.estado.get("cantidad", 0))


class HistorialObserver(Observador):
    """Observador concreto: acumula historial de eventos en memoria."""

    def __init__(self, tema=None):
        self._tema = tema
        self.historial = []
        if tema:
            tema.agregar(self)

    def update(self):
        estado = self._tema.get_estado()
        self.historial.append({"estado": estado})

    def obtener_historial(self):
        return list(self.historial)

    def limpiar(self):
        self.historial.clear()


# ============================================================
# Subject: wrapper para uso del controlador
# ============================================================

class Subject:
    """Subject que usa TemaConcreto para notificar observadores."""

    def __init__(self):
        self._tema = TemaConcreto()

    @property
    def tema(self):
        return self._tema

    def agregar_observador(self, observador):
        if observador._tema is None:
            observador._tema = self._tema
            self._tema.agregar(observador)

    def eliminar_observador(self, observador):
        self._tema.quitar(observador)

    def notificar(self, evento, datos=None):
        estado = {"evento": evento}
        if isinstance(datos, dict):
            estado.update(datos)
        elif hasattr(datos, "nombre"):
            estado["nombre"] = datos.nombre
            estado["datos"] = datos
        self._tema.set_estado(estado)
