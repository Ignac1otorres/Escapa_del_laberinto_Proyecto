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
    def __init__(self, x, y, ancho, alto, texto, color, color_hover):
        self.rectangulo = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color
        self.color_hover = color_hover
        self.esta_hover = False
    
    def dibujar(self, pantalla, fuente):
        color = self.color_hover if self.esta_hover else self.color
        pygame.draw.rect(pantalla, color, self.rectangulo)
        superficie_texto = fuente.render(self.texto, True, NEGRO)
        rect_texto = superficie_texto.get_rect(center=self.rectangulo.center)
        pantalla.blit(superficie_texto, rect_texto)
    
    def verificar_hover(self, posicion):
        self.esta_hover = self.rectangulo.collidepoint(posicion)
    
    def fue_clickeado(self, evento):
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.esta_hover
    
class CajaTexto:
    def __init__(self, x, y, ancho, alto):
        self.rectangulo = pygame.Rect(x, y, ancho, alto)
        self.texto = ""
        self.esta_activa = False
    
    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            self.esta_activa = self.rectangulo.collidepoint(evento.pos)
        if evento.type == pygame.KEYDOWN and self.esta_activa:
            if evento.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif len(self.texto) < 15:
                self.texto += evento.unicode
    
    def dibujar(self, pantalla, fuente):
        color = BLANCO if self.esta_activa else GRIS_CLARO
        pygame.draw.rect(pantalla, color, self.rectangulo)
        superficie_texto = fuente.render(self.texto, True, NEGRO)
        pantalla.blit(superficie_texto, (self.rectangulo.x + 5, self.rectangulo.y + 5))
        pygame.draw.rect(pantalla, NEGRO, self.rectangulo, 2)
class Checkbox:
    pass

class Terreno:
    def __init__(self, x, y):
        self.rectangulo = pygame.Rect(x * TAMANIO_TILE, y * TAMANIO_TILE + MARGEN_SUPERIOR_UI, TAMANIO_TILE, TAMANIO_TILE)

class Camino(Terreno):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = VERDE
        self.caminable = True
    
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rectangulo)

class Muro(Terreno):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = GRIS
        self.caminable = False
    
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rectangulo)

class Lianas(Terreno):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = MARRON
        self.caminable = False
    
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rectangulo)

class Tunel(Terreno):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = GRIS_OSCURO
        self.caminable = True
    
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rectangulo)

class Salida(Terreno):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = AMARILLO
        self.caminable = True
    
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rectangulo)

class Jugador:
    pass
class Enemigo:
    pass
class Trampa:
    pass

# Funciones de manejo de puntajes
def cargar_puntajes():
    try:
        with open("scores.json", "r") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"escapa": [], "cazador_1min": [], "cazador_3min": []}

def guardar_puntajes(puntajes):
    with open("scores.json", "w") as archivo:
        json.dump(puntajes, archivo, indent=4)

def agregar_puntaje(modo, nombre, puntaje):
    puntajes = cargar_puntajes()
    lista = puntajes.get(modo, [])
    lista.append({"name": nombre, "score": puntaje})
    lista.sort(key=lambda x: x["score"], reverse=True)
    puntajes[modo] = lista[:5]
    guardar_puntajes(puntajes)

