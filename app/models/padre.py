from .persona import Persona

class Padre(Persona):
    """Modelo de datos para un Padre de Familia o Apoderado."""
    def __init__(self, id, nombres, apellidos, dni, correo=None, fecha_nacimiento=None):
        super().__init__(id, nombres, apellidos, dni, correo, fecha_nacimiento)