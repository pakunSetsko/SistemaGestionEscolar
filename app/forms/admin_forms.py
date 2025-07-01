# RUTA: app/forms/admin_forms.py
# Define los formularios para las tareas administrativas.

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DateField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Optional, Length, Regexp

# --- Formularios para Configuración ---

class GradoForm(FlaskForm):
    """Formulario para crear y editar Grados."""
    nombre = StringField('Nombre del Grado', validators=[DataRequired()])
    nivel = SelectField('Nivel Académico', choices=[('Inicial', 'Inicial'), ('Primaria', 'Primaria'), ('Secundaria', 'Secundaria')], validators=[DataRequired()])
    submit = SubmitField('Guardar Grado')

class SeccionForm(FlaskForm):
    """Formulario para crear y editar Secciones."""
    grado_id = SelectField('Grado al que Pertenece', coerce=int, validators=[DataRequired()])
    nombre = StringField('Nombre de la Sección (Ej: A, B)', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Guardar Sección')

class PeriodoAcademicoForm(FlaskForm):
    """Formulario para crear y editar Periodos Académicos."""
    anio = StringField('Año', validators=[DataRequired(), Regexp(r'^\d{4}$', message='El año debe tener 4 dígitos.')])
    nombre = StringField('Nombre del Periodo', validators=[DataRequired()])
    fecha_inicio = DateField('Fecha de Inicio', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_fin = DateField('Fecha de Fin', format='%Y-%m-%d', validators=[DataRequired()])
    activo = BooleanField('Marcar como periodo activo')
    submit = SubmitField('Guardar Periodo')

# --- Formularios para Gestión ---

class CursoForm(FlaskForm):
    """Formulario para crear y editar Cursos."""
    nombre = StringField('Nombre del Curso', validators=[DataRequired()])
    area = StringField('Área Académica', validators=[DataRequired()])
    grado_id = SelectField('Grado', coerce=int, validators=[DataRequired(message="Debe seleccionar un grado.")])
    submit = SubmitField('Guardar Curso')

class VincularApoderadoForm(FlaskForm):
    """Formulario para vincular un apoderado a un estudiante."""
    padre_id = SelectField('Apoderado', coerce=int, validators=[DataRequired()])
    estudiante_id = SelectField('Estudiante', coerce=int, validators=[DataRequired()])
    parentesco = StringField('Parentesco', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Crear Vínculo')

# --- Formularios para Creación de Usuarios ---

class BaseUserForm(FlaskForm):
    """Formulario base con campos comunes a todos los usuarios."""
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=4, max=50)])
    nombres = StringField('Nombres', validators=[DataRequired(), Length(max=100)])
    apellidos = StringField('Apellidos', validators=[DataRequired(), Length(max=100)])
    dni = StringField('DNI', validators=[DataRequired(), Regexp(r'^\d{8}$', message='El DNI debe tener 8 dígitos.')])
    correo = StringField('Correo Electrónico', validators=[Optional(), Length(max=100)])
    fecha_nacimiento = DateField('Fecha de Nacimiento', format='%Y-%m-%d', validators=[Optional()])
    activo = BooleanField('Usuario Activo', default=True)

class CreateUserForm(BaseUserForm):
    """Hereda de BaseUserForm y añade campos para la creación."""
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8)])
    rol = SelectField('Rol', choices=[
        ('estudiante', 'Estudiante'),
        ('docente', 'Docente'),
        ('padre_familia', 'Padre de Familia'),
        ('director', 'Director'),
        ('admin', 'Administrador')
    ], validators=[DataRequired()])

class CreateEstudianteForm(CreateUserForm):
    grado_id = SelectField('Grado', coerce=int, validators=[DataRequired()])
    seccion_id = SelectField('Sección', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Crear Estudiante')
    
class CreateDocenteForm(CreateUserForm):
    especialidad = StringField('Especialidad', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Crear Docente')
