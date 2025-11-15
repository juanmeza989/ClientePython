#!/usr/bin/env python3
"""
Test de autenticación usando el método robot.authenticate
Replica la funcionalidad del método CLIHandler::login() del cliente C++
"""

try:
    from client_api import RobotRpcClient
    from config import RPC_ENDPOINT
except ImportError:
    from .client_api import RobotRpcClient
    from .config import RPC_ENDPOINT

import xmlrpc.client
from enum import IntEnum


class UserRole(IntEnum):
    """Roles de usuario según el servidor"""
    OPERATOR = 0
    ADMIN = 1


def login_authenticate(client: RobotRpcClient, username: str, password: str) -> tuple[bool, dict]:
    """
    Autenticación usando robot.authenticate (método directo del servidor)
    
    Retorna:
        tuple: (success: bool, info: dict)
        info contiene: authenticated, role, username
    """
    try:
        # Llamar directamente al método robot.authenticate
        result = client.proxy.robot.connect(username, password)
        
        # El servidor devuelve un struct con:
        # - authenticated: bool
        # - role: int (0=OPERATOR, 1=ADMIN)
        
        if isinstance(result, dict):
            is_authenticated = result.get("authenticated", False)
            
            if is_authenticated:
                role_int = result.get("role", 0)
                role = UserRole(role_int)
                role_str = "Administrador" if role == UserRole.ADMIN else "Operador"
                
                print(f"¡Inicio de sesión exitoso! Bienvenido, {username} ({role_str}).")
                
                return True, {
                    "authenticated": True,
                    "username": username,
                    "password": password,  # En producción NO almacenar contraseñas
                    "role": role,
                    "role_str": role_str
                }
            else:
                print("Error: Usuario o clave incorrectos.")
                return False, {"authenticated": False}
        else:
            print(f"Error: Respuesta inesperada del servidor: {result}")
            return False, {"authenticated": False}
            
    except xmlrpc.client.Fault as f:
        print(f"[CLI] Error de autenticación RPC: {f.faultString}")
        return False, {"authenticated": False, "error": str(f)}
    except (ConnectionRefusedError, OSError) as e:
        print(f"[CLI] Error de conexión con el servidor: {e}")
        print("Asegúrese de que el servidor esté corriendo ('make run').")
        return False, {"authenticated": False, "error": str(e)}
    except Exception as e:
        print(f"[CLI] Error inesperado: {type(e).__name__}: {e}")
        return False, {"authenticated": False, "error": str(e)}


def check_server_connectivity(endpoint: str) -> bool:
    """Verifica si el servidor es alcanzable antes de autenticar"""
    import socket
    import urllib.parse
    
    parsed = urllib.parse.urlparse(endpoint)
    host = parsed.hostname
    port = parsed.port or 8080
    
    print(f"Verificando conectividad con {host}:{port}...")
    
    try:
        # Intentar conexión TCP básica
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✓ Puerto {port} accesible en {host}")
            return True
        else:
            print(f"✗ Puerto {port} no accesible en {host}")
            print(f"  Código de error: {result}")
            return False
    except socket.gaierror:
        print(f"✗ No se puede resolver el hostname: {host}")
        return False
    except socket.timeout:
        print(f"✗ Timeout conectando a {host}:{port}")
        return False
    except Exception as e:
        print(f"✗ Error verificando conectividad: {e}")
        return False


def test_authenticate():
    """Función de prueba interactiva similar al código C++"""
    print("="*60)
    print("TEST DE AUTENTICACIÓN - robot.authenticate")
    print("="*60)
    print(f"Servidor: {RPC_ENDPOINT}")
    print()
    
    # Verificar conectividad primero
    if not check_server_connectivity(RPC_ENDPOINT):
        print()
        print("="*60)
        print("ERROR: No se puede conectar al servidor")
        print("="*60)
        print()
        print("Posibles soluciones:")
        print("1. Verifica que el servidor esté corriendo")
        print("2. Verifica la IP y puerto en config.py")
        print("3. Verifica tu conexión de red")
        print("4. Verifica que no haya firewall bloqueando")
        print()
        print("Para cambiar el servidor, edita config.py o usa:")
        print("  export ROBOT_RPC_ENDPOINT='http://NUEVA_IP:PUERTO/RPC2'")
        return False
    
    print()
    # Solicitar credenciales al usuario
    username = input("Usuario: ").strip()
    password = input("Clave: ").strip()
    
    print()
    print("Conectando al servidor...")
    
    # Crear cliente
    client = RobotRpcClient()
    
    # Intentar autenticación
    success, info = login_authenticate(client, username, password)
    
    print()
    print("="*60)
    if success:
        print("RESULTADO: AUTENTICACIÓN EXITOSA")
        print("="*60)
        print(f"Usuario: {info['username']}")
        print(f"Rol: {info['role_str']} (código: {info['role'].value})")
        print()
        print("Puedes usar estas credenciales en el CLI:")
        print("  python3 cli.py")
    else:
        print("RESULTADO: AUTENTICACIÓN FALLIDA")
        print("="*60)
        if "error" in info:
            print(f"Error: {info['error']}")
    
    return success


def test_authenticate_batch():
    """Test automático con múltiples credenciales predefinidas"""
    print("="*60)
    print("TEST AUTOMÁTICO - robot.authenticate")
    print("="*60)
    print(f"Servidor: {RPC_ENDPOINT}")
    print()
    
    # Verificar conectividad primero
    if not check_server_connectivity(RPC_ENDPOINT):
        print()
        print("="*60)
        print("ERROR: No se puede conectar al servidor")
        print("="*60)
        print()
        print("El servidor no es alcanzable. Verifica config.py")
        return False
    
    print()
    # Credenciales de prueba
    test_credentials = [
        ("admin", "admin"),
        ("operator", "operator"),
        ("admin", "wrongpass"),  # Debería fallar
        ("user", "user"),
    ]
    
    client = RobotRpcClient()
    results = []
    
    for username, password in test_credentials:
        print(f"\nProbando: {username} / {'*' * len(password)}")
        print("-" * 40)
        success, info = login_authenticate(client, username, password)
        results.append((username, password, success, info))
        print()
    
    # Resumen
    print("="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    successful = [r for r in results if r[2]]
    failed = [r for r in results if not r[2]]
    
    print(f"✓ Exitosos: {len(successful)}/{len(results)}")
    for username, _, _, info in successful:
        role_str = info.get('role_str', 'N/A')
        print(f"  - {username} ({role_str})")
    
    print(f"\n✗ Fallidos: {len(failed)}/{len(results)}")
    for username, _, _, _ in failed:
        print(f"  - {username}")
    
    return len(successful) > 0


if __name__ == "__main__":
    import sys
    
    # Determinar modo según argumentos
    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        # Modo batch: prueba automática con credenciales predefinidas
        success = test_authenticate_batch()
    else:
        # Modo interactivo: solicita credenciales al usuario
        success = test_authenticate()
    
    sys.exit(0 if success else 1)
