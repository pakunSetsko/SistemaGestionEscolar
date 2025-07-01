# RUTA: app/forms/director_forms.py
# Define los formularios para las tareas del Director.

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DecimalField, DateField, HiddenField
from wtforms.validators import DataRequired, Length

class ComunicadoForm(FlaskForm):
    """Formulario para crear y editar comunicados."""
    titulo = StringField('Título', validators=[DataRequired(), Length(max=200)])
    contenido = TextAreaField('Contenido', validators=[DataRequired()])
    destinatario = SelectField('Dirigido a', choices=[
        ('todos', 'Todos'),
        ('docentes', 'Solo Docentes'),
        ('estudiantes', 'Estudiantes y Padres')
    ], validators=[DataRequired()])
    submit = SubmitField('Publicar Comunicado')

class PreguntaEvaluacionForm(FlaskForm):
    """Formulario para crear preguntas de evaluación docente."""
    texto_pregunta = TextAreaField('Texto de la Pregunta', validators=[DataRequired(), Length(max=500)])
    tipo_pregunta = SelectField('Tipo de Respuesta', choices=[
        ('escala_1_5', 'Escala (1 a 5)'),
        ('texto_abierto', 'Texto Abierto (Comentario)')
    ], validators=[DataRequired()])
    submit = SubmitField('Guardar Pregunta')

class ConceptoPagoForm(FlaskForm):
    """Formulario para crear un nuevo concepto de pago."""
    nombre = StringField('Nombre del Concepto', validators=[DataRequired(), Length(max=150)])
    monto_sugerido = DecimalField('Monto Sugerido (S/.)', places=2, validators=[DataRequired()])
    submit = SubmitField('Crear Concepto')
    
class AsignarDeudaForm(FlaskForm):
    """Formulario para asignar una deuda masivamente a un grado."""
    grado_id = SelectField('Grado', coerce=int, validators=[DataRequired()])
    concepto_id = SelectField('Concepto a Asignar', coerce=int, validators=[DataRequired()])
    monto = DecimalField('Monto Final (S/.)', places=2, validators=[DataRequired()])
    fecha_vencimiento = DateField('Fecha de Vencimiento', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Asignar Deuda')
    
class RegistrarPagoForm(FlaskForm):
    """Formulario para registrar un pago individual a una deuda."""
    deuda_id = HiddenField(validators=[DataRequired()])
    monto_pagado = DecimalField('Monto a Pagar (S/.)', places=2, validators=[DataRequired()])
    metodo_pago = SelectField('Método de Pago', choices=[
        ('Efectivo', 'Efectivo'),
        ('Yape/Plin', 'Yape/Plin'),
        ('Transferencia', 'Transferencia'),
        ('Tarjeta', 'Tarjeta')
    ])
    observaciones = TextAreaField('Observaciones')
    submit = SubmitField('Guardar Pago')
