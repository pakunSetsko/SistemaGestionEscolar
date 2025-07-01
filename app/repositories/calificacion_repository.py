
from .base_repository import BaseRepository
from collections import defaultdict

class CalificacionRepository(BaseRepository):
    def save_multiple(self, calificaciones_data):
        """Guarda o actualiza una lista de calificaciones usando MERGE."""
        if not calificaciones_data:
            return
        
        merge_sql = """
        MERGE Calificaciones AS target
        USING (VALUES (?, ?, ?, ?, ?, ?)) AS source (estudiante_id, curso_id, periodo_id, bimestre, valor, comentario)
        ON target.estudiante_id = source.estudiante_id AND target.curso_id = source.curso_id AND target.periodo_id = source.periodo_id AND target.bimestre = source.bimestre
        WHEN MATCHED THEN
            UPDATE SET valor = source.valor, comentario = source.comentario
        WHEN NOT MATCHED THEN
            INSERT (estudiante_id, curso_id, periodo_id, bimestre, valor, comentario) 
            VALUES (source.estudiante_id, source.curso_id, source.periodo_id, source.bimestre, source.valor, source.comentario);
        """
        # Se debe ejecutar una consulta por cada calificación en este caso con pyodbc
        for calif in calificaciones_data:
            self._execute_and_commit(merge_sql, tuple(calif.values()))

    def get_by_student_and_curso(self, estudiante_id, curso_id, periodo_id):
        """Obtiene las calificaciones de un estudiante en un curso, organizadas por bimestre."""
        query = "SELECT bimestre, valor, comentario FROM Calificaciones WHERE estudiante_id = ? AND curso_id = ? AND periodo_id = ?"
        rows = self._fetch_all(query, (estudiante_id, curso_id, periodo_id))
        
        calificaciones = defaultdict(lambda: {'valor': None, 'comentario': None})
        for row in rows:
            calificaciones[row.bimestre] = {'valor': row.valor, 'comentario': row.comentario}
        return calificaciones
    
    # Implementación de métodos abstractos no requerida para este repositorio
    def find_by_id(self, entity_id): pass
    def get_all(self): pass
    def save(self, entity): pass
    def delete(self, entity_id): pass