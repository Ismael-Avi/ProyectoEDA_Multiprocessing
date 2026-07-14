import pygame
import constantes
from menu import MenuPrincipal, MenuGameOver, MenuVictoria, MenuPausa, NodoBoton, GrafoMenu
from arbol_decision import ArbolDecisionUI
from selector_niveles import SelectorNiveles
import os
# ============================================================
# ESTE ES EL ARCHIVO MAIN. Se ejecuta con: python DINO.py
# NO hace falta tocar este archivo para agregar un nivel nuevo.
# Solo se toca selector_niveles.py (ver instrucciones ahí).
# ============================================================

# FUNCION ESCALAR IMAGEN
def escala_img(image, scala):
    w = image.get_width()
    h = image.get_height()
    nueva_img = (pygame.transform.scale(image, (w * scala, h * scala)))
    return nueva_img

# FUNCION PARA CONTAR ELEMENTOS
def contar_Elemtos(directorio):
    return len(os.listdir(directorio))

# FUNCION LISTAR NOMBRES ELEMENTOS
def nombre_Carpeta(directory):
    return os.listdir(directory)


pygame.init()

ventana = pygame.display.set_mode((constantes.ANCHO_ventana, constantes.ALTO_ventana))
pygame.display.set_caption("Pygame")


font = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 25)
font_nivel_vacio = pygame.font.Font("assets/Fonts/PixeloidMono.ttf", 35)

corazon_vacio = pygame.image.load("assets/images/Items/heart_empty.png").convert_alpha()
corazon_vacio = escala_img(corazon_vacio, constantes.SCALA_CORAZONES)
corazon_medio = pygame.image.load("assets/images/Items/heart_mid.png").convert_alpha()
corazon_medio = escala_img(corazon_medio, constantes.SCALA_CORAZONES)
corazon_lleno = pygame.image.load("assets/images/Items/heart_full.png").convert_alpha()
corazon_lleno = escala_img(corazon_lleno, constantes.SCALA_CORAZONES)

animaciones = []
for i in range(7):
    img = pygame.image.load(f"assets//images//characters//player//Walking_KG_{i}.png")
    img = escala_img(img, constantes.SCALA_PERSONAJE)
    animaciones.append(img)

directorio_enemigo = "assets//images//characters//enemies"
tipo_enemigos = nombre_Carpeta(directorio_enemigo)

animaciones_enemigos = []
for eni in tipo_enemigos:
    lista_temp = []
    ruta_temp = f"assets//images//characters//enemies//{eni}"
    nun_animaciones = contar_Elemtos(ruta_temp)
    for i in range(nun_animaciones):
        img_enemigo = pygame.image.load(f"{ruta_temp}//{eni}_{i+1}.png").convert_alpha()
        img_enemigo = escala_img(img_enemigo, constantes.SCALA_ENEMIGO)
        lista_temp.append(img_enemigo)
    animaciones_enemigos.append(lista_temp)

imagen_pistola = pygame.image.load("assets//images//weapons//pistola.png").convert_alpha()
imagen_pistola = escala_img(imagen_pistola, constantes.SCALA_ARMA)
imagen_bala = pygame.image.load("assets//images//weapons//bala.png").convert_alpha()
imagen_bala = escala_img(imagen_bala, constantes.SCALA_BALA)


recursos = {
    "font": font,
    "animaciones": animaciones,
    "animaciones_enemigos": animaciones_enemigos,
    "imagen_pistola": imagen_pistola,
    "imagen_bala": imagen_bala,
    "corazon_vacio": corazon_vacio,
    "corazon_medio": corazon_medio,
    "corazon_lleno": corazon_lleno,
}

#  Pantallas / menús (se crean una sola vez)
menu_principal = MenuPrincipal(ventana)
menu_game_over = MenuGameOver(ventana)
menu_victoria = MenuVictoria(ventana)
menu_pausa = MenuPausa(ventana)
arbol_decision_ui = ArbolDecisionUI(ventana)
selector_niveles = SelectorNiveles(ventana, recursos, niveles_desbloqueados=0)

# Botón "Volver" para la pantalla de nivel vacío (niveles sin clase todavía)
grafo_nivel_vacio = GrafoMenu()
grafo_nivel_vacio.agregar_nodo(
    NodoBoton("VOLVER", constantes.ANCHO_ventana // 2 - 100,
              constantes.ALTO_ventana // 2 + 60, 200, 60,
              font, (120, 40, 40), (170, 60, 60), "SELECTOR_NIVELES")
)

