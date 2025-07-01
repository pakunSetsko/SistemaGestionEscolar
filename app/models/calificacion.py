class Calificacion:
    """Modelo de datos para una Calificación."""
    def __init__(self, estudiante_id, curso_id, periodo_id, bimestre, valor, id=None, comentario=None):
        self.id = id
        self.estudiante_id = estudiante_id
        self.curso_id = curso_id
        self.periodo_id = periodo_id
        self.bimestre = bimestre
        self.valor = valor
        self.comentario = comentario