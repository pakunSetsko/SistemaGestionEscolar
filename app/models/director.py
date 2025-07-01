from .persona import Persona

class Director(Persona):
    """Modelo de datos para un Director."""
    def __init__(self, id, nombres, apellidos, dni, correo=None, fecha_nacimiento=None):
        super().__init__(id, nombres, apellidos, dni, correo, fecha_nacimiento)