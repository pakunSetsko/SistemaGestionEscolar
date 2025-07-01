# RUTA: app/services/auth_service.py
# Contiene la lógica de negocio para la autenticación de usuarios.

from app.repositories.usuario_repository import UsuarioRepository
from app.models.usuario import Usuario

class AuthService:
    """
    Servicio para manejar la lógica de autenticación. Su única responsabilidad
    es validar las credenciales de un usuario para iniciar sesión.
    """
    def __init__(self):
        """Inicializa el servicio con una instancia del repositorio de usuarios."""
        self.usuario_repo = UsuarioRepository()

    def authenticate_user(self, username, password):
        """
        Autentica a un usuario basado en su nombre de usuario y contraseña.
        
        Args:
            username (str): El nombre de usuario.
            password (str): La contraseña en texto plano.
            
        Returns:
            Usuario: El objeto de usuario si la autenticación es exitosa.
            
        Raises:
            ValueError: Si las credenciales son incorrectas o el usuario está inactivo,
                        lanzando un mensaje de error específico.
        """
        user = self.usuario_repo.find_by_username(username)

        # Se usa una comparación genérica para no revelar si el usuario o la contraseña es lo que falló.
        if not user or not user.check_password(password):
            raise ValueError("Usuario o contraseña incorrectos.")

        if not user.activo:
            raise ValueError("Esta cuenta de usuario ha sido desactivada. Por favor, contacte a administración.")
            
        return user
