import pygame
import os
import random
import json
import time

# --- Constantes ---
TAMANIO_TILE = 16
ANCHO_MAPA = 56
ALTO_MAPA = 28
ANCHO_PANTALLA = ANCHO_MAPA * TAMANIO_TILE
ALTO_PANTALLA = ALTO_MAPA * TAMANIO_TILE
ANCHO_MENU = 900
ALTO_MENU = 600
USAR_VENTANA_FIJA = True
ANCHO_JUEGO_FIJO = 1280
ALTO_JUEGO_FIJO = 720
RESERVA_UI_JUEGO = 80
MARGEN_SUPERIOR_UI = 0

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (144, 238, 144)
GRIS = (105, 105, 105)
MARRON = (139, 69, 19)
GRIS_OSCURO = (169, 169, 169)
AMARILLO = (255, 255, 0)
GRIS_CLARO = (200, 200, 200)
GRIS_MAS_OSCURO = (50, 50, 50)
NARANJA = (255, 165, 0)
MORADO = (128, 0, 128)

CAMINO = 0
MURO = 1
LIANAS = 2
TUNEL = 3
SALIDA = 4

VELOCIDAD_JUGADOR = 3
VELOCIDAD_CORRER = 6
ENERGIA_MAXIMA = 100
REGENERACION_ENERGIA = 1.0 / 60.0
COSTO_CORRER = 1
DANIO_POR_CAPTURA = 30

MAXIMO_TRAMPAS = 3
ENFRIAMIENTO_TRAMPA = 5
BONIFICACION_TRAMPA = 500

NUMERO_CAZADORES = 3
TIEMPO_REAPARICION = 10
PUNTOS_CAZADOR_AGARRA = 2000
PUNTOS_CAZADOR_ESCAPE = 1000


class Boton:
    pass
class CajaTexto:
    pass
class Checkbox:
    pass
class Terreno:
    pass
class Camino(Terreno):
    pass
class Muro(Terreno):
    pass
class Lianas(Terreno):
    pass
class Tunel(Terreno):
    pass
class Salida(Terreno):
    pass
class Jugador:
    pass
class Enemigo:
    pass
class Trampa:
    pass
class MapaJuego:
    pass


