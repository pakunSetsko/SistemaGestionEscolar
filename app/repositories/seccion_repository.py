# ---

# RUTA: app/repositories/seccion_repository.py

from .base_repository import BaseRepository
from app.models.seccion import Seccion

class SeccionRepository(BaseRepository):
    def _map_row_to_object(self, row):
        if not row:
            return None
        seccion = Seccion(id=row.id, nombre=row.nombre, grado_id=row.grado_id)
        if 'grado_nombre' in [desc[0] for desc in row.cursor_description]:
            seccion.grado_nombre = row.grado_nombre
        return seccion

    def find_by_id(self, seccion_id):
        row = self._fetch_one("SELECT * FROM Secciones WHERE id = ?", (seccion_id,))
        return self._map_row_to_object(row)

    def get_all(self):
        query = """
            SELECT s.*, g.nombre as grado_nombre 
            FROM Secciones s JOIN Grados g ON s.grado_id = g.id
            ORDER BY g.id, s.nombre
        """
        rows = self._fetch_all(query)
        return [self._map_row_to_object(row) for row in rows]
    
    def get_by_grado(self, grado_id):
        rows = self._fetch_all("SELECT * FROM Secciones WHERE grado_id = ? ORDER BY nombre", (grado_id,))
        return [self._map_row_to_object(row) for row in rows]

    def save(self, seccion: Seccion):
        if seccion.id:
            query = "UPDATE Secciones SET nombre = ?, grado_id = ? WHERE id = ?"
            params = (seccion.nombre, seccion.grado_id, seccion.id)
        else:
            query = "INSERT INTO Secciones (nombre, grado_id) VALUES (?, ?)"
            params = (seccion.nombre, seccion.grado_id)
        self._execute_and_commit(query, params)

    def delete(self, seccion_id):
        self._execute_and_commit("DELETE FROM Secciones WHERE id = ?", (seccion_id,))
