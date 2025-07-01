from .base_repository import BaseRepository
from app.models.comunicado import Comunicado

class ComunicadoRepository(BaseRepository):
    """
    Repositorio que encapsula el acceso a datos para la tabla Comunicados.
    """
    def _map_row_to_object(self, row):
        if not row: return None
        comunicado = Comunicado(
            id=row.id,
            titulo=row.titulo,
            contenido=row.contenido,
            autor_id=row.autor_id,
            destinatario=row.destinatario,
            fecha_publicacion=row.fecha_publicacion
        )
        if 'autor_username' in [desc[0] for desc in row.cursor_description]:
            comunicado.autor_username = row.autor_username
        return comunicado

    def find_by_id(self, comunicado_id):
        query = "SELECT c.*, u.username as autor_username FROM Comunicados c JOIN Usuarios u ON c.autor_id = u.id WHERE c.id = ?"
        row = self._fetch_one(query, (comunicado_id,))
        return self._map_row_to_object(row)
        
    def get_all(self):
        query = "SELECT c.*, u.username as autor_username FROM Comunicados c JOIN Usuarios u ON c.autor_id = u.id ORDER BY c.fecha_publicacion DESC"
        rows = self._fetch_all(query)
        return [self._map_row_to_object(row) for row in rows]
        
    def get_for_role(self, rol):
        """Obtiene los comunicados visibles para un rol específico."""
        destinatarios_visibles = ['todos']
        if rol == 'docente':
            destinatarios_visibles.append('docentes')
        elif rol in ['estudiante', 'padre_familia']:
            destinatarios_visibles.append('estudiantes')
        
        placeholders = ','.join('?' for _ in destinatarios_visibles)
        query = f"SELECT c.*, u.username as autor_username FROM Comunicados c JOIN Usuarios u ON c.autor_id = u.id WHERE c.destinatario IN ({placeholders}) ORDER BY c.fecha_publicacion DESC"
        
        rows = self._fetch_all(query, tuple(destinatarios_visibles))
        return [self._map_row_to_object(row) for row in rows]
        
    def save(self, comunicado: Comunicado):
        if comunicado.id:
            query = "UPDATE Comunicados SET titulo = ?, contenido = ?, destinatario = ? WHERE id = ?"
            params = (comunicado.titulo, comunicado.contenido, comunicado.destinatario, comunicado.id)
        else:
            query = "INSERT INTO Comunicados (titulo, contenido, autor_id, destinatario) VALUES (?, ?, ?, ?)"
            params = (comunicado.titulo, comunicado.contenido, comunicado.autor_id, comunicado.destinatario)
        self._execute_and_commit(query, params)

    def delete(self, comunicado_id):
        self._execute_and_commit("DELETE FROM Comunicados WHERE id = ?", (comunicado_id,))
