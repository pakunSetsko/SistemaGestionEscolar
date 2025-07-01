# RUTA: app/repositories/pago_repository.py
# Repositorio para gestionar toda la lógica de finanzas y pagos.

from .base_repository import BaseRepository
from app.models.pago import ConceptoPago, DeudaEstudiante, PagoRegistrado

class PagoRepository(BaseRepository):
    """
    Repositorio para las tablas ConceptosPago, DeudasEstudiante y PagosRegistrados.
    """
    # --- Métodos para Conceptos de Pago ---

    def get_conceptos_by_periodo(self, periodo_id):
        """Obtiene todos los conceptos de pago para un periodo académico."""
        query = "SELECT * FROM ConceptosPago WHERE periodo_id = ? ORDER BY nombre"
        rows = self._fetch_all(query, (periodo_id,))
        return [ConceptoPago(**dict(zip([c[0] for c in row.cursor_description], row))) for row in rows]

    def save_concepto(self, concepto: ConceptoPago):
        """Guarda un nuevo concepto de pago."""
        query = "INSERT INTO ConceptosPago (nombre, monto_sugerido, periodo_id) VALUES (?, ?, ?)"
        self._execute_and_commit(query, (concepto.nombre, concepto.monto_sugerido, concepto.periodo_id))

    # --- Métodos para Deudas de Estudiante ---
    
    def get_deudas_by_estudiante(self, estudiante_id):
        """Obtiene el estado de cuenta completo de un estudiante."""
        query = """
            SELECT d.id, d.monto, d.fecha_vencimiento, d.estado, c.nombre as concepto_nombre,
                   (SELECT SUM(pr.monto_pagado) FROM PagosRegistrados pr WHERE pr.deuda_id = d.id) as total_pagado
            FROM DeudasEstudiante d
            JOIN ConceptosPago c ON d.concepto_id = c.id
            WHERE d.estudiante_id = ?
            ORDER BY d.fecha_vencimiento DESC
        """
        rows = self._fetch_all(query, (estudiante_id,))
        return [dict(zip([column[0] for column in row.cursor_description], row)) for row in rows]
    
    def get_all_deudas_with_details(self):
        """Obtiene un listado de todas las deudas con detalles para el director."""
        query = """
        SELECT d.id, p.nombres, p.apellidos, c.nombre as concepto_nombre, d.monto, d.fecha_vencimiento, d.estado
        FROM DeudasEstudiante d
        JOIN Estudiantes e ON d.estudiante_id = e.id
        JOIN Personas p ON e.id = p.id
        JOIN ConceptosPago c ON d.concepto_id = c.id
        ORDER BY d.fecha_vencimiento DESC, p.apellidos
        """
        rows = self._fetch_all(query)
        return [dict(zip([column[0] for column in row.cursor_description], row)) for row in rows]

    def asignar_deuda_masiva(self, grado_id, concepto_id, monto, fecha_vencimiento):
        """Asigna una nueva deuda a todos los estudiantes de un grado."""
        cursor = self._db.cursor()
        cursor.execute("SELECT id FROM Estudiantes WHERE grado_id = ?", (grado_id,))
        estudiantes_ids = [row.id for row in cursor.fetchall()]

        if not estudiantes_ids:
            return 0
        
        query = "INSERT INTO DeudasEstudiante (estudiante_id, concepto_id, monto, fecha_vencimiento) VALUES (?, ?, ?, ?)"
        params = [(est_id, concepto_id, monto, fecha_vencimiento) for est_id in estudiantes_ids]
        
        try:
            cursor.executemany(query, params)
            self._db.commit()
            return len(estudiantes_ids)
        except Exception as e:
            self._db.rollback()
            raise e

    def get_financial_summary(self, periodo_id):
        """Calcula el resumen financiero para el dashboard del director."""
        query = """
            SELECT 
                SUM(d.monto) as total_deuda,
                SUM(ISNULL(pr.total_pagado, 0)) as total_pagado
            FROM DeudasEstudiante d
            LEFT JOIN (
                SELECT deuda_id, SUM(monto_pagado) as total_pagado 
                FROM PagosRegistrados 
                GROUP BY deuda_id
            ) pr ON d.id = pr.deuda_id
            JOIN ConceptosPago cp ON d.concepto_id = cp.id
            WHERE cp.periodo_id = ?
        """
        row = self._fetch_one(query, (periodo_id,))
        return dict(zip([column[0] for column in row.cursor_description], row)) if row else {'total_deuda': 0, 'total_pagado': 0}

    # --- Métodos para Pagos Registrados ---
    
    def registrar_pago(self, pago: PagoRegistrado):
        """Guarda un nuevo pago y actualiza el estado de la deuda si corresponde."""
        query_pago = "INSERT INTO PagosRegistrados (deuda_id, monto_pagado, metodo_pago, observaciones, registrado_por_id) VALUES (?, ?, ?, ?, ?)"
        params_pago = (pago.deuda_id, pago.monto_pagado, pago.metodo_pago, pago.observaciones, pago.registrado_por_id)
        self._execute_and_commit(query_pago, params_pago)
        
        query_deuda = "SELECT monto FROM DeudasEstudiante WHERE id = ?"
        deuda = self._fetch_one(query_deuda, (pago.deuda_id,))
        
        query_total_pagado = "SELECT SUM(monto_pagado) FROM PagosRegistrados WHERE deuda_id = ?"
        total_pagado = self._fetch_one(query_total_pagado, (pago.deuda_id,))[0] or 0
        
        if deuda and total_pagado >= deuda.monto:
            query_update = "UPDATE DeudasEstudiante SET estado = 'pagado' WHERE id = ?"
            self._execute_and_commit(query_update, (pago.deuda_id,))

    # Métodos abstractos no aplicables
    def find_by_id(self, entity_id): pass
    def get_all(self): pass
    def save(self, entity): pass
    def delete(self, entity_id): pass
