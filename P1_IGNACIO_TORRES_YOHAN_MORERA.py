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

# Variables globales de sprites
IMAGEN_JUGADOR = None
IMAGEN_ENEMIGO = None
IMAGEN_TRAMPA = None
IMAGEN_LIANAS = None
IMAGEN_TUNEL = None
IMAGEN_SALIDA = None

# Configuración de opciones
MOSTRAR_SPRITES = True
MUSICA_SELECCIONADA = "Angry_Birds.mp3"
CANCIONES_DISPONIBLES = [
    "Sin música",
    "Angry_Birds.mp3",
    "Indiana_Jones.mp3",
    "Megalovania_Undertale.mp3",
    "Música_Pou.mp3",
    "Pigstep.mp3",
    "Super_Mario_Bros.mp3"
]


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
    def __init__(self, x, y, tamano, texto, marcada=True):
        self.rectangulo = pygame.Rect(x, y, tamano, tamano)
        self.marcada = marcada
        self.texto = texto
        self.esta_hover = False
    
    def dibujar(self, pantalla, fuente):
        pygame.draw.rect(pantalla, BLANCO, self.rectangulo, 2)
        if self.marcada:
            pygame.draw.line(pantalla, VERDE, (self.rectangulo.x+5, self.rectangulo.centery), 
                        (self.rectangulo.centerx, self.rectangulo.bottom-5), 3)
            pygame.draw.line(pantalla, VERDE, (self.rectangulo.centerx, self.rectangulo.bottom-5),
                        (self.rectangulo.right-5, self.rectangulo.y+5), 3)
        ts = fuente.render(self.texto, True, BLANCO)
        pantalla.blit(ts, (self.rectangulo.right + 10, self.rectangulo.y))
    
    def verificar_hover(self, posicion):
        self.esta_hover = self.rectangulo.collidepoint(posicion)
    
    def fue_clickeado(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.esta_hover:
            self.marcada = not self.marcada
            return True
        return False

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

# --- Algoritmos de pathfinding BFS para navegación de enemigos ---

def bfs_siguiente_paso(mapa, inicio, objetivo, evitar=None):
    if evitar is None:
        evitar = set()
    ancho, alto = mapa.ancho, mapa.alto
    cuadricula = mapa.cuadricula
    sx, sy = inicio
    gx, gy = objetivo
    sx = max(0, min(ancho-1, sx))
    sy = max(0, min(alto-1, sy))
    gx = max(0, min(ancho-1, gx))
    gy = max(0, min(alto-1, gy))
    
    if (sx, sy) == (gx, gy):
        return (sx, sy)
    
    from collections import deque
    cola = deque()
    cola.append((sx, sy))
    previo = {(sx, sy): None}
    direcciones = [(1,0), (-1,0), (0,1), (0,-1)]
    
    while cola:
        x, y = cola.popleft()
        if (x, y) == (gx, gy):
            break
        for dx, dy in direcciones:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < ancho and 0 <= ny < alto):
                continue
            if (nx, ny) in previo:
                continue
            if (nx, ny) in evitar:
                continue
            
            try:
                tile = cuadricula[ny][nx]
                caminable = getattr(tile, 'caminable', False)
            except Exception:
                caminable = False
            
            if not caminable and not isinstance(cuadricula[ny][nx], type(cuadricula[gy][gx])):
                continue
            
            previo[(nx, ny)] = (x, y)
            cola.append((nx, ny))
    
    if (gx, gy) not in previo:
        return None
    
    actual = (gx, gy)
    ruta = []
    while actual is not None:
        ruta.append(actual)
        actual = previo[actual]
    ruta.reverse()
    
    if len(ruta) < 2:
        return ruta[0]
    return ruta[1]


def bfs_ruta(mapa, inicio, objetivo, evitar=None):
    if evitar is None:
        evitar = set()
    ancho, alto = mapa.ancho, mapa.alto
    cuadricula = mapa.cuadricula
    sx, sy = inicio
    gx, gy = objetivo
    sx = max(0, min(ancho-1, sx))
    sy = max(0, min(alto-1, sy))
    gx = max(0, min(ancho-1, gx))
    gy = max(0, min(alto-1, gy))
    
    if (sx, sy) == (gx, gy):
        return [(sx, sy)]
    
    from collections import deque
    cola = deque()
    cola.append((sx, sy))
    previo = {(sx, sy): None}
    direcciones = [(1,0), (-1,0), (0,1), (0,-1)]
    
    while cola:
        x, y = cola.popleft()
        if (x, y) == (gx, gy):
            break
        for dx, dy in direcciones:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < ancho and 0 <= ny < alto):
                continue
            if (nx, ny) in previo:
                continue
            if (nx, ny) in evitar:
                continue
            
            try:
                caminable = getattr(cuadricula[ny][nx], 'caminable', False)
            except Exception:
                caminable = False
            
            if not caminable and not isinstance(cuadricula[ny][nx], type(cuadricula[gy][gx])):
                continue
            
            previo[(nx, ny)] = (x, y)
            cola.append((nx, ny))
    
    if (gx, gy) not in previo:
        return None
    
    actual = (gx, gy)
    ruta = []
    while actual is not None:
        ruta.append(actual)
        actual = previo[actual]
    ruta.reverse()
    return ruta


