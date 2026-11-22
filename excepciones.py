"""
Módulo: excepciones.py
Descripción: Define la jerarquía de excepciones personalizadas para el sistema
de gestión de Software FJ, permitiendo diferenciar errores de dominio y
aplicar encadenamiento de excepciones de manera estructurada.
"""


class SoftwareFJError(Exception):
    """
    Excepción base del dominio Software FJ.
    Todas las excepciones personalizadas del sistema heredan de esta clase
    para facilitar su captura polimórfica en los controladores.
    """

    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        # Almacena un código identificador del tipo de error ocurrido
        self.codigo = codigo
        # Inicializa la clase base Exception con el formato estándar [CODIGO] Mensaje
        super().__init__(f"[{codigo}] {mensaje}")


class DatoInvalidoError(SoftwareFJError):
    """
    Se lanza cuando los datos ingresados por el usuario o el sistema
    no cumplen con las reglas de formato, tipo o longitud establecidas.
    """

    def __init__(self, mensaje: str):
        # Invoca al constructor padre asignando el código específico de validación
        super().__init__(mensaje, codigo="ERR_DATO_INVALIDO")


class ServicioNoDisponibleError(SoftwareFJError):
    """
    Se lanza cuando se intenta reservar o consultar un servicio que no existe
    en el catálogo en memoria o que actualmente se encuentra ocupado/inactivo.
    """

    def __init__(self, mensaje: str):
        # Invoca al constructor padre con el código de indisponibilidad
        super().__init__(mensaje, codigo="ERR_SERVICIO_NO_DISPONIBLE")


class ReservaError(SoftwareFJError):
    """
    Se lanza cuando ocurre una violación en el ciclo de vida de una reserva
    (por ejemplo: duración fuera de rango, cancelación de reserva ya procesada
    o intento de procesar una reserva sin confirmar).
    """

    def __init__(self, mensaje: str):
        # Invoca al constructor padre con el código de conflicto de reserva
        super().__init__(mensaje, codigo="ERR_RESERVA")


class CalculoInconsistenteError(SoftwareFJError):
    """
    Se lanza cuando los parámetros financieros (impuestos, descuentos o recargos)
    producen valores negativos, porcentajes fuera de rango o resultados ilógicos.
    """

    def __init__(self, mensaje: str):
        # Invoca al constructor padre con el código de error aritmético/financiero
        super().__init__(mensaje, codigo="ERR_CALCULO")