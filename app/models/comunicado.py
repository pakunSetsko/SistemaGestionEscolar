class Comunicado:
    """Modelo de datos para un Comunicado."""
    def __init__(self, titulo, contenido, autor_id, destinatario, id=None, fecha_publicacion=None):
        self.id = id
        self.titulo = titulo
        self.contenido = contenido
        self.autor_id = autor_id
        self.destinatario = destinatario
        self.fecha_publicacion = fecha_publicacion