import multiprocessing
import random
import time

def _generar_datos_spawn(ancho, alto, margen, cantidad_tipos):
    """Calcula una sola posicion de aparicion (x, y) fuera de la pantalla
    y un tipo de enemigo. Es una funcion pura basada solo en numeros,
    por eso puede vivir tranquila dentro de otro proceso."""
    lado = random.randint(0, 3)

    if lado == 0:
        x = random.randint(0, ancho)
        y = -margen
    elif lado == 1:
        x = random.randint(0, ancho)
        y = alto + margen
    elif lado == 2:
        x = -margen
        y = random.randint(0, alto)
    else:
        x = ancho + margen
        y = random.randint(0, alto)

    tipo = random.randint(0, cantidad_tipos - 1)
    return x, y, tipo


def proceso_generador_spawns(queue_salida, ancho, alto, margen, cantidad_tipos, intervalo_ms):
    """
    Punto de entrada del PROCESO SECUNDARIO (esto es lo que recibe
    multiprocessing.Process como 'target'). Corre en un bucle infinito
    mientras el proceso este vivo, calculando datos de spawn y
    depositandolos en la Queue para que el proceso principal los use.

    El proceso principal es quien decide cuando terminarlo (ver
    GeneradorSpawnsProceso.detener), por eso este bucle no necesita
    condicion de salida propia.
    """
    random.seed()  # cada proceso hijo debe tener su propia semilla aleatoria
    while True:
        dato = _generar_datos_spawn(ancho, alto, margen, cantidad_tipos)
        queue_salida.put(dato)
        time.sleep(intervalo_ms / 1000)


class GeneradorSpawnsProceso:
    """
    Envoltorio (wrapper) que administra el ciclo de vida del proceso
    secundario encargado de calcular posiciones de aparicion de enemigos.

    Uso tipico dentro de un nivel:
        self.generador_spawns = GeneradorSpawnsProceso(ancho, alto, margen, tipos)
        self.generador_spawns.iniciar()
        ...
        pendientes = self.generador_spawns.obtener_spawns_pendientes()
        ...
        self.generador_spawns.detener()   # al ganar, perder o salir del nivel
    """

    def __init__(self, ancho, alto, margen, cantidad_tipos, intervalo_ms=400):
        self.queue_salida = multiprocessing.Queue()
        self.proceso = multiprocessing.Process(
            target=proceso_generador_spawns,
            args=(self.queue_salida, ancho, alto, margen, cantidad_tipos, intervalo_ms),
            daemon=True,  # si el proceso principal termina, este no queda huerfano
        )
        self._iniciado = False

    def iniciar(self):
        if not self._iniciado:
            self.proceso.start()
            self._iniciado = True

    def obtener_spawns_pendientes(self):
        """Lee, SIN bloquear el bucle de pygame, todos los datos de spawn
        que el proceso secundario ya haya calculado hasta este momento."""
        spawns = []
        while not self.queue_salida.empty():
            try:
                spawns.append(self.queue_salida.get_nowait())
            except Exception:
                break
        return spawns

    def detener(self):
        """Termina el proceso secundario de forma ordenada. Se debe llamar
        al ganar, perder o abandonar el nivel para no dejar procesos
        calculando datos que ya nadie va a leer."""
        if self._iniciado and self.proceso.is_alive():
            self.proceso.terminate()
            self.proceso.join(timeout=1)
        self._iniciado = False
