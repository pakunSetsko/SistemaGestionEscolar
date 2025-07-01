# RUTA: app/routes/docente_routes.py
# Define las rutas para el panel de Docente.

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

# Repositorios y Servicios
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.curso_repository import CursoRepository
from app.repositories.comunicado_repository import ComunicadoRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.services.docente_service import DocenteService

# --- Blueprint, Decorador y Instancias ---
docente_bp = Blueprint('docente', __name__, url_prefix='/docente')

def docente_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.rol != 'docente':
            flash('Acceso no autorizado. Se requiere rol de Docente.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Instancias
asignacion_repo = AsignacionRepository()
curso_repo = CursoRepository()
comunicado_repo = ComunicadoRepository()
estudiante_repo = EstudianteRepository()
calificacion_repo = CalificacionRepository()
docente_service = DocenteService()

# --- Rutas ---

@docente_bp.route('/dashboard')
@docente_required
def dashboard():
    """Muestra el panel principal del docente con sus cursos asignados y comunicados."""
    periodo_activo = session.get('periodo_activo')
    cursos_asignados = []
    if periodo_activo:
        cursos_asignados = asignacion_repo.get_cursos_by_docente(current_user.id, periodo_activo['id'])
    
    comunicados = comunicado_repo.get_for_role(current_user.rol)
        
    return render_template('docente/dashboard.html', 
                           cursos=cursos_asignados, 
                           comunicados=comunicados)

@docente_bp.route('/curso/<int:curso_id>')
@docente_required
def gestion_curso(curso_id):
    """Muestra la página de gestión para un curso específico (calificaciones y asistencia)."""
    periodo_activo = session.get('periodo_activo')
    if not periodo_activo:
        flash("No hay un periodo académico activo.", "danger")
        return redirect(url_for('docente.dashboard'))

    curso = curso_repo.find_by_id(curso_id)
    if not curso:
        flash("Curso no encontrado.", "danger")
        return redirect(url_for('docente.dashboard'))
    
    # Validar que el docente actual esté asignado a este curso (seguridad)
    cursos_docente_ids = [c['id'] for c in asignacion_repo.get_cursos_by_docente(current_user.id, periodo_activo['id'])]
    if curso_id not in cursos_docente_ids:
        flash('No tiene permiso para acceder a este curso.', 'danger')
        return redirect(url_for('docente.dashboard'))

    estudiantes = estudiante_repo.get_by_grado(curso.grado_id)
    calificaciones = {est.id: calificacion_repo.get_by_student_and_curso(est.id, curso_id, periodo_activo['id']) for est in estudiantes}

    fecha_str = request.args.get('fecha', datetime.today().strftime('%Y-%m-%d'))
    asistencia_del_dia = docente_service.asistencia_repo.get_by_curso_and_fecha(curso_id, fecha_str)

    return render_template('docente/gestion_curso.html', 
                           curso=curso, 
                           estudiantes=estudiantes,
                           calificaciones=calificaciones,
                           asistencia_del_dia=asistencia_del_dia,
                           fecha_seleccionada=fecha_str)

@docente_bp.route('/curso/<int:curso_id>/calificaciones', methods=['POST'])
@docente_required
def guardar_calificaciones(curso_id):
    periodo_id = session.get('periodo_activo')['id']
    try:
        docente_service.guardar_calificaciones_desde_formulario(curso_id, periodo_id, request.form)
        flash("Calificaciones guardadas exitosamente.", "success")
    except Exception as e:
        flash(f"Error al guardar calificaciones: {e}", "danger")
    return redirect(url_for('docente.gestion_curso', curso_id=curso_id))

@docente_bp.route('/curso/<int:curso_id>/asistencia', methods=['POST'])
@docente_required
def guardar_asistencia(curso_id):
    periodo_id = session.get('periodo_activo')['id']
    fecha = request.form.get('fecha')
    curso = curso_repo.find_by_id(curso_id)
    
    try:
        docente_service.guardar_asistencias_desde_formulario(curso_id, periodo_id, fecha, curso.grado_id, request.form)
        flash("Asistencia registrada exitosamente.", "success")
    except Exception as e:
        flash(f"Error al registrar la asistencia: {e}", "danger")
    
    return redirect(url_for('docente.gestion_curso', curso_id=curso_id, fecha=fecha, _anchor='asistencia'))
