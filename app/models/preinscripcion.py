class Preinscripcion:
    """Modelo de datos para una solicitud de Preinscripción."""
    def __init__(self, nombres_aspirante, apellidos_aspirante, dni_aspirante, 
                 fecha_nacimiento_aspirante, grado_id_solicitado, nombre_apoderado, 
                 dni_apoderado, correo_apoderado, telefono_apoderado, 
                 id=None, estado='pendiente', fecha_preinscripcion=None):
        self.id = id
        self.nombres_aspirante = nombres_aspirante
        self.apellidos_aspirante = apellidos_aspirante
        self.dni_aspirante = dni_aspirante
        self.fecha_nacimiento_aspirante = fecha_nacimiento_aspirante
        self.grado_id_solicitado = grado_id_solicitado
        self.nombre_apoderado = nombre_apoderado
        self.dni_apoderado = dni_apoderado
        self.correo_apoderado = correo_apoderado
        self.telefono_apoderado = telefono_apoderado
        self.estado = estado
        self.fecha_preinscripcion = fecha_preinscripcion
        self.grado_nombre = None