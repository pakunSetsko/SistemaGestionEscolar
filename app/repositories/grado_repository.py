# RUTA: app/repositories/grado_repository.py

from .base_repository import BaseRepository
from app.models.grado import Grado

class GradoRepository(BaseRepository):
    def _map_row_to_object(self, row):
        if row:
            return Grado(id=row.id, nombre=row.nombre, nivel=row.nivel)
        return None

    def find_by_id(self, grado_id):
        row = self._fetch_one("SELECT * FROM Grados WHERE id = ?", (grado_id,))
        return self._map_row_to_object(row)

    def get_all(self):
        rows = self._fetch_all("SELECT * FROM Grados ORDER BY nivel, id")
        return [self._map_row_to_object(row) for row in rows]

    def save(self, grado: Grado):
        if grado.id:
            query = "UPDATE Grados SET nombre = ?, nivel = ? WHERE id = ?"
            params = (grado.nombre, grado.nivel, grado.id)
        else:
            query = "INSERT INTO Grados (nombre, nivel) VALUES (?, ?)"
            params = (grado.nombre, grado.nivel)
        self._execute_and_commit(query, params)

    def delete(self, grado_id):
        # La BD tiene ON DELETE CASCADE para Secciones, pero es buena práctica
        # tener validaciones en la capa de servicio para no borrar grados con estudiantes.
        self._execute_and_commit("DELETE FROM Grados WHERE id = ?", (grado_id,))