def menu_principal(pantalla, reloj, botones, fuentes):
    pantalla.fill(GRIS_MAS_OSCURO)
    texto_titulo = fuentes['titulo'].render("Escapa del Laberinto", True, BLANCO)
    pantalla.blit(texto_titulo, (ANCHO_PANTALLA//2 - texto_titulo.get_width()//2, 100))
    posicion_raton = pygame.mouse.get_pos()
    for boton in botones.values():
        boton.verificar_hover(posicion_raton)
        boton.dibujar(pantalla, fuentes['boton'])
    pygame.display.flip()

def seleccion_modo(pantalla, reloj, fuentes):
    ancho_btn, alto_btn, espacio = 300, 50, 20
    centro_x = ANCHO_PANTALLA // 2
    alto_total = alto_btn * 2 + espacio
    inicio_y = ALTO_PANTALLA // 2 - alto_total // 2
    boton_escapa = Boton(centro_x - ancho_btn//2, inicio_y, ancho_btn, alto_btn, "Modo Escapa", GRIS_CLARO, BLANCO)
    boton_cazador = Boton(centro_x - ancho_btn//2, inicio_y + alto_btn + espacio, ancho_btn, alto_btn, "Modo Cazador", GRIS_CLARO, BLANCO)
    while True:
        posicion_raton = pygame.mouse.get_pos()
        boton_escapa.verificar_hover(posicion_raton)
        boton_cazador.verificar_hover(posicion_raton)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if boton_escapa.fue_clickeado(evento):
                return ("escapa", None)
            if boton_cazador.fue_clickeado(evento):
                tiempo = seleccion_tiempo_cazador(pantalla, reloj, fuentes)
                if tiempo:
                    return ("cazador", tiempo)
        pantalla.fill(GRIS_MAS_OSCURO)
        mensaje = fuentes['encabezado'].render("Selecciona un Modo de Juego", True, BLANCO)
        pantalla.blit(mensaje, (ANCHO_PANTALLA//2 - mensaje.get_width()//2, inicio_y - 120))
        boton_escapa.dibujar(pantalla, fuentes['boton'])
        boton_cazador.dibujar(pantalla, fuentes['boton'])
        pygame.display.flip()
        reloj.tick(60)

def seleccion_tiempo_cazador(pantalla, reloj, fuentes):
    ancho_btn, alto_btn, espacio = 300, 50, 20
    centro_x = ANCHO_PANTALLA // 2
    alto_total = alto_btn * 3 + espacio * 2
    inicio_y = ALTO_PANTALLA // 2 - alto_total // 2
    boton_1min = Boton(centro_x - ancho_btn//2, inicio_y, ancho_btn, alto_btn, "1 Minuto", GRIS_CLARO, BLANCO)
    boton_3min = Boton(centro_x - ancho_btn//2, inicio_y + alto_btn + espacio, ancho_btn, alto_btn, "3 Minutos", GRIS_CLARO, BLANCO)
    boton_volver = Boton(centro_x - ancho_btn//2, inicio_y + (alto_btn + espacio) * 2, ancho_btn, alto_btn, "Volver", GRIS_CLARO, BLANCO)
    while True:
        posicion_raton = pygame.mouse.get_pos()
        boton_1min.verificar_hover(posicion_raton)
        boton_3min.verificar_hover(posicion_raton)
        boton_volver.verificar_hover(posicion_raton)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if boton_1min.fue_clickeado(evento):
                return 60
            if boton_3min.fue_clickeado(evento):
                return 180
            if boton_volver.fue_clickeado(evento):
                return None
        pantalla.fill(GRIS_MAS_OSCURO)
        mensaje = fuentes['encabezado'].render("Selecciona la Duración", True, BLANCO)
        pantalla.blit(mensaje, (ANCHO_PANTALLA//2 - mensaje.get_width()//2, inicio_y - 120))
        boton_1min.dibujar(pantalla, fuentes['boton'])
        boton_3min.dibujar(pantalla, fuentes['boton'])
        boton_volver.dibujar(pantalla, fuentes['boton'])
        pygame.display.flip()
        reloj.tick(60)

def pantalla_puntajes(pantalla, reloj, boton_volver, fuentes):
    puntajes = cargar_puntajes()
    while True:
        posicion_raton = pygame.mouse.get_pos()
        boton_volver.verificar_hover(posicion_raton)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if boton_volver.fue_clickeado(evento):
                return
        pantalla.fill(GRIS_MAS_OSCURO)
        fuente_titulo = pygame.font.Font(None, 48)
        titulo = fuente_titulo.render("Mejores Puntajes", True, BLANCO)
        pantalla.blit(titulo, (ANCHO_PANTALLA//2 - titulo.get_width()//2, 20))
        
        izquierda_x = ANCHO_PANTALLA // 6
        centro_x = ANCHO_PANTALLA // 2
        derecha_x = 5 * ANCHO_PANTALLA // 6
        datos_modos = [
            ("escapa", "Escapa", izquierda_x),
            ("cazador_1min", "Cazador - 1min", centro_x),
            ("cazador_3min", "Cazador - 3min", derecha_x)
        ]
        
        fuente_categoria = pygame.font.Font(None, 28)
        
        for clave_modo, etiqueta_modo, pos_x in datos_modos:
            titulo_modo = fuente_categoria.render(etiqueta_modo, True, AMARILLO)
            pantalla.blit(titulo_modo, (pos_x - titulo_modo.get_width()//2, 80))
            for i, puntaje in enumerate(puntajes.get(clave_modo, [])):
                texto = f"{i+1}. {puntaje['name']} - {puntaje['score']}"
                texto_puntaje = fuentes['puntaje'].render(texto, True, BLANCO)
                pantalla.blit(texto_puntaje, (pos_x - texto_puntaje.get_width()//2, 120 + i*35))
        
        boton_volver.dibujar(pantalla, fuentes['boton'])
        pygame.display.flip()
        reloj.tick(60)



def principal():
    pygame.init()
    global IMAGEN_JUGADOR, IMAGEN_ENEMIGO, IMAGEN_TRAMPA, IMAGEN_LIANAS, IMAGEN_TUNEL, IMAGEN_SALIDA
    global TAMANIO_TILE, ANCHO_PANTALLA, ALTO_PANTALLA
    
    ANCHO_PANTALLA, ALTO_PANTALLA = ANCHO_MENU, ALTO_MENU
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Escapa del Laberinto")
    reloj = pygame.time.Clock()
    
    fuentes_menu = {
        'titulo': pygame.font.Font(None, 74),
        'encabezado': pygame.font.Font(None, 50),
        'boton': pygame.font.Font(None, 40),
        'puntaje': pygame.font.Font(None, 30),
        'entrada': pygame.font.Font(None, 32)
    }
    
    botones_menu = {
        'jugar': Boton(ANCHO_PANTALLA//2-150, ALTO_PANTALLA//2-110, 300, 50, "Jugar", GRIS_CLARO, BLANCO),
        'puntajes': Boton(ANCHO_PANTALLA//2-150, ALTO_PANTALLA//2-50, 300, 50, "Puntajes", GRIS_CLARO, BLANCO),
        'salir': Boton(ANCHO_PANTALLA//2-150, ALTO_PANTALLA//2+10, 300, 50, "Salir", GRIS_CLARO, BLANCO)
    }
    
    estado_juego = "menu_principal"
    nombre_jugador = ""
    modo_juego = ""
    tiempo_juego = None
    
    try:
        while True:
            if estado_juego == "menu_principal":
                menu_principal(pantalla, reloj, botones_menu, fuentes_menu)
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if botones_menu['jugar'].fue_clickeado(evento):
                        estado_juego = "registro"
                    if botones_menu['puntajes'].fue_clickeado(evento):
                        estado_juego = "mejores_puntajes"
                    if botones_menu['salir'].fue_clickeado(evento):
                        pygame.quit()
                        exit()
                        
            elif estado_juego == "registro":
                nombre_jugador = pantalla_registro(pantalla, reloj, fuentes_menu)
                estado_juego = "seleccion_modo"
                
            elif estado_juego == "seleccion_modo":
                resultado = seleccion_modo(pantalla, reloj, fuentes_menu)
                if resultado:
                    modo_juego, tiempo_juego = resultado
                    estado_juego = "jugando"
                    
            elif estado_juego == "mejores_puntajes":
                boton_volver = Boton(ANCHO_PANTALLA//2-100, 500, 200, 50, "Volver", GRIS_CLARO, BLANCO)
                pantalla_puntajes(pantalla, reloj, boton_volver, fuentes_menu)
                estado_juego = "menu_principal"
                
            elif estado_juego == "jugando":
                if USAR_VENTANA_FIJA:
                    ANCHO_PANTALLA, ALTO_PANTALLA = ANCHO_JUEGO_FIJO, ALTO_JUEGO_FIJO
                    TAMANIO_TILE = max(6, min(ANCHO_PANTALLA // ANCHO_MAPA, ALTO_PANTALLA // ALTO_MAPA))
                else:
                    info = pygame.display.Info()
                    max_ancho_tile = max(1, (info.current_w - 100) // ANCHO_MAPA)
                    max_alto_tile = max(1, (info.current_h - 100) // ALTO_MAPA)
                    TAMANIO_TILE = min(30, max(6, min(max_ancho_tile, max_alto_tile)))
                    ANCHO_PANTALLA, ALTO_PANTALLA = ANCHO_MAPA * TAMANIO_TILE, ALTO_MAPA * TAMANIO_TILE
                    
                pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))    
                
                altura_barra = max(20, min(36, TAMANIO_TILE))
                global MARGEN_SUPERIOR_UI
                MARGEN_SUPERIOR_UI = altura_barra + 12
                
                fuentes_juego = {
                    'titulo': pygame.font.Font(None, 48),
                    'encabezado': pygame.font.Font(None, 36),
                    'boton': pygame.font.Font(None, 28),
                    'puntaje': pygame.font.Font(None, 22),
                    'entrada': pygame.font.Font(None, 20)
                }
                
                resultado, info_puntaje = ejecutar_juego(pantalla, reloj, nombre_jugador, modo_juego, tiempo_juego)
                estado_juego = "fin_juego"
                
                ANCHO_PANTALLA, ALTO_PANTALLA = ANCHO_MENU, ALTO_MENU
                pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
                
                fuentes_menu = {
                    'titulo': pygame.font.Font(None, 74),
                    'encabezado': pygame.font.Font(None, 50),
                    'boton': pygame.font.Font(None, 40),
                    'puntaje': pygame.font.Font(None, 30),
                    'entrada': pygame.font.Font(None, 32)
                }
                
                botones_menu = {
                    'jugar': Boton(ANCHO_PANTALLA//2-150, ALTO_PANTALLA//2-110, 300, 50, "Jugar", GRIS_CLARO, BLANCO),
                    'puntajes': Boton(ANCHO_PANTALLA//2-150, ALTO_PANTALLA//2-50, 300, 50, "Puntajes", GRIS_CLARO, BLANCO),
                    'salir': Boton(ANCHO_PANTALLA//2-150, ALTO_PANTALLA//2+10, 300, 50, "Salir", GRIS_CLARO, BLANCO)
                }
                
            elif estado_juego == "fin_juego":
                pantalla_fin(pantalla, reloj, fuentes_menu, resultado, info_puntaje)
                estado_juego = "menu_principal"
                
    except KeyboardInterrupt:
        pygame.quit()
        exit(0)

if __name__ == "__main__":
    principal()