# RUTA: app/repositories/preinscripcion_repository.py
# Repositorio para las operaciones de la entidad Preinscripcion.

from .base_repository import BaseRepository
from app.models.preinscripcion import Preinscripcion

class PreinscripcionRepository(BaseRepository):
    """
    Repositorio que encapsula el acceso a datos para la tabla Preinscripciones.
    """
    def _map_row_to_object(self, row):
        if not row: return None
        preinscripcion = Preinscripcion(
            id=row.id,
            nombres_aspirante=row.nombres_aspirante,
            apellidos_aspirante=row.apellidos_aspirante,
            dni_aspirante=row.dni_aspirante,
            fecha_nacimiento_aspirante=row.fecha_nacimiento_aspirante,
            grado_id_solicitado=row.grado_id_solicitado,
            nombre_apoderado=row.nombre_apoderado,
            dni_apoderado=row.dni_apoderado,
            correo_apoderado=row.correo_apoderado,
            telefono_apoderado=row.telefono_apoderado,
            estado=row.estado,
            fecha_preinscripcion=row.fecha_preinscripcion
        )
        if 'grado_nombre' in [desc[0] for desc in row.cursor_description]:
            preinscripcion.grado_nombre = row.grado_nombre
        return preinscripcion

    def find_by_id(self, preinscripcion_id):
        query = "SELECT pr.*, g.nombre as grado_nombre FROM Preinscripciones pr JOIN Grados g ON pr.grado_id_solicitado = g.id WHERE pr.id = ?"
        row = self._fetch_one(query, (preinscripcion_id,))
        return self._map_row_to_object(row)
    
    def find_by_dni(self, dni):
        query = "SELECT * FROM Preinscripciones WHERE dni_aspirante = ?"
        row = self._fetch_one(query, (dni,))
        return self._map_row_to_object(row)

    def get_all(self):
        query = "SELECT pr.*, g.nombre as grado_nombre FROM Preinscripciones pr JOIN Grados g ON pr.grado_id_solicitado = g.id ORDER BY pr.fecha_preinscripcion DESC"
        rows = self._fetch_all(query)
        return [self._map_row_to_object(row) for row in rows]

    def get_latest(self, limit=5):
        """Obtiene las últimas 'limit' preinscripciones registradas."""
        query = "SELECT TOP (?) pr.*, g.nombre as grado_nombre FROM Preinscripciones pr JOIN Grados g ON pr.grado_id_solicitado = g.id ORDER BY pr.fecha_preinscripcion DESC"
        rows = self._fetch_all(query, (limit,))
        return [self._map_row_to_object(row) for row in rows]

    def save(self, pre: Preinscripcion):
        """Guarda una nueva preinscripción, validando que el DNI no esté duplicado."""
        if self.find_by_dni(pre.dni_aspirante):
            raise ValueError("Ya existe una preinscripción con este DNI de aspirante.")

        query = """
            INSERT INTO Preinscripciones 
            (nombres_aspirante, apellidos_aspirante, dni_aspirante, fecha_nacimiento_aspirante, 
            grado_id_solicitado, nombre_apoderado, dni_apoderado, correo_apoderado, telefono_apoderado) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            pre.nombres_aspirante, pre.apellidos_aspirante, pre.dni_aspirante,
            pre.fecha_nacimiento_aspirante, pre.grado_id_solicitado, pre.nombre_apoderado,
            pre.dni_apoderado, pre.correo_apoderado, pre.telefono_apoderado
        )
        self._execute_and_commit(query, params)

    def update_status(self, preinscripcion_id, estado):
        """Actualiza el estado de una preinscripción (pendiente, aprobado, rechazado)."""
        query = "UPDATE Preinscripciones SET estado = ? WHERE id = ?"
        self._execute_and_commit(query, (estado, preinscripcion_id))
        
    def delete(self, preinscripcion_id):
        self._execute_and_commit("DELETE FROM Preinscripciones WHERE id = ?", (preinscripcion_id,))

