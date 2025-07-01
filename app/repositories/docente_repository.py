# RUTA: app/repositories/docente_repository.py
# Repositorio para las operaciones de la entidad Docente.

from .base_repository import BaseRepository
from app.models.docente import Docente

class DocenteRepository(BaseRepository):
    """
    Repositorio que encapsula el acceso a datos para la tabla Docentes y su relación con Personas.
    """
    def _map_row_to_object(self, row):
        """Mapea una fila de la BD a un objeto Docente."""
        if not row:
            return None
        
        docente = Docente(
            id=row.id,
            nombres=row.nombres,
            apellidos=row.apellidos,
            dni=row.dni,
            correo=row.correo,
            fecha_nacimiento=row.fecha_nacimiento,
            especialidad=row.especialidad
        )
        # Añadir campos extra si vienen de un JOIN con Usuarios
        if 'username' in [desc[0] for desc in row.cursor_description]:
            docente.username = row.username
            docente.activo = row.activo
            
        return docente

    def find_by_id(self, docente_id):
        """Busca un docente por su ID, obteniendo todos sus detalles."""
        query = """
            SELECT p.*, d.especialidad, u.username, u.activo
            FROM Personas p 
            JOIN Docentes d ON p.id = d.id
            JOIN Usuarios u ON p.id = u.id
            WHERE p.id = ?
        """
        row = self._fetch_one(query, (docente_id,))
        return self._map_row_to_object(row)

    def get_all(self):
        """Obtiene una lista de todos los docentes con sus detalles principales."""
        query = """
            SELECT p.*, d.especialidad, u.username, u.activo
            FROM Personas p 
            JOIN Docentes d ON p.id = d.id
            JOIN Usuarios u ON p.id = u.id
            ORDER BY p.apellidos, p.nombres
        """
        rows = self._fetch_all(query)
        return [self._map_row_to_object(row) for row in rows]

    def save(self, docente: Docente):
        """
        Guarda los datos específicos de un docente en la tabla Docentes.
        Asume que la parte de 'Persona' y 'Usuario' ya fue guardada.
        """
        query_check = "SELECT id FROM Docentes WHERE id = ?"
        exists = self._fetch_one(query_check, (docente.id,))

        if exists:
            query = "UPDATE Docentes SET especialidad = ? WHERE id = ?"
            params = (docente.especialidad, docente.id)
        else:
            query = "INSERT INTO Docentes (id, especialidad) VALUES (?, ?)"
            params = (docente.id, docente.especialidad)

        self._execute_and_commit(query, params)

    def delete(self, docente_id):
        """
        Elimina el registro de la tabla Docentes. La eliminación del usuario
        y persona se maneja desde el UsuarioRepository y la BD.
        """
        self._execute_and_commit("DELETE FROM Docentes WHERE id = ?", (docente_id,))

    def count_all(self):
        """Cuenta el número total de docentes."""
        query = "SELECT COUNT(*) FROM Docentes"
        result = self._fetch_one(query)
        return result[0] if result else 0    
