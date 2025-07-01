# RUTA: app/models/persona.py
# Define la estructura base para cualquier entidad tipo Persona.

from app.core.persona import Persona as PersonaBase

class Persona(PersonaBase):
    """
    Representa los datos de una persona en el sistema.
    Hereda de la clase abstracta PersonaBase para asegurar la consistencia.
    Este modelo de datos puro no contiene lógica de base de datos.
    """
    def __init__(self, id, nombres, apellidos, dni, correo=None, fecha_nacimiento=None):
        super().__init__(
            id=id,
            nombres=nombres,
            apellidos=apellidos,
            dni=dni,
            correo=correo,

            fecha_nacimiento=fecha_nacimiento
        )
