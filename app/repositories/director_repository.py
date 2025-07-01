# RUTA: app/repositories/director_repository.py
# Repositorio para las operaciones de la entidad Director.

from .base_repository import BaseRepository
from app.models.director import Director

class DirectorRepository(BaseRepository):
    """
    Repositorio que encapsula el acceso a datos para la tabla Directores.
    """
    def save(self, director: Director):
        """
        Guarda la entidad Director. La lógica principal de la persona/usuario
        ya se ha gestionado en sus respectivos repositorios.
        """
        query_check = "SELECT id FROM Directores WHERE id = ?"
        exists = self._fetch_one(query_check, (director.id,))
        if not exists:
            self._execute_and_commit("INSERT INTO Directores (id) VALUES (?)", (director.id,))

    # El resto de los métodos no son típicamente necesarios para este rol,
    # ya que se gestiona a través del usuario y persona.
    def find_by_id(self, entity_id): pass
    def get_all(self): pass
    def delete(self, entity_id): pass
