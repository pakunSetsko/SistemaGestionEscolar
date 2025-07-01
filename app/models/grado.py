class Grado:
    """Modelo de datos para un Grado Académico."""
    def __init__(self, nombre, nivel, id=None):
        self.id = id
        self.nombre = nombre
        self.nivel = nivel