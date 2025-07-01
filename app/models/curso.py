# RUTA: app/models/curso.py

# Importa la función para obtener la conexión a la base de datos y la librería pyodbc.
from app.db_connector import get_db
import pyodbc

class Curso:
    """
    Representa un curso específico dentro de un grado (ej. "Matemática de Primer Grado").
    Define los atributos y métodos para gestionar los cursos en la base de datos.
    """

    # Constructor de la clase para inicializar un nuevo objeto Curso.
    def __init__(self, nombre, area, grado_id, id=None):
        self.id = id
        self.nombre = nombre
        self.area = area
        self.grado_id = grado_id # Clave foránea que lo vincula a un Grado.

    def save(self):
        """
        Guarda (crea o actualiza) un curso en la base de datos.
        """
        conn = get_db()
        cursor = conn.cursor()
        try:
            # Si el objeto ya tiene un ID, se actualiza el registro existente.
            if self.id:
                cursor.execute("UPDATE Cursos SET nombre = ?, area = ?, grado_id = ? WHERE id = ?", self.nombre, self.area, self.grado_id, self.id)
            # Si no tiene ID, es un curso nuevo y se inserta.
            else:
                cursor.execute("INSERT INTO Cursos (nombre, area, grado_id) VALUES (?, ?, ?)", self.nombre, self.area, self.grado_id)
            conn.commit() # Confirma la transacción en la base de datos.
        except pyodbc.Error as e:
            conn.rollback() # Revierte los cambios si ocurre un error.
            raise e

    def delete(self):
        """
        Elimina el curso y todos sus datos relacionados en cascada.
        Es importante eliminar las dependencias primero para evitar errores de restricción.
        """
        conn = get_db()
        cursor = conn.cursor()
        try:
            # Elimina registros en tablas que dependen de 'curso_id'.
            cursor.execute("DELETE FROM Asignaciones WHERE curso_id = ?", self.id)
            cursor.execute("DELETE FROM Calificaciones WHERE curso_id = ?", self.id)
            cursor.execute("DELETE FROM Asistencias WHERE curso_id = ?", self.id)
            cursor.execute("DELETE FROM RespuestasEvaluacionDocente WHERE curso_id = ?", self.id)
            
            # Finalmente, elimina el curso principal.
            cursor.execute("DELETE FROM Cursos WHERE id = ?", self.id)
            conn.commit()
        except pyodbc.Error as e:
            conn.rollback()
            raise e

    @staticmethod
    def get_all_with_grado():
        """Obtiene una lista de todos los cursos con el nombre del grado al que pertenecen."""
        conn = get_db()
        cursor = conn.cursor()
        query = "SELECT c.id, c.nombre, c.area, g.nombre as grado_nombre FROM Cursos c JOIN Grados g ON c.grado_id = g.id ORDER BY g.id, c.nombre"
        cursor.execute(query)
        return cursor.fetchall()

    @staticmethod
    def find_by_id(curso_id):
        """
        Busca un curso por su ID y devuelve una instancia de la clase Curso,
        incluyendo el nombre del grado para facilitar su uso en las plantillas.
        """
        conn = get_db()
        cursor = conn.cursor()
        # La consulta une Cursos y Grados para obtener el 'grado_nombre'.
        query = """
        SELECT c.id, c.nombre, c.area, c.grado_id, g.nombre as grado_nombre
        FROM Cursos c
        JOIN Grados g ON c.grado_id = g.id
        WHERE c.id = ?
        """
        cursor.execute(query, curso_id)
        row = cursor.fetchone()
        if row:
            # Crea el objeto base 'Curso' con los datos de la tabla Cursos.
            curso_obj = Curso(id=row.id, nombre=row.nombre, area=row.area, grado_id=row.grado_id)
            # Añade dinámicamente el atributo 'grado_nombre' al objeto desde el resultado del JOIN.
            curso_obj.grado_nombre = row.grado_nombre
            return curso_obj
        return None
        
    @staticmethod
    def get_students(curso_id):
        """Obtiene la lista de todos los estudiantes que están matriculados en el grado de este curso."""
        conn = get_db()
        cursor = conn.cursor()
        # Primero, obtiene el grado_id del curso.
        cursor.execute("SELECT grado_id FROM Cursos WHERE id = ?", curso_id)
        grado_row = cursor.fetchone()
        if not grado_row: return [] # Si el curso no existe, devuelve una lista vacía.
        
        # Luego, busca todos los estudiantes matriculados en ese grado.
        query = "SELECT p.id, p.nombres, p.apellidos, s.nombre as seccion_nombre FROM Personas p JOIN Estudiantes e ON p.id = e.id JOIN Secciones s ON e.seccion_id = s.id WHERE e.grado_id = ? ORDER BY p.apellidos, p.nombres"
        cursor.execute(query, grado_row.grado_id)
        return cursor.fetchall()

    @staticmethod
    def get_by_grado(grado_id):
        """Obtiene todos los cursos que pertenecen a un grado específico."""
        conn = get_db()
        cursor = conn.cursor()
        query = "SELECT id, nombre, area FROM Cursos WHERE grado_id = ? ORDER BY nombre"
        cursor.execute(query, grado_id)
        return cursor.fetchall()
