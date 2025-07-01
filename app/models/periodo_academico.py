class PeriodoAcademico:
    """Modelo de datos para un Periodo Académico (año escolar)."""
    def __init__(self, anio, nombre, fecha_inicio, fecha_fin, activo=False, id=None):
        self.id = id
        self.anio = anio
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.activo = activo
