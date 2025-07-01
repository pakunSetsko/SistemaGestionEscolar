# RUTA: app/services/matricula_service.py
# Contiene la lógica de negocio para el proceso de matrícula y preinscripción.

import random
import string

# Importación de Repositorios
from app.repositories.preinscripcion_repository import PreinscripcionRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.persona_repository import PersonaRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.seccion_repository import SeccionRepository

# Importación de Modelos
from app.models.usuario import Usuario
from app.models.persona import Persona
from app.models.estudiante import Estudiante
from app.models.preinscripcion import Preinscripcion


class MatriculaService:
    """
    Servicio para orquestar el proceso de matrícula a partir de una preinscripción.
    """
    def __init__(self):
        """Inicializa el servicio con todas las instancias de repositorios necesarias."""
        self.preinscripcion_repo = PreinscripcionRepository()
        self.usuario_repo = UsuarioRepository()
        self.persona_repo = PersonaRepository()
        self.estudiante_repo = EstudianteRepository()
        self.seccion_repo = SeccionRepository()

    def _generar_credenciales(self, nombres, apellidos, dni):
        """
        Genera un nombre de usuario único y una contraseña temporal.
        Es un método privado porque solo se usa dentro de este servicio.
        """
        primer_nombre = nombres.split(' ')[0].lower().replace('ñ', 'n')
        primer_apellido = apellidos.split(' ')[0].lower().replace('ñ', 'n')
        # Username: ej. jquispe + ultimos 3 digitos de DNI
        base_username = f"{primer_nombre[0]}{primer_apellido}{dni[-3:]}"
        
        # Asegurar que el username sea único
        username = base_username
        contador = 1
        while self.usuario_repo.find_by_username(username):
            username = f"{base_username}{contador}"
            contador += 1
        
        # Password aleatoria de 8 caracteres
        caracteres = string.ascii_letters + string.digits
        password = ''.join(random.choice(caracteres) for i in range(8))
        
        return username, password

    def crear_preinscripcion(self, form_data):
        """Crea un nuevo registro de preinscripción."""
        if self.preinscripcion_repo.find_by_dni(form_data['dni_aspirante']):
            raise ValueError("Ya existe una preinscripción con este DNI de aspirante.")
        if self.persona_repo.find_by_dni(form_data['dni_aspirante']):
            raise ValueError("El DNI del aspirante ya se encuentra registrado como un usuario en el sistema.")

        nueva_preinscripcion = Preinscripcion(**form_data)
        self.preinscripcion_repo.save(nueva_preinscripcion)

    def aprobar_y_matricular_estudiante(self, preinscripcion_id):
        """
        Procesa una preinscripción aprobada para crear un usuario, persona y estudiante.
        """
        solicitud = self.preinscripcion_repo.find_by_id(preinscripcion_id)
        if not solicitud:
            raise ValueError("La solicitud de preinscripción no existe.")

        if solicitud.estado != 'pendiente':
            raise ValueError(f"La solicitud ya ha sido procesada con estado: {solicitud.estado}.")

        # 1. Generar credenciales
        username, temp_password = self._generar_credenciales(solicitud.nombres_aspirante, solicitud.apellidos_aspirante, solicitud.dni_aspirante)

        # 2. Crear el Usuario
        nuevo_usuario = Usuario(username=username, rol='estudiante')
        nuevo_usuario.set_password(temp_password)
        user_id = self.usuario_repo.save(nuevo_usuario)

        # 3. Crear la Persona
        nueva_persona = Persona(
            id=user_id,
            nombres=solicitud.nombres_aspirante,
            apellidos=solicitud.apellidos_aspirante,
            dni=solicitud.dni_aspirante,
            correo=solicitud.correo_apoderado,
            fecha_nacimiento=solicitud.fecha_nacimiento_aspirante
        )
        self.persona_repo.save(nueva_persona)

        # 4. Asignar una sección por defecto
        secciones_del_grado = self.seccion_repo.get_by_grado(solicitud.grado_id_solicitado)
        if not secciones_del_grado:
            raise ValueError(f"No hay secciones creadas para el grado solicitado. No se puede matricular.")
        seccion_id_defecto = secciones_del_grado[0].id

        # 5. Crear el Estudiante
        nuevo_estudiante = Estudiante(
            id=user_id,
            nombres=solicitud.nombres_aspirante,
            apellidos=solicitud.apellidos_aspirante,
            dni=solicitud.dni_aspirante,
            grado_id=solicitud.grado_id_solicitado,
            seccion_id=seccion_id_defecto
        )
        self.estudiante_repo.save(nuevo_estudiante)

        # 6. Actualizar el estado de la preinscripción
        self.preinscripcion_repo.update_status(preinscripcion_id, 'aprobado')
        
        return username, temp_password
