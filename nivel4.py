import random
import pygame
import constantes
from nivel_juego import NivelJuego
from personaje import Personaje
from textos import DamageText
from spawn_multiproceso import GeneradorSpawnsProceso


class Nivel4(NivelJuego):

    def __init__(self, ventana, recursos, numero=4,
                 enemigos_para_ganar=None, intervalo_spawn=None,
                 max_enemigos=None, velocidad_enemigo=None,
                 corazones_para_ganar=6):
        self.corazones_para_ganar = corazones_para_ganar

        enemigos_para_ganar = enemigos_para_ganar or 9999
        super().__init__(ventana, recursos, numero=numero,
                          enemigos_para_ganar=enemigos_para_ganar,
                          intervalo_spawn=intervalo_spawn,
                          max_enemigos=max_enemigos,
                          velocidad_enemigo=velocidad_enemigo)

    def reiniciar(self):
        super().reiniciar()
        self.corazones_recolectados = 0
        self.lista_corazones = self._generar_corazones()

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

    def _generar_corazones(self):
        corazon = self.recursos["corazon_lleno"]
        corazones = []
        margen = 60
        for _ in range(self.corazones_para_ganar):
            x = random.randint(margen, constantes.ANCHO_ventana - margen)
            y = random.randint(margen + 40, constantes.ALTO_ventana - margen)
            rect = corazon.get_rect(center=(x, y))
            corazones.append({"rect": rect, "recolectado": False})
        return corazones

    def _spawnear_enemigo(self):
  
        animaciones_enemigos = self.recursos["animaciones_enemigos"]
        pendientes = self.generador_spawns.obtener_spawns_pendientes()
        if pendientes:
            x, y, tipo = pendientes[0]
            tipo = tipo % len(animaciones_enemigos)
            return Personaje(x, y, animaciones_enemigos[tipo], 100)

        return super()._spawnear_enemigo()

    def _recolectar_corazones(self):
        for corazon in self.lista_corazones:
            if not corazon["recolectado"] and self.jugador.forma.colliderect(corazon["rect"]):
                corazon["recolectado"] = True
                self.corazones_recolectados += 1
                texto = DamageText(corazon["rect"].centerx, corazon["rect"].centery,
                                    "+1", self.recursos["font"], (255, 105, 180))
                self.grupo_damage_text.add(texto)

    def detener_procesos(self):
   
      
        if not self._procesos_detenidos:
            self.generador_spawns.detener()
            self._procesos_detenidos = True

    def update(self):
        super().update()

        self.gano = False
        if not self.perdio:
            self._recolectar_corazones()
            if self.corazones_recolectados >= self.corazones_para_ganar:
                self.gano = True

        if self.gano or self.perdio:
            self.detener_procesos()

    def dibujar(self):
        super().dibujar()
        corazon = self.recursos["corazon_lleno"]
        for c in self.lista_corazones:
            if not c["recolectado"]:
                self.ventana.blit(corazon, c["rect"])

        font = self.recursos["font"]
        txt = font.render(
            f"Corazones: {self.corazones_recolectados}/{self.corazones_para_ganar}",
            True, (255, 105, 180))
        self.ventana.blit(txt, (10, 90))
