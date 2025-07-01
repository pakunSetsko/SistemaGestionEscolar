# RUTA: app/repositories/curso_repository.py
# Repositorio para gestionar las operaciones CRUD de la entidad Curso.

from .base_repository import BaseRepository
from app.models.curso import Curso

class CursoRepository(BaseRepository):
    """
    Repositorio que encapsula el acceso a datos para la tabla Cursos.
    """
    def _map_row_to_object(self, row):
        """Mapea una fila de la base de datos a un objeto Curso."""
        if not row:
            return None
        
        curso = Curso(
            id=row.id,
            nombre=row.nombre,
            area=row.area,
            grado_id=row.grado_id
        )
        # Si la consulta incluye el nombre del grado (por un JOIN), lo añadimos al objeto.
        if 'grado_nombre' in [desc[0] for desc in row.cursor_description]:
            curso.grado_nombre = row.grado_nombre
            
        return curso

    def find_by_id(self, curso_id):
        """Busca un curso por su ID, incluyendo el nombre del grado."""
        query = """
            SELECT c.*, g.nombre as grado_nombre
            FROM Cursos c
            JOIN Grados g ON c.grado_id = g.id
            WHERE c.id = ?
        """
        row = self._fetch_one(query, (curso_id,))
        return self._map_row_to_object(row)

    def get_all(self):
        """Obtiene todos los cursos con el nombre de su grado, ordenados."""
        query = """
            SELECT c.*, g.nombre as grado_nombre
            FROM Cursos c
            JOIN Grados g ON c.grado_id = g.id
            ORDER BY g.id, c.nombre
        """
        rows = self._fetch_all(query)
        return [self._map_row_to_object(row) for row in rows]

    def get_by_grado(self, grado_id):
        """Obtiene todos los cursos que pertenecen a un grado específico."""
        query = "SELECT * FROM Cursos WHERE grado_id = ? ORDER BY nombre"
        rows = self._fetch_all(query, (grado_id,))
        return [self._map_row_to_object(row) for row in rows]

    def save(self, curso: Curso):
        """
        Guarda (crea o actualiza) un curso en la base de datos.
        Respeta la restricción UNIQUE (nombre, grado_id) de la BD.
        """
        # El manejo de errores de violación de unicidad se debe hacer en la capa de servicio/ruta.
        if curso.id:
            # Actualizar curso existente
            query = "UPDATE Cursos SET nombre = ?, area = ?, grado_id = ? WHERE id = ?"
            params = (curso.nombre, curso.area, curso.grado_id, curso.id)
        else:
            # Insertar nuevo curso
            query = "INSERT INTO Cursos (nombre, area, grado_id) VALUES (?, ?, ?)"
            params = (curso.nombre, curso.area, curso.grado_id)
        
        self._execute_and_commit(query, params)

    def delete(self, curso_id):
        """
        Elimina un curso y todos sus datos relacionados en cascada.
        El orden es importante para no violar las restricciones de clave foránea.
        """
        # Se asume que la BD no tiene ON DELETE CASCADE para estas tablas y se hace manualmente.
        # Si la BD SÍ lo tuviera, solo haría falta eliminar de la tabla Cursos.
        
        # Lista de consultas a ejecutar en orden de dependencia inversa.
        queries_to_execute = [
            ("DELETE FROM RespuestasEvaluacionDocente WHERE curso_id = ?", (curso_id,)),
            ("DELETE FROM Calificaciones WHERE curso_id = ?", (curso_id,)),
            ("DELETE FROM Asistencias WHERE curso_id = ?", (curso_id,)),
            ("DELETE FROM Asignaciones WHERE curso_id = ?", (curso_id,)),
            # Finalmente, se elimina el curso principal.
            ("DELETE FROM Cursos WHERE id = ?", (curso_id,))
        ]

        for query, params in queries_to_execute:
            self._execute_and_commit(query, params)

    def count_all(self):
        """Cuenta el número total de cursos."""
        query = "SELECT COUNT(*) FROM Cursos"
        result = self._fetch_one(query)
        return result[0] if result else 0        
