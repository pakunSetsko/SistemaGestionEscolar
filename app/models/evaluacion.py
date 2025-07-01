class PreguntaEvaluacion:
    """Modelo de datos para una Pregunta de Evaluación Docente."""
    def __init__(self, texto_pregunta, tipo_pregunta='escala_1_5', activa=True, id=None):
        self.id = id
        self.texto_pregunta = texto_pregunta
        self.tipo_pregunta = tipo_pregunta
        self.activa = activa

class RespuestaEvaluacion:
    """Modelo de datos para una Respuesta a una pregunta de evaluación."""
    def __init__(self, estudiante_id, docente_id, curso_id, pregunta_id, periodo_id, 
                 respuesta_escala=None, respuesta_texto=None, id=None, fecha_respuesta=None):
        self.id = id
        self.estudiante_id = estudiante_id
        self.docente_id = docente_id
        self.curso_id = curso_id
        self.pregunta_id = pregunta_id
        self.periodo_id = periodo_id
        self.respuesta_escala = respuesta_escala
        self.respuesta_texto = respuesta_texto
        self.fecha_respuesta = fecha_respuesta