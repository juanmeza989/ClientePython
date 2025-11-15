#!/usr/bin/env python3
"""
Configuración del visualizador 3D del robot.
Ajusta estos valores para personalizar la visualización.
"""

# === CONFIGURACIÓN DE LA CÁMARA ===
CAMERA_INITIAL_ROTATION = [45, -20]  # [horizontal, vertical] en grados
CAMERA_INITIAL_DISTANCE = 25.0       # Distancia inicial de la cámara
CAMERA_MIN_DISTANCE = 8.0            # Distancia mínima (zoom máximo)
CAMERA_MAX_DISTANCE = 50.0           # Distancia máxima (zoom mínimo)
CAMERA_ZOOM_SENSITIVITY = 1.0        # Sensibilidad del zoom con rueda del mouse
CAMERA_ROTATION_SENSITIVITY = 0.5    # Sensibilidad de rotación con mouse

# === DIMENSIONES DEL ROBOT ===
# Dimensiones realistas para un brazo robótico industrial
BASE_HEIGHT = 2.0          # Altura de la base - más robusta
LOWER_ARM_LENGTH = 6.0     # Brazo inferior más largo para mejor alcance
UPPER_ARM_LENGTH = 5.5     # Brazo superior proporcional
EFFECTOR_LENGTH = 1.8      # Efector final más compacto

# Configuración adicional de geometría
BASE_RADIUS = 2.5          # Radio de la base del robot
JOINT_SIZE_FACTOR = 0.6    # Factor para el tamaño de las articulaciones
ARM_THICKNESS_FACTOR = 0.3  # Factor para el grosor de los brazos

# === CONFIGURACIÓN DE ANIMACIÓN ===
ANIMATION_SPEED = 2.0      # Velocidad de las animaciones (mayor = más rápido)
FPS_TARGET = 60           # Frames por segundo objetivo

# === CONFIGURACIÓN VISUAL ===
BACKGROUND_COLOR = (0.1, 0.1, 0.15, 1.0)  # Color de fondo (R, G, B, A)

# Configuración de iluminación
LIGHT_POSITION = (10.0, 15.0, 10.0, 1.0)  # Posición de la luz principal
LIGHT_AMBIENT = (0.4, 0.4, 0.4, 1.0)      # Luz ambiente
LIGHT_DIFFUSE = (0.8, 0.8, 0.8, 1.0)      # Luz difusa
LIGHT_SPECULAR = (1.0, 1.0, 1.0, 1.0)     # Luz especular

# Campo de visión de la cámara
FIELD_OF_VIEW = 60  # Grados

# === COLORES DEL ROBOT ===
# Base del robot
BASE_COLOR = (0.3, 0.3, 0.3)

# Estados de los motores
MOTORS_ON_LOWER_ARM = (0.8, 0.2, 0.2)   # Rojo brillante
MOTORS_ON_UPPER_ARM = (0.2, 0.8, 0.2)   # Verde brillante
MOTORS_OFF_LOWER_ARM = (0.4, 0.1, 0.1)  # Rojo oscuro
MOTORS_OFF_UPPER_ARM = (0.1, 0.4, 0.1)  # Verde oscuro

# Estados del efector
EFFECTOR_ACTIVE_BODY = (1.0, 1.0, 0.0)    # Amarillo brillante
EFFECTOR_ACTIVE_TIP = (1.0, 0.0, 0.0)     # Rojo
EFFECTOR_INACTIVE_BODY = (0.5, 0.5, 0.0)  # Amarillo oscuro
EFFECTOR_INACTIVE_TIP = (0.3, 0.3, 0.3)   # Gris

# === CONFIGURACIÓN DEL ENTORNO ===
# Cuadrícula del suelo
GRID_SIZE = 20           # Tamaño de la cuadrícula
GRID_SPACING = 1         # Espaciado entre líneas
GRID_COLOR = (0.4, 0.4, 0.4)           # Color líneas normales
GRID_MAIN_COLOR = (0.6, 0.6, 0.6)     # Color líneas principales

# Ejes de coordenadas con valores de referencia
AXIS_LENGTH = 15         # Longitud extendida para mejor referencia
AXIS_WIDTH = 3.0         # Grosor de las líneas de los ejes
AXIS_X_COLOR = (1.0, 0.0, 0.0)  # Rojo
AXIS_Y_COLOR = (0.0, 1.0, 0.0)  # Verde  
AXIS_Z_COLOR = (0.0, 0.0, 1.0)  # Azul

# Configuración de marcas de referencia
AXIS_MARKS_INTERVAL = 2  # Intervalo entre marcas (cada 2 unidades)
AXIS_MARKS_SIZE = 0.4    # Tamaño de las marcas
AXIS_NUMBERS_INTERVAL = 5 # Intervalo para números de referencia

# Indicador de posición objetivo
TARGET_INDICATOR_COLOR = (0.0, 1.0, 1.0)  # Cian
TARGET_INDICATOR_SIZE = 0.3                # Tamaño de la esfera

# === CONFIGURACIÓN AVANZADA ===
# Calidad de renderizado (más segments = mejor calidad, menor rendimiento)
CYLINDER_SEGMENTS = 16    # Segmentos de los cilindros del brazo
SPHERE_SLICES = 8         # Segmentos horizontales de las esferas
SPHERE_STACKS = 8         # Segmentos verticales de las esferas

# Configuración de viewport
WINDOW_WIDTH = 1000       # Ancho por defecto de la ventana
WINDOW_HEIGHT = 700       # Alto por defecto de la ventana

# === POSICIÓN HOME ===
# Calculada automáticamente basada en las dimensiones del brazo
# HOME_X = 0.0
# HOME_Y = UPPER_ARM_LENGTH + EFFECTOR_LENGTH  
# HOME_Z = LOWER_ARM_LENGTH

# === NOTAS DE CONFIGURACIÓN ===
"""
CONSEJOS DE CONFIGURACIÓN:

1. Para un robot más grande en pantalla:
   - Reducir CAMERA_INITIAL_DISTANCE
   - Aumentar las dimensiones del brazo (LOWER_ARM_LENGTH, etc.)

2. Para movimientos más suaves:
   - Reducir ANIMATION_SPEED
   - Aumentar FPS_TARGET

3. Para mejor calidad visual:
   - Aumentar CYLINDER_SEGMENTS, SPHERE_SLICES, SPHERE_STACKS
   - Ajustar configuración de iluminación

4. Para mejor rendimiento:
   - Reducir FPS_TARGET
   - Reducir segmentos de geometría
   - Reducir GRID_SIZE

5. Para vista más cinematográfica:
   - Ajustar BACKGROUND_COLOR a negro: (0.0, 0.0, 0.0, 1.0)
   - Aumentar LIGHT_AMBIENT para más iluminación
"""