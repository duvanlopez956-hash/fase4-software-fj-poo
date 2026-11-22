"""
Módulo: modelos.py
Descripción: Contiene el modelo de dominio orientado a objetos de Software FJ.
Implementa:
- Abstracción (clases abstractas EntidadSistema y Servicio).
- Encapsulación (atributos privados protegidos mediante @property y setters).
- Herencia (tres especializaciones de Servicio).
- Polimorfismo (sobrescritura de validación y cálculo tarifario).
- Sobrecarga funcional (variantes de cálculo de costos con parámetros opcionales).
"""

# Importa ABC y abstractmethod para definir clases y métodos abstractos
from abc import ABC, abstractmethod
# Importa re para validar formatos mediante expresiones regulares (correos)
import re
# Importa Optional para tipado estático de parámetros opcionales
from typing import Optional
# Importa las excepciones personalizadas del dominio
from excepciones import (
    DatoInvalidoError,
    ServicioNoDisponibleError,
    ReservaError,
    CalculoInconsistenteError,
)


class EntidadSistema(ABC):
    """
    Clase abstracta raíz que representa cualquier entidad identificable del sistema.
    Obliga a todas las subclases a poseer un ID válido y un método de resumen.
    """

    def __init__(self, id_entidad: str):
        # Valida que el identificador sea una cadena de texto no vacía
        if not id_entidad or not isinstance(id_entidad, str) or not id_entidad.strip():
            raise DatoInvalidoError("El identificador de la entidad no puede estar vacío.")
        # Almacena el identificador como atributo protegido (encapsulación)
        self._id_entidad = id_entidad.strip()

    @property
    def id_entidad(self) -> str:
        """Propiedad de solo lectura para consultar el identificador de la entidad."""
        return self._id_entidad

    @abstractmethod
    def obtener_resumen(self) -> str:
        """
        Método abstracto que obliga a cada clase derivada a implementar su propia
        representación textual legible.
        """
        pass


