import random
import pygame
import constantes
from nivel_juego import NivelJuego
from personaje import Personaje
from textos import DamageText
from spawn_multiproceso import GeneradorSpawnsProceso

COLOR_BARRA_FONDO = (60, 60, 60)
COLOR_BARRA_VIDA = (200, 30, 30)
DAÑO_JEFE = 20
COOLDOWN_ATAQUE_JEFE = 700
ESCALA_JEFE = 2.4


class Nivel6(NivelJuego):

    def __init__(self, ventana, recursos, numero=6,
                 intervalo_spawn=None, max_enemigos=None,
                 velocidad_enemigo=None, vida_jefe=400):
        self.vida_jefe = vida_jefe

        super().__init__(ventana, recursos, numero=numero,
                          enemigos_para_ganar=9999,
                          intervalo_spawn=intervalo_spawn,
                          max_enemigos=max_enemigos,
                          velocidad_enemigo=velocidad_enemigo)

    def reiniciar(self):
        super().reiniciar()

        self.lista_enemigos = []

        animaciones_enemigos = self.recursos["animaciones_enemigos"]
        animaciones_jefe_base = animaciones_enemigos[-1]
        animaciones_jefe = [
            pygame.transform.scale(
                img,
                (int(img.get_width() * ESCALA_JEFE), int(img.get_height() * ESCALA_JEFE))
            )
            for img in animaciones_jefe_base
        ]

        self.jefe = Personaje(constantes.ANCHO_ventana // 2, 120, animaciones_jefe, self.vida_jefe)
        self.jefe.ultimo_ataque = pygame.time.get_ticks() - COOLDOWN_ATAQUE_JEFE

        self.fase_actual = 1


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
            return Personaje(x, y, animaciones_enemigos[tipo], 60)
        return super()._spawnear_enemigo()

    def _invocar_minions_si_corresponde(self):
        progreso_vida = self.jefe.energia / self.vida_jefe
        if progreso_vida <= 0.5 and self.fase_actual == 1:
            self.fase_actual = 2
            self.max_enemigos += 2
        if progreso_vida <= 0.2 and self.fase_actual == 2:
            self.fase_actual = 3
            self.max_enemigos += 2

    def _actualizar_jefe(self):
        if not self.jefe.vivo:
            return

        self.jefe.update()
        self.jefe.mover_hacia(self.jugador, self.velocidad_enemigo * 0.8)

        if self.jefe.forma.colliderect(self.jugador.forma):
            ahora = pygame.time.get_ticks()
            if ahora - self.jefe.ultimo_ataque >= COOLDOWN_ATAQUE_JEFE:
                self.jugador.energia -= DAÑO_JEFE
                self.jefe.ultimo_ataque = ahora
                texto = DamageText(self.jugador.forma.centerx, self.jugador.forma.centery,
                                    DAÑO_JEFE, self.recursos["font"], constantes.ROJO_JUGADOR)
                self.grupo_damage_text.add(texto)
                if self.jugador.energia <= 0:
                    self.jugador.energia = 0
                    self.jugador.vivo = False

        for bala in self.grupos_balas:
            if self.jefe.forma.colliderect(bala.rect):
                daño = 15 + random.randint(-7, 7)
                self.jefe.energia -= daño
                texto = DamageText(self.jefe.forma.centerx, self.jefe.forma.centery,
                                    daño, self.recursos["font"], constantes.ROJO)
                self.grupo_damage_text.add(texto)
                bala.kill()

        if self.jefe.energia <= 0:
            self.jefe.energia = 0
            self.jefe.vivo = False

    def detener_procesos(self):
        if not self._procesos_detenidos:
            self.generador_spawns.detener()
            self._procesos_detenidos = True

    def update(self):
        super().update()
        self.gano = False

        if not self.perdio:
            self._actualizar_jefe()
            self._invocar_minions_si_corresponde()
            if not self.jefe.vivo:
                self.gano = True
            if not self.jugador.vivo:
                self.perdio = True

        if self.gano or self.perdio:
            self.detener_procesos()

    def _dibujar_barra_jefe(self):
        ancho_barra = 400
        alto_barra = 22
        x = constantes.ANCHO_ventana // 2 - ancho_barra // 2
        y = 20
        progreso = max(0, self.jefe.energia) / self.vida_jefe

        pygame.draw.rect(self.ventana, COLOR_BARRA_FONDO, (x, y, ancho_barra, alto_barra))
        pygame.draw.rect(self.ventana, COLOR_BARRA_VIDA, (x, y, int(ancho_barra * progreso), alto_barra))
        pygame.draw.rect(self.ventana, (255, 255, 255), (x, y, ancho_barra, alto_barra), 2)

        font = self.recursos["font"]
        txt = font.render(f"JEFE - Fase {self.fase_actual}", True, (255, 255, 255))
        txt_rect = txt.get_rect(center=(constantes.ANCHO_ventana // 2, y + alto_barra + 16))
        self.ventana.blit(txt, txt_rect)

    def dibujar(self):
        super().dibujar()
        
        pygame.draw.rect(self.ventana, constantes.COLOR_BG,
                          (constantes.ANCHO_ventana - 300, 0, 300, 35))

        if self.jefe.vivo:
            self.jefe.dibujar(self.ventana)
        self._dibujar_barra_jefe()
