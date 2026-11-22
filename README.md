# fase4-software-fj-poo
Sistema Integral de Gestión de Clientes, Servicios y Reservas - POO y Manejo de Excepciones (UNAD)
# Sistema Integral de Gestión de Clientes, Servicios y Reservas – Software FJ

Proyecto desarrollado para la **Fase 4** del curso de **Programación** (Universidad Nacional Abierta y a Distancia – UNAD).

## Descripción del Proyecto

Aplicación orientada a objetos desarrollada en **Python** (sin uso de motores de bases de datos) para la empresa **Software FJ**, diseñada para gestionar el registro de clientes, el catálogo de servicios especializados (reserva de salas, alquiler de equipos y asesorías especializadas) y el ciclo de vida completo de las reservas.

El sistema garantiza estabilidad y continuidad operativa mediante una arquitectura modular y manejo avanzado de excepciones, registrando cada evento y anomalía en un archivo plano de auditoría (`sistema_fj.log`).

## Características Principales

* **Programación Orientada a Objetos (POO):**
  * **Abstracción:** Clases base abstractas (`EntidadSistema` y `Servicio`) con contratos obligatorios.
  * **Encapsulación:** Validación estricta de atributos privados mediante decoradores `@property` y *setters* con expresiones regulares.
  * **Herencia y Polimorfismo:** Especialización de tres líneas de negocio (`ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada`) con reglas propias de validación y cálculo tarifario.
  * **Sobrecarga funcional:** Cálculo de costos con parámetros opcionales para impuestos, descuentos porcentuales y recargos fijos.
* **Manejo Avanzado de Excepciones:** Jerarquía de errores personalizados (`SoftwareFJError`), bloques `try/except`, `try/except/else`, `try/except/finally` y encadenamiento de excepciones (`raise ... from ...`).
* **Auditoría sin Base de Datos:** Gestión de colecciones en memoria y persistencia de eventos y trazas de error en el archivo `sistema_fj.log`.

## Estructura del Repositorio

```text
├── excepciones.py   # Jerarquía de excepciones personalizadas del dominio
├── logger.py        # Registrador de eventos y errores en archivo plano (.log)
├── modelos.py       # Clases abstractas, Cliente, Servicios especializados y Reserva
├── gestor.py        # Controlador central en memoria con bloques try/except/else/finally
├── main.py          # Punto de entrada con simulación secuencial de 12 operaciones
├── sistema_fj.log   # Archivo de auditoría generado tras la ejecución
└── README.md        # Documentación general del repositorio
