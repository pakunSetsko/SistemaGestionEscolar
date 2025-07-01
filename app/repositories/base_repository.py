# RUTA: app/repositories/base_repository.py
# Define la interfaz abstracta para todos los repositorios.

from abc import ABC, abstractmethod
from app.db_connector import get_db
import pyodbc

class BaseRepository(ABC):
    """
    Clase base abstracta para los repositorios. Define las operaciones CRUD comunes
    y encapsula los métodos de ejecución de consultas para reutilización.
    """
    # El constructor ahora no hace nada, evitando el error de contexto.
    def __init__(self):
        pass

    @abstractmethod
    def find_by_id(self, entity_id):
        """Método abstracto para encontrar una entidad por su ID."""
        pass

    @abstractmethod
    def get_all(self):
        """Método abstracto para obtener todas las entidades."""
        pass

    @abstractmethod
    def save(self, entity):
        """Método abstracto para guardar (crear o actualizar) una entidad."""
        pass

    @abstractmethod
    def delete(self, entity_id):
        """Método abstracto para eliminar una entidad por su ID."""
        pass

    def _fetch_one(self, query, params=None):
        """
        Ejecuta una consulta y devuelve una única fila.
        Obtiene la conexión a la BD justo a tiempo (dentro del contexto de la app).
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params or ())
        return cursor.fetchone()

    def _fetch_all(self, query, params=None):
        """
        Ejecuta una consulta y devuelve todas las filas coincidentes.
        Obtiene la conexión a la BD justo a tiempo.
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params or ())
        return cursor.fetchall()

    def _execute_and_commit(self, query, params=None):
        """
        Ejecuta una consulta que modifica datos (INSERT, UPDATE, DELETE).
        Obtiene la conexión a la BD justo a tiempo y maneja la transacción.
        """
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(query, params or ())
            db.commit()
            return cursor
        except pyodbc.Error as e:
            db.rollback() # Revierte la transacción en caso de error.
            print(f"Error en la base de datos: {e}")
            raise e
