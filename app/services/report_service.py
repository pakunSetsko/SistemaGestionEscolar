# RUTA: app/services/report_service.py
# Contiene la lógica de negocio para generar reportes complejos.

from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.curso_repository import CursoRepository
from app.repositories.periodo_repository import PeriodoRepository
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.docente_repository import DocenteRepository
from collections import defaultdict

class ReportService:
    """
    Servicio que encapsula la lógica para generar reportes consolidados,
    como el rendimiento académico y los resultados de la evaluación docente.
    """
    def __init__(self):
        self.estudiante_repo = EstudianteRepository()
        self.calificacion_repo = CalificacionRepository()
        self.curso_repo = CursoRepository()
        self.periodo_repo = PeriodoRepository()
        self.evaluacion_repo = EvaluacionRepository()
        self.docente_repo = DocenteRepository()

    def generar_reporte_academico_general(self):
        """Prepara un consolidado con el rendimiento académico de todos los estudiantes."""
        periodo_activo = self.periodo_repo.find_active()
        if not periodo_activo:
            raise ValueError("No hay un periodo académico activo para generar el reporte.")

        estudiantes = self.estudiante_repo.get_all()
        reporte = []

        for est in estudiantes:
            cursos_del_grado = self.curso_repo.get_by_grado(est.grado_id)
            promedios_por_curso = []

            for curso in cursos_del_grado:
                calificaciones = self.calificacion_repo.get_by_student_and_curso(est.id, curso.id, periodo_activo.id)
                notas_validas = [c['valor'] for c in calificaciones.values() if c and c.get('valor') is not None]
                
                if notas_validas:
                    promedio_curso = sum(notas_validas) / len(notas_validas)
                    promedios_por_curso.append(promedio_curso)

            promedio_general = sum(promedios_por_curso) / len(promedios_por_curso) if promedios_por_curso else 0.0

            reporte.append({
                'id': est.id,
                'nombre_completo': est.nombre_completo,
                'dni': est.dni,
                'grado_seccion': f"{est.grado_nombre} - {est.seccion_nombre}",
                'promedio_general': promedio_general
            })
            
        reporte.sort(key=lambda x: (x['grado_seccion'], x['nombre_completo']))
        return reporte

    def generar_reporte_evaluacion_docente(self, periodo_id):
        """Genera un reporte consolidado de las evaluaciones docentes para un periodo."""
        docentes = self.docente_repo.get_all()
        preguntas = self.evaluacion_repo.get_all_preguntas(activa_only=True)
        reporte_final = []

        for docente in docentes:
            respuestas_docente = self.evaluacion_repo.get_respuestas_by_docente(docente.id, periodo_id)
            if not respuestas_docente:
                continue

            resultados_por_pregunta = defaultdict(lambda: {'escala_sum': 0, 'escala_count': 0, 'comentarios': []})
            estudiantes_evaluadores = set()

            for r in respuestas_docente:
                estudiantes_evaluadores.add(r.estudiante_id)
                if r.respuesta_escala is not None:
                    resultados_por_pregunta[r.pregunta_id]['escala_sum'] += r.respuesta_escala
                    resultados_por_pregunta[r.pregunta_id]['escala_count'] += 1
                if r.respuesta_texto:
                    resultados_por_pregunta[r.pregunta_id]['comentarios'].append(r.respuesta_texto)
            
            promedio_general_sum = 0
            promedio_general_count = 0
            preguntas_con_promedio = []

            for p in preguntas:
                datos_pregunta = resultados_por_pregunta[p.id]
                promedio = 0
                if p.tipo_pregunta == 'escala_1_5' and datos_pregunta['escala_count'] > 0:
                    promedio = datos_pregunta['escala_sum'] / datos_pregunta['escala_count']
                    promedio_general_sum += promedio
                    promedio_general_count += 1
                
                preguntas_con_promedio.append({
                    'texto': p.texto_pregunta,
                    'tipo': p.tipo_pregunta,
                    'promedio': promedio,
                    'comentarios': [c for c in datos_pregunta['comentarios'] if c]
                })

            promedio_final_docente = promedio_general_sum / promedio_general_count if promedio_general_count > 0 else 0.0
            
            reporte_final.append({
                'docente_id': docente.id,
                'nombre_completo': docente.nombre_completo,
                'promedio_general': promedio_final_docente,
                'total_evaluaciones': len(estudiantes_evaluadores),
                'detalle_preguntas': preguntas_con_promedio
            })

        reporte_final.sort(key=lambda x: x['promedio_general'], reverse=True)
        return reporte_final