nivel_actual = None
nivel_seleccionado = 1

reloj = pygame.time.Clock()
run = True


estado = "MENU"

while run:
    reloj.tick(constantes.FPS)

    # EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if estado == "JUGANDO_NIVEL":
                estado = "PAUSA"
            elif estado == "PAUSA":
                estado = "JUGANDO_NIVEL"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if estado == "MENU":
                destino = menu_principal.manejar_click(event.pos)
                if destino == "ARBOL_DECISION":
                    arbol_decision_ui.reiniciar()
                    estado = "ARBOL_DECISION"
                elif destino == "SALIR":
                    run = False

            elif estado == "ARBOL_DECISION":
                resultado = arbol_decision_ui.manejar_click(event.pos)
                if resultado is not None:
                    selector_niveles.actualizar_desbloqueo(resultado)
                    estado = "SELECTOR_NIVELES"

            elif estado == "SELECTOR_NIVELES":
                destino = selector_niveles.manejar_click(event.pos)
                if destino == "MENU":
                    estado = "MENU"
                elif destino is not None:
                    numero_nivel = destino
                    nivel_seleccionado = numero_nivel
                    nodo = selector_niveles.obtener_nodo(numero_nivel)
                    if nodo.fabrica_nivel is not None:
                        nivel_actual = nodo.fabrica_nivel()  # crea el nivel desde cero
                        estado = "JUGANDO_NIVEL"
                    else:
                        estado = "NIVEL_VACIO"

            elif estado == "PAUSA":
                destino = menu_pausa.manejar_click(event.pos)
                if destino == "REANUDAR":
                    estado = "JUGANDO_NIVEL"
                elif destino == "SELECTOR_NIVELES":
                    estado = "SELECTOR_NIVELES"

            elif estado == "NIVEL_VACIO":
                destino = grafo_nivel_vacio.procesar_click(event.pos)
                if destino == "SELECTOR_NIVELES":
                    estado = "SELECTOR_NIVELES"

            elif estado == "GAME_OVER":
                destino = menu_game_over.manejar_click(event.pos)
                if destino == "SELECTOR_NIVELES":
                    estado = "SELECTOR_NIVELES"

            elif estado == "GANASTE":
                destino = menu_victoria.manejar_click(event.pos)
                if destino == "SELECTOR_NIVELES":
                    estado = "SELECTOR_NIVELES"

        if estado == "JUGANDO_NIVEL" and nivel_actual is not None:
            nivel_actual.manejar_evento(event)


    if estado == "MENU":
        menu_principal.dibujar()

    elif estado == "ARBOL_DECISION":
        arbol_decision_ui.dibujar()

    elif estado == "SELECTOR_NIVELES":
        selector_niveles.dibujar()

    elif estado == "NIVEL_VACIO":
        ventana.fill(constantes.COLOR_BG)
        texto = font_nivel_vacio.render(f"NIVEL {nivel_seleccionado}", True, (255, 255, 0))
        texto_rect = texto.get_rect(
            center=(ventana.get_width() // 2, ventana.get_height() // 2 - 60)
        )
        ventana.blit(texto, texto_rect)
        texto2 = font.render("En construccion", True, (200, 200, 200))
        texto2_rect = texto2.get_rect(
            center=(ventana.get_width() // 2, ventana.get_height() // 2 - 10)
        )
        ventana.blit(texto2, texto2_rect)
        grafo_nivel_vacio.dibujar(ventana)

    elif estado == "JUGANDO_NIVEL":
        nivel_actual.update()
        nivel_actual.dibujar()

        if nivel_actual.perdio:
            estado = "GAME_OVER"
        elif nivel_actual.gano:
            selector_niveles.marcar_completado(nivel_seleccionado)
            estado = "GANASTE"

    elif estado == "PAUSA":

        if nivel_actual is not None:
            nivel_actual.dibujar()
        menu_pausa.dibujar()

    elif estado == "GANASTE":
        menu_victoria.dibujar()

    elif estado == "GAME_OVER":
        menu_game_over.dibujar()

    pygame.display.update()

pygame.quit()