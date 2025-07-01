# RUTA: app/repositories/persona_repository.py
# Repositorio para gestionar las operaciones CRUD de la entidad Persona.

from .base_repository import BaseRepository
from app.core.persona import Persona

class PersonaRepository(BaseRepository):
    """
    Repositorio que encapsula el acceso a datos para la tabla Personas.
    """
    def _map_row_to_object(self, row):
        """Mapea una fila de la base de datos a un objeto Persona."""
        if row:
            return Persona(
                id=row.id,
                nombres=row.nombres,
                apellidos=row.apellidos,
                dni=row.dni,
                correo=row.correo,
                fecha_nacimiento=row.fecha_nacimiento
            )
        return None
    
    def find_by_dni(self, dni):
        """Busca una persona por su DNI para evitar duplicados."""
        query = "SELECT * FROM Personas WHERE dni = ?"
        row = self._fetch_one(query, (dni,))
        return self._map_row_to_object(row)

    def save(self, persona: Persona):
        """
        Guarda los datos de una persona. La tabla Personas espera que el ID
        ya exista en la tabla Usuarios debido a la relación 1 a 1.
        """
        # La lógica de 'save' para Persona es un poco diferente.
        # Asume que el registro en Usuarios ya fue creado y tenemos un ID.
        # Primero, verificamos si la persona ya existe para decidir si es INSERT o UPDATE.
        
        query_check = "SELECT id FROM Personas WHERE id = ?"
        exists = self._fetch_one(query_check, (persona.id,))

        if exists:
            # UPDATE
            query = """
                UPDATE Personas 
                SET nombres=?, apellidos=?, dni=?, correo=?, fecha_nacimiento=?
                WHERE id=?
            """
            params = (persona.nombres, persona.apellidos, persona.dni, persona.correo, persona.fecha_nacimiento, persona.id)
        else:
            # INSERT
            query = """
                INSERT INTO Personas (id, nombres, apellidos, dni, correo, fecha_nacimiento)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (persona.id, persona.nombres, persona.apellidos, persona.dni, persona.correo, persona.fecha_nacimiento)
        
        self._execute_and_commit(query, params)

    # Los métodos find_by_id, get_all, y delete no se implementan aquí
    # porque la gestión de personas siempre se hará a través de su rol específico
    # (Estudiante, Docente, etc.), y la eliminación es manejada por 'ON DELETE CASCADE'
    # desde la tabla Usuarios.
    def find_by_id(self, entity_id):
        pass

    def get_all(self):
        pass

    def delete(self, entity_id):
        pass
