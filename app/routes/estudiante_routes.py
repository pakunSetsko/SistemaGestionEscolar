# RUTA: app/routes/estudiante_routes.py
# Define las rutas para el panel de Estudiante.

from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from flask_login import login_required, current_user
from functools import wraps

# Repositorios y Servicios
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.comunicado_repository import ComunicadoRepository
from app.repositories.pago_repository import PagoRepository
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.services.dashboard_service import DashboardService
from app.services.boleta_service import BoletaService
from app.models.evaluacion import RespuestaEvaluacion

# --- Blueprint, Decorador y Instancias ---
estudiante_bp = Blueprint('estudiante', __name__, url_prefix='/estudiante')

def estudiante_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.rol != 'estudiante':
            flash('Acceso no autorizado.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Instancias
estudiante_repo = EstudianteRepository()
comunicado_repo = ComunicadoRepository()
pago_repo = PagoRepository()
asignacion_repo = AsignacionRepository()
evaluacion_repo = EvaluacionRepository()
dashboard_service = DashboardService()
boleta_service = BoletaService()

# --- Rutas ---

@estudiante_bp.route('/dashboard')
@estudiante_required
def dashboard():
    periodo_activo = session.get('periodo_activo')
    if not periodo_activo:
        flash("No hay un periodo académico activo. Consulta con administración.", "warning")
        return render_template('estudiante/dashboard.html', data=None)

    try:
        dashboard_data = dashboard_service.get_estudiante_dashboard_data(current_user.id, periodo_activo['id'])
    except Exception as e:
        flash(f"Error crítico al cargar los datos del panel: {e}", "danger")
        return redirect(url_for('auth.logout'))

    return render_template('estudiante/dashboard.html', data=dashboard_data)

@estudiante_bp.route('/boleta')
@estudiante_required
def ver_boleta():
    periodo_activo = session.get('periodo_activo')
    if not periodo_activo:
        flash("No hay un periodo académico activo para generar la boleta.", "warning")
        return redirect(url_for('estudiante.dashboard'))
    
    try:
        datos_boleta = boleta_service.generar_datos_boleta(current_user.id, periodo_activo['id'])
        return render_template('estudiante/boleta_notas.html', **datos_boleta)
    except Exception as e:
        flash(f"Error al generar la boleta: {e}", "danger")
        return redirect(url_for('estudiante.dashboard'))

@estudiante_bp.route('/estado-de-cuenta')
@estudiante_required
def estado_de_cuenta():
    try:
        deudas = pago_repo.get_deudas_by_estudiante(current_user.id)
    except Exception as e:
        flash(f"Error al cargar tu estado de cuenta: {e}", "danger")
        deudas = []
    return render_template('estudiante/estado_cuenta.html', deudas=deudas)

@estudiante_bp.route('/evaluacion-docente')
@estudiante_required
def evaluacion_docente_lista():
    periodo_activo = session.get('periodo_activo')
    if not periodo_activo:
        flash("La evaluación docente no está activa en este momento.", "warning")
        return redirect(url_for('estudiante.dashboard'))
    
    docentes_a_evaluar = asignacion_repo.get_docentes_by_estudiante(current_user.id, periodo_activo['id'])
    for docente in docentes_a_evaluar:
        docente['evaluado'] = evaluacion_repo.has_student_evaluated_teacher(
            current_user.id, docente['docente_id'], docente['curso_id'], periodo_activo['id']
        )
    return render_template('estudiante/evaluacion_lista_docentes.html', docentes=docentes_a_evaluar)

@estudiante_bp.route('/evaluacion-docente/evaluar/<int:docente_id>/<int:curso_id>', methods=['GET', 'POST'])
@estudiante_required
def realizar_evaluacion(docente_id, curso_id):
    periodo_activo = session.get('periodo_activo')
    if not periodo_activo:
        flash("La evaluación docente no está activa en este momento.", "warning")
        return redirect(url_for('estudiante.evaluacion_docente_lista'))

    if request.method == 'POST':
        try:
            preguntas = evaluacion_repo.get_all_preguntas(activa_only=True)
            for pregunta in preguntas:
                respuesta_form = request.form.get(f'pregunta_{pregunta.id}')
                if respuesta_form:
                    respuesta = RespuestaEvaluacion(
                        estudiante_id=current_user.id, docente_id=docente_id, curso_id=curso_id,
                        pregunta_id=pregunta.id, periodo_id=periodo_activo['id']
                    )
                    if pregunta.tipo_pregunta == 'escala_1_5':
                        respuesta.respuesta_escala = int(respuesta_form)
                    else:
                        respuesta.respuesta_texto = respuesta_form
                    evaluacion_repo.save_respuesta(respuesta)
            flash('Evaluación enviada exitosamente. ¡Gracias por tu participación!', 'success')
            return redirect(url_for('estudiante.evaluacion_docente_lista'))
        except Exception as e:
            flash(f'Ocurrió un error al guardar tu evaluación: {e}', 'danger')
            return redirect(url_for('estudiante.evaluacion_docente_lista'))

    preguntas = evaluacion_repo.get_all_preguntas(activa_only=True)
    return render_template('estudiante/evaluacion_formulario.html', preguntas=preguntas, docente_id=docente_id, curso_id=curso_id)

