# GUI Client para Robot RPC con Visualizador 3D

Este directorio contiene una interfaz gráfica completa en Tkinter para el cliente RPC del robot, incluyendo un visualizador 3D en tiempo real.

## Características Principales

### 🖥️ Interfaz Gráfica Completa
- **Autenticación**: Sistema de login con roles (Administrador/Operador)
- **Controles del Robot**: Botones para todas las operaciones básicas
- **Gestión de Usuarios**: Agregar usuarios y ver conexiones activas
- **Reportes**: Generación de reportes de actividad y logs
- **Tareas**: Sistema de aprendizaje y ejecución de tareas automatizadas
- **Audio**: Retroalimentación sonora para acciones

### 🎮 Visualizador 3D
- **Modelo 3D Realista**: Representación tridimensional del brazo robótico
- **Animaciones Suaves**: Transiciones fluidas entre posiciones
- **Estados Visuales**: Colores que cambian según el estado del robot
- **Control de Cámara**: Rotación orbital y zoom con mouse
- **Sincronización Automática**: Se actualiza en tiempo real con los comandos

## Instalación

### Dependencias del Sistema
```bash
sudo apt install python3-opengl python3-pygame python3-tk
```

### Verificar Instalación
```bash
python3 -c "import tkinter, pygame, OpenGL.GL; print('Todas las dependencias están instaladas')"
```

## Uso

### Inicio Rápido
```bash
cd TP_IINTEGRADOR_POO/ClientePython
python3 gui_client/main.py
```

### Variables de Entorno (Opcional)
```bash
export ROBOT_USER="tu_usuario"
export ROBOT_PASS="tu_contraseña" 
python3 gui_client/main.py
```

## Funcionalidades

### 🔧 Controles del Robot
- **Conectar/Desconectar**: Establecer comunicación con el robot
- **Motores ON/OFF**: Habilitar/deshabilitar motores del brazo
- **Efector ON/OFF**: Activar/desactivar herramienta final
- **Modo Absoluto/Relativo**: Cambiar sistema de coordenadas
- **Estado**: Consultar estado actual del robot
- **Mover**: Control de posición (X, Y, Z) con velocidad opcional

### 👥 Gestión de Usuarios
- **Agregar Usuario**: Crear nuevos usuarios con roles específicos
- **Usuarios Conectados**: Ver sesiones activas en tiempo real
- **Roles**: Administrador (0) y Operador (1)

### 📊 Sistema de Reportes
- **Reporte de Actividad**: Historial de órdenes ejecutadas
- **Reporte de Administrador**: Vista completa con filtros avanzados
- **Reporte de Logs**: Análisis de logs del sistema con filtros

### 🤖 Sistema de Tareas
- **Listar Tareas**: Ver tareas disponibles programadas
- **Ejecutar Tarea**: Ejecutar secuencias automatizadas
- **Aprender Inicio/Fin**: Grabar nuevas secuencias de movimientos
- **Comandos G-Code**: Grabación automática de comandos

### 🎨 Visualizador 3D
- **Abrir Visualizador 3D**: Lanzar ventana de visualización
- **Home (Posición Inicial)**: Mover a posición de referencia
- **Sincronización Automática**: Refleja todos los comandos en 3D

## Estructura de Archivos

```
gui_client/
├── main.py                 # Interfaz principal de Tkinter
├── robot_3d_viewer.py      # Visualizador 3D con OpenGL
├── test_3d_viewer.py       # Script de prueba del visualizador
├── README.md               # Este archivo
├── README_3D.md            # Documentación detallada del 3D
└── sounds/                 # Archivos de audio (opcional)
    ├── moviment.wav
    ├── effector.wav
    └── error.wav
```

## Controles del Visualizador 3D

### 🖱️ Mouse
- **Click Izquierdo + Arrastrar**: Rotar cámara alrededor del robot
- **Rueda del Mouse**: Zoom in/out
- **Rotación**: 360° horizontal, -90° a +90° vertical

