# RUTA: app/repositories/estudiante_repository.py
# Repositorio para las operaciones de la entidad Estudiante.

from .base_repository import BaseRepository
from app.models.estudiante import Estudiante
import math

class EstudianteRepository(BaseRepository):
    """
    Repositorio que encapsula el acceso a datos para la tabla Estudiantes
    y sus relaciones con Personas, Grados y Secciones.
    """
    def _map_row_to_object(self, row):
        """Mapea una fila de la BD a un objeto Estudiante, incluyendo detalles de otras tablas."""
        if not row:
            return None
        
        estudiante = Estudiante(
            id=row.id,
            nombres=row.nombres,
            apellidos=row.apellidos,
            dni=row.dni,
            grado_id=row.grado_id,
            seccion_id=row.seccion_id,
            correo=row.correo,
            fecha_nacimiento=row.fecha_nacimiento
        )
        # Añadir datos extra de los JOINs para facilitar su uso
        estudiante.grado_nombre = getattr(row, 'grado_nombre', None)
        estudiante.seccion_nombre = getattr(row, 'seccion_nombre', None)
        
        return estudiante

    def find_by_id(self, estudiante_id):
        """Busca un estudiante por su ID, obteniendo todos sus detalles."""
        query = """
            SELECT p.*, e.grado_id, e.seccion_id, g.nombre as grado_nombre, s.nombre as seccion_nombre
            FROM Personas p 
            JOIN Estudiantes e ON p.id = e.id
            JOIN Grados g ON e.grado_id = g.id
            JOIN Secciones s ON e.seccion_id = s.id
            WHERE p.id = ?
        """
        row = self._fetch_one(query, (estudiante_id,))
        return self._map_row_to_object(row)
    
    def get_all(self):
        """Obtiene una lista de todos los estudiantes con sus detalles principales."""
        query = """
        SELECT p.id, p.nombres, p.apellidos, p.dni, p.correo, p.fecha_nacimiento,
               e.grado_id, e.seccion_id, g.nombre as grado_nombre, s.nombre as seccion_nombre
        FROM Personas p
        JOIN Estudiantes e ON p.id = e.id
        JOIN Grados g ON e.grado_id = g.id
        JOIN Secciones s ON e.seccion_id = s.id
        ORDER BY p.apellidos, p.nombres
        """
        rows = self._fetch_all(query)
        return [self._map_row_to_object(row) for row in rows]

    def get_by_grado(self, grado_id):
        """Obtiene todos los estudiantes que pertenecen a un grado específico."""
        query = "SELECT p.*, e.grado_id, e.seccion_id FROM Personas p JOIN Estudiantes e ON p.id = e.id WHERE e.grado_id = ? ORDER BY p.apellidos, p.nombres"
        rows = self._fetch_all(query, (grado_id,))
        return [self._map_row_to_object(row) for row in rows]
        
    def save(self, estudiante: Estudiante):
        """
        Guarda los datos específicos de un estudiante.
        Asume que la parte de 'Persona' ya fue guardada.
        """
        query_check = "SELECT id FROM Estudiantes WHERE id = ?"
        exists = self._fetch_one(query_check, (estudiante.id,))

        if exists:
            query = "UPDATE Estudiantes SET grado_id = ?, seccion_id = ? WHERE id = ?"
            params = (estudiante.grado_id, estudiante.seccion_id, estudiante.id)
        else:
            query = "INSERT INTO Estudiantes (id, grado_id, seccion_id) VALUES (?, ?, ?)"
            params = (estudiante.id, estudiante.grado_id, estudiante.seccion_id)

        self._execute_and_commit(query, params)

    def delete(self, estudiante_id):
        """
        Elimina el registro de la tabla Estudiantes. La eliminación del usuario
        y persona se maneja desde el UsuarioRepository y la BD.
        """
        query = "DELETE FROM Estudiantes WHERE id = ?"
        self._execute_and_commit(query, (estudiante_id,))

    def get_paginated(self, page=1, per_page=15):
        """Obtiene una lista paginada de estudiantes para las tablas de administración."""
        offset = (page - 1) * per_page
        query = """
        SELECT u.username, p.id, p.nombres, p.apellidos, p.dni, p.correo, 
               g.nombre as grado_nombre, s.nombre as seccion_nombre
        FROM Personas p
        JOIN Estudiantes e ON p.id = e.id
        JOIN Usuarios u ON p.id = u.id
        JOIN Grados g ON e.grado_id = g.id
        JOIN Secciones s ON e.seccion_id = s.id
        ORDER BY p.apellidos, p.nombres
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """
        rows = self._fetch_all(query, (offset, per_page))
        
        total_query = "SELECT COUNT(*) FROM Estudiantes"
        total_estudiantes = self._fetch_one(total_query)[0]
        total_pages = math.ceil(total_estudiantes / per_page) if total_estudiantes > 0 else 1
        
        return rows, page, total_pages
        
    def count_by_grado(self):
        """
        Cuenta el número de estudiantes en cada grado para el gráfico del dashboard.
        """
        query = """
            SELECT g.nombre, COUNT(e.id) as total
            FROM Estudiantes e
            JOIN Grados g ON e.grado_id = g.id
            GROUP BY g.id, g.nombre
            ORDER BY g.id
        """
        rows = self._fetch_all(query)
        return [dict(zip([column[0] for column in row.cursor_description], row)) for row in rows]
    
    def count_all(self):
        """Cuenta el número total de estudiantes."""
        query = "SELECT COUNT(*) FROM Estudiantes"
        # _fetch_one devuelve una tupla, por eso accedemos al primer elemento [0]
        result = self._fetch_one(query)
        return result[0] if result else 0