class Cliente(EntidadSistema):
    """
    Representa un cliente registrado en Software FJ.
    Aplica encapsulación estricta sobre nombre, correo electrónico y teléfono.
    """

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str):
        # Invoca al constructor de la clase abstracta EntidadSistema
        super().__init__(id_cliente)
        # Asigna los atributos a través de sus setters para activar las validaciones
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        """Getter que retorna el nombre encapsulado del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """Setter que valida que el nombre sea texto con al menos 3 caracteres."""
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre del cliente debe contener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        """Getter que retorna el correo electrónico normalizado."""
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        """Setter que valida la estructura del correo mediante expresión regular."""
        patron_correo = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not valor or not isinstance(valor, str) or not re.match(patron_correo, valor.strip()):
            raise DatoInvalidoError(f"El correo electrónico '{valor}' no tiene un formato válido.")
        # Almacena el correo en minúsculas y sin espacios laterales
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        """Getter que retorna el número telefónico encapsulado."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        """Setter que exige que el teléfono contenga únicamente dígitos (mínimo 7)."""
        if not valor or not isinstance(valor, str) or not valor.strip().isdigit() or len(valor.strip()) < 7:
            raise DatoInvalidoError(
                f"El teléfono '{valor}' es inválido; debe tener al menos 7 dígitos numéricos."
            )
        self._telefono = valor.strip()

    def obtener_resumen(self) -> str:
        """Implementación concreta del método abstracto de EntidadSistema."""
        return f"Cliente [{self.id_entidad}] {self.nombre} | Correo: {self.correo} | Tel: {self.telefono}"


class Servicio(EntidadSistema, ABC):
    """
    Clase abstracta que define la estructura base y el contrato polimórfico
    para todos los servicios ofrecidos por Software FJ.
    """

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, disponible: bool = True):
        # Inicializa el identificador en la superclase
        super().__init__(id_servicio)

        # Valida que el nombre del servicio tenga una longitud mínima coherente
        if not nombre or not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise DatoInvalidoError("El nombre del servicio debe tener al menos 3 caracteres.")

        # Intenta convertir la tarifa base a flotante; si falla, encadena la excepción técnica
        try:
            tarifa_convertida = float(tarifa_base)
        except (TypeError, ValueError) as error_conversion:
            # Encadenamiento de excepciones (raise ... from ...) para conservar la causa raíz
            raise DatoInvalidoError(
                f"La tarifa base '{tarifa_base}' no corresponde a un valor numérico válido."
            ) from error_conversion

        # Verifica que la tarifa sea estrictamente positiva
        if tarifa_convertida <= 0:
            raise DatoInvalidoError("La tarifa base del servicio debe ser mayor a cero.")

        # Almacena los atributos encapsulados
        self._nombre = nombre.strip()
        self._tarifa_base = tarifa_convertida
        self._disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        """Retorna el nombre del servicio."""
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        """Retorna la tarifa base por hora del servicio."""
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        """Indica si el servicio está libre para ser reservado."""
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        """Permite actualizar el estado de disponibilidad del servicio."""
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, horas: int) -> None:
        """
        Método abstracto que cada servicio especializado sobrescribirá
        para validar sus propias reglas de duración o condiciones de uso.
        """
        pass

    @abstractmethod
    def calcular_costo_base(self, horas: int) -> float:
        """
        Método abstracto que cada subclase sobrescribirá para aplicar
        su propia lógica tarifaria (polimorfismo).
        """
        pass

    def calcular_costo_total(
        self,
        horas: int,
        impuesto_pct: Optional[float] = None,
        descuento_pct: Optional[float] = None,
        recargo_fijo: float = 0.0,
    ) -> float:
        """
        Implementación de método sobrecargado mediante parámetros opcionales.
        Permite invocar el cálculo financiero en múltiples variantes:
        1. calcular_costo_total(horas) -> Solo costo base polimórfico.
        2. calcular_costo_total(horas, impuesto_pct=19.0) -> Costo con impuestos.
        3. calcular_costo_total(horas, impuesto_pct=19.0, descuento_pct=10.0, recargo_fijo=5000)
           -> Costo completo con descuentos, recargos e impuestos.
        """
        # Ejecuta la validación específica de la subclase (llamada polimórfica)
        self.validar_parametros(horas)
        # Obtiene el subtotal base según el tipo de servicio (llamada polimórfica)
        subtotal = self.calcular_costo_base(horas)

        # Aplica descuento porcentual si fue suministrado
        if descuento_pct is not None:
            if not (0 <= descuento_pct <= 100):
                raise CalculoInconsistenteError(
                    f"El porcentaje de descuento ({descuento_pct}%) debe estar entre 0 y 100."
                )
            subtotal -= subtotal * (descuento_pct / 100.0)

        # Valida y suma el recargo fijo en caso de existir
        if recargo_fijo < 0:
            raise CalculoInconsistenteError("El recargo fijo no puede ser un valor negativo.")
        subtotal += recargo_fijo

        # Aplica el impuesto porcentual (por ejemplo, IVA) si fue suministrado
        if impuesto_pct is not None:
            if impuesto_pct < 0:
                raise CalculoInconsistenteError("El porcentaje de impuesto no puede ser negativo.")
            subtotal += subtotal * (impuesto_pct / 100.0)

        # Verificación final de consistencia financiera
        if subtotal < 0:
            raise CalculoInconsistenteError("Inconsistencia detectada: el costo final es negativo.")

        # Retorna el monto redondeado a dos cifras decimales
        return round(subtotal, 2)


class ReservaSala(Servicio):
    """
    Servicio especializado 1: Reserva de salas físicas de reuniones o capacitación.
    Hereda de Servicio y sobrescribe validación, cálculo base y resumen.
    """

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, capacidad: int, disponible: bool = True):
        # Inicializa atributos comunes en la clase Servicio
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        # Valida que la capacidad de personas sea un entero positivo
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser un número entero positivo.")
        self._capacidad = capacidad

    def validar_parametros(self, horas: int) -> None:
        """Regla de negocio: las salas se reservan entre 1 y 12 horas máximo."""
        if not isinstance(horas, int) or horas < 1 or horas > 12:
            raise ReservaError("Las salas solo pueden reservarse entre 1 y 12 horas por jornada.")

    def calcular_costo_base(self, horas: int) -> float:
        """
        Cálculo polimórfico: si la capacidad supera las 20 personas, aplica un
        incremento del 10 % por concepto de logística y climatización.
        """
        factor_logistica = 1.10 if self._capacidad > 20 else 1.0
        return self.tarifa_base * horas * factor_logistica

    def obtener_resumen(self) -> str:
        """Descripción polimórfica específica para salas."""
        estado = "Disponible" if self.disponible else "Ocupada"
        return (
            f"Sala [{self.id_entidad}] {self.nombre} (Aforo: {self._capacidad} pers.) "
            f"- ${self.tarifa_base:,.2f}/h [{estado}]"
        )


class AlquilerEquipo(Servicio):
    """
    Servicio especializado 2: Alquiler de hardware, servidores o estaciones gráficas.
    Hereda de Servicio y aplica reglas propias de duración mínima y descuento por volumen.
    """

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, categoria_equipo: str, disponible: bool = True):
        # Inicializa atributos comunes en la clase Servicio
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        # Valida que se indique la categoría técnica del equipo
        if not categoria_equipo or not isinstance(categoria_equipo, str) or not categoria_equipo.strip():
            raise DatoInvalidoError("Debe especificar la categoría del equipo a alquilar.")
        self._categoria_equipo = categoria_equipo.strip()

    def validar_parametros(self, horas: int) -> None:
        """Regla de negocio: el alquiler de hardware requiere un mínimo de 2 horas."""
        if not isinstance(horas, int) or horas < 2:
            raise ReservaError("El alquiler de equipos requiere una duración mínima de 2 horas.")

    def calcular_costo_base(self, horas: int) -> float:
        """
        Cálculo polimórfico: otorga un descuento automático del 15 % cuando
        el alquiler cubre una jornada completa (8 horas o más).
        """
        costo = self.tarifa_base * horas
        if horas >= 8:
            costo *= 0.85
        return costo

    def obtener_resumen(self) -> str:
        """Descripción polimórfica específica para equipos."""
        estado = "Disponible" if self.disponible else "Alquilado"
        return (
            f"Equipo [{self.id_entidad}] {self.nombre} (Categoría: {self._categoria_equipo}) "
            f"- ${self.tarifa_base:,.2f}/h [{estado}]"
        )


class AsesoriaEspecializada(Servicio):
    """
    Servicio especializado 3: Consultoría técnica en ingeniería de software y arquitectura.
    Hereda de Servicio y limita las sesiones a bloques de máximo 8 horas.
    """

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, especialidad: str, disponible: bool = True):
        # Inicializa atributos comunes en la clase Servicio
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        # Valida que el área de especialidad no esté vacía
        if not especialidad or not isinstance(especialidad, str) or not especialidad.strip():
            raise DatoInvalidoError("Debe indicar el área de especialidad de la asesoría.")
        self._especialidad = especialidad.strip()

    def validar_parametros(self, horas: int) -> None:
        """Regla de negocio: las sesiones de consultoría permiten entre 1 y 8 horas."""
        if not isinstance(horas, int) or horas < 1 or horas > 8:
            raise ReservaError("Las asesorías especializadas permiten entre 1 y 8 horas por sesión.")

    def calcular_costo_base(self, horas: int) -> float:
        """Cálculo polimórfico: tarifa directa proporcional a las horas contratadas."""
        return self.tarifa_base * horas

    def obtener_resumen(self) -> str:
        """Descripción polimórfica específica para asesorías."""
        estado = "Disponible" if self.disponible else "Asignada"
        return (
            f"Asesoría [{self.id_entidad}] {self.nombre} (Especialidad: {self._especialidad}) "
            f"- ${self.tarifa_base:,.2f}/h [{estado}]"
        )


class Reserva(EntidadSistema):
    """
    Entidad transaccional que integra un Cliente, un Servicio especializado,
    la duración en horas y el control de estados (PENDIENTE, CONFIRMADA, CANCELADA, PROCESADA).
    """

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion_horas: int):
        # Valida el ID de la reserva en la superclase
        super().__init__(id_reserva)

        # Verifica integridad de tipos de los objetos asociados
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("La reserva requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva requiere una instancia válida de Servicio.")

        # Verifica que el servicio se encuentre disponible antes de crear la reserva
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no está disponible para reservar."
            )

        # Ejecuta la validación polimórfica de duración según el tipo de servicio
        servicio.validar_parametros(duracion_horas)

        # Inicializa los atributos encapsulados de la reserva
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._estado = "PENDIENTE"
        self._costo_final: float = 0.0

    @property
    def estado(self) -> str:
        """Retorna el estado actual de la reserva."""
        return self._estado

    @property
    def costo_final(self) -> float:
        """Retorna el costo total calculado tras la confirmación."""
        return self._costo_final

    def confirmar(
        self,
        impuesto_pct: Optional[float] = 19.0,
        descuento_pct: Optional[float] = None,
        recargo_fijo: float = 0.0,
    ) -> float:
        """
        Calcula el costo total invocando el método sobrecargado del servicio,
        cambia el estado a CONFIRMADA y bloquea la disponibilidad del servicio.
        """
        # Solo una reserva en estado PENDIENTE puede confirmarse
        if self._estado != "PENDIENTE":
            raise ReservaError(
                f"Operación inválida: no se puede confirmar una reserva en estado '{self._estado}'."
            )
        # Revalida disponibilidad del servicio en el instante de confirmación
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.nombre}' ya fue ocupado por otra transacción."
            )

        # Calcula el costo total aplicando impuestos, descuentos o recargos
        self._costo_final = self._servicio.calcular_costo_total(
            horas=self._duracion_horas,
            impuesto_pct=impuesto_pct,
            descuento_pct=descuento_pct,
            recargo_fijo=recargo_fijo,
        )
        # Actualiza el estado de la reserva y marca el servicio como ocupado
        self._estado = "CONFIRMADA"
        self._servicio.disponible = False
        return self._costo_final

    def cancelar(self) -> None:
        """
        Cancela la reserva siempre que no haya sido procesada previamente
        y libera nuevamente el servicio en el catálogo.
        """
        if self._estado == "PROCESADA":
            raise ReservaError("Operación denegada: una reserva PROCESADA no puede cancelarse.")
        if self._estado == "CANCELADA":
            raise ReservaError("La reserva ya se encuentra en estado CANCELADA.")

        # Cambia el estado y restablece la disponibilidad del servicio
        self._estado = "CANCELADA"
        self._servicio.disponible = True

    def procesar(self) -> str:
        """
        Completa el ciclo de vida de una reserva CONFIRMADA, marcándola como PROCESADA
        y liberando el recurso para futuras solicitudes.
        """
        if self._estado != "CONFIRMADA":
            raise ReservaError(
                f"Solo se pueden procesar reservas CONFIRMADAS (estado actual: '{self._estado}')."
            )

        # Finaliza el proceso y libera el servicio
        self._estado = "PROCESADA"
        self._servicio.disponible = True
        return (
            f"Reserva {self.id_entidad} procesada satisfactoriamente. "
            f"Total facturado: ${self._costo_final:,.2f}."
        )

    def obtener_resumen(self) -> str:
        """Retorna el detalle completo de la reserva para reportes y logs."""
        return (
            f"Reserva [{self.id_entidad}] | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | Tiempo: {self._duracion_horas}h | "
            f"Estado: {self._estado} | Total: ${self._costo_final:,.2f}"
        )