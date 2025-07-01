# RUTA: app/routes/padre_routes.py
# Define las rutas para el panel de Padre de Familia.

from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_required, current_user
from functools import wraps

# Repositorios y Servicios
from app.repositories.padre_repository import PadreRepository
from app.services.boleta_service import BoletaService
from app.repositories.pago_repository import PagoRepository

# --- Blueprint, Decorador y Instancias ---
padre_bp = Blueprint('padre', __name__, url_prefix='/padre')

def padre_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.rol != 'padre_familia':
            flash('Acceso no autorizado.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Instancias
padre_repo = PadreRepository()
boleta_service = BoletaService()
pago_repo = PagoRepository()

# --- Rutas ---

@padre_bp.route('/dashboard')
@padre_required
def dashboard():
    """Muestra el panel del padre con la lista de sus hijos vinculados."""
    try:
        hijos = padre_repo.get_hijos_by_padre_id(current_user.id)
    except Exception as e:
        flash(f"Error al cargar la información de sus hijos: {e}", "danger")
        hijos = []
    return render_template('padre/dashboard.html', hijos=hijos)

@padre_bp.route('/hijo/<int:hijo_id>')
@padre_required
def ver_hijo(hijo_id):
    """Muestra un panel detallado con la información de un hijo específico."""
    periodo_activo = session.get('periodo_activo')
    if not periodo_activo:
        flash('No hay un periodo académico activo para mostrar información.', 'warning')
        return redirect(url_for('padre.dashboard'))

    try:
        # Validar que el estudiante sea hijo del padre actual (seguridad)
        hijos_ids = [h['id'] for h in padre_repo.get_hijos_by_padre_id(current_user.id)]
        if hijo_id not in hijos_ids:
            flash('No tiene permiso para ver la información de este estudiante.', 'danger')
            return redirect(url_for('padre.dashboard'))

        # El servicio empaqueta todos los datos académicos en un solo diccionario
        datos_boleta = boleta_service.generar_datos_boleta(hijo_id, periodo_activo['id'])
        # Los datos financieros se obtienen por separado
        deudas = pago_repo.get_deudas_by_estudiante(hijo_id)
        
    except Exception as e:
        flash(f'Error al cargar el detalle del estudiante: {e}', 'danger')
        return redirect(url_for('padre.dashboard'))

    return render_template('padre/vista_hijo.html', 
                           datos_boleta=datos_boleta, 
                           deudas=deudas)
