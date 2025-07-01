# RUTA: app/config.py
# Archivo de configuración central de la aplicación.

import os
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env.
# Esto es ideal para el desarrollo local. En producción (Google Cloud),
# las variables de entorno se configuran directamente en la plataforma.
load_dotenv()

class Config:
    """
    Clase de configuración que carga sus valores desde variables de entorno.
    Esto es crucial para la seguridad y portabilidad, permitiendo diferentes
    configuraciones para desarrollo y producción sin cambiar el código.
    """
    # Clave secreta para firmar sesiones y tokens CSRF.
    # Es VITAL que en producción esta clave sea compleja y se cargue desde el entorno.
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Configuración de la Base de Datos SQL Server
    DB_SERVER = os.environ.get('DB_SERVER')
    DB_DATABASE = os.environ.get('DB_DATABASE')
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_DRIVER = os.environ.get('DB_DRIVER', '{ODBC Driver 17 for SQL Server}')
