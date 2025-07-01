class ConceptoPago:
    """Modelo de datos para un Concepto de Pago."""
    def __init__(self, nombre, monto_sugerido, periodo_id, id=None):
        self.id = id
        self.nombre = nombre
        self.monto_sugerido = monto_sugerido
        self.periodo_id = periodo_id

class DeudaEstudiante:
    """Modelo de datos para una Deuda asignada a un Estudiante."""
    def __init__(self, estudiante_id, concepto_id, monto, fecha_vencimiento, id=None, 
                 fecha_emision=None, estado='pendiente'):
        self.id = id
        self.estudiante_id = estudiante_id
        self.concepto_id = concepto_id
        self.monto = monto
        self.fecha_emision = fecha_emision
        self.fecha_vencimiento = fecha_vencimiento
        self.estado = estado

class PagoRegistrado:
    """Modelo de datos para un Pago Registrado."""
    def __init__(self, deuda_id, monto_pagado, registrado_por_id, id=None, fecha_pago=None, 
                 metodo_pago=None, observaciones=None):
        self.id = id
        self.deuda_id = deuda_id
        self.monto_pagado = monto_pagado
        self.fecha_pago = fecha_pago
        self.metodo_pago = metodo_pago
        self.observaciones = observaciones
        self.registrado_por_id = registrado_por_id