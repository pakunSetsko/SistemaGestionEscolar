# RUTA: app/repositories/evaluacion_repository.py
# Repositorio para gestionar preguntas y respuestas de evaluación docente.

from .base_repository import BaseRepository
from app.models.evaluacion import PreguntaEvaluacion, RespuestaEvaluacion

class EvaluacionRepository(BaseRepository):
    """
    Repositorio para las tablas PreguntasEvaluacionDocente y RespuestasEvaluacionDocente.
    """
    # --- Métodos para Preguntas ---

    def get_all_preguntas(self, activa_only=False):
        """
        Obtiene todas las preguntas de la evaluación.
        Si 'activa_only' es True, devuelve solo las preguntas marcadas como activas.
        """
        query = "SELECT * FROM PreguntasEvaluacionDocente"
        if activa_only:
            query += " WHERE activa = 1"
        query += " ORDER BY id"
        
        rows = self._fetch_all(query)
        return [
            PreguntaEvaluacion(id=r.id, texto_pregunta=r.texto_pregunta, tipo_pregunta=r.tipo_pregunta, activa=r.activa)
            for r in rows
        ]

    def save_pregunta(self, pregunta: PreguntaEvaluacion):
        """Guarda una nueva pregunta o actualiza una existente."""
        if pregunta.id:
            query = "UPDATE PreguntasEvaluacionDocente SET texto_pregunta=?, tipo_pregunta=?, activa=? WHERE id=?"
            params = (pregunta.texto_pregunta, pregunta.tipo_pregunta, pregunta.activa, pregunta.id)
        else:
            query = "INSERT INTO PreguntasEvaluacionDocente (texto_pregunta, tipo_pregunta, activa) VALUES (?, ?, ?)"
            params = (pregunta.texto_pregunta, pregunta.tipo_pregunta, pregunta.activa)
        self._execute_and_commit(query, params)

    def delete_pregunta(self, pregunta_id):
        """Elimina una pregunta por su ID. La BD se encarga de la cascada a las respuestas."""
        self._execute_and_commit("DELETE FROM PreguntasEvaluacionDocente WHERE id = ?", (pregunta_id,))

    # --- Métodos para Respuestas ---
    
    def save_respuesta(self, respuesta: RespuestaEvaluacion):
        """Guarda una nueva respuesta de evaluación."""
        query = """
        INSERT INTO RespuestasEvaluacionDocente 
        (estudiante_id, docente_id, curso_id, pregunta_id, periodo_id, respuesta_escala, respuesta_texto)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            respuesta.estudiante_id, respuesta.docente_id, respuesta.curso_id, 
            respuesta.pregunta_id, respuesta.periodo_id, respuesta.respuesta_escala, 
            respuesta.respuesta_texto
        )
        self._execute_and_commit(query, params)
    
    def has_student_evaluated_teacher(self, estudiante_id, docente_id, curso_id, periodo_id):
        """Verifica si un estudiante ya evaluó a un docente en un curso/periodo."""
        query = "SELECT COUNT(id) FROM RespuestasEvaluacionDocente WHERE estudiante_id=? AND docente_id=? AND curso_id=? AND periodo_id=?"
        count = self._fetch_one(query, (estudiante_id, docente_id, curso_id, periodo_id))[0]
        return count > 0

    def get_respuestas_by_docente(self, docente_id, periodo_id):
        """Obtiene todas las respuestas para un docente en un periodo."""
        query = "SELECT * FROM RespuestasEvaluacionDocente WHERE docente_id = ? AND periodo_id = ?"
        rows = self._fetch_all(query, (docente_id, periodo_id))
        return [
            RespuestaEvaluacion(
                id=r.id, estudiante_id=r.estudiante_id, docente_id=r.docente_id,
                curso_id=r.curso_id, pregunta_id=r.pregunta_id, periodo_id=r.periodo_id,
                respuesta_escala=r.respuesta_escala, respuesta_texto=r.respuesta_texto
            ) for r in rows
        ]

    # Métodos abstractos de BaseRepository no aplicables directamente
    def find_by_id(self, entity_id): pass
    def get_all(self): pass
    def save(self, entity): pass
    def delete(self, entity_id): pass
