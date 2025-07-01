# RUTA: app/models/usuario.py
# Define la estructura del objeto Usuario.

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Usuario(UserMixin):
    """
    Representa un usuario en el sistema. Hereda de UserMixin de Flask-Login
    para integrarse con el sistema de autenticación.
    Este es un modelo de datos, no contiene lógica de base de datos.
    """
    def __init__(self, username, rol, password_hash=None, id=None, activo=True):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.rol = rol
        self.activo = activo

    def set_password(self, password):
        """Genera un hash seguro para la contraseña."""
        self.password_hash = generate_password_hash(password, method='scrypt')

    def check_password(self, password):
        """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
        if self.password_hash:
            return check_password_hash(self.password_hash.strip(), password)
        return False
