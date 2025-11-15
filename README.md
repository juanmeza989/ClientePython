# Cliente Python para Robot 3DF

Cliente XML-RPC independiente para conectarse a un servidor de Robot 3DF remoto.

## 📋 Requisitos

- Python 3.6 o superior
- Conexión de red al servidor

## 🚀 Uso Rápido

### 1. Configurar el servidor

Edita `config.py` para cambiar la IP del servidor:

```python
RPC_ENDPOINT = os.getenv("ROBOT_RPC_ENDPOINT", "http://18.68.4.101:8080/RPC2")
```

O usa una variable de entorno:

```bash
export ROBOT_RPC_ENDPOINT="http://IP_DEL_SERVIDOR:PUERTO/RPC2"
```

### 2. Probar la conexión

```bash
# Prueba rápida de conectividad
python3 test_quick.py

# Prueba de autenticación
python3 test_login.py
```

### 3. Usar el cliente interactivo

```bash
python3 cli.py
```

Luego ingresa tus credenciales cuando se soliciten.

## 📁 Archivos

- **config.py** - Configuración del endpoint del servidor
- **models.py** - Modelos de datos (Vector3, GCodeProgram, Command)
- **client_api.py** - API del cliente XML-RPC
- **cli.py** - Interfaz de línea de comandos interactiva
- **test_quick.py** - Script de prueba de conexión
- **test_login.py** - Script de prueba de autenticación

## 🔧 Comandos Disponibles

Una vez autenticado en el CLI, puedes usar:

1. Conectar/Desconectar robot
2. Habilitar/Deshabilitar acceso remoto (admin)
3. Activar/Desactivar motores
4. Ir a Home
5. Mover robot (X, Y, Z con velocidad opcional)
6. Controlar efector final
7. Seleccionar modo (MANUAL/AUTOMATIC, ABSOLUTE/RELATIVE)
8. Aprendizaje manual (iniciar, agregar paso, guardar)
9. Subir y ejecutar programas G-Code
10. Ver reportes (Operador/Admin)

## 🌐 Configuración de Red

Asegúrate de:

1. Tener conectividad de red con el servidor:
   ```bash
   ping IP_DEL_SERVIDOR
   ```

2. Que el puerto esté abierto:
   ```bash
   nc -zv IP_DEL_SERVIDOR PUERTO
   ```

3. Que el servidor XML-RPC esté corriendo en la PC remota

## 📝 Ejemplo de Uso Programático

```python
from client_api import RobotRpcClient
from models import Vector3

# Crear cliente
client = RobotRpcClient()

# Login
if client.login("admin", "admin"):
    # Conectar robot
    result = client.connect_robot()
    print(result)
    
    # Mover a posición
    pos = Vector3(x=10.0, y=20.0, z=30.0)
    client.move(pos, speed=50.0)
    
    # Logout
    client.logout()
```

## 🔒 Seguridad

- Las credenciales se transmiten por la red
- Se recomienda usar VPN o red segura
- No hardcodear contraseñas en scripts

## 📞 Soporte

Este cliente se conecta a servidores XML-RPC compatibles con el protocolo del Robot 3DF.
