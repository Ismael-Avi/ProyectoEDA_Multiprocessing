import pygame
import constantes
from menu import NodoBoton, GrafoMenu


class NodoPregunta:

    def __init__(self, texto="", hijo_si=None, hijo_no=None, resultado=None):
        self.texto = texto
        self.hijo_si = hijo_si
        self.hijo_no = hijo_no
        self.resultado = resultado

    def es_hoja(self):
        return self.resultado is not None


def construir_arbol():
    hoja_a = NodoPregunta(resultado=9)   # SI, SI  DEVUELVE LOS 9 NIVELES HABILITADOS
    hoja_b = NodoPregunta(resultado=6)   # SI, NO   DEVUELVE LOS 6 NIVELES HABILITADOS
    hoja_c = NodoPregunta(resultado=6)   # NO, SI   DEVUELVE LOS 6 NIVELES HABILITADOS
    hoja_d = NodoPregunta(resultado=3)   # NO, NO   DEVUELVE LOS 3 NIVELES HABILITADOS

    pregunta_2a = NodoPregunta("Te consideras experto en juegos de disparos?",
                                hijo_si=hoja_a, hijo_no=hoja_b)
    pregunta_2b = NodoPregunta("Prefieres un desafio alto desde el inicio?",
                                hijo_si=hoja_c, hijo_no=hoja_d)

    raiz = NodoPregunta("Has jugado shooters de sobrevivencia antes?",
                         hijo_si=pregunta_2a, hijo_no=pregunta_2b)
    return raiz


class ArbolDecisionUI:

    def __init__(self, ventana):
        self.ventana = ventana
        self.font_pregunta = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 22)
        self.font_boton = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 25)
        self.raiz = construir_arbol()
        self.nodo_actual = self.raiz
        self._armar_botones()

    def reiniciar(self):
        self.nodo_actual = self.raiz

    def _armar_botones(self):
        ancho = self.ventana.get_width()
        alto = self.ventana.get_height()
        self.grafo = GrafoMenu()

        boton_si = NodoBoton("SI", ancho // 2 - 130, alto // 2 + 40, 110, 55,
                              self.font_boton, (40, 120, 40), (60, 170, 60), "SI")
        boton_no = NodoBoton("NO", ancho // 2 + 20, alto // 2 + 40, 110, 55,
                              self.font_boton, (120, 40, 40), (170, 60, 60), "NO")

        self.grafo.agregar_nodo(boton_si)
        self.grafo.agregar_nodo(boton_no)

    def dibujar(self):
        self.ventana.fill(constantes.COLOR_BG)


        palabras = self.nodo_actual.texto.split(" ")
        lineas = []
        linea_actual = ""
        for palabra in palabras:
            prueba = (linea_actual + " " + palabra).strip()
            if self.font_pregunta.size(prueba)[0] > self.ventana.get_width() - 100:
                lineas.append(linea_actual)
                linea_actual = palabra
            else:
                linea_actual = prueba
        lineas.append(linea_actual)

        y = self.ventana.get_height() // 2 - 100
        for linea in lineas:
            texto_render = self.font_pregunta.render(linea, True, (255, 255, 0))
            texto_rect = texto_render.get_rect(center=(self.ventana.get_width() // 2, y))
            self.ventana.blit(texto_render, texto_rect)
            y += 32

        self.grafo.dibujar(self.ventana)

    def manejar_click(self, pos):

        respuesta = self.grafo.procesar_click(pos)
        if respuesta is None:
            return None

        if respuesta == "SI":
            self.nodo_actual = self.nodo_actual.hijo_si
        elif respuesta == "NO":
            self.nodo_actual = self.nodo_actual.hijo_no

        if self.nodo_actual.es_hoja():
            return self.nodo_actual.resultado

        return None