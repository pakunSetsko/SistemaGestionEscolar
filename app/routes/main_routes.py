# RUTA: app/routes/main_routes.py
# Define las rutas principales y públicas de la aplicación.

from flask import Blueprint, redirect, url_for, render_template, request, flash
from flask_login import current_user
from datetime import datetime

from app.forms.public_forms import PreinscripcionForm
from app.services.matricula_service import MatriculaService
from app.repositories.grado_repository import GradoRepository

main_bp = Blueprint('main', __name__)
matricula_service = MatriculaService()
grado_repo = GradoRepository()

@main_bp.route('/')
def index():
    """
    Página de inicio. Redirige al usuario a su dashboard correspondiente
    si está autenticado, o al login si no lo está.
    """
    if current_user.is_authenticated:
        role_dashboard_map = {
            'admin': 'admin.dashboard',
            'docente': 'docente.dashboard',
            'estudiante': 'estudiante.dashboard',
            'director': 'director.dashboard',
            'padre_familia': 'padre.dashboard'
        }
        dashboard_route = role_dashboard_map.get(current_user.rol)
        if dashboard_route:
            return redirect(url_for(dashboard_route))
    
    return redirect(url_for('auth.login'))

@main_bp.route('/preinscripcion', methods=['GET', 'POST'])
def preinscripcion_form():
    """
    Muestra y procesa el formulario de preinscripción para nuevos aspirantes.
    """
    form = PreinscripcionForm()
    form.grado_id_solicitado.choices = [(g.id, f"{g.nombre} ({g.nivel})") for g in grado_repo.get_all()]

    if form.validate_on_submit():
        try:
            matricula_service.crear_preinscripcion(form.data)
            flash('¡Preinscripción enviada exitosamente! Nos pondremos en contacto con usted pronto.', 'success')
            return redirect(url_for('main.preinscripcion_form'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Ocurrió un error inesperado al procesar su solicitud: {e}', 'danger')
    
    # --- CORRECCIÓN ---
    # Obtenemos el año actual y se lo pasamos a la plantilla.
    current_year = datetime.now().year
    return render_template('public/preinscripcion_form.html', form=form, current_year=current_year)
