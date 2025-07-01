# RUTA: app/repositories/periodo_repository.py
# Repositorio para gestionar las operaciones de la entidad PeriodoAcademico.

from .base_repository import BaseRepository
from app.models.periodo_academico import PeriodoAcademico

class PeriodoRepository(BaseRepository):
    """
    Repositorio que encapsula el acceso a datos para la tabla PeriodosAcademicos.
    """
    def _map_row_to_object(self, row):
        """Mapea una fila de la base de datos a un objeto PeriodoAcademico."""
        if row:
            return PeriodoAcademico(
                id=row.id,
                anio=row.anio,
                nombre=row.nombre,
                fecha_inicio=row.fecha_inicio,
                fecha_fin=row.fecha_fin,
                activo=row.activo
            )
        return None

    def find_active(self):
        """Encuentra el único periodo académico activo."""
        query = "SELECT * FROM PeriodosAcademicos WHERE activo = 1"
        row = self._fetch_one(query)
        return self._map_row_to_object(row)

    def find_by_id(self, entity_id):
        # Implementación de los métodos abstractos
        pass

    def get_all(self):
        query = "SELECT * FROM PeriodosAcademicos ORDER BY anio DESC"
        rows = self._fetch_all(query)
        return [self._map_row_to_object(row) for row in rows]

    def save(self, entity):
        pass
    
    def delete(self, entity_id):
        pass
