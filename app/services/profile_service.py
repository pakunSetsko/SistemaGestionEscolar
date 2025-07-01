# RUTA: app/services/profile_service.py
# Contiene la lógica de negocio para la gestión del perfil del usuario logueado.

from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.persona_repository import PersonaRepository
from werkzeug.security import check_password_hash

class ProfileService:
    """
    Servicio que encapsula la lógica de negocio para las operaciones
    del perfil de un usuario.
    """
    def __init__(self):
        self.usuario_repo = UsuarioRepository()
        self.persona_repo = PersonaRepository()

    def get_user_profile_details(self, user):
        """
        Recupera los detalles completos de un usuario, incluyendo sus datos
        de la tabla Personas si su rol lo requiere.
        """
        if user.rol in ['estudiante', 'docente', 'director', 'padre_familia']:
            # Busca en la tabla Personas usando el ID del usuario.
            persona_details = self.persona_repo.find_by_id(user.id)
            return persona_details
        
        # Para roles como 'admin', que no tienen una entrada en Personas,
        # se devuelve el objeto de usuario tal como está.
        return user

    def change_user_password(self, user, old_password, new_password):
        """
        Valida y procesa el cambio de contraseña para un usuario.
        """
        user_from_db = self.usuario_repo.find_by_id(user.id)
        
        if not user_from_db:
            raise ValueError("El usuario no fue encontrado en la base de datos.")

        # Verifica si la contraseña antigua es correcta.
        if not user_from_db.check_password(old_password):
            raise ValueError("La contraseña actual es incorrecta.")
            
        # Verifica que la nueva contraseña no sea la misma que la anterior.
        if old_password == new_password:
            raise ValueError("La nueva contraseña no puede ser igual a la anterior.")

        # Genera el nuevo hash y lo guarda a través del repositorio.
        user_from_db.set_password(new_password)
        self.usuario_repo.update_password(user_from_db.id, user_from_db.password_hash)
