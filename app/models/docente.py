
from .persona import Persona

class Docente(Persona):
    """Modelo de datos para un Docente."""
    def __init__(self, id, nombres, apellidos, dni, especialidad=None, correo=None, fecha_nacimiento=None):
        super().__init__(id, nombres, apellidos, dni, correo, fecha_nacimiento)
        self.especialidad = especialidad
        # Atributos que pueden ser poblados por el repositorio
        self.username = None
        self.activo = None