# RUTA: app/services/admin_service.py
# Contiene la lógica de negocio para las operaciones del administrador.

from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.persona_repository import PersonaRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.docente_repository import DocenteRepository
from app.repositories.padre_repository import PadreRepository
from app.repositories.director_repository import DirectorRepository

from app.models.usuario import Usuario
from app.models.persona import Persona
from app.models.estudiante import Estudiante
from app.models.docente import Docente
from app.models.padre import Padre
from app.models.director import Director

class AdminService:
    """
    Servicio para orquestar las operaciones de gestión del administrador.
    """
    def __init__(self):
        self.usuario_repo = UsuarioRepository()
        self.persona_repo = PersonaRepository()
        self.estudiante_repo = EstudianteRepository()
        self.docente_repo = DocenteRepository()
        self.padre_repo = PadreRepository()
        self.director_repo = DirectorRepository()

    def create_full_user(self, form_data):
        """
        Crea un usuario completo con su persona y rol específico.
        Orquesta la creación en las tablas Usuarios, Personas y la tabla de rol.
        """
        if self.usuario_repo.find_by_username(form_data['username']):
            raise ValueError(f"El nombre de usuario '{form_data['username']}' ya existe.")
        if self.persona_repo.find_by_dni(form_data['dni']):
            raise ValueError(f"El DNI '{form_data['dni']}' ya está registrado.")

        nuevo_usuario = Usuario(username=form_data['username'], rol=form_data['rol'])
        nuevo_usuario.set_password(form_data['password'])
        user_id = self.usuario_repo.save(nuevo_usuario)

        nueva_persona = Persona(
            id=user_id,
            nombres=form_data['nombres'],
            apellidos=form_data['apellidos'],
            dni=form_data['dni'],
            correo=form_data.get('correo'),
            fecha_nacimiento=form_data.get('fecha_nacimiento')
        )
        self.persona_repo.save(nueva_persona)

        rol = form_data['rol']
        if rol == 'estudiante':
            estudiante = Estudiante(id=user_id, grado_id=form_data['grado_id'], seccion_id=form_data['seccion_id'], **form_data)
            self.estudiante_repo.save(estudiante)
        elif rol == 'docente':
            docente = Docente(id=user_id, especialidad=form_data.get('especialidad'), **form_data)
            self.docente_repo.save(docente)
        elif rol == 'padre_familia':
            padre = Padre(id=user_id, **form_data)
            self.padre_repo.save(padre)
        elif rol == 'director':
            director = Director(id=user_id, **form_data)
            self.director_repo.save(director)
        
        return user_id

    def update_full_user(self, user_id, form_data):
        """Actualiza los datos de un usuario y su persona/rol asociado."""
        user = self.usuario_repo.find_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado.")

        # Validar unicidad de username si ha cambiado
        new_username = form_data['username']
        if user.username != new_username and self.usuario_repo.find_by_username(new_username):
            raise ValueError(f"El nuevo nombre de usuario '{new_username}' ya está en uso.")

        # Validar unicidad de DNI si ha cambiado
        person = self.persona_repo.find_by_id(user_id)
        new_dni = form_data['dni']
        if person and person.dni != new_dni and self.persona_repo.find_by_dni(new_dni):
            raise ValueError(f"El nuevo DNI '{new_dni}' ya está registrado por otro usuario.")

        # Actualizar tabla Usuarios
        user.username = new_username
        user.activo = form_data.get('activo', False)
        self.usuario_repo.save(user)

        # Actualizar tabla Personas
        if person:
            person.nombres = form_data['nombres']
            person.apellidos = form_data['apellidos']
            person.dni = new_dni
            person.correo = form_data.get('correo')
            person.fecha_nacimiento = form_data.get('fecha_nacimiento')
            self.persona_repo.save(person)

        # Actualizar tabla de rol específico
        rol = user.rol
        if rol == 'estudiante':
            estudiante = self.estudiante_repo.find_by_id(user_id)
            if estudiante:
                estudiante.grado_id = form_data['grado_id']
                estudiante.seccion_id = form_data['seccion_id']
                self.estudiante_repo.save(estudiante)
        elif rol == 'docente':
            docente = self.docente_repo.find_by_id(user_id)
            if docente:
                docente.especialidad = form_data.get('especialidad')
                self.docente_repo.save(docente)

    def delete_user(self, user_id):
        """Elimina un usuario y todos sus datos en cascada."""
        user_to_delete = self.usuario_repo.find_by_id(user_id)
        if not user_to_delete:
            raise ValueError("El usuario que intenta eliminar no existe.")
        
        # La BD se encarga de la cascada gracias a ON DELETE CASCADE.
        self.usuario_repo.delete(user_id)
        return user_to_delete.username
