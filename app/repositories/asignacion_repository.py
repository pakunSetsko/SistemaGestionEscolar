# RUTA: app/repositories/asignacion_repository.py
# Repositorio para gestionar las asignaciones de docentes a cursos.

from .base_repository import BaseRepository

class AsignacionRepository(BaseRepository):
    """
    Repositorio para las operaciones de la tabla Asignaciones.
    """
    
    def create(self, docente_id, curso_id, periodo_id):
        """Crea una nueva asignación de un docente a un curso para un periodo específico."""
        query = "INSERT INTO Asignaciones (docente_id, curso_id, periodo_id) VALUES (?, ?, ?)"
        try:
            self._execute_and_commit(query, (docente_id, curso_id, periodo_id))
        except Exception as e:
            # Captura el error de la restricción UNIQUE para dar un mensaje claro.
            if 'UQ_Asignacion' in str(e):
                raise ValueError("Esta asignación (docente-curso-periodo) ya existe.")
            raise e

    def get_cursos_by_docente(self, docente_id, periodo_id):
        """Obtiene la lista de cursos que un docente específico enseña en un periodo académico."""
        query = """
            SELECT c.id, c.nombre, g.nombre as grado_nombre
            FROM Asignaciones a
            JOIN Cursos c ON a.curso_id = c.id
            JOIN Grados g ON c.grado_id = g.id
            WHERE a.docente_id = ? AND a.periodo_id = ?
            ORDER BY g.id, c.nombre
        """
        rows = self._fetch_all(query, (docente_id, periodo_id))
        return [dict(zip([column[0] for column in row.cursor_description], row)) for row in rows]

    def get_docente_by_curso(self, curso_id, periodo_id):
        """Encuentra el nombre completo del docente asignado a un curso en un periodo."""
        query = """
            SELECT p.nombres + ' ' + p.apellidos as nombre_completo
            FROM Asignaciones a
            JOIN Personas p ON a.docente_id = p.id
            WHERE a.curso_id = ? AND a.periodo_id = ?
        """
        row = self._fetch_one(query, (curso_id, periodo_id))
        return row.nombre_completo if row else None

    def get_docentes_by_estudiante(self, estudiante_id, periodo_id):
        """
        Obtiene la lista de todos los docentes que un estudiante tiene en un periodo.
        """
        query = """
            SELECT DISTINCT p.id as docente_id, p.nombres, p.apellidos, c.id as curso_id, c.nombre as curso_nombre
            FROM Asignaciones a
            JOIN Cursos c ON a.curso_id = c.id
            JOIN Estudiantes e ON c.grado_id = e.grado_id
            JOIN Personas p ON a.docente_id = p.id
            WHERE e.id = ? AND a.periodo_id = ?
        """
        rows = self._fetch_all(query, (estudiante_id, periodo_id))
        return [dict(zip([column[0] for column in row.cursor_description], row)) for row in rows]

    # Métodos abstractos no aplicables o gestionados de otra forma
    def find_by_id(self, entity_id): pass
    def get_all(self): pass
    def save(self, entity): pass
    def delete(self, entity_id): pass
