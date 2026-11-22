"""
Módulo: gestor.py
Descripción: Controlador central del sistema Software FJ.
Administra las colecciones en memoria (listas internas sin base de datos)
y demuestra el uso riguroso de try/except, try/except/else y try/except/finally.
"""

# Importa utilidades de tipado para listas y valores opcionales
from typing import List, Optional
# Importa excepciones del dominio
from excepciones import (
    SoftwareFJError,
    DatoInvalidoError,
    ServicioNoDisponibleError,
    ReservaError,
)
# Importa el registrador de logs
from logger import RegistradorLogs
# Importa las entidades del modelo de dominio
from modelos import Cliente, Servicio, Reserva


class GestorSoftwareFJ:
    """
    Clase orquestadora que mantiene en memoria las listas de clientes,
    servicios y reservas, garantizando estabilidad ante cualquier excepción.
    """

    def __init__(self, logger: RegistradorLogs):
        # Inyecta la instancia del registrador de auditoría
        self._logger = logger
        # Inicializa las listas internas en memoria (sin motor de base de datos)
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []

    def registrar_cliente(self, cliente: Cliente) -> bool:
        """
        Registra un nuevo cliente verificando que su ID no esté duplicado.
        Implementa la estructura try / except / else.
        """
        try:
            # Verifica si ya existe un cliente con el mismo identificador en memoria
            if any(c.id_entidad == cliente.id_entidad for c in self._clientes):
                raise DatoInvalidoError(
                    f"Duplicidad detectada: ya existe un cliente con ID '{cliente.id_entidad}'."
                )
        except SoftwareFJError as error:
            # Registra el error en el log y notifica en consola sin detener el sistema
            self._logger.registrar_error("Fallo al registrar cliente", error)
            print(f"[ERROR CONTROLADO] {error}")
            return False
        else:
            # El bloque else se ejecuta únicamente si no ocurrió ninguna excepción
            self._clientes.append(cliente)
            self._logger.registrar_evento("INFO", f"Cliente registrado: {cliente.obtener_resumen()}")
            print(f"[OK] {cliente.obtener_resumen()}")
            return True

    def registrar_servicio(self, servicio: Servicio) -> bool:
        """
        Añade un servicio especializado al catálogo interno en memoria.
        Implementa la estructura try / except / else.
        """
        try:
            # Comprueba que no exista otro servicio registrado con el mismo ID
            if any(s.id_entidad == servicio.id_entidad for s in self._servicios):
                raise DatoInvalidoError(
                    f"Duplicidad detectada: ya existe un servicio con ID '{servicio.id_entidad}'."
                )
        except SoftwareFJError as error:
            # Registra la anomalía en el archivo de auditoría
            self._logger.registrar_error("Fallo al registrar servicio", error)
            print(f"[ERROR CONTROLADO] {error}")
            return False
        else:
            # Añade el servicio a la lista interna y registra el evento exitoso
            self._servicios.append(servicio)
            self._logger.registrar_evento("INFO", f"Servicio registrado: {servicio.obtener_resumen()}")
            print(f"[OK] {servicio.obtener_resumen()}")
            return True

    def crear_y_confirmar_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        horas: int,
        impuesto_pct: Optional[float] = 19.0,
        descuento_pct: Optional[float] = None,
        recargo_fijo: float = 0.0,
    ) -> Optional[Reserva]:
        """
        Crea y confirma una reserva en una sola transacción controlada.
        Implementa la estructura completa: try / except / else / finally.
        """
        # Variable local para almacenar la instancia si la creación tiene éxito
        nueva_reserva: Optional[Reserva] = None

        try:
            # Busca el cliente en la lista interna por su ID
            cliente = next((c for c in self._clientes if c.id_entidad == id_cliente), None)
            if cliente is None:
                raise DatoInvalidoError(f"El cliente con ID '{id_cliente}' no está registrado.")

            # Busca el servicio en la lista interna por su ID
            servicio = next((s for s in self._servicios if s.id_entidad == id_servicio), None)
            if servicio is None:
                raise ServicioNoDisponibleError(f"El servicio con ID '{id_servicio}' no existe.")

            # Verifica que no exista una reserva previa con el mismo ID
            if any(r.id_entidad == id_reserva for r in self._reservas):
                raise ReservaError(f"Ya existe una reserva registrada con el ID '{id_reserva}'.")

            # Instancia la reserva y ejecuta su confirmación (calcula costos y bloquea servicio)
            nueva_reserva = Reserva(id_reserva, cliente, servicio, horas)
            nueva_reserva.confirmar(
                impuesto_pct=impuesto_pct,
                descuento_pct=descuento_pct,
                recargo_fijo=recargo_fijo,
            )

        except SoftwareFJError as error:
            # Captura cualquier error de negocio, validación o cálculo sin abortar el programa
            self._logger.registrar_error(f"Transacción fallida en reserva '{id_reserva}'", error)
            print(f"[ERROR CONTROLADO] Reserva '{id_reserva}' rechazada: {error}")
            return None
        else:
            # Si la reserva se confirmó sin errores, se persiste en la lista en memoria
            self._reservas.append(nueva_reserva)
            self._logger.registrar_evento("INFO", f"Reserva confirmada: {nueva_reserva.obtener_resumen()}")
            print(f"[OK] {nueva_reserva.obtener_resumen()}")
            return nueva_reserva
        finally:
            # Se ejecuta siempre (haya éxito o error) para dejar traza de auditoría de cierre
            self._logger.registrar_evento(
                "AUDIT", f"Cierre de evaluación transaccional para reserva '{id_reserva}'."
            )

    def procesar_reserva(self, id_reserva: str) -> bool:
        """
        Busca una reserva confirmada y la marca como PROCESADA.
        Implementa try / except / else.
        """
        try:
            # Localiza la reserva en la colección en memoria
            reserva = next((r for r in self._reservas if r.id_entidad == id_reserva), None)
            if reserva is None:
                raise ReservaError(f"No se encontró ninguna reserva con ID '{id_reserva}'.")
            # Ejecuta la transición de estado a PROCESADA
            mensaje_exito = reserva.procesar()
        except SoftwareFJError as error:
            # Registra el intento fallido en el archivo de logs
            self._logger.registrar_error(f"Error al procesar reserva '{id_reserva}'", error)
            print(f"[ERROR CONTROLADO] {error}")
            return False
        else:
            # Registra la confirmación de procesamiento en el log
            self._logger.registrar_evento("INFO", mensaje_exito)
            print(f"[OK] {mensaje_exito}")
            return True

    def cancelar_reserva(self, id_reserva: str) -> bool:
        """
        Cancela una reserva activa si su estado lo permite.
        Implementa try / except / else.
        """
        try:
            # Localiza la reserva en la lista interna
            reserva = next((r for r in self._reservas if r.id_entidad == id_reserva), None)
            if reserva is None:
                raise ReservaError(f"No se encontró ninguna reserva con ID '{id_reserva}'.")
            # Ejecuta la cancelación y liberación del recurso
            reserva.cancelar()
        except SoftwareFJError as error:
            # Registra el error (por ejemplo, si ya estaba procesada)
            self._logger.registrar_error(f"Error al cancelar reserva '{id_reserva}'", error)
            print(f"[ERROR CONTROLADO] {error}")
            return False
        else:
            # Registra la cancelación exitosa
            self._logger.registrar_evento("INFO", f"Reserva '{id_reserva}' cancelada exitosamente.")
            print(f"[OK] Reserva '{id_reserva}' cancelada; el servicio vuelve a estar disponible.")
            return True

    def mostrar_reporte_general(self) -> None:
        """
        Imprime en consola el resumen consolidado de los objetos almacenados
        en memoria al finalizar la ejecución.
        """
        print("\n" + "=" * 75)
        print("REPORTE CONSOLIDADO EN MEMORIA - SOFTWARE FJ")
        print("=" * 75)
        print(f"Clientes registrados en memoria : {len(self._clientes)}")
        print(f"Servicios activos en catálogo   : {len(self._servicios)}")
        print(f"Reservas válidas almacenadas    : {len(self._reservas)}")
        print("-" * 75)
        for reserva in self._reservas:
            print(f" * {reserva.obtener_resumen()}")
        print("=" * 75)