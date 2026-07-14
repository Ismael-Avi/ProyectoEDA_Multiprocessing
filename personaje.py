import math
import pygame
import constantes

class Personaje():
    def __init__(self, x, y, animaciones, energia):
        self.energia = energia
        self.flip = False
        self.vivo = True
        self.animaciones = animaciones
        self.frame_index = 0
        self.udate_time = pygame.time.get_ticks()
        self.image = animaciones[self.frame_index]
        self.forma = self.image.get_rect()
        self.forma.center = (x, y)

        # Cooldown de ataque (para enemigos): empieza listo para atacar
        self.ultimo_ataque = pygame.time.get_ticks() - constantes.COOLDOWN_ATAQUE_ENEMIGO

    def movimiento(self, delta_x, delta_y):
        if delta_x < 0:
            self.flip = True
        if delta_x > 0:
            self.flip = False
        self.forma.x = self.forma.x + delta_x
        self.forma.y = self.forma.y + delta_y

    # mueve enemigo hacia el jugador
    def mover_hacia(self, objetivo, velocidad=None):
        if velocidad is None:
            velocidad = constantes.VELOCIDAD_ENEMIGO
        dx = objetivo.forma.centerx - self.forma.centerx
        dy = objetivo.forma.centery - self.forma.centery
        distancia = math.sqrt(dx**2 + dy**2)
        if distancia > 0:
            dx = (dx / distancia) * velocidad
            dy = (dy / distancia) * velocidad
            self.movimiento(dx, dy)

    #  intenta atacar al objetivo; devuelve el daño causado
    def atacar(self, objetivo):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_ataque >= constantes.COOLDOWN_ATAQUE_ENEMIGO:
            objetivo.energia -= constantes.DAÑO_ENEMIGO
            self.ultimo_ataque = ahora
            return constantes.DAÑO_ENEMIGO
        return 0

    def update(self):
        # Comprobar si sigue vivo
        if self.energia <= 0:
            self.energia = 0
            self.vivo = False
        cooldown_animacion = 100
        self.image = self.animaciones[self.frame_index]
        if pygame.time.get_ticks() - self.udate_time >= cooldown_animacion:
            self.frame_index = self.frame_index + 1
            self.udate_time = pygame.time.get_ticks()
            if self.frame_index >= len(self.animaciones):
                self.frame_index = 0

    def dibujar(self, interfaz):
        image_flip = pygame.transform.flip(self.image, self.flip, False)
        interfaz.blit(image_flip, self.forma)
        pygame.draw.rect(interfaz, constantes.COLOR_ARMA, self.forma, 1)