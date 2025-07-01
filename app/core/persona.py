# RUTA: app/core/persona.py
# Define la clase base abstracta para todas las entidades tipo persona.

from abc import ABC

class Persona(ABC):
    """
    Clase base abstracta para todas las personas en el sistema.
    Aplica el principio de Herencia al definir atributos comunes
    que serán heredados por sus clases hijas (Estudiante, Docente, etc.).
    Es 'abstracta' porque no se espera que se creen objetos 'Persona' directamente.
    """
    def __init__(self, id, nombres, apellidos, dni, correo=None, fecha_nacimiento=None):
        """
        Constructor que inicializa los atributos comunes a toda persona.
        """
        self.id = id # Corresponde al ID del usuario
        self.nombres = nombres
        self.apellidos = apellidos
        self.dni = dni
        self.correo = correo
        self.fecha_nacimiento = fecha_nacimiento

    @property
    def nombre_completo(self):
        """
        Propiedad que encapsula la lógica de unir nombres y apellidos.
        Se accede como un atributo (ej. mi_persona.nombre_completo) y no como
        un método (mi_persona.nombre_completo()), ocultando la implementación.
        """
        return f"{self.nombres} {self.apellidos}"
