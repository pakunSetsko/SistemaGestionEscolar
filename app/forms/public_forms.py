# RUTA: app/forms/public_forms.py
# Define los formularios para las páginas de acceso público.

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Regexp, Email

class PreinscripcionForm(FlaskForm):
    """Formulario para la preinscripción de nuevos aspirantes."""
    # Datos del Aspirante
    nombres_aspirante = StringField('Nombres del Aspirante', validators=[DataRequired(), Length(max=100)])
    apellidos_aspirante = StringField('Apellidos del Aspirante', validators=[DataRequired(), Length(max=100)])
    dni_aspirante = StringField('DNI del Aspirante', validators=[DataRequired(), Regexp(r'^\d{8}$', message='El DNI debe tener 8 dígitos.')])
    fecha_nacimiento_aspirante = DateField('Fecha de Nacimiento del Aspirante', format='%Y-%m-%d', validators=[DataRequired()])
    grado_id_solicitado = SelectField('Grado al que Postula', coerce=int, validators=[DataRequired(message="Debe seleccionar un grado.")])

    # Datos del Apoderado
    nombre_apoderado = StringField('Nombres y Apellidos del Apoderado', validators=[DataRequired(), Length(max=200)])
    dni_apoderado = StringField('DNI del Apoderado', validators=[DataRequired(), Regexp(r'^\d{8}$', message='El DNI debe tener 8 dígitos.')])
    correo_apoderado = StringField('Correo Electrónico de Contacto', validators=[DataRequired(), Email(), Length(max=100)])
    telefono_apoderado = StringField('Teléfono de Contacto', validators=[DataRequired(), Length(max=20)])

    submit = SubmitField('Enviar Preinscripción')
