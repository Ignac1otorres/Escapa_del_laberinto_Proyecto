# 🎮 Escapa del Laberinto

Un juego de laberinto desarrollado en Python con Pygame donde puedes jugar en dos modos: **Escapa** (escapa del laberinto antes de que los cazadores te atrapen) o **Cazador** (captura a los enemigos antes de que escapen).

## 📥 Cómo Descargar el Juego

### Opción 1: Descargar como ZIP (Recomendado para principiantes)

1. Ve a la página principal del repositorio: https://github.com/Ignac1otorres/Escapa_del_laberinto_Proyecto
2. Haz clic en el botón verde **"Code"** (Código)
3. Selecciona **"Download ZIP"**
4. Extrae el archivo ZIP en la carpeta de tu preferencia

### Opción 2: Clonar con Git

Si tienes Git instalado, abre una terminal y ejecuta:

```bash
git clone https://github.com/Ignac1otorres/Escapa_del_laberinto_Proyecto.git
```

## 🔧 Requisitos del Sistema

- **Python 3.7** o superior
- **Pygame** (biblioteca de Python para juegos)

## 📦 Instalación de Dependencias

### Paso 1: Instalar Python

Si no tienes Python instalado:
- **Windows**: Descarga desde https://www.python.org/downloads/ y marca la opción "Add Python to PATH" durante la instalación
- **macOS**: Descarga desde https://www.python.org/downloads/ o usa Homebrew: `brew install python`
- **Linux**: Usa tu gestor de paquetes, por ejemplo: `sudo apt install python3`

### Paso 2: Instalar Pygame

Abre una terminal o línea de comandos y ejecuta:

```bash
pip install pygame
```

O si tienes múltiples versiones de Python:

```bash
pip3 install pygame
```

## 🚀 Cómo Ejecutar el Juego

1. Abre una terminal o línea de comandos
2. Navega a la carpeta donde descargaste el juego:
   ```bash
   cd ruta/a/Escapa_del_laberinto_Proyecto
   ```
3. Ejecuta el juego:
   ```bash
   python P1_IGNACIO_TORRES_YOHAN_MORERA.py
   ```
   O en algunos sistemas:
   ```bash
   python3 P1_IGNACIO_TORRES_YOHAN_MORERA.py
   ```

## 🎯 Modos de Juego

### Modo Escapa
- **Objetivo**: Escapa del laberinto antes de que los cazadores te atrapen
- **Controles**:
  - Flechas o WASD para moverse
  - Shift izquierdo para correr (consume energía)
  - Espacio para colocar trampas

### Modo Cazador
- **Objetivo**: Captura a los enemigos antes de que escapen por las salidas
- **Duraciones**: 1 minuto o 3 minutos
- **Controles**: Flechas o WASD para moverse, Shift izquierdo para correr

## 📁 Estructura del Proyecto

```
Escapa_del_laberinto_Proyecto/
├── P1_IGNACIO_TORRES_YOHAN_MORERA.py   # Archivo principal del juego
├── config.json                          # Configuración guardada
├── CODEFILES/CodeFiles/                 # Carpeta de recursos
│   ├── *.mp3                            # Archivos de música
│   └── *.png, *.webp                    # Sprites y gráficos
└── README.md                            # Este archivo
```

## ⚙️ Opciones del Juego

- **Mostrar Sprites**: Activa/desactiva los gráficos pixel art
- **Música**: Selecciona entre varias canciones disponibles
- **Reiniciar Puntajes**: Borra todos los puntajes guardados

## 👥 Autores

- Ignacio Torres
- Yohan Morera

---

¡Disfruta del juego! 🎮
