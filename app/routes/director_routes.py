# RUTA: app/routes/director_routes.py
# Define las rutas para el panel de Director.

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
from functools import wraps

# Formularios
from app.forms.director_forms import ComunicadoForm, PreguntaEvaluacionForm, ConceptoPagoForm, AsignarDeudaForm, RegistrarPagoForm

# Repositorios y Servicios
from app.repositories.preinscripcion_repository import PreinscripcionRepository
from app.repositories.comunicado_repository import ComunicadoRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.pago_repository import PagoRepository
from app.repositories.grado_repository import GradoRepository
from app.services.matricula_service import MatriculaService
from app.services.report_service import ReportService
from app.services.dashboard_service import DashboardService

# --- Blueprint, Decorador y Instancias ---
director_bp = Blueprint('director', __name__, url_prefix='/director')

def director_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.rol != 'director':
            flash('Acceso no autorizado. Se requiere rol de Director.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Instancias
preinscripcion_repo = PreinscripcionRepository()
comunicado_repo = ComunicadoRepository()
evaluacion_repo = EvaluacionRepository()
pago_repo = PagoRepository()
grado_repo = GradoRepository()
matricula_service = MatriculaService()
report_service = ReportService()
dashboard_service = DashboardService()

# --- Rutas de Vistas ---

@director_bp.route('/dashboard')
@director_required
def dashboard():
    periodo_activo = session.get('periodo_activo')
    if not periodo_activo:
        flash("No hay un periodo académico activo. Algunas estadísticas pueden no estar disponibles.", "warning")
        return render_template('director/dashboard.html', data=dashboard_service.get_default_data())
    
    try:
        dashboard_data = dashboard_service.get_director_dashboard_data(periodo_activo['id'])
    except Exception as e:
        flash(f"Error al cargar datos del dashboard: {e}", "danger")
        dashboard_data = dashboard_service.get_default_data()
        
    return render_template('director/dashboard.html', data=dashboard_data)

@director_bp.route('/preinscripciones')
@director_required
def gestionar_preinscripciones():
    solicitudes = preinscripcion_repo.get_all()
    return render_template('director/gestionar_preinscripciones.html', solicitudes=solicitudes)

@director_bp.route('/comunicados', methods=['GET', 'POST'])
@director_required
def gestionar_comunicados():
    form = ComunicadoForm()
    if form.validate_on_submit():
        try:
            comunicado = comunicado_repo.model(
                titulo=form.titulo.data,
                contenido=form.contenido.data,
                destinatario=form.destinatario.data,
                autor_id=current_user.id
            )
            comunicado_repo.save(comunicado)
            flash('Comunicado publicado exitosamente.', 'success')
        except Exception as e:
            flash(f'Error al publicar el comunicado: {e}', 'danger')
        return redirect(url_for('director.gestionar_comunicados'))
    
    comunicados = comunicado_repo.get_all()
    return render_template('director/gestionar_comunicados.html', comunicados=comunicados, form=form)

@director_bp.route('/evaluacion/preguntas', methods=['GET', 'POST'])
@director_required
def gestionar_preguntas_evaluacion():
    form = PreguntaEvaluacionForm()
    if form.validate_on_submit():
        try:
            pregunta = evaluacion_repo.pregunta_model(
                texto_pregunta=form.texto_pregunta.data,
                tipo_pregunta=form.tipo_pregunta.data
            )
            evaluacion_repo.save_pregunta(pregunta)
            flash('Pregunta creada exitosamente.', 'success')
        except Exception as e:
            flash(f'Error al crear la pregunta: {e}', 'danger')
        return redirect(url_for('director.gestionar_preguntas_evaluacion'))
        
    preguntas = evaluacion_repo.get_all_preguntas()
    return render_template('director/gestionar_preguntas_evaluacion.html', preguntas=preguntas, form=form)

@director_bp.route('/finanzas', methods=['GET', 'POST'])
@director_required
def gestion_financiera():
    periodo_activo = session.get('periodo_activo')
    if not periodo_activo:
        flash("Debe haber un periodo académico activo para gestionar finanzas.", "warning")
        return redirect(url_for('director.dashboard'))

    # Instanciar todos los formularios necesarios para la página
    form_concepto = ConceptoPagoForm()
    form_deuda = AsignarDeudaForm()
    form_pago = RegistrarPagoForm()

    # Poblar choices de los selects
    conceptos = pago_repo.get_conceptos_by_periodo(periodo_activo['id'])
    grados = grado_repo.get_all()
    form_deuda.concepto_id.choices = [(c.id, f"{c.nombre} (S/. {c.monto_sugerido:.2f})") for c in conceptos]
    form_deuda.grado_id.choices = [(g.id, g.nombre) for g in grados]
    
    deudas = pago_repo.get_all_deudas_with_details()
    
    return render_template('director/gestion_financiera.html', 
                           deudas=deudas, conceptos=conceptos, grados=grados,
                           form_concepto=form_concepto, form_deuda=form_deuda, form_pago=form_pago)

@director_bp.route('/reporte/academico')
@director_required
def reporte_academico():
    try:
        datos_reporte = report_service.generar_reporte_academico_general()
    except Exception as e:
        flash(f"Error al generar el reporte académico: {e}", "danger")
        datos_reporte = []
    return render_template('director/reporte_academico.html', reporte=datos_reporte)
    
@director_bp.route('/reporte/evaluacion')
@director_required
def resultados_evaluacion():
    periodo_activo = session.get('periodo_activo')
    if not periodo_activo:
        flash("No hay un periodo académico activo para ver resultados.", "warning")
        return redirect(url_for('director.dashboard'))

    try:
        reporte = report_service.generar_reporte_evaluacion_docente(periodo_activo['id'])
    except Exception as e:
        flash(f"Error al generar el reporte de evaluación: {e}", "danger")
        reporte = []
    return render_template('director/resultados_evaluacion.html', reporte=reporte)

# --- Rutas de Procesamiento POST ---

@director_bp.route('/preinscripcion/<int:preinscripcion_id>/procesar', methods=['POST'])
@director_required
def procesar_preinscripcion(preinscripcion_id):
    estado = request.form.get('estado')
    try:
        if estado == 'aprobado':
            username, temp_password = matricula_service.aprobar_y_matricular_estudiante(preinscripcion_id)
            flash(f"Estudiante matriculado. Usuario: '{username}', Contraseña Temporal: '{temp_password}'.", "success")
        elif estado == 'rechazado':
            matricula_service.preinscripcion_repo.update_status(preinscripcion_id, 'rechazado')
            flash(f"La solicitud {preinscripcion_id} ha sido marcada como 'rechazada'.", "info")
    except ValueError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Error inesperado al procesar la solicitud: {e}", "danger")
    return redirect(url_for('director.gestionar_preinscripciones'))

@director_bp.route('/evaluacion/pregunta/<int:pregunta_id>/eliminar', methods=['POST'])
@director_required
def eliminar_pregunta_evaluacion(pregunta_id):
    try:
        evaluacion_repo.delete_pregunta(pregunta_id)
        flash('Pregunta eliminada correctamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar la pregunta: {e}', 'danger')
    return redirect(url_for('director.gestionar_preguntas_evaluacion'))

@director_bp.route('/comunicado/<int:comunicado_id>/eliminar', methods=['POST'])
@director_required
def eliminar_comunicado(comunicado_id):
    comunicado = comunicado_repo.find_by_id(comunicado_id)
    if comunicado and comunicado.autor_id == current_user.id:
        try:
            comunicado_repo.delete(comunicado_id)
            flash('Comunicado eliminado.', 'success')
        except Exception as e:
            flash(f'Error al eliminar: {e}', 'danger')
    else:
        flash('No tiene permisos para eliminar este comunicado.', 'danger')
    return redirect(url_for('director.gestionar_comunicados'))

# --- Rutas de Finanzas POST ---

@director_bp.route('/finanzas/concepto', methods=['POST'])
@director_required
def crear_concepto_pago():
    form = ConceptoPagoForm()
    if form.validate_on_submit():
        periodo_activo = session.get('periodo_activo')
        if periodo_activo:
            concepto = pago_repo.concepto_model(
                nombre=form.nombre.data,
                monto_sugerido=form.monto_sugerido.data,
                periodo_id=periodo_activo['id']
            )
            pago_repo.save_concepto(concepto)
            flash("Concepto de pago creado exitosamente.", "success")
        else:
            flash("No hay un periodo activo para asociar el concepto.", "danger")
    return redirect(url_for('director.gestion_financiera'))

@director_bp.route('/finanzas/deuda-masiva', methods=['POST'])
@director_required
def asignar_deuda_masiva():
    form = AsignarDeudaForm()
    # Repopular choices en caso de error
    conceptos = pago_repo.get_conceptos_by_periodo(session.get('periodo_activo')['id'])
    grados = grado_repo.get_all()
    form.concepto_id.choices = [(c.id, f"{c.nombre} (S/. {c.monto_sugerido:.2f})") for c in conceptos]
    form.grado_id.choices = [(g.id, g.nombre) for g in grados]

    if form.validate_on_submit():
        try:
            num_asignados = pago_repo.asignar_deuda_masiva(
                form.grado_id.data,
                form.concepto_id.data,
                form.monto.data,
                form.fecha_vencimiento.data
            )
            flash(f"Deuda asignada a {num_asignados} estudiante(s) del grado seleccionado.", "success")
        except Exception as e:
            flash(f"Error al asignar la deuda: {e}", "danger")
    return redirect(url_for('director.gestion_financiera'))
    
@director_bp.route('/finanzas/registrar-pago', methods=['POST'])
@director_required
def registrar_pago():
    form = RegistrarPagoForm()
    if form.validate_on_submit():
        pago = pago_repo.pago_model(
            deuda_id=form.deuda_id.data,
            monto_pagado=form.monto_pagado.data,
            metodo_pago=form.metodo_pago.data,
            observaciones=form.observaciones.data,
            registrado_por_id=current_user.id
        )
        pago_repo.registrar_pago(pago)
        flash("Pago registrado exitosamente.", "success")
    else:
        flash("Error en el formulario de registro de pago.", "danger")
    return redirect(url_for('director.gestion_financiera'))

