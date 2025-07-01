# RUTA: app/services/boleta_service.py
# Contiene la lógica de negocio para generar los datos de la boleta de notas.

from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.curso_repository import CursoRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.periodo_repository import PeriodoRepository
from app.repositories.grado_repository import GradoRepository
from app.repositories.seccion_repository import SeccionRepository

class BoletaService:
    def __init__(self):
        self.estudiante_repo = EstudianteRepository()
        self.curso_repo = CursoRepository()
        self.calificacion_repo = CalificacionRepository()
        self.asignacion_repo = AsignacionRepository()
        self.periodo_repo = PeriodoRepository()
        self.grado_repo = GradoRepository()
        self.seccion_repo = SeccionRepository()
        
    def generar_datos_boleta(self, estudiante_id, periodo_id):
        """Prepara todos los datos necesarios para la boleta de notas."""
        estudiante = self.estudiante_repo.find_by_id(estudiante_id)
        if not estudiante:
            raise ValueError("Estudiante no encontrado.")
            
        periodo_obj = self.periodo_repo.find_by_id(periodo_id)
        grado = self.grado_repo.find_by_id(estudiante.grado_id)
        seccion = self.seccion_repo.find_by_id(estudiante.seccion_id)
        cursos = self.curso_repo.get_by_grado(estudiante.grado_id)
        
        calificaciones_por_curso = {
            c.id: self.calificacion_repo.get_by_student_and_curso(estudiante.id, c.id, periodo_id) for c in cursos
        }
        docentes_por_curso = {
            c.id: self.asignacion_repo.get_docente_by_curso(c.id, periodo_id) for c in cursos
        }

        return {
            'estudiante': estudiante,
            'periodo': periodo_obj,
            'grado': grado,
            'seccion': seccion,
            'cursos': cursos,
            'calificaciones_por_curso': calificaciones_por_curso,
            'docentes_por_curso': docentes_por_curso
        }
