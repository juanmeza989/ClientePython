#!/usr/bin/env python3
"""
Visualizador 3D del robot brazo utilizando pygame y OpenGL.
Simula el movimiento del brazo robótico basado en coordenadas.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import threading
import time

try:
    from viewer_3d_config import *
except ImportError:
    # Valores por defecto si no existe el archivo de configuración
    CAMERA_INITIAL_ROTATION = [45, -20]
    CAMERA_INITIAL_DISTANCE = 30.0
    CAMERA_MIN_DISTANCE = 10.0
    CAMERA_MAX_DISTANCE = 60.0
    CAMERA_ZOOM_SENSITIVITY = 1.0
    CAMERA_ROTATION_SENSITIVITY = 0.5
    
    BASE_HEIGHT = 2.0
    LOWER_ARM_LENGTH = 6.0
    UPPER_ARM_LENGTH = 5.5
    EFFECTOR_LENGTH = 1.8
    BASE_RADIUS = 2.5
    JOINT_SIZE_FACTOR = 0.6
    ARM_THICKNESS_FACTOR = 0.3
    
    ANIMATION_SPEED = 2.0
    FPS_TARGET = 60
    
    BACKGROUND_COLOR = (0.1, 0.1, 0.15, 1.0)
    LIGHT_POSITION = (10.0, 15.0, 10.0, 1.0)
    LIGHT_AMBIENT = (0.4, 0.4, 0.4, 1.0)
    LIGHT_DIFFUSE = (0.8, 0.8, 0.8, 1.0)
    LIGHT_SPECULAR = (1.0, 1.0, 1.0, 1.0)
    FIELD_OF_VIEW = 60
    
    BASE_COLOR = (0.3, 0.3, 0.3)
    MOTORS_ON_LOWER_ARM = (0.8, 0.2, 0.2)
    MOTORS_ON_UPPER_ARM = (0.2, 0.8, 0.2)
    MOTORS_OFF_LOWER_ARM = (0.4, 0.1, 0.1)
    MOTORS_OFF_UPPER_ARM = (0.1, 0.4, 0.1)
    
    EFFECTOR_ACTIVE_BODY = (1.0, 1.0, 0.0)
    EFFECTOR_ACTIVE_TIP = (1.0, 0.0, 0.0)
    EFFECTOR_INACTIVE_BODY = (0.5, 0.5, 0.0)
    EFFECTOR_INACTIVE_TIP = (0.3, 0.3, 0.3)
    
    GRID_SIZE = 20
    GRID_SPACING = 1
    GRID_COLOR = (0.4, 0.4, 0.4)
    GRID_MAIN_COLOR = (0.6, 0.6, 0.6)
    
    AXIS_LENGTH = 15
    AXIS_WIDTH = 3.0
    AXIS_X_COLOR = (1.0, 0.0, 0.0)
    AXIS_Y_COLOR = (0.0, 1.0, 0.0)
    AXIS_Z_COLOR = (0.0, 0.0, 1.0)
    AXIS_MARKS_INTERVAL = 2
    AXIS_MARKS_SIZE = 0.4
    AXIS_NUMBERS_INTERVAL = 5
    
    TARGET_INDICATOR_COLOR = (0.0, 1.0, 1.0)
    TARGET_INDICATOR_SIZE = 0.3
    
    CYLINDER_SEGMENTS = 20
    SPHERE_SLICES = 12
    SPHERE_STACKS = 12
    
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800

class Robot3DViewer:
    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
        """
        Inicializa el visualizador 3D del robot.
        
        Args:
            width (int): Ancho de la ventana
            height (int): Alto de la ventana
        """
        self.width = width
        self.height = height
        self.running = False
        self.thread = None
        
        # Configuración del robot (desde archivo de configuración)
        self.base_height = BASE_HEIGHT
        self.lower_arm_length = LOWER_ARM_LENGTH
        self.upper_arm_length = UPPER_ARM_LENGTH
        self.effector_length = EFFECTOR_LENGTH
        
        # Posición inicial del robot (posición home) - Ajustada para nueva orientación
        # Ahora Y es vertical, Z es profundidad
        self.robot_position = [0.0, self.lower_arm_length + self.upper_arm_length + self.effector_length, 0.0]
        self.target_position = [0.0, self.lower_arm_length + self.upper_arm_length + self.effector_length, 0.0]
        
        # Variables de animación
        self.animation_progress = 1.0  # 1.0 = movimiento completo
        self.animation_speed = ANIMATION_SPEED
        
        # Variables de cámara (desde configuración)
        self.camera_rotation = CAMERA_INITIAL_ROTATION.copy()
        self.camera_distance = CAMERA_INITIAL_DISTANCE
        
        # Estado del robot
        self.motors_enabled = False
        self.effector_active = False
        
        # Posición home del robot - Ajustada para nueva orientación
        self.home_position = [0.0, self.lower_arm_length + self.upper_arm_length + self.effector_length, 0.0]
        
    def start(self):
        """Inicia el visualizador 3D en un hilo separado."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_viewer, daemon=True)
            self.thread.start()
            
    def stop(self):
        """Detiene el visualizador 3D."""
        self.running = False
        if self.thread:
            self.thread.join()
            
    def update_position(self, x, y, z, animate=True):
        """
        Actualiza la posición objetivo del robot.
        
        Args:
            x, y, z (float): Nueva posición objetivo
            animate (bool): Si debe animar el movimiento
        """
        # Verificar que los motores estén activados antes de permitir movimiento
        if not self.motors_enabled:
            print("Advertencia: No se puede mover el robot en el visualizador 3D - los motores no están activados")
            return
            
        self.target_position = [x, y, z]
        if animate:
            self.animation_progress = 0.0
        else:
            self.robot_position = [x, y, z]
            self.animation_progress = 1.0
            
    def set_robot_state(self, motors_enabled=None, effector_active=None):
        """
        Actualiza el estado del robot.
        
        Args:
            motors_enabled (bool): Estado de los motores
            effector_active (bool): Estado del efector
        """
        if motors_enabled is not None:
            self.motors_enabled = motors_enabled
        if effector_active is not None:
            self.effector_active = effector_active
            
    def home_robot(self):
        """Mueve el robot a la posición home."""
        # Verificar que los motores estén activados antes de permitir movimiento
        if not self.motors_enabled:
            print("Advertencia: No se puede mover el robot a la posición home - los motores no están activados")
            return
            
        self.update_position(*self.home_position)
        
    def _run_viewer(self):
        """Bucle principal del visualizador 3D."""
        pygame.init()
        display = (self.width, self.height)
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Robot 3D Viewer")
        
        # Configuración inicial de OpenGL
        self._setup_opengl()
        
        clock = pygame.time.Clock()
        
        # Variables para control del mouse
        mouse_down = False
        last_mouse_pos = (0, 0)
        
        while self.running:
            dt = clock.tick(60) / 1000.0  # Delta time en segundos
            
            # Manejo de eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Botón izquierdo
                        mouse_down = True
                        last_mouse_pos = pygame.mouse.get_pos()
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_down = False
                        
                elif event.type == pygame.MOUSEMOTION and mouse_down:
                    # Rotación de cámara con mouse
                    mouse_pos = pygame.mouse.get_pos()
                    dx = mouse_pos[0] - last_mouse_pos[0]
                    dy = mouse_pos[1] - last_mouse_pos[1]
                    
                    self.camera_rotation[0] += dx * CAMERA_ROTATION_SENSITIVITY
                    self.camera_rotation[1] += dy * CAMERA_ROTATION_SENSITIVITY
                    
                    # Limitar rotación vertical
                    self.camera_rotation[1] = max(-90, min(90, self.camera_rotation[1]))
                    
                    last_mouse_pos = mouse_pos
                    
                elif event.type == pygame.MOUSEWHEEL:
                    # Zoom con rueda del mouse
                    self.camera_distance -= event.y * CAMERA_ZOOM_SENSITIVITY
                    self.camera_distance = max(CAMERA_MIN_DISTANCE, min(CAMERA_MAX_DISTANCE, self.camera_distance))
            
            # Actualizar animación
            if self.animation_progress < 1.0:
                self.animation_progress = min(1.0, self.animation_progress + dt * self.animation_speed)
                
                # Interpolación suave de la posición
                for i in range(3):
                    self.robot_position[i] = self._lerp(
                        self.robot_position[i], 
                        self.target_position[i], 
                        self._smooth_step(self.animation_progress)
                    )
            
            # Renderizar escena
            self._render_scene()
            pygame.display.flip()
            
        pygame.quit()
        
    def _setup_opengl(self):
        """Configuración inicial de OpenGL."""
        # Configuración básica
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Configurar color de fondo (desde configuración)
        glClearColor(*BACKGROUND_COLOR)
        
        # Configuración de iluminación (desde configuración)
        glLightfv(GL_LIGHT0, GL_POSITION, LIGHT_POSITION)
        glLightfv(GL_LIGHT0, GL_AMBIENT, LIGHT_AMBIENT)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, LIGHT_DIFFUSE)
        glLightfv(GL_LIGHT0, GL_SPECULAR, LIGHT_SPECULAR)
        
        # Configuración de perspectiva
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FIELD_OF_VIEW, (self.width / self.height), 0.1, 100.0)
        
        # Volver a matriz de modelo/vista
        glMatrixMode(GL_MODELVIEW)
        
    def _render_scene(self):
        """Renderiza la escena 3D completa."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Configurar cámara
        glLoadIdentity()
        
        # Posicionar cámara con rotación orbital centrada en el robot
        cam_x = self.camera_distance * math.cos(math.radians(self.camera_rotation[1])) * math.sin(math.radians(self.camera_rotation[0]))
        cam_y = self.camera_distance * math.sin(math.radians(self.camera_rotation[1])) + 5.0  # Elevar ligeramente el punto de vista
        cam_z = self.camera_distance * math.cos(math.radians(self.camera_rotation[1])) * math.cos(math.radians(self.camera_rotation[0]))
        
        # Centrar la cámara en el punto medio del robot (altura media)
        center_height = self.base_height + self.lower_arm_length / 2
        gluLookAt(cam_x, cam_y, cam_z,          # posición de la cámara
                  0, center_height, 0,          # punto al que mira (centro del robot)
                  0, 1, 0)                      # vector up
        
        # Renderizar elementos de la escena
        self._render_ground()
        self._render_coordinate_axes()
        self._render_robot()
        
    def _render_ground(self):
        """Renderiza el plano del suelo en XZ (Y=0)."""
        glColor3f(0.4, 0.4, 0.4)
        glBegin(GL_LINES)
        
        # Líneas de cuadrícula en el plano XZ (Y=0)
        grid_size = 20
        grid_spacing = 1
        for i in range(-grid_size, grid_size + 1, grid_spacing):
            # Líneas paralelas al eje X (en plano XZ)
            glVertex3f(i, 0.0, -grid_size)
            glVertex3f(i, 0.0, grid_size)
            # Líneas paralelas al eje Z (en plano XZ)
            glVertex3f(-grid_size, 0.0, i)
            glVertex3f(grid_size, 0.0, i)
            
        glEnd()
        
        # Líneas principales más gruesas
        glLineWidth(2.0)
        glColor3f(0.6, 0.6, 0.6)
        glBegin(GL_LINES)
        # Línea central X (en Y=0)
        glVertex3f(-grid_size, 0.0, 0)
        glVertex3f(grid_size, 0.0, 0)
        # Línea central Z (en Y=0)
        glVertex3f(0, 0.0, -grid_size)
        glVertex3f(0, 0.0, grid_size)
        glEnd()
        glLineWidth(1.0)
        
    def _render_coordinate_axes(self):
        """Renderiza los ejes de coordenadas con valores de referencia mejorados."""
        # Ejes principales más largos
        glLineWidth(3.0)
        glBegin(GL_LINES)
        
        # Eje X (rojo) - Horizontal derecha
        glColor3f(*AXIS_X_COLOR)
        glVertex3f(0, 0, 0)
        glVertex3f(AXIS_LENGTH, 0, 0)
        
        # Eje Y (verde) - Vertical arriba (era Z antes)
        glColor3f(*AXIS_Y_COLOR)
        glVertex3f(0, 0, 0)
        glVertex3f(0, AXIS_LENGTH, 0)
        
        # Eje Z (azul) - Horizontal adelante/atrás
        glColor3f(*AXIS_Z_COLOR)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, AXIS_LENGTH)
        glEnd()
        
        # Marcas de graduación más densas y visibles
        glLineWidth(2.0)
        glBegin(GL_LINES)
        
        # Marcas en eje X (cada AXIS_MARKS_INTERVAL unidades)
        glColor3f(AXIS_X_COLOR[0] * 0.8, AXIS_X_COLOR[1] * 0.8, AXIS_X_COLOR[2] * 0.8)
        for i in range(AXIS_MARKS_INTERVAL, AXIS_LENGTH + 1, AXIS_MARKS_INTERVAL):
            # Marcas principales (más largas)
            mark_size = AXIS_MARKS_SIZE * 1.5 if i % AXIS_NUMBERS_INTERVAL == 0 else AXIS_MARKS_SIZE
            glVertex3f(i, -mark_size, 0)
            glVertex3f(i, mark_size, 0)
            glVertex3f(i, 0, -mark_size)
            glVertex3f(i, 0, mark_size)
        
        # Marcas en eje Y (cada AXIS_MARKS_INTERVAL unidades) - Ahora vertical
        glColor3f(AXIS_Y_COLOR[0] * 0.8, AXIS_Y_COLOR[1] * 0.8, AXIS_Y_COLOR[2] * 0.8)
        for i in range(AXIS_MARKS_INTERVAL, AXIS_LENGTH + 1, AXIS_MARKS_INTERVAL):
            mark_size = AXIS_MARKS_SIZE * 1.5 if i % AXIS_NUMBERS_INTERVAL == 0 else AXIS_MARKS_SIZE
            glVertex3f(-mark_size, i, 0)
            glVertex3f(mark_size, i, 0)
            glVertex3f(0, i, -mark_size)
            glVertex3f(0, i, mark_size)
        
        # Marcas en eje Z (cada AXIS_MARKS_INTERVAL unidades) - Ahora profundidad
        glColor3f(AXIS_Z_COLOR[0] * 0.8, AXIS_Z_COLOR[1] * 0.8, AXIS_Z_COLOR[2] * 0.8)
        for i in range(AXIS_MARKS_INTERVAL, AXIS_LENGTH + 1, AXIS_MARKS_INTERVAL):
            mark_size = AXIS_MARKS_SIZE * 1.5 if i % AXIS_NUMBERS_INTERVAL == 0 else AXIS_MARKS_SIZE
            glVertex3f(-mark_size, 0, i)
            glVertex3f(mark_size, 0, i)
            glVertex3f(0, -mark_size, i)
            glVertex3f(0, mark_size, i)
        
        glEnd()
        
        # Renderizar etiquetas de valores principales
        self._render_axis_labels()
        glLineWidth(1.0)
    
    def _render_axis_labels(self):
        """Renderiza etiquetas numéricas en los ejes principales."""
        # Marcadores numéricos más visibles en posiciones clave
        label_size = 0.6
        
        # Etiquetas en eje X (rojo)
        glColor3f(*AXIS_X_COLOR)
        for i in range(AXIS_NUMBERS_INTERVAL, AXIS_LENGTH + 1, AXIS_NUMBERS_INTERVAL):
            self._render_number_display(i, -1.0, -1.0, str(i), label_size)
        
        # Etiquetas en eje Y (verde) - Ahora vertical
        glColor3f(*AXIS_Y_COLOR)
        for i in range(AXIS_NUMBERS_INTERVAL, AXIS_LENGTH + 1, AXIS_NUMBERS_INTERVAL):
            self._render_number_display(-1.0, i, -1.0, str(i), label_size)
        
        # Etiquetas en eje Z (azul) - Ahora profundidad
        glColor3f(*AXIS_Z_COLOR)
        for i in range(AXIS_NUMBERS_INTERVAL, AXIS_LENGTH + 1, AXIS_NUMBERS_INTERVAL):
            self._render_number_display(-1.0, -1.0, i, str(i), label_size)
    
    def _render_number_display(self, x, y, z, number, size):
        """Renderiza números usando geometría simple pero más legible."""
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(size, size, size)
        
        glLineWidth(3.0)
        glBegin(GL_LINES)
        
        # Renderizar dígitos usando líneas más elaboradas
        for i, digit in enumerate(number):
            offset_x = i * 1.2  # Espaciado entre dígitos
            self._render_digit(digit, offset_x, 0, 0)
        
        glEnd()
        glLineWidth(1.0)
        glPopMatrix()
    
    def _render_digit(self, digit, offset_x, offset_y, offset_z):
        """Renderiza un dígito específico usando líneas."""
        # Coordenadas base para formar los números
        def line(x1, y1, x2, y2):
            glVertex3f(offset_x + x1, offset_y + y1, offset_z)
            glVertex3f(offset_x + x2, offset_y + y2, offset_z)
        
        if digit == '0':
            line(0, 0, 1, 0)    # base
            line(0, 1, 1, 1)    # top
            line(0, 0, 0, 1)    # left
            line(1, 0, 1, 1)    # right
        elif digit == '1':
            line(0.5, 0, 0.5, 1)  # vertical
            line(0.3, 0.8, 0.5, 1) # top angle
        elif digit == '2':
            line(0, 1, 1, 1)    # top
            line(1, 1, 1, 0.5)  # right top
            line(1, 0.5, 0, 0.5) # middle
            line(0, 0.5, 0, 0)  # left bottom
            line(0, 0, 1, 0)    # bottom
        elif digit == '3':
            line(0, 1, 1, 1)    # top
            line(1, 1, 1, 0)    # right
            line(0, 0.5, 1, 0.5) # middle
            line(0, 0, 1, 0)    # bottom
        elif digit == '4':
            line(0, 1, 0, 0.5)  # left top
            line(0, 0.5, 1, 0.5) # middle
            line(1, 1, 1, 0)    # right
        elif digit == '5':
            line(0, 1, 1, 1)    # top
            line(0, 1, 0, 0.5)  # left top
            line(0, 0.5, 1, 0.5) # middle
            line(1, 0.5, 1, 0)  # right bottom
            line(1, 0, 0, 0)    # bottom
        
    def _render_robot(self):
        """Renderiza el brazo robótico con geometría realista."""
        # Aplicar rotación global para orientar el robot correctamente
        # Rotar -90° en X para que la base apoye en el suelo (plano XZ)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)  # Rotar todo el robot -90° en X
        
        # Calcular ángulos del brazo basados en la posición
        angles = self._calculate_arm_angles(self.robot_position)
        
        # 1. BASE DEL ROBOT - Más robusta y realista
        self._render_robot_base()
        
        # 2. ARTICULACIÓN DE LA BASE (motor de rotación)
        glPushMatrix()
        glTranslatef(0.0, 0.0, self.base_height)
        glRotatef(angles['rotation'], 0, 0, 1)  # Rotación en Z para base
        
        # Motor de la base
        base_motor_color = MOTORS_ON_LOWER_ARM if self.motors_enabled else MOTORS_OFF_LOWER_ARM
        self._render_cylinder(0.0, 0.0, 0.0, 0.8, 0.6, base_motor_color)
        
        # 3. BRAZO INFERIOR (lower arm) - Más detallado
        glTranslatef(0.0, 0.0, 0.6)
        glRotatef(angles['lower_arm'], 1, 0, 0)  # Ángulo brazo inferior
        
        # Articulación del brazo inferior
        joint_color = (0.5, 0.5, 0.5)
        self._render_cylinder(0.0, 0.0, 0.0, 0.4, 0.3, joint_color)
        
        # Brazo inferior principal
        glTranslatef(0.0, 0.0, 0.3)
        lower_arm_color = MOTORS_ON_LOWER_ARM if self.motors_enabled else MOTORS_OFF_LOWER_ARM
        self._render_arm_segment(self.lower_arm_length - 0.3, 0.35, lower_arm_color)
        
        # 4. ARTICULACIÓN INTERMEDIA (codo)
        glTranslatef(0.0, 0.0, self.lower_arm_length - 0.3)
        self._render_joint(0.5, 0.4, joint_color)
        
        # 5. BRAZO SUPERIOR (upper arm)
        glRotatef(angles['upper_arm'], 1, 0, 0)  # Ángulo brazo superior
        glTranslatef(0.0, 0.0, 0.4)
        
        upper_arm_color = MOTORS_ON_UPPER_ARM if self.motors_enabled else MOTORS_OFF_UPPER_ARM
        self._render_arm_segment(self.upper_arm_length - 0.4, 0.3, upper_arm_color)
        
        # 6. ARTICULACIÓN DE MUÑECA
        glTranslatef(0.0, 0.0, self.upper_arm_length - 0.4)
        self._render_joint(0.4, 0.3, joint_color)
        
        # 7. EFECTOR FINAL - Más detallado
        glTranslatef(0.0, 0.0, 0.3)
        self._render_advanced_effector(self.effector_active)
        
        # 8. Indicador de posición objetivo
        if self.animation_progress < 1.0:
            self._render_target_position()
        
        glPopMatrix()  # Fin de transformaciones del brazo
        glPopMatrix()  # Fin de rotación global del robot
        
    def _render_robot_base(self):
        """Renderiza una base robusta y realista para el robot."""
        # Base principal (plataforma circular más grande)
        base_platform_color = (0.2, 0.2, 0.2)
        platform_radius = getattr(globals(), 'BASE_RADIUS', 2.5)
        self._render_cylinder(0.0, 0.0, 0.0, platform_radius, 0.4, base_platform_color)
        
        # Anillo decorativo en la base
        ring_color = (0.3, 0.3, 0.3)
        self._render_cylinder(0.0, 0.0, 0.35, platform_radius * 0.9, 0.1, ring_color)
        
        # Soporte central más robusto
        support_color = (0.35, 0.35, 0.35)
        support_radius = platform_radius * 0.4
        self._render_cylinder(0.0, 0.0, 0.4, support_radius, self.base_height - 0.4, support_color)
        
        # Detalles de la base (pernos decorativos en círculo)
        bolt_color = (0.45, 0.45, 0.45)
        bolt_positions = 8  # 8 pernos alrededor
        for i in range(bolt_positions):
            angle = (2 * math.pi * i) / bolt_positions
            x = (platform_radius * 0.7) * math.cos(angle)
            y = (platform_radius * 0.7) * math.sin(angle)
            self._render_cylinder(x, y, 0.05, 0.12, 0.3, bolt_color)
        
        # Placa superior de montaje
        mount_color = (0.4, 0.4, 0.4)
        mount_radius = support_radius * 1.1
        self._render_cylinder(0.0, 0.0, self.base_height - 0.2, mount_radius, 0.2, mount_color)
    
    def _render_arm_segment(self, length, base_radius, color):
        """Renderiza un segmento de brazo con geometría realista de brazo robótico."""
        # Parámetros de diseño industrial
        segment_sections = 4  # Dividir el brazo en secciones
        section_length = length / segment_sections
        
        for i in range(segment_sections):
            z_offset = i * section_length
            
            # Variación del radio para dar forma cónica/aerodinámica
            radius_factor = 1.0 - (i * 0.1)  # Gradualmente más delgado
            current_radius = base_radius * radius_factor
            
            # Sección principal
            section_color = color
            if i % 2 == 1:  # Alternar colores para detalle visual
                section_color = (color[0] * 0.9, color[1] * 0.9, color[2] * 0.9)
            
            self._render_cylinder(0.0, 0.0, z_offset, current_radius, section_length * 0.8, section_color)
            
            # Uniones entre secciones (anillos)
            if i < segment_sections - 1:
                ring_color = (color[0] * 0.7, color[1] * 0.7, color[2] * 0.7)
                ring_z = z_offset + section_length * 0.8
                self._render_cylinder(0.0, 0.0, ring_z, current_radius * 1.15, section_length * 0.2, ring_color)
        
        # Carcasa protectora (cables/mangueras simuladas)
        self._render_cable_protection(length, base_radius * 0.3, (0.1, 0.1, 0.1))
    
    def _render_cable_protection(self, length, radius, color):
        """Renderiza protección de cables a lo largo del brazo."""
        # Simular mangueras/cables que corren por el brazo
        cable_count = 3
        for i in range(cable_count):
            angle = (2 * math.pi * i) / cable_count
            offset_x = radius * 2 * math.cos(angle) 
            offset_y = radius * 2 * math.sin(angle)
            
            # Cable/manguera
            self._render_cylinder(offset_x, offset_y, 0.1, radius, length * 0.9, color)
    
    def _render_joint(self, radius, height, color):
        """Renderiza una articulación industrial realista."""
        # Cuerpo principal de la articulación
        self._render_cylinder(0.0, 0.0, 0.0, radius, height * 0.6, color)
        
        # Placa superior e inferior
        plate_color = (color[0] * 1.3, color[1] * 1.3, color[2] * 1.3)
        self._render_cylinder(0.0, 0.0, 0.0, radius * 1.2, height * 0.1, plate_color)
        self._render_cylinder(0.0, 0.0, height * 0.9, radius * 1.2, height * 0.1, plate_color)
        
        # Detalles de pernos en la articulación
        bolt_color = (0.3, 0.3, 0.3)
        bolt_count = 6
        for i in range(bolt_count):
            angle = (2 * math.pi * i) / bolt_count
            x = radius * 0.9 * math.cos(angle)
            y = radius * 0.9 * math.sin(angle)
            self._render_cylinder(x, y, height * 0.05, 0.05, height * 0.1, bolt_color)
            self._render_cylinder(x, y, height * 0.85, 0.05, height * 0.1, bolt_color)
        
        # Indicador de movimiento (marca de referencia)
        glPushMatrix()
        glTranslatef(radius * 0.7, 0, height * 0.5)
        glColor3f(1.0, 1.0, 0.0)  # Amarillo para visibilidad
        self._render_sphere(0.08, 6, 6)
        glPopMatrix()
    
    def _render_advanced_effector(self, active):
        """Renderiza un efector final industrial detallado."""
        body_color = EFFECTOR_ACTIVE_BODY if active else EFFECTOR_INACTIVE_BODY
        tip_color = EFFECTOR_ACTIVE_TIP if active else EFFECTOR_INACTIVE_TIP
        
        # Cuerpo base del efector (conector)
        self._render_cylinder(0.0, 0.0, 0.0, 0.3, self.effector_length * 0.4, body_color)
        
        # Cabeza principal del efector
        glPushMatrix()
        glTranslatef(0.0, 0.0, self.effector_length * 0.4)
        
        # Cuerpo principal
        self._render_cylinder(0.0, 0.0, 0.0, 0.35, self.effector_length * 0.4, body_color)
        
        # Plataforma de herramienta
        platform_color = (body_color[0] * 1.2, body_color[1] * 1.2, body_color[2] * 1.2)
        self._render_cylinder(0.0, 0.0, self.effector_length * 0.35, 0.4, self.effector_length * 0.1, platform_color)
        
        # Indicador de estado central
        glTranslatef(0.0, 0.0, self.effector_length * 0.45)
        glColor3f(*tip_color)
        self._render_sphere(0.15, SPHERE_SLICES, SPHERE_STACKS)
        
        # Sistema de garra/herramienta
        if active:
            self._render_tool_system()
        else:
            self._render_inactive_tool()
            
        glPopMatrix()
    
    def _render_tool_system(self):
        """Renderiza un sistema de herramientas activo (pinzas, garra, etc.)."""
        # Herramienta activa: pinzas abiertas
        claw_color = (0.9, 0.7, 0.0)  # Dorado
        claw_length = 0.8
        claw_width = 0.08
        
        # Pinza izquierda
        glPushMatrix()
        glRotatef(-15, 1, 0, 0)  # Abertura de pinza
        glTranslatef(-0.2, 0.0, 0.0)
        self._render_cylinder(0.0, 0.0, 0.0, claw_width, claw_length, claw_color)
        # Punta de la pinza
        glTranslatef(0.0, 0.0, claw_length)
        self._render_sphere(claw_width * 1.5, 6, 6)
        glPopMatrix()
        
        # Pinza derecha
        glPushMatrix()
        glRotatef(15, 1, 0, 0)  # Abertura de pinza
        glTranslatef(0.2, 0.0, 0.0)
        self._render_cylinder(0.0, 0.0, 0.0, claw_width, claw_length, claw_color)
        # Punta de la pinza
        glTranslatef(0.0, 0.0, claw_length)
        self._render_sphere(claw_width * 1.5, 6, 6)
        glPopMatrix()
        
        # Actuador central
        actuator_color = (0.6, 0.6, 0.6)
        self._render_cylinder(0.0, 0.0, 0.1, 0.12, 0.3, actuator_color)
    
    def _render_inactive_tool(self):
        """Renderiza herramienta inactiva (cerrada/retraída)."""
        # Herramienta cerrada/retraída
        inactive_color = (0.5, 0.5, 0.5)
        self._render_cylinder(0.0, 0.0, 0.0, 0.15, 0.4, inactive_color)
        
        # Tapa protectora
        cap_color = (0.3, 0.3, 0.3)
        glTranslatef(0.0, 0.0, 0.4)
        self._render_sphere(0.18, 8, 8)
        
    # Remover funciones obsoletas que ya no se usan
    # _render_axis_numbers y _render_number_markers han sido reemplazadas
        
    def _render_cylinder(self, x, y, z, radius, height, color):
        """Renderiza un cilindro en la posición especificada."""
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Crear cilindro usando quads
        segments = 16
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            x_pos = radius * math.cos(angle)
            y_pos = radius * math.sin(angle)
            
            glVertex3f(x_pos, y_pos, 0)
            glVertex3f(x_pos, y_pos, height)
            
        glEnd()
        
        # Tapas del cilindro
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            glVertex3f(radius * math.cos(angle), radius * math.sin(angle), 0)
        glEnd()
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, height)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            glVertex3f(radius * math.cos(angle), radius * math.sin(angle), height)
        glEnd()
        
        glPopMatrix()
        
    def _render_effector(self, active):
        """Renderiza el efector final."""
        body_color = EFFECTOR_ACTIVE_BODY if active else EFFECTOR_INACTIVE_BODY
        tip_color = EFFECTOR_ACTIVE_TIP if active else EFFECTOR_INACTIVE_TIP
        
        # Cuerpo del efector
        self._render_cylinder(0.0, 0.0, 0.0, 0.2, self.effector_length, body_color)
        
        # Indicador de estado (esfera)
        glPushMatrix()
        glTranslatef(0.0, 0.0, self.effector_length)
        glColor3f(*tip_color)
            
        # Renderizar esfera simple
        self._render_sphere(0.3, SPHERE_SLICES, SPHERE_STACKS)
        glPopMatrix()
        
    def _render_sphere(self, radius, slices, stacks):
        """Renderiza una esfera."""
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            z0 = radius * math.sin(lat0)
            zr0 = radius * math.cos(lat0)
            
            lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
            z1 = radius * math.sin(lat1)
            zr1 = radius * math.cos(lat1)
            
            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j) / slices
                x = math.cos(lng)
                y = math.sin(lng)
                
                glVertex3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr1, y * zr1, z1)
                
            glEnd()
            
    def _render_target_position(self):
        """Renderiza un indicador de la posición objetivo."""
        glColor3f(0.0, 1.0, 1.0)  # Cian
        glPushMatrix()
        glLoadIdentity()
        
        # Posicionar cámara nuevamente para el indicador
        cam_x = self.camera_distance * math.cos(math.radians(self.camera_rotation[1])) * math.sin(math.radians(self.camera_rotation[0]))
        cam_y = self.camera_distance * math.sin(math.radians(self.camera_rotation[1])) + 5.0
        cam_z = self.camera_distance * math.cos(math.radians(self.camera_rotation[1])) * math.cos(math.radians(self.camera_rotation[0]))
        
        # Centrar en el robot (altura media ajustada para nueva orientación)
        center_height = (self.lower_arm_length + self.upper_arm_length) / 2
        gluLookAt(cam_x, cam_y, cam_z, 0, center_height, 0, 0, 1, 0)
        
        # La posición objetivo también necesita transformación para la nueva orientación
        target_x, target_y, target_z = self.target_position
        glTranslatef(target_x, target_y, target_z)
        self._render_sphere(0.3, 6, 6)
        glPopMatrix()
        
    def _calculate_arm_angles(self, position):
        """
        Calcula los ángulos del brazo para alcanzar la posición dada.
        Implementa cinemática inversa adaptada para la nueva orientación.
        Ahora: X=horizontal derecha, Y=vertical arriba, Z=profundidad
        """
        x, y, z = position
        
        # Ángulo de rotación de la base (rotación en plano XZ)
        rotation_angle = math.degrees(math.atan2(x, z)) if z != 0 or x != 0 else 0
        
        # Distancia horizontal desde el centro (en plano XZ)
        horizontal_dist = math.sqrt(x*x + z*z)
        
        # Altura desde la base (Y - base_height)
        vertical_dist = y - self.base_height
        if vertical_dist < 0:
            vertical_dist = 0  # No permitir posiciones bajo la base
        
        # Distancia total al objetivo
        target_dist = math.sqrt(horizontal_dist*horizontal_dist + vertical_dist*vertical_dist)
        
        # Verificar si la posición es alcanzable
        max_reach = self.lower_arm_length + self.upper_arm_length
        if target_dist > max_reach:
            # Si no es alcanzable, escalar la posición
            scale = max_reach / target_dist
            horizontal_dist *= scale
            vertical_dist *= scale
            target_dist = max_reach
            
        # Ángulo del brazo inferior usando ley de cosenos
        try:
            cos_lower = (self.lower_arm_length*self.lower_arm_length + target_dist*target_dist - self.upper_arm_length*self.upper_arm_length) / (2 * self.lower_arm_length * target_dist)
            cos_lower = max(-1, min(1, cos_lower))  # Clamp entre -1 y 1
            
            angle_to_target = math.degrees(math.atan2(vertical_dist, horizontal_dist))
            lower_arm_angle = angle_to_target - math.degrees(math.acos(cos_lower))
            
            # Ángulo del brazo superior
            cos_upper = (self.lower_arm_length*self.lower_arm_length + self.upper_arm_length*self.upper_arm_length - target_dist*target_dist) / (2 * self.lower_arm_length * self.upper_arm_length)
            cos_upper = max(-1, min(1, cos_upper))
            upper_arm_angle = 180 - math.degrees(math.acos(cos_upper))
            
        except (ValueError, ZeroDivisionError):
            # En caso de error, usar ángulos por defecto
            lower_arm_angle = 45
            upper_arm_angle = 90
            
        return {
            'rotation': rotation_angle,
            'lower_arm': lower_arm_angle,
            'upper_arm': upper_arm_angle
        }
        
    def _lerp(self, a, b, t):
        """Interpolación lineal entre a y b."""
        return a + (b - a) * t
        
    def _smooth_step(self, t):
        """Función de suavizado para animaciones."""
        return t * t * (3.0 - 2.0 * t)


if __name__ == "__main__":
    # Test del visualizador 3D
    viewer = Robot3DViewer()
    viewer.start()
    
    # Simular algunos movimientos
    time.sleep(2)
    viewer.set_robot_state(motors_enabled=True)
    viewer.update_position(5, 8, 5)
    
    time.sleep(3)
    viewer.update_position(-3, 10, 8)
    
    time.sleep(3)
    viewer.set_robot_state(effector_active=True)
    
    time.sleep(3)
    viewer.home_robot()
    
    # Mantener la ventana abierta
    try:
        while viewer.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        viewer.stop()