### 🎨 Indicadores Visuales
- **Base**: Gris sólido
- **Brazos (Motores ON)**: Rojo y verde brillantes
- **Brazos (Motores OFF)**: Colores oscuros
- **Efector (Activo)**: Amarillo con punto rojo
- **Efector (Inactivo)**: Amarillo oscuro con punto gris
- **Objetivo**: Esfera cian durante movimientos

### 📐 Sistema de Coordenadas
- **Eje X**: Rojo (lateral)
- **Eje Y**: Verde (frontal/posterior)
- **Eje Z**: Azul (vertical)
- **Cuadrícula**: Referencia en el suelo

## Ejemplos de Uso

### Demo Completa
```bash
# Ejecutar demo interactiva del visualizador
python3 gui_client/test_3d_viewer.py
```

### Conexión y Movimiento Básico
1. Ejecutar `python3 gui_client/main.py`
2. Hacer login (usuario: `principalAdmin`, contraseña según configuración)
3. Hacer clic en "Abrir Visualizador 3D"
4. Hacer clic en "Conectar"
5. Hacer clic en "Motores ON"
6. Introducir coordenadas (ej: X=50, Y=100, Z=80) y hacer clic en "Mover"
7. Observar el movimiento en el visualizador 3D

### Grabación de Tareas
1. Hacer clic en "Aprender Inicio" e introducir ID y nombre
2. Realizar secuencia de movimientos y configuraciones
3. Hacer clic en "Aprender Fin" para guardar
4. Usar "Ejecutar Tarea" para reproducir la secuencia

## Resolución de Problemas

### ❌ Error: "No se pudo cargar el visualizador 3D"
```bash
sudo apt install python3-opengl python3-pygame
# O reinstalar:
sudo apt remove python3-opengl python3-pygame
sudo apt install python3-opengl python3-pygame
```

### ❌ Error: "No module named 'tkinter'"
```bash
sudo apt install python3-tk
```

### ❌ La ventana 3D no aparece
- Verificar que estás en un entorno gráfico (no SSH sin X11)
- Comprobar que OpenGL funciona: `glxinfo | grep OpenGL`
- Verificar permisos de pantalla si usas SSH: `ssh -X usuario@servidor`

### ❌ Pygame warnings
Los warnings de pygame sobre AVX2 son normales y no afectan la funcionalidad.

## Configuración Avanzada

### Audio (Opcional)
Colocar archivos WAV en el directorio `sounds/`:
- `moviment.wav`: Sonido de movimiento
- `effector.wav`: Sonido del efector
- `error.wav`: Sonido de error

### Personalización Visual
Editar `robot_3d_viewer.py` para modificar:
- Colores del robot
- Velocidad de animación
- Dimensiones del modelo
- Configuración de cámara

## Arquitectura Técnica

### Componentes Principales
- **RobotGUI (main.py)**: Interfaz principal de Tkinter
- **Robot3DViewer (robot_3d_viewer.py)**: Motor de renderizado 3D
- **RobotRpcClient**: Cliente RPC para comunicación con servidor

### Tecnologías Utilizadas
- **Tkinter**: Interfaz gráfica nativa de Python
- **Pygame**: Ventanas y manejo de eventos para 3D
- **PyOpenGL**: Renderizado 3D con OpenGL
- **Threading**: Ejecución concurrente del visualizador
- **XML-RPC**: Comunicación cliente-servidor

### Flujo de Datos
```
GUI (Tkinter) → RPC Client → Servidor Robot
     ↓
Visualizador 3D (OpenGL) ← Sincronización
```

## Contribución

Para agregar nuevas funcionalidades:

1. **Nuevos Controles GUI**: Editar `create_main_panel()` en `main.py`
2. **Funciones 3D**: Agregar métodos en `Robot3DViewer`
3. **Efectos Visuales**: Modificar `_render_robot()` o crear nuevos shaders
4. **Sonidos**: Agregar archivos WAV y llamadas a `reproduce_sound()`

## Notas de Desarrollo

- El GUI utiliza el cliente RPC existente `client_api.RobotRpcClient`
- La sincronización 3D se maneja automáticamente mediante callbacks
- El visualizador funciona en un hilo separado para no bloquear la GUI
- La cinemática inversa es una aproximación simplificada para visualización
