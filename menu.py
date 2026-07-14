import pygame
import constantes

class NodoBoton:

    def __init__(self, texto, x, y, ancho, alto, font, color, color_hover,
                 id_destino, habilitado=True):
        self.texto = texto
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.font = font
        self.color = color
        self.color_hover = color_hover
        self.id_destino = id_destino
        self.habilitado = habilitado
        self.conexiones = []

    def agregar_conexion(self, nodo):
        self.conexiones.append(nodo)

    def dibujar(self, ventana):
        mouse_pos = pygame.mouse.get_pos()
        if not self.habilitado:
            color_actual = (50, 50, 50)
        else:
            color_actual = self.color_hover if self.rect.collidepoint(mouse_pos) else self.color

        pygame.draw.rect(ventana, color_actual, self.rect, border_radius=10)
        pygame.draw.rect(ventana, (255, 255, 255), self.rect, 2, border_radius=10)
        texto_render = self.font.render(self.texto, True, (255, 255, 255))
        texto_rect = texto_render.get_rect(center=self.rect.center)
        ventana.blit(texto_render, texto_rect)

    def fue_clickeado(self, pos):
        return self.habilitado and self.rect.collidepoint(pos)


class GrafoMenu:

    def __init__(self):
        self.nodos = []

    def agregar_nodo(self, nodo):
        self.nodos.append(nodo)

    def dibujar(self, ventana):
        for nodo in self.nodos:
            nodo.dibujar(ventana)

    def procesar_click(self, pos):
        for nodo in self.nodos:
            if nodo.fue_clickeado(pos):
                return nodo.id_destino
        return None


class MenuPrincipal:
    def __init__(self, ventana):
        self.ventana = ventana
        ancho = ventana.get_width()
        alto = ventana.get_height()

        self.font_titulo = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 45)
        self.font_boton = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 25)

        self.grafo = GrafoMenu()


        boton_jugar = NodoBoton(
            "JUGAR", ancho // 2 - 100, alto // 2 - 40, 200, 60,
            self.font_boton, (40, 120, 40), (60, 170, 60), "ARBOL_DECISION"
        )
        boton_salir = NodoBoton(
            "SALIR", ancho // 2 - 100, alto // 2 + 40, 200, 60,
            self.font_boton, (120, 40, 40), (170, 60, 60), "SALIR"
        )

        boton_jugar.agregar_conexion(boton_salir)
        boton_salir.agregar_conexion(boton_jugar)

        self.grafo.agregar_nodo(boton_jugar)
        self.grafo.agregar_nodo(boton_salir)

    def dibujar(self):
        self.ventana.fill(constantes.COLOR_BG)
        titulo = self.font_titulo.render("DINO SHOOTER", True, (255, 255, 0))
        titulo_rect = titulo.get_rect(center=(self.ventana.get_width() // 2, 150))
        self.ventana.blit(titulo, titulo_rect)
        self.grafo.dibujar(self.ventana)

    def manejar_click(self, pos):

        return self.grafo.procesar_click(pos)


class MenuGameOver:
    def __init__(self, ventana):
        self.ventana = ventana
        ancho = ventana.get_width()
        alto = ventana.get_height()

        self.font_titulo = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 50)
        self.font_boton = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 25)

        self.overlay = pygame.Surface((ancho, alto))
        self.overlay.set_alpha(180)
        self.overlay.fill((0, 0, 0))

        self.grafo = GrafoMenu()

        boton_salir = NodoBoton(
            "VOLVER A NIVELES", ancho // 2 - 130, alto // 2 + 40, 260, 60,
            self.font_boton, (120, 40, 40), (170, 60, 60), "SELECTOR_NIVELES"
        )
        self.grafo.agregar_nodo(boton_salir)

    def dibujar(self):
        self.ventana.blit(self.overlay, (0, 0))
        texto = self.font_titulo.render("GAME OVER", True, constantes.ROJO_JUGADOR)
        texto_rect = texto.get_rect(
            center=(self.ventana.get_width() // 2, self.ventana.get_height() // 2 - 60)
        )
        self.ventana.blit(texto, texto_rect)
        self.grafo.dibujar(self.ventana)

    def manejar_click(self, pos):
        # Devuelve "SELECTOR_NIVELES"
        return self.grafo.procesar_click(pos)


class MenuVictoria:
    def __init__(self, ventana):
        self.ventana = ventana
        ancho = ventana.get_width()
        alto = ventana.get_height()

        self.font_titulo = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 50)
        self.font_boton = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 25)

        self.overlay = pygame.Surface((ancho, alto))
        self.overlay.set_alpha(180)
        self.overlay.fill((0, 0, 0))

        self.grafo = GrafoMenu()

        boton_selector = NodoBoton(
            "SIGUIENTE / SELECTOR", ancho // 2 - 150, alto // 2 + 40, 300, 60,
            self.font_boton, (40, 120, 40), (60, 170, 60), "SELECTOR_NIVELES"
        )
        self.grafo.agregar_nodo(boton_selector)

    def dibujar(self):
        self.ventana.blit(self.overlay, (0, 0))
        texto = self.font_titulo.render("GANASTE", True, (255, 255, 0))
        texto_rect = texto.get_rect(
            center=(self.ventana.get_width() // 2, self.ventana.get_height() // 2 - 60)
        )
        self.ventana.blit(texto, texto_rect)
        self.grafo.dibujar(self.ventana)

    def manejar_click(self, pos):

        return self.grafo.procesar_click(pos)


class MenuPausa:

    def __init__(self, ventana):
        self.ventana = ventana
        ancho = ventana.get_width()
        alto = ventana.get_height()

        self.font_titulo = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 40)
        self.font_texto = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 18)
        self.font_boton = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 25)

        self.overlay = pygame.Surface((ancho, alto))
        self.overlay.set_alpha(200)
        self.overlay.fill((0, 0, 0))

        self.lineas = [
            "CONTROLES",
            "",
            "W A S D: moverse",
            "Mouse: apuntar   |   Click: disparar",
            "ESC: pausar / reanudar",
            "",
            "OBJETIVO",
            "Elimina enemigos hasta llegar al numero",
            "indicado para ganar el nivel.",
        ]

        self.grafo = GrafoMenu()
        self.grafo.agregar_nodo(NodoBoton(
            "REANUDAR", ancho // 2 - 220, alto - 90, 200, 60,
            self.font_boton, (40, 120, 40), (60, 170, 60), "REANUDAR"
        ))
        self.grafo.agregar_nodo(NodoBoton(
            "SALIR AL SELECTOR", ancho // 2 + 20, alto - 90, 220, 60,
            self.font_boton, (120, 40, 40), (170, 60, 60), "SELECTOR_NIVELES"
        ))

    def dibujar(self):
        self.ventana.blit(self.overlay, (0, 0))
        titulo = self.font_titulo.render("PAUSA / AYUDA", True, (255, 255, 0))
        titulo_rect = titulo.get_rect(center=(self.ventana.get_width() // 2, 70))
        self.ventana.blit(titulo, titulo_rect)

        y = 140
        for linea in self.lineas:
            texto = self.font_texto.render(linea, True, (220, 220, 220))
            texto_rect = texto.get_rect(center=(self.ventana.get_width() // 2, y))
            self.ventana.blit(texto, texto_rect)
            y += 26

        self.grafo.dibujar(self.ventana)

    def manejar_click(self, pos):
        # Devuelve "REANUDAR", "SELECTOR_NIVELES" o None
        return self.grafo.procesar_click(pos)