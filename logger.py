"""
Módulo: logger.py
Descripción: Implementa el componente de auditoría y persistencia en archivo plano.
Registra todos los eventos operativos y excepciones capturadas sin detener la
ejecución principal del programa.
"""

# Importa datetime para estampar fecha y hora exacta en cada línea del log
from datetime import datetime


class RegistradorLogs:
    """
    Clase encargada de administrar la escritura segura en un archivo de texto (.log)
    mediante manejo explícito de recursos y bloques try/except/finally.
    """

    def __init__(self, ruta_archivo: str = "sistema_fj.log"):
        # Define la ruta o nombre del archivo plano donde se guardarán los registros
        self.ruta_archivo = ruta_archivo

    def registrar_evento(self, nivel: str, mensaje: str) -> None:
        """
        Escribe una entrada formateada en el archivo de logs.
        Parámetros:
            nivel (str): Categoría del evento (INFO, AUDIT, ERROR, START, END).
            mensaje (str): Descripción detallada del suceso ocurrido.
        """
        # Obtiene la marca de tiempo actual en formato Año-Mes-Día Hora:Minuto:Segundo
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Construye la línea estructurada que se escribirá en el archivo
        linea = f"[{marca_tiempo}] [{nivel.upper()}] {mensaje}\n"

        # Inicializa la referencia del archivo en None antes de intentar abrirlo
        archivo = None
        try:
            # Abre el archivo en modo 'a' (append/añadir) con codificación UTF-8
            archivo = open(self.ruta_archivo, mode="a", encoding="utf-8")
            # Escribe la línea de auditoría al final del archivo
            archivo.write(linea)
        except OSError as error_io:
            # Captura posibles fallos de entrada/salida (permisos, disco lleno, ruta inválida)
            # sin permitir que el programa colapse
            print(f"[FALLO CRÍTICO DE LOG] No se pudo escribir en el archivo: {error_io}")
        finally:
            # El bloque finally garantiza el cierre seguro del descriptor de archivo
            # sin importar si la escritura fue exitosa o lanzó una excepción
            if archivo is not None and not archivo.closed:
                archivo.close()

    def registrar_error(self, contexto: str, excepcion: Exception) -> None:
        """
        Formatea y registra una excepción capturada, incluyendo su excepción original
        en caso de existir encadenamiento (raise ... from ...).
        """
        # Variable auxiliar para almacenar información de la causa raíz si existe
        detalle_causa = ""
        # Verifica el atributo __cause__ generado por el encadenamiento de excepciones
        if excepcion.__cause__ is not None:
            nombre_causa = type(excepcion.__cause__).__name__
            detalle_causa = f" | Causa encadenada: {nombre_causa}: {excepcion.__cause__}"

        # Construye el mensaje completo combinando contexto, tipo de error y causa raíz
        mensaje_completo = (
            f"{contexto} -> {type(excepcion).__name__}: {excepcion}{detalle_causa}"
        )
        # Delega la escritura física al método registrar_evento con nivel ERROR
        self.registrar_evento("ERROR", mensaje_completo)