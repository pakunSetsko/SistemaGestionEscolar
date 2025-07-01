# RUTA: app/models/estudiante.py
from app.core.persona import Persona
from app.db_connector import get_db
import pyodbc

class Estudiante(Persona):
    def __init__(self, id, nombres, apellidos, dni, grado_id, seccion_id, correo=None, fecha_nacimiento=None):
        super().__init__(id=id, nombres=nombres, apellidos=apellidos, dni=dni, correo=correo, fecha_nacimiento=fecha_nacimiento)
        self.grado_id = grado_id
        self.seccion_id = seccion_id
        self.grado_nombre = None
        self.seccion_nombre = None

    def save(self):
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM Personas WHERE id=?", self.id)
            if cursor.fetchone():
                cursor.execute(
                    "UPDATE Personas SET nombres=?, apellidos=?, dni=?, correo=?, fecha_nacimiento=? WHERE id=?",
                    self.nombres, self.apellidos, self.dni, self.correo, self.fecha_nacimiento, self.id
                )
            else:
                cursor.execute(
                    "INSERT INTO Personas (id, nombres, apellidos, dni, correo, fecha_nacimiento) VALUES (?, ?, ?, ?, ?, ?)",
                    self.id, self.nombres, self.apellidos, self.dni, self.correo, self.fecha_nacimiento
                )

            cursor.execute("SELECT id FROM Estudiantes WHERE id=?", self.id)
            if cursor.fetchone():
                cursor.execute("UPDATE Estudiantes SET grado_id=?, seccion_id=? WHERE id=?", self.grado_id, self.seccion_id, self.id)
            else:
                cursor.execute("INSERT INTO Estudiantes (id, grado_id, seccion_id) VALUES (?, ?, ?)", self.id, self.grado_id, self.seccion_id)
            conn.commit()
        except pyodbc.Error as e:
            conn.rollback()
            raise e
    
    @classmethod
    def find_by_id(cls, id):
        conn = get_db()
        cursor = conn.cursor()
        query = """
            SELECT p.*, e.grado_id, e.seccion_id, g.nombre as grado_nombre, s.nombre as seccion_nombre
            FROM Personas p 
            JOIN Estudiantes e ON p.id = e.id
            JOIN Grados g ON e.grado_id = g.id
            JOIN Secciones s ON e.seccion_id = s.id
            WHERE p.id = ?
        """
        cursor.execute(query, id)
        row = cursor.fetchone()
        if row:
            estudiante_obj = cls(id=row.id, nombres=row.nombres, apellidos=row.apellidos, dni=row.dni, correo=row.correo, fecha_nacimiento=row.fecha_nacimiento, grado_id=row.grado_id, seccion_id=row.seccion_id)
            estudiante_obj.grado_nombre = row.grado_nombre
            estudiante_obj.seccion_nombre = row.seccion_nombre
            return estudiante_obj
        return None

    @classmethod
    def get_paginated(cls, page=1, per_page=15):
        """Obtiene una lista paginada de estudiantes con sus detalles principales."""
        conn = get_db()
        cursor = conn.cursor()
        offset = (page - 1) * per_page
        query = """
        SELECT u.username, p.id, p.nombres, p.apellidos, p.dni, p.correo, g.nombre as grado_nombre, s.nombre as seccion_nombre
        FROM Personas p
        JOIN Estudiantes e ON p.id = e.id
        JOIN Usuarios u ON p.id = u.id
        JOIN Grados g ON e.grado_id = g.id
        JOIN Secciones s ON e.seccion_id = s.id
        ORDER BY p.apellidos, p.nombres
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """
        cursor.execute(query, offset, per_page)
        return cursor.fetchall()

    @classmethod
    def count_all(cls):
        """Cuenta el número total de estudiantes en el sistema."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(id) FROM Estudiantes")
        return cursor.fetchone()[0]

    @classmethod
    def find_by_id_with_details(cls, id):
        """Busca un único estudiante por ID y devuelve todos sus detalles en un diccionario."""
        conn = get_db()
        cursor = conn.cursor()
        query = "SELECT u.id, u.username, u.activo, p.*, e.grado_id, e.seccion_id FROM Personas p JOIN Estudiantes e ON p.id = e.id JOIN Usuarios u ON p.id = u.id WHERE p.id = ?"
        cursor.execute(query, id)
        row = cursor.fetchone()
        if row:
            return dict(zip([column[0] for column in cursor.description], row))
        return None
    
    @classmethod
    def get_all_with_details(cls):
        conn = get_db()
        cursor = conn.cursor()
        query = """
        SELECT u.username, p.id, p.nombres, p.apellidos, p.dni, p.correo, g.nombre as grado_nombre, s.nombre as seccion_nombre
        FROM Personas p
        JOIN Estudiantes e ON p.id = e.id
        JOIN Usuarios u ON p.id = u.id
        JOIN Grados g ON e.grado_id = g.id
        JOIN Secciones s ON e.seccion_id = s.id
        ORDER BY p.apellidos, p.nombres
        """
        cursor.execute(query)
        return cursor.fetchall()