def bfs_ruta_enemigo(mapa, inicio, objetivo, evitar=None, modo="escapa"):
    if evitar is None:
        evitar = set()
    ancho, alto = mapa.ancho, mapa.alto
    cuadricula = mapa.cuadricula
    sx, sy = inicio
    gx, gy = objetivo
    sx = max(0, min(ancho-1, sx))
    sy = max(0, min(alto-1, sy))
    gx = max(0, min(ancho-1, gx))
    gy = max(0, min(alto-1, gy))
    
    if (sx, sy) == (gx, gy):
        return [(sx, sy)]
    
    from collections import deque
    cola = deque()
    cola.append((sx, sy))
    previo = {(sx, sy): None}
    direcciones = [(1,0), (-1,0), (0,1), (0,-1)]
    
    while cola:
        x, y = cola.popleft()
        if (x, y) == (gx, gy):
            break
        for dx, dy in direcciones:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < ancho and 0 <= ny < alto):
                continue
            if (nx, ny) in previo:
                continue
            if (nx, ny) in evitar:
                continue
            
            tile = cuadricula[ny][nx]
            bloqueado = False
            
            if isinstance(tile, Muro):
                bloqueado = True
            elif modo == "escapa" and isinstance(tile, Tunel):
                bloqueado = True
            elif modo == "cazador" and isinstance(tile, Lianas):
                bloqueado = True
            
            if bloqueado:
                continue
            
            previo[(nx, ny)] = (x, y)
            cola.append((nx, ny))
    
    if (gx, gy) not in previo:
        return None
    
    actual = (gx, gy)
    ruta = []
    while actual is not None:
        ruta.append(actual)
        actual = previo[actual]
    ruta.reverse()
    return ruta


# --- Clases de entidades del juego ---

class Jugador:
    def __init__(self, x, y):
        tamano = max(6, TAMANIO_TILE-6)
        self.rectangulo = pygame.Rect(x, y, tamano, tamano)
        self.color = ROJO
        self.energia = ENERGIA_MAXIMA
    
    def mover(self, dx, dy, obstaculos, corriendo, modo):
        velocidad = VELOCIDAD_CORRER if corriendo and self.energia > COSTO_CORRER else VELOCIDAD_JUGADOR
        if corriendo and (dx != 0 or dy != 0) and self.energia > COSTO_CORRER:
            self.energia -= COSTO_CORRER
        if dx != 0:
            self.mover_eje(dx * velocidad, 0, obstaculos, modo)
        if dy != 0:
            self.mover_eje(0, dy * velocidad, obstaculos, modo)
    
    def mover_eje(self, dx, dy, obstaculos, modo):
        self.rectangulo.x += dx
        self.rectangulo.y += dy
        for o in obstaculos:
            bloqueado = False
            if isinstance(o, Muro):
                bloqueado = True
            elif modo == "escapa" and isinstance(o, Lianas):
                bloqueado = True
            elif modo == "cazador" and isinstance(o, Tunel):
                bloqueado = True
            
            if self.rectangulo.colliderect(o.rectangulo) and bloqueado:
                if dx > 0:
                    self.rectangulo.right = o.rectangulo.left
                if dx < 0:
                    self.rectangulo.left = o.rectangulo.right
                if dy > 0:
                    self.rectangulo.bottom = o.rectangulo.top
                if dy < 0:
                    self.rectangulo.top = o.rectangulo.bottom
        
        min_x = 0
        min_y = MARGEN_SUPERIOR_UI
        max_x = ANCHO_MAPA * TAMANIO_TILE - self.rectangulo.width
        max_y = MARGEN_SUPERIOR_UI + ALTO_MAPA * TAMANIO_TILE - self.rectangulo.height
        if self.rectangulo.x < min_x:
            self.rectangulo.x = min_x
        if self.rectangulo.x > max_x:
            self.rectangulo.x = max_x
        if self.rectangulo.y < min_y:
            self.rectangulo.y = min_y
        if self.rectangulo.y > max_y:
            self.rectangulo.y = max_y
    
    def actualizar(self):
        self.energia = min(ENERGIA_MAXIMA, self.energia + REGENERACION_ENERGIA)
    
    def recibir_dano(self, cantidad):
        self.energia = max(0, self.energia - cantidad)
    
    def esta_vivo(self):
        return self.energia >= 1
    
    def dibujar(self, pantalla):
        if MOSTRAR_SPRITES and IMAGEN_JUGADOR:
            pantalla.blit(IMAGEN_JUGADOR, (self.rectangulo.x, self.rectangulo.y))
        else:
            pygame.draw.rect(pantalla, self.color, self.rectangulo)