def pantalla_registro(pantalla, reloj, fuentes):
    ancho_btn, alto_btn = 200, 50
    ancho_entrada, alto_entrada = 300, 50
    centro_x = ANCHO_PANTALLA // 2
    centro_y = ALTO_PANTALLA // 2
    caja_entrada = CajaTexto(centro_x - ancho_entrada//2, centro_y - alto_entrada//2, ancho_entrada, alto_entrada)
    boton_continuar = Boton(centro_x - ancho_btn//2, centro_y + alto_entrada//2 + 20, ancho_btn, alto_btn, "Continuar", GRIS_CLARO, BLANCO)
    
    while True:
        posicion_raton = pygame.mouse.get_pos()
        boton_continuar.verificar_hover(posicion_raton)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            caja_entrada.manejar_evento(evento)
            if boton_continuar.fue_clickeado(evento) and caja_entrada.texto.strip() != "":
                return caja_entrada.texto.strip()
        
        pantalla.fill(GRIS_MAS_OSCURO)
        mensaje = fuentes['encabezado'].render("Ingresa tu Nombre:", True, BLANCO)
        pantalla.blit(mensaje, (ANCHO_PANTALLA//2 - mensaje.get_width()//2, centro_y - 100))
        caja_entrada.dibujar(pantalla, fuentes['entrada'])
        boton_continuar.dibujar(pantalla, fuentes['boton'])
        pygame.display.flip()
        reloj.tick(60)

def pantalla_fin(pantalla, reloj, fuentes, texto_resultado, texto_puntaje):
    ancho_btn, alto_btn = 200, 50
    boton_menu = Boton(ANCHO_PANTALLA//2 - ancho_btn//2, ALTO_PANTALLA//2 + 100, ancho_btn, alto_btn, "Menú Principal", GRIS_CLARO, BLANCO)
    
    while True:
        posicion_raton = pygame.mouse.get_pos()
        boton_menu.verificar_hover(posicion_raton)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if boton_menu.fue_clickeado(evento):
                return
        
        pantalla.fill(GRIS_MAS_OSCURO)
        superficie_resultado = fuentes['titulo'].render(texto_resultado, True, BLANCO)
        superficie_puntaje = fuentes['encabezado'].render(texto_puntaje, True, BLANCO)
        pantalla.blit(superficie_resultado, (ANCHO_PANTALLA//2 - superficie_resultado.get_width()//2, ALTO_PANTALLA//2 - 100))
        pantalla.blit(superficie_puntaje, (ANCHO_PANTALLA//2 - superficie_puntaje.get_width()//2, ALTO_PANTALLA//2))
        boton_menu.dibujar(pantalla, fuentes['boton'])
        pygame.display.flip()
        reloj.tick(60)

class MapaJuego:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.cuadricula = []
        self.obstaculos = []
        self.salidas = []
    
    def generar_laberinto(self, modo):
        mapa_temporal = [[MURO for _ in range(self.ancho)] for _ in range(self.alto)]
        pila = []
        inicio_x = random.randrange(1, self.ancho-1, 2)
        inicio_y = random.randrange(1, self.alto-1, 2)
        mapa_temporal[inicio_y][inicio_x] = CAMINO
        pila.append((inicio_x, inicio_y))
        
        while pila:
            x, y = pila[-1]
            vecinos = []
            for dx, dy in [(0,2), (0,-2), (2,0), (-2,0)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.ancho and 0 < ny < self.alto and mapa_temporal[ny][nx] == MURO:
                    vecinos.append((nx, ny))
            if vecinos:
                nx, ny = random.choice(vecinos)
                mapa_temporal[ny][nx] = CAMINO
                mapa_temporal[y + (ny-y)//2][x + (nx-x)//2] = CAMINO
                pila.append((nx, ny))
            else:
                pila.pop()
        
        self._suavizar_muros(mapa_temporal)
        self._agregar_caracteristicas(mapa_temporal, modo)
        self._crear_areas_abiertas(mapa_temporal)
        self._crear_cuadricula(mapa_temporal)
    
    def _agregar_caracteristicas(self, mapa_temporal, modo):
        if modo == "escapa":
            salida_colocada = False
            for i in range(self.alto-2, 0, -1):
                if mapa_temporal[i][self.ancho-2] == CAMINO:
                    mapa_temporal[i][self.ancho-1] = SALIDA
                    salida_colocada = True
                    break
            if not salida_colocada:
                mapa_temporal[self.alto-2][self.ancho-1] = SALIDA
        else:
            for _ in range(4):
                lado = random.choice(['arriba', 'abajo', 'izquierda', 'derecha'])
                if lado == 'arriba':
                    mapa_temporal[0][random.randint(1, self.ancho-2)] = SALIDA
                elif lado == 'abajo':
                    mapa_temporal[self.alto-1][random.randint(1, self.ancho-2)] = SALIDA
                elif lado == 'izquierda':
                    mapa_temporal[random.randint(1, self.alto-2)][0] = SALIDA
                elif lado == 'derecha':
                    mapa_temporal[random.randint(1, self.alto-2)][self.ancho-1] = SALIDA
        
        for y in range(1, self.alto-1):
            for x in range(1, self.ancho-1):
                if mapa_temporal[y][x] == CAMINO and random.random() < 0.015:
                    mapa_temporal[y][x] = LIANAS
                elif mapa_temporal[y][x] == CAMINO and random.random() < 0.02:
                    mapa_temporal[y][x] = TUNEL

    def _suavizar_muros(self, mapa_temporal):
        ancho, alto = self.ancho, self.alto
        intentos = max((ancho * alto) // 6, 20)
        
        for _ in range(intentos):
            x = random.randint(1, ancho-2)
            y = random.randint(1, alto-2)
            if mapa_temporal[y][x] != MURO:
                continue
            
            caminos_adyacentes = 0
            for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < ancho and 0 <= ny < alto and mapa_temporal[ny][nx] == CAMINO:
                    caminos_adyacentes += 1
            
            if caminos_adyacentes >= 2:
                probabilidad = 0.5
            elif caminos_adyacentes == 1:
                probabilidad = 0.25
            else:
                probabilidad = 0.03
            
            if random.random() < probabilidad:
                mapa_temporal[y][x] = CAMINO
        
        caminatas_extra = max((ancho * alto) // 120, 3)
        for _ in range(caminatas_extra):
            sx = random.randint(1, ancho-2)
            sy = random.randint(1, alto-2)
            if mapa_temporal[sy][sx] != CAMINO:
                continue
            
            longitud = random.randint(3, 8)
            cx, cy = sx, sy
            for _ in range(longitud):
                dx, dy = random.choice(((1,0), (-1,0), (0,1), (0,-1)))
                nx, ny = cx + dx, cy + dy
                if not (1 <= nx < ancho-1 and 1 <= ny < alto-1):
                    break
                if mapa_temporal[ny][nx] == MURO and random.random() < 0.6:
                    mapa_temporal[ny][nx] = CAMINO
                cx, cy = nx, ny
    
    def _crear_areas_abiertas(self, mapa_temporal):
        ancho, alto = self.ancho, self.alto
        numero_islas = max(3, (ancho * alto) // 80)
        
        for _ in range(numero_islas):
            centro_x = random.randint(2, ancho - 3)
            centro_y = random.randint(2, alto - 3)
            ancho_isla = random.randint(3, 5)
            alto_isla = random.randint(2, 4)
            
            for dy in range(alto_isla):
                for dx in range(ancho_isla):
                    nx = centro_x + dx - ancho_isla // 2
                    ny = centro_y + dy - alto_isla // 2
                    if 1 <= nx < ancho - 1 and 1 <= ny < alto - 1:
                        if mapa_temporal[ny][nx] in (MURO, LIANAS, TUNEL):
                            mapa_temporal[ny][nx] = CAMINO
    
    def _crear_cuadricula(self, mapa_temporal):
        self.cuadricula = []
        self.obstaculos = []
        self.salidas = []
        
        for y, fila in enumerate(mapa_temporal):
            fila_cuadricula = []
            for x, tipo in enumerate(fila):
                tile = {
                    MURO: Muro,
                    LIANAS: Lianas,
                    TUNEL: Tunel,
                    SALIDA: Salida,
                    CAMINO: Camino
                }[tipo](x, y)
                
                if isinstance(tile, Salida):
                    self.salidas.append(tile)
                if isinstance(tile, (Muro, Lianas, Tunel)):
                    self.obstaculos.append(tile)
                
                fila_cuadricula.append(tile)
            self.cuadricula.append(fila_cuadricula)
    
    def obtener_posicion_valida(self):
        while True:
            x = random.randint(1, self.ancho-2)
            y = random.randint(1, self.alto-2)
            if isinstance(self.cuadricula[y][x], Camino):
                return (x * TAMANIO_TILE + 5, y * TAMANIO_TILE + 5 + MARGEN_SUPERIOR_UI)
    
    def dibujar(self, pantalla):
        for fila in self.cuadricula:
            for tile in fila:
                tile.dibujar(pantalla)


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