# RUTA: app/forms/auth_forms.py
# Define los formularios para la autenticación de usuarios.

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length

class LoginForm(FlaskForm):
    """Formulario para el inicio de sesión de usuarios."""
    username = StringField(
        'Nombre de Usuario',
        validators=[DataRequired(message="El nombre de usuario es obligatorio.")]
    )
    password = PasswordField(
        'Contraseña',
        validators=[DataRequired(message="La contraseña es obligatoria.")]
    )
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Entrar')


class ChangePasswordForm(FlaskForm):
    """Formulario para que un usuario cambie su propia contraseña."""
    old_password = PasswordField(
        'Contraseña Actual',
        validators=[DataRequired(message="La contraseña actual es obligatoria.")]
    )
    new_password = PasswordField(
        'Nueva Contraseña',
        validators=[
            DataRequired(message="La nueva contraseña es obligatoria."),
            Length(min=8, message="La nueva contraseña debe tener al menos 8 caracteres.")
        ]
    )
    confirm_password = PasswordField(
        'Confirmar Nueva Contraseña',
        validators=[
            DataRequired(message="Por favor, confirme la nueva contraseña."),
            EqualTo('new_password', message='Las contraseñas no coinciden.')
        ]
    )
    submit = SubmitField('Actualizar Contraseña')
