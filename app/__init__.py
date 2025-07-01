# RUTA: app/__init__.py
# Configura y crea la aplicación Flask (Patrón Factory).

from flask import Flask, session, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from .config import Config
from .db_connector import init_app as init_db_app
from .repositories.usuario_repository import UsuarioRepository
from .repositories.periodo_repository import PeriodoRepository
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env (especialmente para desarrollo)
load_dotenv()

# Inicializar extensiones
csrf = CSRFProtect()
login_manager = LoginManager()
# --- CORRECCIÓN ---
# Apuntar al endpoint correcto: 'auth.login' en lugar de 'auth.show_login_form'
login_manager.login_view = 'auth.login'
login_manager.login_message = "Por favor, inicie sesión para acceder a esta página."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario desde la base de datos para la sesión de Flask-Login."""
    usuario_repo = UsuarioRepository()
    return usuario_repo.find_by_id(int(user_id))


def create_app():
    """Crea y configura una instancia de la aplicación Flask."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Inicializar las extensiones con la app
    csrf.init_app(app)
    login_manager.init_app(app)
    init_db_app(app)

    app.jinja_env.add_extension('jinja2.ext.do')

    @app.context_processor
    def inject_periodo_activo():
        """Inyecta el periodo académico activo en el contexto de todas las plantillas."""
        if 'periodo_activo' not in session:
            periodo_repo = PeriodoRepository()
            periodo_obj = periodo_repo.find_active()
            if periodo_obj:
                session['periodo_activo'] = {'id': periodo_obj.id, 'nombre': periodo_obj.nombre}
            else:
                session['periodo_activo'] = None
        return dict(periodo_activo=session['periodo_activo'])

    # Importar y registrar los Blueprints
    from .routes import (
        auth_routes, main_routes, admin_routes, docente_routes,
        estudiante_routes, director_routes, padre_routes, profile_routes
    )
    app.register_blueprint(auth_routes.auth_bp)
    app.register_blueprint(main_routes.main_bp)
    app.register_blueprint(admin_routes.admin_bp, url_prefix='/admin')
    app.register_blueprint(docente_routes.docente_bp, url_prefix='/docente')
    app.register_blueprint(estudiante_routes.estudiante_bp, url_prefix='/estudiante')
    app.register_blueprint(director_routes.director_bp, url_prefix='/director')
    app.register_blueprint(padre_routes.padre_bp, url_prefix='/padre')
    app.register_blueprint(profile_routes.profile_bp, url_prefix='/perfil')

    return app
