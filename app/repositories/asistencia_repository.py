from collections import Counter
from .base_repository import BaseRepository

class AsistenciaRepository(BaseRepository):
    def save_multiple(self, asistencias_data):
        """Guarda o actualiza una lista de registros de asistencia usando MERGE."""
        if not asistencias_data:
            return

        merge_sql = """
        MERGE Asistencias AS target
        USING (VALUES (?, ?, ?, ?, ?)) AS source (estudiante_id, curso_id, periodo_id, fecha, estado)
        ON target.estudiante_id = source.estudiante_id AND target.curso_id = source.curso_id AND target.fecha = source.fecha
        WHEN MATCHED THEN
            UPDATE SET estado = source.estado
        WHEN NOT MATCHED THEN
            INSERT (estudiante_id, curso_id, periodo_id, fecha, estado) 
            VALUES (source.estudiante_id, source.curso_id, source.periodo_id, source.fecha, source.estado);
        """
        for asis in asistencias_data:
            self._execute_and_commit(merge_sql, tuple(asis.values()))

    def get_by_curso_and_fecha(self, curso_id, fecha):
        """Obtiene la asistencia de un curso en una fecha, retornando un diccionario para acceso rápido."""
        query = "SELECT estudiante_id, estado FROM Asistencias WHERE curso_id = ? AND fecha = ?"
        rows = self._fetch_all(query, (curso_id, fecha))
        return {row.estudiante_id: row.estado for row in rows}

    def get_stats_by_student(self, estudiante_id, periodo_id):
        """Calcula las estadísticas de asistencia para un estudiante en un periodo."""
        query = "SELECT estado FROM Asistencias WHERE estudiante_id = ? AND periodo_id = ?"
        rows = self._fetch_all(query, (estudiante_id, periodo_id))
        estados = [row.estado for row in rows]
        
        stats = Counter(estados)
        return {
            'Presente': stats.get('Presente', 0),
            'Tardanza': stats.get('Tardanza', 0),
            'Falta': stats.get('Falta', 0)
        }
    
    # Métodos abstractos no aplicables
    def find_by_id(self, entity_id): pass
    def get_all(self): pass
    def save(self, entity): pass
    def delete(self, entity_id): pass
