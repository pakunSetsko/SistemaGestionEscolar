class Asignacion:
    """Modelo de datos para la asignación de un Docente a un Curso."""
    def __init__(self, docente_id, curso_id, periodo_id, id=None):
        self.id = id
        self.docente_id = docente_id
        self.curso_id = curso_id
        self.periodo_id = periodo_id
