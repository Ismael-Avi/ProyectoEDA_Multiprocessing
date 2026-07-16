import pygame
import constantes
from menu import NodoBoton, GrafoMenu
from nivel_juego import NivelJuego
from nivel_juego123 import NivelJuego
from nivel4 import Nivel4
from nivel5 import Nivel5
from nivel6 import Nivel6
# ============================================================
# PARA AGREGAR TU NIVEL:
# 1. Crea tu clase de nivel en tu propio archivo (ej: nivel4.py)
# 2. Tu clase DEBE tener estos métodos/atributos:
#       - manejar_evento(self, event)
#       - update(self)
#       - dibujar(self)
#       - self.gano   (True/False)
#       - self.perdio (True/False)
# 3. Importa tu clase arriba del archivo (junto al import de NivelJuego)
# 4. Reemplaza tu NodoNivel(None) de abajo por:
#    NodoNivel(4, fabrica_nivel=lambda: TuClase(self.ventana))
# NO cambies el número que ya tiene asignado tu NodoNivel.
# ============================================================

class NodoNivel:

    def __init__(self, numero, fabrica_nivel=None):
        self.numero = numero
        self.fabrica_nivel = fabrica_nivel
        self.desbloqueado = False
        self.conexiones = []

    def agregar_conexion(self, otro_nivel):
        self.conexiones.append(otro_nivel)


class SelectorNiveles:

    def __init__(self, ventana, recursos, niveles_desbloqueados=9):
        self.ventana = ventana
        self.recursos = recursos
        self.font_titulo = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 32)
        self.font_boton = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 22)

        self.completados = set()  # niveles ya ganados, para el desbloqueo progresivo

        self.nodos_nivel = [
            NodoNivel(1, fabrica_nivel=lambda: NivelJuego(
                    self.ventana, self.recursos, numero=4,
                    enemigos_para_ganar=5, intervalo_spawn=1000,
                    max_enemigos=2, velocidad_enemigo=2.5)),
            NodoNivel(2, fabrica_nivel=lambda: NivelJuego(
                    self.ventana, self.recursos, numero=4,
                    enemigos_para_ganar=6, intervalo_spawn=1500,
                    max_enemigos=4, velocidad_enemigo=2.5)),
            NodoNivel(3, fabrica_nivel=lambda: NivelJuego(
                    self.ventana, self.recursos, numero=4,
                    enemigos_para_ganar=8, intervalo_spawn=1900,
                    max_enemigos=5, velocidad_enemigo=2.5)),
            NodoNivel(4, fabrica_nivel=lambda: Nivel4(
                    self.ventana, self.recursos, numero=4,
                    intervalo_spawn=1800, max_enemigos=4,
                    velocidad_enemigo=1.6, corazones_para_ganar=6)),

            NodoNivel(5, fabrica_nivel=lambda: Nivel5(
                    self.ventana, self.recursos, numero=5,
                    enemigos_para_ganar=10, intervalo_spawn=1500,
                    max_enemigos=6, velocidad_enemigo=2.2)),

            NodoNivel(6, fabrica_nivel=lambda: Nivel6(
                    self.ventana, self.recursos, numero=6,
                    intervalo_spawn=4000, max_enemigos=4,
                    velocidad_enemigo=1.8, vida_jefe=400)),

            NodoNivel(7, fabrica_nivel=lambda: NivelJuego(
                self.ventana, self.recursos, numero=7,
                enemigos_para_ganar=15, intervalo_spawn=3000,
                max_enemigos=8, velocidad_enemigo=2)),

            NodoNivel(8, fabrica_nivel=lambda: NivelJuego(
                self.ventana, self.recursos, numero=8,
                enemigos_para_ganar=25, intervalo_spawn=2000,
                max_enemigos=10, velocidad_enemigo=3)),

            NodoNivel(9, fabrica_nivel=lambda: NivelJuego(
                self.ventana, self.recursos, numero=9,
                enemigos_para_ganar=40, intervalo_spawn=1200,
                max_enemigos=12, velocidad_enemigo=4)),
        ]

        for i in range(len(self.nodos_nivel) - 1):
            self.nodos_nivel[i].agregar_conexion(self.nodos_nivel[i + 1])

        self.actualizar_desbloqueo(niveles_desbloqueados)

    def actualizar_desbloqueo(self, niveles_desbloqueados):
        self.desbloqueados = niveles_desbloqueados
        for nodo in self.nodos_nivel:
            nodo.desbloqueado = nodo.numero <= niveles_desbloqueados
        self._armar_botones()

    def marcar_completado(self, numero):

        self.completados.add(numero)
        if self.desbloqueados == 3 and {1, 2, 3} <= self.completados:
            self.actualizar_desbloqueo(6)
        elif self.desbloqueados == 6 and {1, 2, 3, 4, 5, 6} <= self.completados:
            self.actualizar_desbloqueo(9)

    def _armar_botones(self):
        self.grafo = GrafoMenu()
        ancho = self.ventana.get_width()

        cols = 3
        tam = 80
        gap = 20
        inicio_x = ancho // 2 - (cols * tam + (cols - 1) * gap) // 2
        inicio_y = 180

        for idx, nodo in enumerate(self.nodos_nivel):
            fila = idx // cols
            col = idx % cols
            x = inicio_x + col * (tam + gap)
            y = inicio_y + fila * (tam + gap)

            if nodo.desbloqueado:
                color = (40, 120, 40)
                color_hover = (60, 170, 60)
            else:
                color = (50, 50, 50)
                color_hover = (50, 50, 50)

            boton = NodoBoton(str(nodo.numero), x, y, tam, tam,
                               self.font_boton, color, color_hover,
                               id_destino=nodo.numero, habilitado=nodo.desbloqueado)
            self.grafo.agregar_nodo(boton)


        boton_menu = NodoBoton(
            "MENU", 20, 20, 140, 50,
            self.font_boton, (80, 80, 80), (110, 110, 110), "MENU"
        )
        self.grafo.agregar_nodo(boton_menu)

    def dibujar(self):
        self.ventana.fill(constantes.COLOR_BG)
        titulo = self.font_titulo.render("SELECCIONA UN NIVEL", True, (255, 255, 0))
        titulo_rect = titulo.get_rect(center=(self.ventana.get_width() // 2, 100))
        self.ventana.blit(titulo, titulo_rect)
        self.grafo.dibujar(self.ventana)

    def manejar_click(self, pos):

        return self.grafo.procesar_click(pos)

    def obtener_nodo(self, numero_nivel):
        return self.nodos_nivel[numero_nivel - 1]
