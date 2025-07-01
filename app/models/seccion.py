class Seccion:
    """Modelo de datos para una Sección dentro de un Grado."""
    def __init__(self, nombre, grado_id, id=None):
        self.id = id
        self.nombre = nombre
        self.grado_id = grado_id
        # Atributo poblado por el repositorio
        self.grado_nombre = None