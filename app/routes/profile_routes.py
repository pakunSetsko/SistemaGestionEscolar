# RUTA: app/routes/profile_routes.py
# Define las rutas para la gestión del perfil del usuario logueado.

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app.forms.auth_forms import ChangePasswordForm
from app.services.profile_service import ProfileService

profile_bp = Blueprint('profile', __name__, url_prefix='/perfil')
profile_service = ProfileService()

@profile_bp.route('/')
@login_required
def view():
    """Muestra la página de perfil del usuario actual."""
    form = ChangePasswordForm()
    try:
        # El servicio obtiene los detalles adicionales (ej. de la tabla Personas).
        details = profile_service.get_user_profile_details(current_user)
    except Exception as e:
        flash(f"Error al cargar los datos del perfil: {e}", "danger")
        details = current_user
    return render_template('profile/view.html', details=details, form=form)

@profile_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Procesa la solicitud de cambio de contraseña."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        try:
            # El servicio se encarga de toda la lógica de validación y actualización.
            profile_service.change_user_password(
                user=current_user,
                old_password=form.old_password.data,
                new_password=form.new_password.data
            )
            flash("Contraseña actualizada exitosamente.", "success")
        except ValueError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Ocurrió un error inesperado: {e}", "danger")
    else:
        # Si el formulario no es válido, mostrar los errores.
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en el campo '{getattr(form, field).label.text}': {error}", 'danger')

    return redirect(url_for('profile.view'))
