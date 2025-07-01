# RUTA: app/services/docente_service.py
# Contiene la lógica de negocio para las operaciones del rol de docente.

from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.asistencia_repository import AsistenciaRepository
from app.repositories.estudiante_repository import EstudianteRepository

class DocenteService:
    """
    Servicio que encapsula la lógica de negocio para las acciones de un docente.
    """
    def __init__(self):
        self.calificacion_repo = CalificacionRepository()
        self.asistencia_repo = AsistenciaRepository()
        self.estudiante_repo = EstudianteRepository()

    def guardar_calificaciones_desde_formulario(self, curso_id, periodo_id, form_data):
        """
        Procesa los datos de un formulario de calificaciones y los prepara
        para ser guardados en la base de datos de manera eficiente.
        """
        calificaciones_a_guardar = []
        for key, valor in form_data.items():
            if key.startswith('calificacion_') and valor.strip():
                try:
                    parts = key.split('_')
                    estudiante_id = int(parts[1])
                    bimestre = int(parts[2])
                    comentario = form_data.get(f'comentario_{estudiante_id}_{bimestre}', None)
                    
                    # Validación simple del valor
                    nota = float(valor)
                    if not (0 <= nota <= 20):
                        continue # Ignorar notas fuera de rango

                    calificaciones_a_guardar.append({
                        'estudiante_id': estudiante_id,
                        'curso_id': curso_id,
                        'periodo_id': periodo_id,
                        'bimestre': bimestre,
                        'valor': nota,
                        'comentario': comentario
                    })
                except (ValueError, IndexError):
                    # Ignorar campos de formulario malformados o vacíos
                    continue
        
        if calificaciones_a_guardar:
            self.calificacion_repo.save_multiple(calificaciones_a_guardar)

    def guardar_asistencias_desde_formulario(self, curso_id, periodo_id, fecha, grado_id, form_data):
        """
        Procesa los datos de un formulario de asistencia y los prepara para guardarlos.
        """
        # Obtenemos la lista de estudiantes del grado para asegurar que procesamos todos.
        estudiantes_del_grado = self.estudiante_repo.get_by_grado(grado_id)
        asistencias_a_guardar = []

        for estudiante in estudiantes_del_grado:
            estado = form_data.get(f'asistencia_{estudiante.id}', 'Falta') # Si no se envía nada, se asume Falta.
            asistencias_a_guardar.append({
                'estudiante_id': estudiante.id,
                'curso_id': curso_id,
                'periodo_id': periodo_id,
                'fecha': fecha,
                'estado': estado
            })
            
        if asistencias_a_guardar:
            self.asistencia_repo.save_multiple(asistencias_a_guardar)

