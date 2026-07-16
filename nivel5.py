import math
import pygame
import constantes
from nivel_juego import NivelJuego
from personaje import Personaje
from textos import DamageText
from spawn_multiproceso import GeneradorSpawnsProceso

COLOR_ZONA = (255, 255, 0)
COLOR_TORMENTA = (170, 60, 220)
DAÑO_TORMENTA = 5
COOLDOWN_DAÑO_TORMENTA = 800  
RADIO_INICIAL = 260
RADIO_MINIMO = 90
TIEMPO_ENCOGIMIENTO = 25000   


class Nivel5(NivelJuego):

    def __init__(self, ventana, recursos, numero=5,
                 enemigos_para_ganar=None, intervalo_spawn=None,
                 max_enemigos=None, velocidad_enemigo=None):
        super().__init__(ventana, recursos, numero=numero,
                          enemigos_para_ganar=enemigos_para_ganar,
                          intervalo_spawn=intervalo_spawn,
                          max_enemigos=max_enemigos,
                          velocidad_enemigo=velocidad_enemigo)

    def reiniciar(self):
        super().reiniciar()
        self.centro_zona = (constantes.ANCHO_ventana // 2, constantes.ALTO_ventana // 2)
        self.radio_zona = RADIO_INICIAL
        self.tiempo_inicio_zona = pygame.time.get_ticks()
        self.ultimo_daño_tormenta = pygame.time.get_ticks()


        animaciones_enemigos = self.recursos["animaciones_enemigos"]
        self.generador_spawns = GeneradorSpawnsProceso(
            ancho=constantes.ANCHO_ventana,
            alto=constantes.ALTO_ventana,
            margen=constantes.MARGEN_SPAWN,
            cantidad_tipos=len(animaciones_enemigos),
            intervalo_ms=self.intervalo_spawn,
        )
        self.generador_spawns.iniciar()
        self._procesos_detenidos = False

    def _spawnear_enemigo(self):
        animaciones_enemigos = self.recursos["animaciones_enemigos"]
        pendientes = self.generador_spawns.obtener_spawns_pendientes()
        if pendientes:
            x, y, tipo = pendientes[0]
            tipo = tipo % len(animaciones_enemigos)
            return Personaje(x, y, animaciones_enemigos[tipo], 100)
        return super()._spawnear_enemigo()

    def _actualizar_zona(self):
        transcurrido = pygame.time.get_ticks() - self.tiempo_inicio_zona
        progreso = min(1.0, transcurrido / TIEMPO_ENCOGIMIENTO)
        self.radio_zona = RADIO_INICIAL - (RADIO_INICIAL - RADIO_MINIMO) * progreso

    def _aplicar_daño_tormenta(self):
        dx = self.jugador.forma.centerx - self.centro_zona[0]
        dy = self.jugador.forma.centery - self.centro_zona[1]
        distancia = math.hypot(dx, dy)

        if distancia > self.radio_zona:
            ahora = pygame.time.get_ticks()
            if ahora - self.ultimo_daño_tormenta >= COOLDOWN_DAÑO_TORMENTA:
                self.jugador.energia -= DAÑO_TORMENTA
                self.ultimo_daño_tormenta = ahora
                texto = DamageText(self.jugador.forma.centerx, self.jugador.forma.centery,
                                    DAÑO_TORMENTA, self.recursos["font"], COLOR_TORMENTA)
                self.grupo_damage_text.add(texto)
                if self.jugador.energia <= 0:
                    self.jugador.energia = 0
                    self.jugador.vivo = False

    def detener_procesos(self):
        if not self._procesos_detenidos:
            self.generador_spawns.detener()
            self._procesos_detenidos = True

    def update(self):
        super().update()
        if not self.perdio and not self.gano:
            self._actualizar_zona()
            self._aplicar_daño_tormenta()
            if not self.jugador.vivo:
                self.perdio = True

        if self.gano or self.perdio:
            self.detener_procesos()

    def dibujar(self):
        super().dibujar()
        pygame.draw.circle(self.ventana, COLOR_ZONA, self.centro_zona,
                            int(self.radio_zona), 3)

        font = self.recursos["font"]
        txt = font.render("Mantente dentro del circulo", True, COLOR_ZONA)
        self.ventana.blit(txt, (10, 90))