class Enemigo:
    def __init__(self, x, y):
        tamano = max(6, TAMANIO_TILE-6)
        self.rectangulo = pygame.Rect(x, y, tamano, tamano)
        self.color = AZUL
        self.velocidad = 1.8
        self.esta_activo = True
        self.tiempo_muerte = 0
        self.ruta = None
        self.indice_ruta = 0
        self.intervalo_recalculo = 12
        self.temporizador_recalculo = 0
        self.contador_atasco = 0
        self.ultima_posicion = (x, y)
    
    def mover_ia(self, objetivo, obstaculos, modo, salidas, mapa):
        if not self.esta_activo:
            return
        
        def pixel_a_tile(px, py):
            tx = int(px // TAMANIO_TILE)
            ty = int((py - MARGEN_SUPERIOR_UI) // TAMANIO_TILE)
            return tx, ty
        
        centro_x, centro_y = self.rectangulo.centerx, self.rectangulo.centery
        tile_inicio = pixel_a_tile(centro_x, centro_y)
        
        if modo == "escapa":
            tile_objetivo = pixel_a_tile(objetivo.rectangulo.centerx, objetivo.rectangulo.centery)
            evitar = set()
        else:
            tiles_salida = [pixel_a_tile(s.rectangulo.centerx, s.rectangulo.centery) for s in salidas]
            if not tiles_salida:
                tile_objetivo = pixel_a_tile(objetivo.rectangulo.centerx, objetivo.rectangulo.centery)
            else:
                def dist_tiles(a, b):
                    return abs(a[0] - b[0]) + abs(a[1] - b[1])
                tile_objetivo = min(tiles_salida, key=lambda e: dist_tiles(tile_inicio, e))
            evitar = {pixel_a_tile(objetivo.rectangulo.centerx, objetivo.rectangulo.centery)}
        
        if self.temporizador_recalculo <= 0 or not self.ruta:
            self.ruta = bfs_ruta_enemigo(mapa, tile_inicio, tile_objetivo, evitar, modo)
            if self.ruta:
                if len(self.ruta) > 1 and self.ruta[0] == tile_inicio:
                    self.indice_ruta = 1
                else:
                    self.indice_ruta = 0
            else:
                self.indice_ruta = 0
            self.temporizador_recalculo = self.intervalo_recalculo
        else:
            self.temporizador_recalculo -= 1
        
        if not self.ruta:
            return
        
        if self.indice_ruta >= len(self.ruta):
            self.ruta = None
            return
        
        nx, ny = self.ruta[self.indice_ruta]
        objetivo_px = nx * TAMANIO_TILE + TAMANIO_TILE // 2
        objetivo_py = ny * TAMANIO_TILE + TAMANIO_TILE // 2 + MARGEN_SUPERIOR_UI
        
        dx = objetivo_px - self.rectangulo.centerx
        dy = objetivo_py - self.rectangulo.centery
        distancia = (dx * dx + dy * dy) ** 0.5
        
        if distancia <= max(1.0, self.velocidad):
            if self.indice_ruta < len(self.ruta) - 1:
                self.indice_ruta += 1
            else:
                self.ruta = None
            return
        
        vx = (dx / distancia) * self.velocidad if distancia > 0 else 0.0
        vy = (dy / distancia) * self.velocidad if distancia > 0 else 0.0
        
        prev_x, prev_y = self.rectangulo.x, self.rectangulo.y
        
        self.rectangulo.x = int(self.rectangulo.x + vx)
        
        def esta_bloqueado(obst):
            if isinstance(obst, Muro):
                return True
            if modo == "escapa" and isinstance(obst, Tunel):
                return True
            if modo == "cazador" and isinstance(obst, Lianas):
                return True
            return False
        
        colision_x = any(self.rectangulo.colliderect(o.rectangulo) and esta_bloqueado(o) for o in obstaculos)
        if colision_x:
            self.rectangulo.x = prev_x
        
        self.rectangulo.y = int(self.rectangulo.y + vy)
        colision_y = any(self.rectangulo.colliderect(o.rectangulo) and esta_bloqueado(o) for o in obstaculos)
        if colision_y:
            self.rectangulo.y = prev_y
        
        posicion_actual = (self.rectangulo.x, self.rectangulo.y)
        if posicion_actual == self.ultima_posicion:
            self.contador_atasco += 1
            if self.contador_atasco >= 6:
                self.ruta = None
                self.temporizador_recalculo = 0
                self.contador_atasco = 0
                tile_actual_x = int(self.rectangulo.centerx // TAMANIO_TILE)
                tile_actual_y = int((self.rectangulo.centery - MARGEN_SUPERIOR_UI) // TAMANIO_TILE)
                centro_px = tile_actual_x * TAMANIO_TILE + TAMANIO_TILE // 2
                centro_py = tile_actual_y * TAMANIO_TILE + TAMANIO_TILE // 2 + MARGEN_SUPERIOR_UI
                empujon_x = 1 if centro_px > self.rectangulo.centerx else -1 if centro_px < self.rectangulo.centerx else 0
                empujon_y = 1 if centro_py > self.rectangulo.centery else -1 if centro_py < self.rectangulo.centery else 0
                self.rectangulo.x += empujon_x
                self.rectangulo.y += empujon_y
        else:
            self.contador_atasco = 0
        self.ultima_posicion = posicion_actual
        
        if colision_x or colision_y:
            self.temporizador_recalculo = min(self.temporizador_recalculo, 3)
        
        min_x = 0
        min_y = MARGEN_SUPERIOR_UI
        max_x = ANCHO_MAPA * TAMANIO_TILE - self.rectangulo.width
        max_y = MARGEN_SUPERIOR_UI + ALTO_MAPA * TAMANIO_TILE - self.rectangulo.height
        if self.rectangulo.x < min_x:
            self.rectangulo.x = min_x
        if self.rectangulo.x > max_x:
            self.rectangulo.x = max_x
        if self.rectangulo.y < min_y:
            self.rectangulo.y = min_y
        if self.rectangulo.y > max_y:
            self.rectangulo.y = max_y
    
    def morir(self):
        self.esta_activo = False
        self.tiempo_muerte = time.time()
    
    def revisar_reaparicion(self, posicion):
        if not self.esta_activo and time.time() - self.tiempo_muerte > TIEMPO_REAPARICION:
            self.esta_activo = True
            self.rectangulo.topleft = posicion
    
    def dibujar(self, pantalla):
        if not self.esta_activo:
            return
        if MOSTRAR_SPRITES and IMAGEN_ENEMIGO:
            pantalla.blit(IMAGEN_ENEMIGO, (self.rectangulo.x, self.rectangulo.y))
        else:
            pygame.draw.rect(pantalla, self.color, self.rectangulo)

class Trampa:
    def __init__(self, x, y):
        self.rectangulo = pygame.Rect(x, y, TAMANIO_TILE, TAMANIO_TILE)
        self.color = NARANJA
    
    def dibujar(self, pantalla):
        if MOSTRAR_SPRITES and IMAGEN_TRAMPA:
            pantalla.blit(IMAGEN_TRAMPA, (self.rectangulo.x, self.rectangulo.y))
        else:
            pygame.draw.rect(pantalla, self.color, self.rectangulo, 3)

# --- Sistema de configuración y opciones ---

def cargar_configuracion():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            return config.get("mostrar_sprites", True), config.get("musica", "Angry_Birds.mp3")
    except (FileNotFoundError, json.JSONDecodeError):
        return True, "Angry_Birds.mp3"

def guardar_configuracion(mostrar_sprites, musica):
    config = {"mostrar_sprites": mostrar_sprites, "musica": musica}
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

def cargar_musica(nombre_cancion):
    if nombre_cancion == "Sin música":
        pygame.mixer.music.stop()
        return
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    posibles = [
        os.path.join(script_dir, 'CodeFiles', nombre_cancion),
        os.path.join(script_dir, '..', 'CodeFiles', nombre_cancion),
        os.path.join(script_dir, '..', '..', 'CodeFiles', nombre_cancion),
        os.path.join('CodeFiles', nombre_cancion),
        os.path.join('..', 'CodeFiles', nombre_cancion),
        os.path.join('..', '..', 'CodeFiles', nombre_cancion),
        nombre_cancion
    ]
    
    for p in posibles:
        ruta_normalizada = os.path.normpath(p)
        if os.path.exists(ruta_normalizada):
            try:
                pygame.mixer.music.load(ruta_normalizada)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.5)
                return
            except Exception as e:
                print(f"Error al cargar {ruta_normalizada}: {e}")
                continue
    
    print(f"No se pudo cargar la música: {nombre_cancion}")

def cargar_sprite(nombre_archivo, tamano=None):
    if tamano is None:
        tamano = (max(4, TAMANIO_TILE-4), max(4, TAMANIO_TILE-4))
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    posibles = [
        os.path.join(script_dir, 'CodeFiles', nombre_archivo),
        os.path.join(script_dir, '..', 'CodeFiles', nombre_archivo),
        os.path.join(script_dir, '..', '..', 'CodeFiles', nombre_archivo),
        os.path.join('CodeFiles', nombre_archivo),
        os.path.join('..', 'CodeFiles', nombre_archivo),
        os.path.join('..', '..', 'CodeFiles', nombre_archivo),
        nombre_archivo
    ]
    
    for p in posibles:
        ruta_normalizada = os.path.normpath(p)
        if os.path.exists(ruta_normalizada):
            try:
                img = pygame.image.load(ruta_normalizada).convert_alpha()
                return pygame.transform.scale(img, tamano)
            except Exception as e:
                print(f"Error cargando sprite {ruta_normalizada}: {e}")
                continue
    
    print(f"No se pudo cargar el sprite: {nombre_archivo}")
    return None


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

def pantalla_opciones(pantalla, reloj, fuentes):
    global MOSTRAR_SPRITES, MUSICA_SELECCIONADA
    
    ancho_boton, alto_boton, espacio = 300, 50, 20
    centro_x = ANCHO_PANTALLA // 2
    
    boton_ajustes = Boton(centro_x - ancho_boton//2, 150, ancho_boton, alto_boton, "Ajustes", GRIS_CLARO, BLANCO)
    boton_sonido = Boton(centro_x - ancho_boton//2, 150 + alto_boton + espacio, ancho_boton, alto_boton, "Sonido", GRIS_CLARO, BLANCO)
    boton_volver = Boton(centro_x - ancho_boton//2, 150 + (alto_boton + espacio) * 2, ancho_boton, alto_boton, "Volver", GRIS_CLARO, BLANCO)
    
    while True:
        posicion_mouse = pygame.mouse.get_pos()
        boton_ajustes.verificar_hover(posicion_mouse)
        boton_sonido.verificar_hover(posicion_mouse)
        boton_volver.verificar_hover(posicion_mouse)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if boton_ajustes.fue_clickeado(evento):
                pantalla_ajustes(pantalla, reloj, fuentes)
            if boton_sonido.fue_clickeado(evento):
                pantalla_sonido(pantalla, reloj, fuentes)
            if boton_volver.fue_clickeado(evento):
                return
        
        pantalla.fill(GRIS_MAS_OSCURO)
        titulo = fuentes['titulo'].render("Opciones", True, BLANCO)
        pantalla.blit(titulo, (ANCHO_PANTALLA//2 - titulo.get_width()//2, 50))
        
        boton_ajustes.dibujar(pantalla, fuentes['boton'])
        boton_sonido.dibujar(pantalla, fuentes['boton'])
        boton_volver.dibujar(pantalla, fuentes['boton'])
        
        pygame.display.flip()
        reloj.tick(60)

def pantalla_ajustes(pantalla, reloj, fuentes):
    global MOSTRAR_SPRITES
    
    checkbox = Checkbox(ANCHO_PANTALLA//2 - 150, 200, 30, "Mostrar Pixel Arts (Sprites)", MOSTRAR_SPRITES)
    boton_reiniciar = Boton(ANCHO_PANTALLA//2 - 150, 280, 300, 50, "Reiniciar Puntajes", ROJO, NARANJA)
    boton_volver = Boton(ANCHO_PANTALLA//2 - 100, 400, 200, 50, "Volver", GRIS_CLARO, BLANCO)
    
    mensaje_confirmacion = ""
    tiempo_mensaje = 0
    
    while True:
        posicion_mouse = pygame.mouse.get_pos()
        checkbox.verificar_hover(posicion_mouse)
        boton_reiniciar.verificar_hover(posicion_mouse)
        boton_volver.verificar_hover(posicion_mouse)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if checkbox.fue_clickeado(evento):
                MOSTRAR_SPRITES = checkbox.marcada
                guardar_configuracion(MOSTRAR_SPRITES, MUSICA_SELECCIONADA)
            if boton_reiniciar.fue_clickeado(evento):
                if confirmar_reinicio(pantalla, reloj, fuentes):
                    puntajes_vacios = {"escapa": [], "cazador_1min": [], "cazador_3min": []}
                    guardar_puntajes(puntajes_vacios)
                    mensaje_confirmacion = "¡Puntajes reiniciados!"
                    tiempo_mensaje = time.time()
            if boton_volver.fue_clickeado(evento):
                return
        
        pantalla.fill(GRIS_MAS_OSCURO)
        titulo = fuentes['encabezado'].render("Ajustes", True, BLANCO)
        pantalla.blit(titulo, (ANCHO_PANTALLA//2 - titulo.get_width()//2, 100))
        
        checkbox.dibujar(pantalla, fuentes['puntaje'])
        boton_reiniciar.dibujar(pantalla, fuentes['boton'])
        boton_volver.dibujar(pantalla, fuentes['boton'])
        
        if mensaje_confirmacion and time.time() - tiempo_mensaje < 3:
            msg_surf = fuentes['puntaje'].render(mensaje_confirmacion, True, VERDE)
            pantalla.blit(msg_surf, (ANCHO_PANTALLA//2 - msg_surf.get_width()//2, 350))
        elif mensaje_confirmacion and time.time() - tiempo_mensaje >= 3:
            mensaje_confirmacion = ""
        
        pygame.display.flip()
        reloj.tick(60)

def confirmar_reinicio(pantalla, reloj, fuentes):
    ancho_boton, alto_boton = 120, 50
    centro_x = ANCHO_PANTALLA // 2
    centro_y = ALTO_PANTALLA // 2
    
    boton_si = Boton(centro_x - ancho_boton - 10, centro_y + 50, ancho_boton, alto_boton, "Sí", ROJO, NARANJA)
    boton_no = Boton(centro_x + 10, centro_y + 50, ancho_boton, alto_boton, "No", GRIS_CLARO, BLANCO)
    
    while True:
        posicion_mouse = pygame.mouse.get_pos()
        boton_si.verificar_hover(posicion_mouse)
        boton_no.verificar_hover(posicion_mouse)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if boton_si.fue_clickeado(evento):
                return True
            if boton_no.fue_clickeado(evento):
                return False
        
        overlay = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
        overlay.set_alpha(200)
        overlay.fill(NEGRO)
        pantalla.blit(overlay, (0, 0))
        
        ancho_dialogo, alto_dialogo = 500, 200
        rect_dialogo = pygame.Rect(centro_x - ancho_dialogo//2, centro_y - alto_dialogo//2, ancho_dialogo, alto_dialogo)
        pygame.draw.rect(pantalla, GRIS_MAS_OSCURO, rect_dialogo)
        pygame.draw.rect(pantalla, BLANCO, rect_dialogo, 3)
        
        fuente_advertencia = pygame.font.Font(None, 36)
        advertencia = fuente_advertencia.render("¿Estás seguro?", True, AMARILLO)
        pantalla.blit(advertencia, (centro_x - advertencia.get_width()//2, centro_y - 60))
        
        fuente_mensaje = pygame.font.Font(None, 28)
        mensaje = fuente_mensaje.render("Se borrarán todos los puntajes", True, BLANCO)
        pantalla.blit(mensaje, (centro_x - mensaje.get_width()//2, centro_y - 20))
        
        boton_si.dibujar(pantalla, fuentes['boton'])
        boton_no.dibujar(pantalla, fuentes['boton'])
        
        pygame.display.flip()
        reloj.tick(60)

def pantalla_sonido(pantalla, reloj, fuentes):
    global MUSICA_SELECCIONADA
    
    ancho_boton, alto_boton, espacio = 350, 40, 10
    centro_x = ANCHO_PANTALLA // 2
    inicio_y = 120
    
    botones_canciones = []
    for i, cancion in enumerate(CANCIONES_DISPONIBLES):
        nombre_mostrar = cancion.replace(".mp3", "").replace("_", " ")
        boton = Boton(centro_x - ancho_boton//2, inicio_y + i * (alto_boton + espacio), ancho_boton, alto_boton, 
                    nombre_mostrar, GRIS_CLARO, BLANCO)
        botones_canciones.append((boton, cancion))
    
    boton_volver = Boton(centro_x - 100, inicio_y + len(CANCIONES_DISPONIBLES) * (alto_boton + espacio) + 20, 
                    200, 50, "Volver", GRIS_CLARO, BLANCO)
    
    while True:
        posicion_mouse = pygame.mouse.get_pos()
        for boton, _ in botones_canciones:
            boton.verificar_hover(posicion_mouse)
        boton_volver.verificar_hover(posicion_mouse)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            for boton, cancion in botones_canciones:
                if boton.fue_clickeado(evento):
                    MUSICA_SELECCIONADA = cancion
                    cargar_musica(cancion)
                    guardar_configuracion(MOSTRAR_SPRITES, MUSICA_SELECCIONADA)
            
            if boton_volver.fue_clickeado(evento):
                return
        
        pantalla.fill(GRIS_MAS_OSCURO)
        titulo = fuentes['encabezado'].render("Seleccionar Música", True, BLANCO)
        pantalla.blit(titulo, (ANCHO_PANTALLA//2 - titulo.get_width()//2, 50))
        
        actual = fuentes['puntaje'].render(f"Actual: {MUSICA_SELECCIONADA.replace('.mp3', '').replace('_', ' ')}", 
                                    True, AMARILLO)
        pantalla.blit(actual, (ANCHO_PANTALLA//2 - actual.get_width()//2, 85))
        
        for boton, cancion in botones_canciones:
            if cancion == MUSICA_SELECCIONADA:
                pygame.draw.rect(pantalla, VERDE, boton.rectangulo, 3)
            boton.dibujar(pantalla, fuentes['puntaje'])
        
        boton_volver.dibujar(pantalla, fuentes['boton'])
        
        pygame.display.flip()
        reloj.tick(60)

def dibujar_interfaz(pantalla, jugador, ultimo_tiempo_trampa, modo, puntaje, tiempo_restante=None):
    ancho_barra = max(200, ANCHO_PANTALLA // 5)
    ancho_barra = min(ancho_barra, ANCHO_PANTALLA - 20)
    x_barra, y_barra = 10, 10
    altura_barra = max(20, min(36, TAMANIO_TILE))
    energia = max(0, min(ENERGIA_MAXIMA, jugador.energia))
    ancho_relleno = int((energia / ENERGIA_MAXIMA) * ancho_barra)
    
    pygame.draw.rect(pantalla, NEGRO, (x_barra, y_barra, ancho_barra+4, altura_barra+4))
    pygame.draw.rect(pantalla, GRIS_OSCURO, (x_barra+2, y_barra+2, ancho_barra, altura_barra))
    pygame.draw.rect(pantalla, ROJO, (x_barra+2, y_barra+2, ancho_relleno, altura_barra))
    
    if modo == "escapa":
        enfriamiento = ENFRIAMIENTO_TRAMPA - (time.time() - ultimo_tiempo_trampa)
        lista = enfriamiento <= 0
        texto = "Trampa: LISTA" if lista else f"Trampa: {enfriamiento:.1f}s"
        color = VERDE if lista else AMARILLO
    else:
        texto = f"Puntaje: {puntaje}"
        color = BLANCO
    
    fuente = pygame.font.Font(None, max(18, altura_barra-2))
    texto_ui = fuente.render(texto, True, color)
    pantalla.blit(texto_ui, (x_barra, y_barra + altura_barra + 6))
    
    fuente_pct = pygame.font.Font(None, max(18, altura_barra-2))
    texto_pct = fuente_pct.render(f"{int(energia)}/{ENERGIA_MAXIMA}", True, BLANCO)
    pantalla.blit(texto_pct, (x_barra + ancho_barra - texto_pct.get_width(), y_barra + (altura_barra - texto_pct.get_height())//2))
    
    if modo == "cazador" and tiempo_restante is not None:
        minutos = int(tiempo_restante // 60)
        segundos = int(tiempo_restante % 60)
        texto_temporizador = f"{minutos:02d}:{segundos:02d}"
        fuente_temporizador = pygame.font.Font(None, max(36, altura_barra + 8))
        superficie_temporizador = fuente_temporizador.render(texto_temporizador, True, AMARILLO)
        x_temporizador = ANCHO_PANTALLA - superficie_temporizador.get_width() - 15
        y_temporizador = 10
        rect_fondo = pygame.Rect(x_temporizador - 5, y_temporizador - 2, superficie_temporizador.get_width() + 10, superficie_temporizador.get_height() + 4)
        pygame.draw.rect(pantalla, NEGRO, rect_fondo)
        pygame.draw.rect(pantalla, AMARILLO, rect_fondo, 2)
        pantalla.blit(superficie_temporizador, (x_temporizador, y_temporizador))

def ejecutar_juego(pantalla, reloj, nombre_jugador, modo, tiempo_limite=None):
    tiempo_inicio = time.time()
    puntaje = 0
    mapa = MapaJuego(ANCHO_MAPA, ALTO_MAPA)
    mapa.generar_laberinto(modo)
    jugador = Jugador(*mapa.obtener_posicion_valida())
    enemigos = [Enemigo(*mapa.obtener_posicion_valida()) for _ in range(NUMERO_CAZADORES)]
    trampas = []
    ultimo_tiempo_trampa = -ENFRIAMIENTO_TRAMPA
    
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if modo == "escapa" and evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                if len(trampas) < MAXIMO_TRAMPAS and time.time() - ultimo_tiempo_trampa > ENFRIAMIENTO_TRAMPA:
                    trampas.append(Trampa(jugador.rectangulo.x, jugador.rectangulo.y))
                    ultimo_tiempo_trampa = time.time()
        
        teclas = pygame.key.get_pressed()
        corriendo = teclas[pygame.K_LSHIFT]
        dx, dy = 0, 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            dx = -1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            dx = 1
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            dy = -1
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            dy = 1
        
        jugador.mover(dx, dy, mapa.obstaculos, corriendo, modo)
        jugador.actualizar()
        
        for enemigo in enemigos:
            enemigo.mover_ia(jugador, mapa.obstaculos, modo, mapa.salidas, mapa)
            if modo == "escapa":
                enemigo.revisar_reaparicion(mapa.obtener_posicion_valida())
                if enemigo.esta_activo and jugador.rectangulo.colliderect(enemigo.rectangulo):
                    jugador.recibir_dano(DANIO_POR_CAPTURA)
                    enemigo.rectangulo.topleft = mapa.obtener_posicion_valida()
                    if not jugador.esta_vivo():
                        return "¡Perdiste!", f"Puntaje final: {puntaje}"
            else:
                if jugador.rectangulo.colliderect(enemigo.rectangulo):
                    puntaje += PUNTOS_CAZADOR_AGARRA
                    enemigo.rectangulo.topleft = mapa.obtener_posicion_valida()
                for tile_salida in mapa.salidas:
                    if enemigo.rectangulo.colliderect(tile_salida.rectangulo):
                        puntaje -= PUNTOS_CAZADOR_ESCAPE
                        enemigo.rectangulo.topleft = mapa.obtener_posicion_valida()
        
        if modo == "escapa":
            for trampa in trampas[:]:
                for enemigo in enemigos:
                    if enemigo.esta_activo and trampa.rectangulo.colliderect(enemigo.rectangulo):
                        enemigo.morir()
                        trampas.remove(trampa)
                        puntaje += BONIFICACION_TRAMPA
                        break
            if any(jugador.rectangulo.colliderect(salida.rectangulo) for salida in mapa.salidas):
                puntaje_tiempo = max(0, int(10000 - (time.time() - tiempo_inicio) * 100))
                puntaje_final = puntaje_tiempo + puntaje
                agregar_puntaje("escapa", nombre_jugador, puntaje_final)
                return "¡Ganaste!", f"Puntaje: {puntaje_final}"
        
        if modo == "cazador" and tiempo_limite and time.time() - tiempo_inicio > tiempo_limite:
            modo_puntaje = "cazador_1min" if tiempo_limite == 60 else "cazador_3min"
            agregar_puntaje(modo_puntaje, nombre_jugador, puntaje)
            return "¡Tiempo Agotado!", f"Puntaje Final: {puntaje}"
        
        pantalla.fill(NEGRO)
        mapa.dibujar(pantalla)
        jugador.dibujar(pantalla)
        for trampa in trampas:
            trampa.dibujar(pantalla)
        for enemigo in enemigos:
            enemigo.dibujar(pantalla)
        
        tiempo_restante = None
        if modo == "cazador" and tiempo_limite:
            tiempo_restante = max(0, tiempo_limite - (time.time() - tiempo_inicio))
        
        dibujar_interfaz(pantalla, jugador, ultimo_tiempo_trampa, modo, puntaje, tiempo_restante)
        pygame.display.flip()
        reloj.tick(60)



def principal():
    pygame.init()
    global TAMANIO_TILE, ANCHO_PANTALLA, ALTO_PANTALLA
    pygame.init()
    pygame.mixer.init()
    global TAMANIO_TILE, ANCHO_PANTALLA, ALTO_PANTALLA, IMAGEN_JUGADOR, IMAGEN_ENEMIGO, IMAGEN_TRAMPA, IMAGEN_LIANAS, IMAGEN_TUNEL, IMAGEN_SALIDA, MOSTRAR_SPRITES, MUSICA_SELECCIONADA

# Cargar configuración guardada
    MOSTRAR_SPRITES, MUSICA_SELECCIONADA = cargar_configuracion()
    cargar_musica(MUSICA_SELECCIONADA)
    
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
    'opciones': Boton(ANCHO_PANTALLA//2-150, ALTO_PANTALLA//2+10, 300, 50, "Opciones", GRIS_CLARO, BLANCO),
    'salir': Boton(ANCHO_PANTALLA//2-150, ALTO_PANTALLA//2+70, 300, 50, "Salir", GRIS_CLARO, BLANCO)
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

                    if botones_menu['opciones'].fue_clickeado(evento):
                        estado_juego = "opciones"
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
            elif estado_juego == "opciones":
                pantalla_opciones(pantalla, reloj, fuentes_menu)
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
    'opciones': Boton(ANCHO_PANTALLA//2-150, ALTO_PANTALLA//2+10, 300, 50, "Opciones", GRIS_CLARO, BLANCO),
    'salir': Boton(ANCHO_PANTALLA//2-150, ALTO_PANTALLA//2+70, 300, 50, "Salir", GRIS_CLARO, BLANCO)
}
                
            elif estado_juego == "fin_juego":
                pantalla_fin(pantalla, reloj, fuentes_menu, resultado, info_puntaje)
                estado_juego = "menu_principal"
                
    except KeyboardInterrupt:
        pygame.quit()
        exit(0)

if __name__ == "__main__":
    principal()