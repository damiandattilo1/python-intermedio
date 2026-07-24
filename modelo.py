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
