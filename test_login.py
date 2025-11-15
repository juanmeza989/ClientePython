#!/usr/bin/env python3
"""
Script para probar login al servidor
"""

try:
    from client_api import RobotRpcClient
    from config import RPC_ENDPOINT
except ImportError:
    from .client_api import RobotRpcClient
    from .config import RPC_ENDPOINT

def test_login(client: RobotRpcClient, username: str, password: str) -> tuple[bool, dict]:
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

# def test_login():
#     print("="*60)
#     print("PRUEBA DE LOGIN")
#     print("="*60)
#     print(f"Servidor: {RPC_ENDPOINT}")
#     print()
    
#     # Crear cliente
#     client = RobotRpcClient()
    
#     # Credenciales de prueba (ajusta según tu servidor)
#     usuarios = [
#         ("admin", "admin"),
#         ("operator", "operator"),
#         ("user", "user"),
#     ]
    
#     for username, password in usuarios:
#         print(f"Probando login con: {username}/{password}")
#         try:
#             if client.login(username, password):
#                 print(f"✓ Login exitoso con {username}")
                
#                 # Probar listar comandos
#                 try:
#                     commands = client.list_commands()
#                     print(f"  Comandos disponibles: {len(commands)}")
#                     for cmd in commands[:5]:  # Mostrar solo los primeros 5
#                         print(f"    - {cmd}")
#                     if len(commands) > 5:
#                         print(f"    ... y {len(commands) - 5} más")
#                 except Exception as e:
#                     print(f"  Error listando comandos: {e}")
                
#                 # Logout
#                 client.logout()
#                 print(f"✓ Logout exitoso")
#                 return True
#             else:
#                 print(f"✗ Login falló con {username}")
#         except Exception as e:
#             print(f"✗ Error: {e}")
    
#     print("\n✗ No se pudo hacer login con ninguna credencial de prueba")
#     return False

# if __name__ == "__main__":
#     import sys
#     success = test_login()
#     sys.exit(0 if success else 1)
