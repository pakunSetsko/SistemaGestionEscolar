# RUTA: app/services/dashboard_service.py
# Contiene la lógica de negocio para recopilar datos para los dashboards.

from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.docente_repository import DocenteRepository
from app.repositories.curso_repository import CursoRepository
from app.repositories.pago_repository import PagoRepository
from app.repositories.asistencia_repository import AsistenciaRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.comunicado_repository import ComunicadoRepository

class DashboardService:
    def __init__(self):
        self.estudiante_repo = EstudianteRepository()
        self.docente_repo = DocenteRepository()
        self.curso_repo = CursoRepository()
        self.pago_repo = PagoRepository()
        self.asistencia_repo = AsistenciaRepository()
        self.calificacion_repo = CalificacionRepository()
        self.comunicado_repo = ComunicadoRepository()

    def get_default_data(self):
        """Devuelve una estructura de datos vacía para el dashboard cuando no hay periodo activo."""
        return {
            "estadisticas_generales": {'estudiantes': 0, 'docentes': 0, 'cursos': 0},
            "grafico_estudiantes_por_grado": {'labels': [], 'data': []},
            "grafico_financiero": {'labels': ['Total Pagado', 'Saldo Pendiente'], 'data': [0, 0]}
        }

    def get_director_dashboard_data(self, periodo_id):
        """Recopila y procesa los datos para el dashboard del director."""
        total_estudiantes = len(self.estudiante_repo.get_all())
        total_docentes = len(self.docente_repo.get_all())
        total_cursos = len(self.curso_repo.get_all())
        
        estudiantes_por_grado = self.estudiante_repo.count_by_grado()
        resumen_financiero = self.pago_repo.get_financial_summary(periodo_id)

        total_deuda = resumen_financiero['total_deuda'] or 0
        total_pagado = resumen_financiero['total_pagado'] or 0
        saldo_pendiente = total_deuda - total_pagado

        return {
            "estadisticas_generales": {
                "estudiantes": total_estudiantes,
                "docentes": total_docentes,
                "cursos": total_cursos
            },
            "grafico_estudiantes_por_grado": {
                "labels": [row['nombre'] for row in estudiantes_por_grado],
                "data": [row['total'] for row in estudiantes_por_grado]
            },
            "grafico_financiero": {
                "labels": ["Total Pagado", "Saldo Pendiente"],
                "data": [float(total_pagado), float(saldo_pendiente)]
            }
        }

    def get_estudiante_dashboard_data(self, estudiante_id, periodo_id):
        """Recopila y procesa los datos para el dashboard del estudiante."""
        estudiante = self.estudiante_repo.find_by_id(estudiante_id)
        if not estudiante:
            return None

        cursos_del_grado = self.curso_repo.get_by_grado(estudiante.grado_id)
        calificaciones_por_curso = {}
        total_notas, num_notas = 0, 0

        for curso in cursos_del_grado:
            notas_curso = self.calificacion_repo.get_by_student_and_curso(estudiante_id, curso.id, periodo_id)
            calificaciones_por_curso[curso.nombre] = notas_curso
            for bimestre in notas_curso.values():
                if bimestre and bimestre.get('valor') is not None:
                    total_notas += float(bimestre['valor'])
                    num_notas += 1
        
        promedio_general = total_notas / num_notas if num_notas > 0 else 0.0
        
        return {
            "estudiante": estudiante,
            "calificaciones_por_curso": calificaciones_por_curso,
            "promedio_general": promedio_general,
            "asistencia_stats": self.asistencia_repo.get_stats_by_student(estudiante_id, periodo_id),
            "comunicados": self.comunicado_repo.get_for_role('estudiante')
        }
    
    def get_admin_dashboard_data(self):
        """Recopila y procesa los datos para el dashboard del administrador."""
        # Se usan los repositorios para contar directamente en la base de datos
        total_estudiantes = self.estudiante_repo.count_all()
        total_docentes = self.docente_repo.count_all()
        total_cursos = self.curso_repo.count_all()

        # Obtenemos las últimas 5 preinscripciones
        # Asumiendo que el repositorio de preinscripciones está disponible en el servicio
        if not hasattr(self, 'preinscripcion_repo'):
            from app.repositories.preinscripcion_repository import PreinscripcionRepository
            self.preinscripcion_repo = PreinscripcionRepository()

        ultimas_preinscripciones = self.preinscripcion_repo.get_latest(5)

        # Obtenemos datos para el gráfico
        estudiantes_por_grado = self.estudiante_repo.count_by_grado()

        return {
            "total_estudiantes": total_estudiantes,
            "total_docentes": total_docentes,
            "total_cursos": total_cursos,
            "ultimas_preinscripciones": ultimas_preinscripciones,
            "grafico_estudiantes_por_grado": {
                "labels": [row['nombre'] for row in estudiantes_por_grado],
                "data": [row['total'] for row in estudiantes_por_grado]
            }
        }
