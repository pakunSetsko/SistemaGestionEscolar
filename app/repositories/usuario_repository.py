# RUTA: app/repositories/usuario_repository.py
# Repositorio para gestionar las operaciones CRUD de la entidad Usuario.

from .base_repository import BaseRepository
from app.models.usuario import Usuario

class UsuarioRepository(BaseRepository):
    """
    Repositorio para el modelo Usuario. Encapsula todo el acceso a datos para Usuarios.
    """

    def _map_row_to_object(self, row):
        """Mapea una fila de la base de datos a un objeto Usuario."""
        if row:
            return Usuario(
                id=row.id,
                username=row.username,
                password_hash=row.password_hash,
                rol=row.rol,
                activo=row.activo
            )
        return None

    def find_by_id(self, user_id):
        query = "SELECT * FROM Usuarios WHERE id = ?"
        row = self._fetch_one(query, (user_id,))
        return self._map_row_to_object(row)

    def find_by_username(self, username):
        query = "SELECT * FROM Usuarios WHERE username = ?"
        row = self._fetch_one(query, (username,))
        return self._map_row_to_object(row)

    def get_all(self):
        query = "SELECT * FROM Usuarios ORDER BY username"
        rows = self._fetch_all(query)
        return [self._map_row_to_object(row) for row in rows]

    def save(self, user: Usuario):
        """
        Guarda (crea o actualiza) un usuario. Devuelve el ID del usuario.
        """
        if user.id:
            # Actualizar usuario existente
            query = "UPDATE Usuarios SET username = ?, rol = ?, activo = ? WHERE id = ?"
            params = (user.username, user.rol, user.activo, user.id)
            self._execute_and_commit(query, params)
        else:
            # Insertar nuevo usuario y obtener el ID generado
            query = "INSERT INTO Usuarios (username, password_hash, rol, activo) OUTPUT INSERTED.id VALUES (?, ?, ?, ?)"
            params = (user.username, user.password_hash, user.rol, user.activo)
            cursor = self._execute_and_commit(query, params)
            user.id = cursor.fetchone()[0]
        return user.id
    
    def update_password(self, user_id, new_password_hash):
        """Actualiza únicamente la contraseña de un usuario."""
        query = "UPDATE Usuarios SET password_hash = ? WHERE id = ?"
        self._execute_and_commit(query, (new_password_hash, user_id))

    def delete(self, user_id):
        """
        Elimina un usuario. La restricción 'ON DELETE CASCADE' en la BD
        se encargará de eliminar los registros relacionados en la tabla Personas.
        """
        query = "DELETE FROM Usuarios WHERE id = ?"
        self._execute_and_commit(query, (user_id,))
