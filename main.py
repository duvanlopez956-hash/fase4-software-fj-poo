"""
Módulo: main.py
Descripción: Punto de entrada principal del sistema Software FJ.
Ejecuta secuencialmente 12 operaciones completas (exitosas y fallidas) para
validar el comportamiento polimórfico, la encapsulación, el encadenamiento
de excepciones y la continuidad operativa sin base de datos.
"""

# Importa la excepción base para capturar errores de instanciación directa
from excepciones import SoftwareFJError
# Importa el sistema de auditoría en archivo plano
from logger import RegistradorLogs
# Importa las clases del modelo de dominio
from modelos import Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
# Importa el controlador principal del sistema
from gestor import GestorSoftwareFJ


def ejecutar_simulacion() -> None:
    """
    Orquesta la batería de pruebas funcionales y de estrés del sistema Software FJ.
    """
    # Inicializa el registrador de logs apuntando al archivo 'sistema_fj.log'
    logger = RegistradorLogs("sistema_fj.log")
    logger.registrar_evento("START", "=== INICIO DE EJECUCIÓN DEL SISTEMA SOFTWARE FJ ===")

    # Instancia el controlador principal inyectando el logger
    gestor = GestorSoftwareFJ(logger)

    print("=== INICIANDO SIMULACIÓN DE 12 OPERACIONES - SOFTWARE FJ ===\n")

    # -------------------------------------------------------------------------
    # OPERACIÓN 1: Registro válido de un primer cliente
    # -------------------------------------------------------------------------
    print("--- Operación 1: Registro válido de Cliente 1 ---")
    cliente1 = Cliente("CLI-01", "Laura Gómez", "laura.gomez@empresa.com", "3001234567")
    gestor.registrar_cliente(cliente1)

    # -------------------------------------------------------------------------
    # OPERACIÓN 2: Registro válido de un segundo cliente
    # -------------------------------------------------------------------------
    print("\n--- Operación 2: Registro válido de Cliente 2 ---")
    cliente2 = Cliente("CLI-02", "Carlos Mendoza", "cmendoza@tech.co", "3109876543")
    gestor.registrar_cliente(cliente2)

    # -------------------------------------------------------------------------
    # OPERACIÓN 3: Intento de registro inválido de cliente (datos mal formados)
    # -------------------------------------------------------------------------
    print("\n--- Operación 3: Registro inválido de Cliente (correo y teléfono erróneos) ---")
    try:
        # Intenta crear un cliente con nombre corto, correo sin '@' y teléfono inválido
        cliente_invalido = Cliente("CLI-03", "An", "correo_invalido.com", "123")
        gestor.registrar_cliente(cliente_invalido)
    except SoftwareFJError as error:
        # Captura el error de validación, lo registra en el log y continúa ejecutando
        logger.registrar_error("Instanciación de cliente inválida", error)
        print(f"[ERROR CONTROLADO] {error}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 4: Creación y registro válido de tres servicios especializados
    # -------------------------------------------------------------------------
    print("\n--- Operación 4: Creación válida de 3 servicios especializados (Polimorfismo) ---")
    sala1 = ReservaSala("SRV-01", "Sala Innovación A", tarifa_base=80000, capacidad=25)
    equipo1 = AlquilerEquipo(
        "SRV-02",
        "Workstation Render RTX",
        tarifa_base=45000,
        categoria_equipo="Cómputo Alto Rendimiento",
    )
    asesoria1 = AsesoriaEspecializada(
        "SRV-03",
        "Auditoría Arquitectura Cloud",
        tarifa_base=150000,
        especialidad="Cloud & DevOps",
    )
    gestor.registrar_servicio(sala1)
    gestor.registrar_servicio(equipo1)
    gestor.registrar_servicio(asesoria1)

    # -------------------------------------------------------------------------
    # OPERACIÓN 5: Creación incorrecta de servicio (encadenamiento de excepciones)
    # -------------------------------------------------------------------------
    print("\n--- Operación 5: Creación incorrecta de Servicio (tarifa no numérica) ---")
    try:
        # Al pasar 'gratis' como tarifa, Servicio captura ValueError y lanza DatoInvalidoError
        servicio_corrupto = AlquilerEquipo(
            "SRV-99",
            "Servidor Rack",
            tarifa_base="gratis",  # type: ignore
            categoria_equipo="Infraestructura",
        )
        gestor.registrar_servicio(servicio_corrupto)
    except SoftwareFJError as error:
        # El logger registrará tanto DatoInvalidoError como su causa encadenada ValueError
        logger.registrar_error("Instanciación de servicio inválida", error)
        print(f"[ERROR CONTROLADO] {error}")

    # -------------------------------------------------------------------------
    # OPERACIÓN 6: Reserva exitosa de Sala (uso de método sobrecargado con IVA y descuento)
    # -------------------------------------------------------------------------
    print("\n--- Operación 6: Reserva exitosa de Sala (4h, IVA 19%, descuento 10%) ---")
    gestor.crear_y_confirmar_reserva(
        id_reserva="RES-101",
        id_cliente="CLI-01",
        id_servicio="SRV-01",
        horas=4,
        impuesto_pct=19.0,
        descuento_pct=10.0,
    )

    # -------------------------------------------------------------------------
    # OPERACIÓN 7: Reserva fallida por servicio no disponible (SRV-01 está ocupado)
    # -------------------------------------------------------------------------
    print("\n--- Operación 7: Intento de reserva sobre sala ya ocupada ---")
    gestor.crear_y_confirmar_reserva(
        id_reserva="RES-102",
        id_cliente="CLI-02",
        id_servicio="SRV-01",
        horas=2,
    )

    # -------------------------------------------------------------------------
    # OPERACIÓN 8: Reserva fallida por incumplimiento de duración mínima en equipo
    # -------------------------------------------------------------------------
    print("\n--- Operación 8: Reserva fallida por duración menor al mínimo (1h en equipo) ---")
    gestor.crear_y_confirmar_reserva(
        id_reserva="RES-103",
        id_cliente="CLI-02",
        id_servicio="SRV-02",
        horas=1,
    )

    # -------------------------------------------------------------------------
    # OPERACIÓN 9: Reserva exitosa de Alquiler de Equipo (8h -> descuento automático)
    # -------------------------------------------------------------------------
    print("\n--- Operación 9: Reserva exitosa de Alquiler de Equipo (8 horas) ---")
    gestor.crear_y_confirmar_reserva(
        id_reserva="RES-104",
        id_cliente="CLI-02",
        id_servicio="SRV-02",
        horas=8,
        impuesto_pct=19.0,
    )

    # -------------------------------------------------------------------------
    # OPERACIÓN 10: Procesamiento exitoso de la reserva RES-101
    # -------------------------------------------------------------------------
    print("\n--- Operación 10: Procesamiento exitoso de reserva RES-101 ---")
    gestor.procesar_reserva("RES-101")

    # -------------------------------------------------------------------------
    # OPERACIÓN 11: Operación no permitida (intentar cancelar una reserva PROCESADA)
    # -------------------------------------------------------------------------
    print("\n--- Operación 11: Intento de cancelar una reserva ya PROCESADA ---")
    gestor.cancelar_reserva("RES-101")

    # -------------------------------------------------------------------------
    # OPERACIÓN 12: Error de cálculo inconsistente (descuento > 100%) y recuperación
    # -------------------------------------------------------------------------
    print("\n--- Operación 12: Cálculo inconsistente (descuento 150%) y reserva válida ---")
    # Primer intento: falla controladamente por descuento fuera de rango
    gestor.crear_y_confirmar_reserva(
        id_reserva="RES-105-ERR",
        id_cliente="CLI-01",
        id_servicio="SRV-03",
        horas=3,
        descuento_pct=150.0,
    )
    # Segundo intento: se corrige el parámetro y la reserva se confirma exitosamente
    gestor.crear_y_confirmar_reserva(
        id_reserva="RES-105",
        id_cliente="CLI-01",
        id_servicio="SRV-03",
        horas=3,
        impuesto_pct=0.0,
    )

    # Muestra el resumen final de todos los objetos vigentes en memoria
    gestor.mostrar_reporte_general()

    # Registra el cierre ordenado de la ejecución en el archivo de logs
    logger.registrar_evento("END", "=== FIN DE EJECUCIÓN SIN INTERRUPCIONES ===")
    print("\nEjecución completada. Revise 'sistema_fj.log' para auditar todos los eventos y errores.")


# Punto de entrada estándar de Python cuando el archivo se ejecuta directamente
if __name__ == "__main__":
    ejecutar_simulacion()