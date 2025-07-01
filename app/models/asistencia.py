class Asistencia:
    """Modelo de datos para un registro de Asistencia."""
    def __init__(self, estudiante_id, curso_id, periodo_id, fecha, estado, id=None):
        self.id = id
        self.estudiante_id = estudiante_id
        self.curso_id = curso_id
        self.periodo_id = periodo_id
        self.fecha = fecha
        self.estado = estado