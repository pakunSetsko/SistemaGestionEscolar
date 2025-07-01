# RUTA: app/db_connector.py
# Gestiona la conexión a la base de datos para cada solicitud.

import pyodbc
from flask import g
from app.config import Config

def get_db():
    """
    Crea y devuelve una conexión a la base de datos para la solicitud actual.
    Si ya existe una conexión en el contexto 'g' de Flask, la reutiliza.
    Esto evita abrir y cerrar conexiones innecesariamente.
    """
    if 'db' not in g:
        try:
            conn_str = (
                f"DRIVER={Config.DB_DRIVER};"
                f"SERVER={Config.DB_SERVER};"
                f"DATABASE={Config.DB_DATABASE};"
                f"UID={Config.DB_USERNAME};"
                f"PWD={Config.DB_PASSWORD};"
            )
            g.db = pyodbc.connect(conn_str)
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            # Es importante registrar este error en un sistema de logging en producción.
            print(f"Error de conexión a la base de datos: {sqlstate}")
            raise ex
    return g.db

def close_db(e=None):
    """
    Cierra la conexión a la base de datos al final de la solicitud para liberar recursos.
    """
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_app(app):
    """
    Integra la gestión de la base de datos con la aplicación Flask.
    Registra la función 'close_db' para que se ejecute después de cada solicitud.
    """
    app.teardown_appcontext(close_db)
