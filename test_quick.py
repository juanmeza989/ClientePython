#!/usr/bin/env python3
"""
Script rápido para probar conexión al servidor remoto
"""

try:
    from client_api import RobotRpcClient
    from config import RPC_ENDPOINT
except ImportError:
    from .client_api import RobotRpcClient
    from .config import RPC_ENDPOINT

import xmlrpc.client

def test_connection():
    print("="*60)
    print("PRUEBA DE CONEXIÓN RÁPIDA")
    print("="*60)
    print(f"Servidor: {RPC_ENDPOINT}")
    print()
    
    try:
        # Crear cliente
        client = RobotRpcClient()
        print("✓ Cliente creado")
        
        # Intentar obtener lista de métodos
        print("✓ Intentando conectar al servidor...")
        methods = client.proxy.system.listMethods()
        print(f"✓ ¡Conexión exitosa! Métodos disponibles: {len(methods)}")
        print("\nMétodos del servidor:")
        for method in sorted(methods):
            print(f"  - {method}")
        
        print("\n" + "="*60)
        print("SERVIDOR ALCANZABLE - Listo para usar")
        print("="*60)
        print("\nPuedes ejecutar el cliente con:")
        print("  python3 cli.py")
        print("\nO probar login programáticamente con:")
        print("  python3 test_login.py")
        return True
        
    except ConnectionRefusedError:
        print("✗ Conexión rechazada")
        print("  El servidor no está escuchando en esa dirección")
        return False
    except OSError as e:
        if "timed out" in str(e) or "Timeout" in str(e):
            print("✗ Timeout de conexión")
            print("  El servidor no responde o no es alcanzable")
        else:
            print(f"✗ Error de red: {e}")
        return False
    except xmlrpc.client.ProtocolError as e:
        print(f"✗ Error de protocolo XML-RPC: {e}")
        return False
    except Exception as e:
        print(f"✗ Error inesperado: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = test_connection()
    sys.exit(0 if success else 1)
