# RUTA: app/repositories/padre_repository.py
# Repositorio para las operaciones de las entidades Padre y Estudiante_Apoderado.

from .base_repository import BaseRepository
from app.models.padre import Padre
from app.models.estudiante import Estudiante

class PadreRepository(BaseRepository):
    """
    Repositorio para gestionar apoderados y sus vínculos con estudiantes.
    """
    def _map_row_to_padre(self, row):
        if not row: return None
        return Padre(
            id=row.id,
            nombres=row.nombres,
            apellidos=row.apellidos,
            dni=row.dni,
            correo=row.correo,
            fecha_nacimiento=row.fecha_nacimiento
        )
        
    def find_by_id(self, padre_id):
        """Busca un padre por su ID."""
        query = "SELECT p.* FROM Personas p JOIN Padres f ON p.id = f.id WHERE p.id = ?"
        row = self._fetch_one(query, (padre_id,))
        return self._map_row_to_padre(row)
        
    def get_all(self):
        """Obtiene todos los apoderados registrados."""
        query = "SELECT p.* FROM Personas p JOIN Padres f ON p.id = f.id ORDER BY p.apellidos, p.nombres"
        rows = self._fetch_all(query)
        return [self._map_row_to_padre(row) for row in rows]
    
    def save(self, padre: Padre):
        """Guarda la entidad Padre, asumiendo que Persona y Usuario ya existen."""
        query_check = "SELECT id FROM Padres WHERE id = ?"
        exists = self._fetch_one(query_check, (padre.id,))
        if not exists:
            self._execute_and_commit("INSERT INTO Padres (id) VALUES (?)", (padre.id,))

    def delete(self, padre_id):
        self._execute_and_commit("DELETE FROM Padres WHERE id = ?", (padre_id,))

    # --- Métodos para la tabla Estudiante_Apoderado ---

    def vincular_estudiante(self, padre_id, estudiante_id, parentesco):
        """Crea un nuevo vínculo familiar en la tabla Estudiante_Apoderado."""
        query = "INSERT INTO Estudiante_Apoderado (padre_id, estudiante_id, parentesco) VALUES (?, ?, ?)"
        try:
            self._execute_and_commit(query, (padre_id, estudiante_id, parentesco))
        except Exception as e:
            # Captura el error de la restricción UNIQUE para dar un mensaje claro.
            if 'UQ_Parentesco' in str(e):
                raise ValueError("Este vínculo familiar ya ha sido registrado.")
            raise e

    def desvincular_estudiante(self, padre_id, estudiante_id):
        """Elimina un vínculo específico entre un padre y un estudiante."""
        query = "DELETE FROM Estudiante_Apoderado WHERE padre_id = ? AND estudiante_id = ?"
        self._execute_and_commit(query, (padre_id, estudiante_id))

    def get_hijos_by_padre_id(self, padre_id):
        """Obtiene la lista de todos los estudiantes (hijos) vinculados a un padre específico."""
        query = """
            SELECT p.id, p.nombres, p.apellidos, g.nombre as grado_nombre, s.nombre as seccion_nombre
            FROM Personas p
            JOIN Estudiantes e ON p.id = e.id
            JOIN Estudiante_Apoderado ea ON e.id = ea.estudiante_id
            JOIN Grados g ON e.grado_id = g.id
            JOIN Secciones s ON e.seccion_id = s.id
            WHERE ea.padre_id = ?
            ORDER BY p.fecha_nacimiento
        """
        rows = self._fetch_all(query, (padre_id,))
        # Devuelve una lista de diccionarios para un uso fácil en la plantilla
        return [dict(zip([column[0] for column in row.cursor_description], row)) for row in rows]

    def get_all_vinculos(self):
        """Recupera todos los vínculos familiares registrados en el sistema."""
        query = """
            SELECT 
                ea.padre_id, ea.estudiante_id,
                (p_padre.nombres + ' ' + p_padre.apellidos) as nombre_padre,
                (p_est.nombres + ' ' + p_est.apellidos) as nombre_estudiante,
                ea.parentesco
            FROM Estudiante_Apoderado ea
            JOIN Personas p_padre ON ea.padre_id = p_padre.id
            JOIN Personas p_est ON ea.estudiante_id = p_est.id
            ORDER BY nombre_padre, nombre_estudiante
        """
        rows = self._fetch_all(query)
        return [dict(zip([column[0] for column in row.cursor_description], row)) for row in rows]

