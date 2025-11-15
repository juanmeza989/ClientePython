#!/usr/bin/env python3
"""
Configuración del visualizador 3D del robot.
Ajusta estos valores para personalizar la visualización.
"""

# === CONFIGURACIÓN DE LA CÁMARA ===
CAMERA_INITIAL_ROTATION = [45, -20]  # [horizontal, vertical] en grados
CAMERA_INITIAL_DISTANCE = 600.0      # Distancia inicial más alejada para mejor vista
CAMERA_MIN_DISTANCE = 300.0          # Distancia mínima (zoom máximo)
CAMERA_MAX_DISTANCE = 1200.0         # Distancia máxima (zoom mínimo)
CAMERA_ZOOM_SENSITIVITY = 8.0        # Sensibilidad del zoom aumentada
CAMERA_ROTATION_SENSITIVITY = 0.5    # Sensibilidad de rotación con mouse

# === DIMENSIONES DEL ROBOT ===
# Dimensiones realistas para un brazo robótico industrial
BASE_HEIGHT = 60.0          # Altura de la base - más robusta
LOWER_ARM_LENGTH = 120.0     # Brazo inferior más largo para mejor alcance
UPPER_ARM_LENGTH = 120.0     # Brazo superior proporcional
EFFECTOR_LENGTH = 18.0      # Efector final más compacto

# Configuración adicional de geometría
BASE_RADIUS = 30.0          # Radio de la base del robot
JOINT_SIZE_FACTOR = 2.0     # Factor para el tamaño de las articulaciones (más grandes)
ARM_THICKNESS_FACTOR = 3.0  # Factor para el grosor de los brazos (mucho más gruesos)

# === CONFIGURACIÓN DE ANIMACIÓN ===
ANIMATION_SPEED = 1.0      # Velocidad de las animaciones (mayor = más rápido)
FPS_TARGET = 60           # Frames por segundo objetivo

# === CONFIGURACIÓN VISUAL ===
BACKGROUND_COLOR = (0.1, 0.1, 0.15, 1.0)  # Color de fondo (R, G, B, A)

# Configuración de iluminación - ajustada para robot grande
LIGHT_POSITION = (100.0, 200.0, 100.0, 1.0)  # Posición de la luz principal escalada
LIGHT_AMBIENT = (0.5, 0.5, 0.5, 1.0)         # Luz ambiente aumentada
LIGHT_DIFFUSE = (0.8, 0.8, 0.8, 1.0)         # Luz difusa
LIGHT_SPECULAR = (1.0, 1.0, 1.0, 1.0)        # Luz especular

# Campo de visión de la cámara - ajustado para mejor vista del robot grande
FIELD_OF_VIEW = 50  # Grados (aumentado para ver mejor el robot)

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
# Cuadrícula del suelo - ajustada para robot grande
GRID_SIZE = 150              # Tamaño de la cuadrícula aumentado
GRID_SPACING = 10            # Espaciado entre líneas aumentado
GRID_COLOR = (0.4, 0.4, 0.4)           # Color líneas normales
GRID_MAIN_COLOR = (0.6, 0.6, 0.6)     # Color líneas principales

# Ejes de coordenadas con valores de referencia - escalados
AXIS_LENGTH = 200            # Longitud extendida para robot grande
AXIS_WIDTH = 3.0             # Grosor de las líneas de los ejes
AXIS_X_COLOR = (1.0, 0.0, 0.0)  # Rojo
AXIS_Y_COLOR = (0.0, 1.0, 0.0)  # Verde  
AXIS_Z_COLOR = (0.0, 0.0, 1.0)  # Azul

# Configuración de marcas de referencia - escaladas
AXIS_MARKS_INTERVAL = 20     # Intervalo entre marcas (cada 20 unidades)
AXIS_MARKS_SIZE = 4.0        # Tamaño de las marcas aumentado
AXIS_NUMBERS_INTERVAL = 50   # Intervalo para números de referencia

# Indicador de posición objetivo - escalado
TARGET_INDICATOR_COLOR = (0.0, 1.0, 1.0)  # Cian
TARGET_INDICATOR_SIZE = 3.0                # Tamaño de la esfera aumentado

# === CONFIGURACIÓN AVANZADA ===
# Calidad de renderizado (más segments = mejor calidad, menor rendimiento)
CYLINDER_SEGMENTS = 20       # Segmentos de los cilindros del brazo (mejor calidad)
SPHERE_SLICES = 12           # Segmentos horizontales de las esferas
SPHERE_STACKS = 12           # Segmentos verticales de las esferas

# Configuración de viewport - aumentada para mejor visualización
WINDOW_WIDTH = 500         # Ancho por defecto de la ventana
WINDOW_HEIGHT = 400         # Alto por defecto de la ventana

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

CONFIGURACIÓN ACTUAL:
Esta configuración está optimizada para un robot industrial grande y bien visible:
- Base: 60 unidades de altura, 30 de radio (más robusta y escalada)
- Brazo inferior: 120 unidades de longitud, radio 10.5 (3.5 × 3.0)
- Brazo superior: 120 unidades de longitud, radio 9 (3.0 × 3.0)  
- Efector: 18 unidades, radio ~12 para buena visibilidad
- Alcance total vertical: ~258 unidades
- Cámara configurada para distancia 600 unidades (más alejada)
- Grid de 150x150 unidades con espaciado de 10
- Ejes de referencia cada 20 unidades, números cada 50
- Factores de grosor: brazos ×3.0, articulaciones ×2.0
"""