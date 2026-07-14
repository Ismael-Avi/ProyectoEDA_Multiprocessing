import random
import pygame
import constantes
from personaje import Personaje
from weapon import Weapon
from textos import DamageText
# Esta es la clase que usa Jose para los niveles 7, 8 y 9.
# No es obligatorio copiar esta estructura — es solo un EJEMPLO
# de cómo cumplir el contrato pedido en selector_niveles.py.

class NivelJuego:

    def __init__(self, ventana, recursos, numero=1,
                 enemigos_para_ganar=None, intervalo_spawn=None,
                 max_enemigos=None, velocidad_enemigo=None):
        self.ventana = ventana
        self.recursos = recursos
        self.numero = numero


        self.enemigos_para_ganar = enemigos_para_ganar or constantes.ENEMIGOS_PARA_GANAR
        self.intervalo_spawn = intervalo_spawn or constantes.INTERVALO_SPAWN
        self.max_enemigos = max_enemigos or constantes.MAX_ENEMIGOS
        self.velocidad_enemigo = velocidad_enemigo or constantes.VELOCIDAD_ENEMIGO

        self.gano = False
        self.perdio = False

        self.mover_arriba = False
        self.mover_abajo = False
        self.mover_izquierda = False
        self.mover_derecha = False

        self.reiniciar()

    def reiniciar(self):
        animaciones = self.recursos["animaciones"]
        self.jugador = Personaje(100, 50, animaciones, 100)

        animaciones_enemigos = self.recursos["animaciones_enemigos"]
        self.lista_enemigos = [
            Personaje(400, 300, animaciones_enemigos[0], 100),
            Personaje(200, 200, animaciones_enemigos[1 % len(animaciones_enemigos)], 100),
        ]

        self.pistola = Weapon(self.recursos["imagen_pistola"], self.recursos["imagen_bala"])
        self.grupo_damage_text = pygame.sprite.Group()
        self.grupos_balas = pygame.sprite.Group()

        self.tiempo_ultimo_spawn = pygame.time.get_ticks()
        self.enemigos_eliminados = 0
        self.gano = False
        self.perdio = False

    def manejar_evento(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.mover_izquierda = True
            if event.key == pygame.K_d:
                self.mover_derecha = True
            if event.key == pygame.K_w:
                self.mover_arriba = True
            if event.key == pygame.K_s:
                self.mover_abajo = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.mover_izquierda = False
            if event.key == pygame.K_d:
                self.mover_derecha = False
            if event.key == pygame.K_w:
                self.mover_arriba = False
            if event.key == pygame.K_s:
                self.mover_abajo = False

    def _spawnear_enemigo(self):
        lado = random.randint(0, 3)
        m = constantes.MARGEN_SPAWN

        if lado == 0:
            x = random.randint(0, constantes.ANCHO_ventana)
            y = -m
        elif lado == 1:
            x = random.randint(0, constantes.ANCHO_ventana)
            y = constantes.ALTO_ventana + m
        elif lado == 2:
            x = -m
            y = random.randint(0, constantes.ALTO_ventana)
        else:
            x = constantes.ANCHO_ventana + m
            y = random.randint(0, constantes.ALTO_ventana)

        animaciones_enemigos = self.recursos["animaciones_enemigos"]
        tipo = random.randint(0, len(animaciones_enemigos) - 1)
        return Personaje(x, y, animaciones_enemigos[tipo], 100)

    def update(self):
        ahora = pygame.time.get_ticks()

        # 1. SPAWN (limitado a max_enemigos en pantalla al mismo tiempo)
        if (len(self.lista_enemigos) < self.max_enemigos and
                ahora - self.tiempo_ultimo_spawn >= self.intervalo_spawn):
            self.lista_enemigos.append(self._spawnear_enemigo())
            self.tiempo_ultimo_spawn = ahora

        # 2. MOVIMIENTO DEL JUGADOR
        delta_x = 0
        delta_y = 0
        if self.mover_derecha:
            delta_x = constantes.VELOCIDAD
        if self.mover_izquierda:
            delta_x = -constantes.VELOCIDAD
        if self.mover_arriba:
            delta_y = -constantes.VELOCIDAD
        if self.mover_abajo:
            delta_y = constantes.VELOCIDAD

        self.jugador.movimiento(delta_x, delta_y)
        self.jugador.update()

        # 3. IA ENEMIGOS
        for ene in self.lista_enemigos:
            ene.update()
            ene.mover_hacia(self.jugador, self.velocidad_enemigo)

            if ene.forma.colliderect(self.jugador.forma):
                daño = ene.atacar(self.jugador)
                if daño > 0:
                    texto = DamageText(self.jugador.forma.centerx, self.jugador.forma.centery,
                                       daño, self.recursos["font"], constantes.ROJO_JUGADOR)
                    self.grupo_damage_text.add(texto)

        # 4. ELIMINAR MUERTOS Y CONTAR
        cantidad_antes = len(self.lista_enemigos)
        self.lista_enemigos = [e for e in self.lista_enemigos if e.vivo]
        self.enemigos_eliminados += (cantidad_antes - len(self.lista_enemigos))

        # 5. BALAS
        bala = self.pistola.update(self.jugador)
        if bala:
            self.grupos_balas.add(bala)

        for bala in self.grupos_balas:
            damage, pos_damage = bala.update(self.lista_enemigos)
            if damage:
                damage_text = DamageText(pos_damage.centerx, pos_damage.centery,
                                         damage, self.recursos["font"], constantes.ROJO)
                self.grupo_damage_text.add(damage_text)

        self.grupo_damage_text.update()

        # 6. CONDICIONES DE FIN DE NIVEL
        if not self.jugador.vivo:
            self.perdio = True
        elif self.enemigos_eliminados >= self.enemigos_para_ganar:
            self.gano = True

    def _dibujar_vida(self):
        corazon_vacio = self.recursos["corazon_vacio"]
        corazon_medio = self.recursos["corazon_medio"]
        corazon_lleno = self.recursos["corazon_lleno"]

        c_medio_dibujado = False
        for i in range(4):
            if self.jugador.energia >= ((i + 1) * 25):
                self.ventana.blit(corazon_lleno, (5 + i * 50, 5))
            elif self.jugador.energia % 25 > 0 and not c_medio_dibujado:
                self.ventana.blit(corazon_medio, (5 + i * 50, 5))
                c_medio_dibujado = True
            else:
                self.ventana.blit(corazon_vacio, (5 + i * 50, 5))

    def dibujar(self):
        self.ventana.fill(constantes.COLOR_BG)

        self.jugador.dibujar(self.ventana)
        for ene in self.lista_enemigos:
            ene.dibujar(self.ventana)
        self.pistola.dibujar(self.ventana)
        for bala in self.grupos_balas:
            bala.dibujar(self.ventana)

        self._dibujar_vida()
        self.grupo_damage_text.draw(self.ventana)

        font = self.recursos["font"]
        txt_nivel = font.render(f"Nivel {self.numero}", True, (200, 200, 200))
        self.ventana.blit(txt_nivel, (10, 60))

        txt_ene = font.render(
            f"Eliminados: {self.enemigos_eliminados}/{self.enemigos_para_ganar}",
            True, (200, 200, 200))
        self.ventana.blit(txt_ene, (constantes.ANCHO_ventana - txt_ene.get_width() - 10, 10))
        txt_ayuda = font.render("ESC: pausar", True, (150, 150, 150))
        self.ventana.blit(
            txt_ayuda,
            (constantes.ANCHO_ventana - txt_ayuda.get_width() - 10,
             constantes.ALTO_ventana - txt_ayuda.get_height() - 10)
        )