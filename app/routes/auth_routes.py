# RUTA: app/routes/auth_routes.py
# Define las rutas para la autenticación de usuarios (login y logout).

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required

from app.forms.auth_forms import LoginForm
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Muestra el formulario de login y procesa el intento de inicio de sesión.
    """
    # Si el usuario ya está autenticado, lo redirige a su dashboard.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            # Llama al servicio de autenticación para validar las credenciales.
            user = auth_service.authenticate_user(form.username.data, form.password.data)
            # Inicia la sesión para el usuario.
            login_user(user, remember=form.remember_me.data)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('main.index'))
        except ValueError as e:
            # Si el servicio lanza un error (ej. credenciales incorrectas), se muestra al usuario.
            flash(str(e), 'danger')
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Cierra la sesión del usuario actual.
    """
    logout_user()
    flash('Has cerrado la sesión de forma segura.', 'info')
    return redirect(url_for('auth.login'))
