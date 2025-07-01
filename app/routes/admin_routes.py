# RUTA: app/routes/admin_routes.py
# Define las rutas para el panel de administración.

from app.services.dashboard_service import DashboardService 
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps

# Formularios
from app.forms.admin_forms import (
    GradoForm, SeccionForm, PeriodoAcademicoForm, CursoForm, 
    VincularApoderadoForm, CreateEstudianteForm, CreateDocenteForm
)
# Repositorios (para obtener datos para los formularios)
from app.repositories.docente_repository import DocenteRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.grado_repository import GradoRepository
from app.repositories.seccion_repository import SeccionRepository
from app.repositories.curso_repository import CursoRepository
from app.repositories.padre_repository import PadreRepository
from app.repositories.periodo_repository import PeriodoRepository
from app.repositories.preinscripcion_repository import PreinscripcionRepository



# Servicios (para la lógica de negocio)
from app.services.admin_service import AdminService
from app.models.curso import Curso
from app.models.periodo_academico import PeriodoAcademico
from app.models.grado import Grado
from app.models.seccion import Seccion

# --- Configuración del Blueprint y Decorador de Autorización ---
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorador para verificar que el usuario tenga el rol de 'admin'."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.rol != 'admin':
            flash('Acceso no autorizado. Se requiere rol de Administrador.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# --- Instancias de Repositorios y Servicios ---
docente_repo = DocenteRepository()
estudiante_repo = EstudianteRepository()
grado_repo = GradoRepository()
seccion_repo = SeccionRepository()
curso_repo = CursoRepository()
padre_repo = PadreRepository()
periodo_repo = PeriodoRepository()
preinscripcion_repo = PreinscripcionRepository()
admin_service = AdminService()
dashboard_service = DashboardService()

# --- Rutas de Vistas Principales (Dashboard y Gestión) ---

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Llamamos al servicio para obtener todos los datos del dashboard
    stats = dashboard_service.get_admin_dashboard_data()

    # Pasamos el diccionario de estadísticas a la plantilla
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/estudiantes')
@admin_required
def gestionar_estudiantes():
    page = request.args.get('page', 1, type=int)
    estudiantes, current_page, total_pages = estudiante_repo.get_paginated(page=page)
    form_crear = CreateEstudianteForm()
    form_crear.grado_id.choices = [(g.id, g.nombre) for g in grado_repo.get_all()]
    form_crear.seccion_id.choices = [(s.id, f"{s.nombre} ({s.grado_nombre})") for s in seccion_repo.get_all()]
    return render_template('admin/gestionar_estudiantes.html', 
                           estudiantes=estudiantes, page=current_page, total_pages=total_pages,
                           form_crear=form_crear)

@admin_bp.route('/docentes')
@admin_required
def gestionar_docentes():
    docentes = docente_repo.get_all()
    form_crear = CreateDocenteForm()
    return render_template('admin/gestionar_docentes.html', docentes=docentes, form_crear=form_crear)

@admin_bp.route('/cursos')
@admin_required
def gestionar_cursos():
    cursos = curso_repo.get_all()
    form = CursoForm()
    form.grado_id.choices = [(g.id, g.nombre) for g in grado_repo.get_all()]
    return render_template('admin/gestionar_cursos.html', cursos=cursos, form=form)

@admin_bp.route('/vinculos')
@admin_required
def gestionar_vinculos():
    vinculos = padre_repo.get_all_vinculos()
    form = VincularApoderadoForm()
    form.padre_id.choices = [(p.id, p.nombre_completo) for p in padre_repo.get_all()]
    form.estudiante_id.choices = [(e.id, e.nombre_completo) for e in estudiante_repo.get_all()]
    return render_template('admin/vincular_apoderados.html', vinculos=vinculos, form=form)

@admin_bp.route('/configuracion')
@admin_required
def configuracion():
    periodos = periodo_repo.get_all()
    grados = grado_repo.get_all()
    secciones = seccion_repo.get_all()
    form_grado = GradoForm()
    form_seccion = SeccionForm()
    form_seccion.grado_id.choices = [(g.id, g.nombre) for g in grados]
    form_periodo = PeriodoAcademicoForm()
    return render_template('admin/configuracion.html', 
                           periodos=periodos, grados=grados, secciones=secciones,
                           form_grado=form_grado, form_seccion=form_seccion, form_periodo=form_periodo)


# --- Rutas de Procesamiento de Formularios (Lógica POST) ---

# --- USUARIOS ---
@admin_bp.route('/usuario/crear', methods=['POST'])
@admin_required
def crear_usuario():
    rol = request.form.get('rol')
    if rol == 'estudiante':
        form = CreateEstudianteForm()
        form.grado_id.choices = [(g.id, g.nombre) for g in grado_repo.get_all()]
        form.seccion_id.choices = [(s.id, s.nombre) for s in seccion_repo.get_all()]
    elif rol == 'docente':
        form = CreateDocenteForm()
    else:
        flash('Rol de usuario no válido para la creación.', 'danger')
        return redirect(request.referrer)

    if form.validate_on_submit():
        try:
            admin_service.create_full_user(form.data)
            flash(f'{rol.capitalize()} creado exitosamente.', 'success')
        except ValueError as e:
            flash(str(e), 'danger')
    else:
        for field, errors in form.errors.items():
            flash(f"Error en el campo '{getattr(form, field).label.text}': {', '.join(errors)}", 'danger')
    return redirect(request.referrer)

@admin_bp.route('/usuario/<int:user_id>/editar', methods=['POST'])
@admin_required
def editar_usuario(user_id):
    user = admin_service.usuario_repo.find_by_id(user_id)
    if not user:
        flash("Usuario no encontrado.", "danger")
        return redirect(request.referrer)
    
    # Aquí se debería usar un formulario de edición, pero por simplicidad usamos los datos del request
    # En una app real, se crearía un EditUserForm.
    try:
        admin_service.update_full_user(user_id, request.form)
        flash("Usuario actualizado correctamente.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(request.referrer)

@admin_bp.route('/usuario/<int:user_id>/eliminar', methods=['POST'])
@admin_required
def eliminar_usuario(user_id):
    if user_id == current_user.id:
        flash('No puedes eliminar tu propia cuenta.', 'danger')
        return redirect(request.referrer)
    try:
        username = admin_service.delete_user(user_id)
        flash(f"Usuario '{username}' y todos sus datos han sido eliminados.", 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(request.referrer)


# --- CURSOS ---
@admin_bp.route('/curso/crear', methods=['POST'])
@admin_required
def crear_curso():
    form = CursoForm(request.form)
    form.grado_id.choices = [(g.id, g.nombre) for g in grado_repo.get_all()]
    if form.validate_on_submit():
        nuevo_curso = Curso(nombre=form.nombre.data, area=form.area.data, grado_id=form.grado_id.data)
        curso_repo.save(nuevo_curso)
        flash("Curso creado exitosamente.", "success")
    return redirect(url_for('admin.gestionar_cursos'))

@admin_bp.route('/curso/<int:curso_id>/eliminar', methods=['POST'])
@admin_required
def eliminar_curso(curso_id):
    try:
        curso_repo.delete(curso_id)
        flash("Curso eliminado exitosamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar el curso: {e}", "danger")
    return redirect(url_for('admin.gestionar_cursos'))


# --- VÍNCULOS ---
@admin_bp.route('/vinculos/crear', methods=['POST'])
@admin_required
def vincular_apoderado():
    form = VincularApoderadoForm(request.form)
    form.padre_id.choices = [(p.id, p.nombre_completo) for p in padre_repo.get_all()]
    form.estudiante_id.choices = [(e.id, e.nombre_completo) for e in estudiante_repo.get_all()]
    if form.validate_on_submit():
        try:
            padre_repo.vincular_estudiante(form.padre_id.data, form.estudiante_id.data, form.parentesco.data)
            flash('Vínculo creado exitosamente.', 'success')
        except ValueError as e:
            flash(str(e), 'danger')
    return redirect(url_for('admin.gestionar_vinculos'))

@admin_bp.route('/vinculo/<int:padre_id>/<int:estudiante_id>/eliminar', methods=['POST'])
@admin_required
def eliminar_vinculo(padre_id, estudiante_id):
    padre_repo.desvincular_estudiante(padre_id, estudiante_id)
    flash("Vínculo familiar eliminado.", "success")
    return redirect(url_for('admin.gestionar_vinculos'))


# --- CONFIGURACIÓN ---
@admin_bp.route('/configuracion/periodo/crear', methods=['POST'])
@admin_required
def crear_periodo():
    form = PeriodoAcademicoForm(request.form)
    if form.validate_on_submit():
        periodo = PeriodoAcademico(
            anio=form.anio.data, nombre=form.nombre.data,
            fecha_inicio=form.fecha_inicio.data, fecha_fin=form.fecha_fin.data,
            activo=form.activo.data
        )
        periodo_repo.save(periodo)
        flash('Periodo creado exitosamente.', 'success')
    return redirect(url_for('admin.configuracion'))

@admin_bp.route('/configuracion/periodo/<int:id>/activar', methods=['POST'])
@admin_required
def activar_periodo(id):
    periodo_repo.activate(id)
    flash('Periodo activado exitosamente.', 'success')
    return redirect(url_for('admin.configuracion'))

@admin_bp.route('/configuracion/grado/crear', methods=['POST'])
@admin_required
def crear_grado():
    form = GradoForm(request.form)
    if form.validate_on_submit():
        nuevo_grado = Grado(nombre=form.nombre.data, nivel=form.nivel.data)
        grado_repo.save(nuevo_grado)
        flash('Grado creado.', 'success')
    return redirect(url_for('admin.configuracion'))

@admin_bp.route('/configuracion/grado/<int:id>/editar', methods=['POST'])
@admin_required
def editar_grado(id):
    form = GradoForm(request.form)
    if form.validate_on_submit():
        grado_a_editar = grado_repo.find_by_id(id)
        if grado_a_editar:
            grado_a_editar.nombre = form.nombre.data
            grado_a_editar.nivel = form.nivel.data
            grado_repo.save(grado_a_editar)
            flash('Grado actualizado.', 'success')
    return redirect(url_for('admin.configuracion'))


@admin_bp.route('/configuracion/grado/<int:id>/eliminar', methods=['POST'])
@admin_required
def eliminar_grado(id):
    try:
        grado_repo.delete(id)
        flash("Grado eliminado.", "success")
    except Exception as e:
        flash(f"No se pudo eliminar el grado. Causa: {e}", "danger")
    return redirect(url_for('admin.configuracion'))

@admin_bp.route('/configuracion/seccion/crear', methods=['POST'])
@admin_required
def crear_seccion():
    form = SeccionForm(request.form)
    form.grado_id.choices = [(g.id, g.nombre) for g in grado_repo.get_all()]
    if form.validate_on_submit():
        nueva_seccion = Seccion(nombre=form.nombre.data, grado_id=form.grado_id.data)
        seccion_repo.save(nueva_seccion)
        flash('Sección creada.', 'success')
    return redirect(url_for('admin.configuracion'))

@admin_bp.route('/configuracion/seccion/<int:id>/editar', methods=['POST'])
@admin_required
def editar_seccion(id):
    form = SeccionForm(request.form)
    form.grado_id.choices = [(g.id, g.nombre) for g in grado_repo.get_all()]
    if form.validate_on_submit():
        seccion_a_editar = seccion_repo.find_by_id(id)
        if seccion_a_editar:
            seccion_a_editar.nombre = form.nombre.data
            seccion_a_editar.grado_id = form.grado_id.data
            seccion_repo.save(seccion_a_editar)
            flash('Sección actualizada.', 'success')
    return redirect(url_for('admin.configuracion'))

@admin_bp.route('/configuracion/seccion/<int:id>/eliminar', methods=['POST'])
@admin_required
def eliminar_seccion(id):
    try:
        seccion_repo.delete(id)
        flash("Sección eliminada.", "success")
    except Exception as e:
        flash(f"No se pudo eliminar la sección. Causa: {e}", "danger")
    return redirect(url_for('admin.configuracion'))

# --- API Endpoints ---
@admin_bp.route('/api/usuario/<int:user_id>')
@admin_required
def get_user_data_api(user_id):
    """
    Endpoint de API para obtener los datos de un usuario en formato JSON.
    Utilizado por el JavaScript para llenar los modales de edición.
    """
    user = admin_service.usuario_repo.find_by_id(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
        
    person = admin_service.persona_repo.find_by_id(user_id)
    if not person:
        # Esto podría pasar si es un admin sin entrada en Personas, aunque no se debería llamar para ellos.
        return jsonify({'error': 'Datos personales no encontrados'}), 404

    data = {
        'username': user.username,
        'activo': user.activo,
        'nombres': person.nombres,
        'apellidos': person.apellidos,
        'dni': person.dni,
        'correo': person.correo,
        'fecha_nacimiento': person.fecha_nacimiento.strftime('%Y-%m-%d') if person.fecha_nacimiento else ''
    }

    if user.rol == 'estudiante':
        estudiante = admin_service.estudiante_repo.find_by_id(user_id)
        if estudiante:
            data.update({
                'grado_id': estudiante.grado_id,
                'seccion_id': estudiante.seccion_id
            })
    elif user.rol == 'docente':
        docente = admin_service.docente_repo.find_by_id(user_id)
        if docente:
            data.update({'especialidad': docente.especialidad})
            
    return jsonify(data)

@admin_bp.route('/api/curso/<int:curso_id>')
@admin_required
def get_curso_data_api(curso_id):
    """Endpoint de API para obtener los datos de un curso en formato JSON."""
    curso = curso_repo.find_by_id(curso_id)
    if curso:
        return jsonify({
            'id': curso.id,
            'nombre': curso.nombre,
            'area': curso.area,
            'grado_id': curso.grado_id
        })
    return jsonify({'error': 'Curso no encontrado'}), 404

@admin_bp.route('/api/grado/<int:id>')
@admin_required
def get_grado_data_api(id):
    """Endpoint de API para obtener los datos de un grado."""
    grado = grado_repo.find_by_id(id)
    if grado:
        return jsonify({'id': grado.id, 'nombre': grado.nombre, 'nivel': grado.nivel})
    return jsonify({'error': 'Grado no encontrado'}), 404

@admin_bp.route('/api/seccion/<int:id>')
@admin_required
def get_seccion_data_api(id):
    """Endpoint de API para obtener los datos de una sección."""
    seccion = seccion_repo.find_by_id(id)
    if seccion:
        return jsonify({'id': seccion.id, 'nombre': seccion.nombre, 'grado_id': seccion.grado_id})
    return jsonify({'error': 'Sección no encontrada'}), 404
