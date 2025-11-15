#!/usr/bin/env python3
import socket
import xmlrpc.client
from typing import Any, List, Optional, Dict

# Imports flexibles
try:
    from config import RPC_ENDPOINT, RPC_TIMEOUT
    from models import Vector3, GCodeProgram
except ImportError:
    from .config import RPC_ENDPOINT, RPC_TIMEOUT
    from .models import Vector3, GCodeProgram


class RobotRpcClient:
    """
    Envoltura del ServerProxy XML-RPC con helpers y compatibilidad de nombres.
    """

    def __init__(self, endpoint: str = RPC_ENDPOINT, timeout: int = RPC_TIMEOUT) -> None:
        # Agregar timeout al transporte
        class TimeoutTransport(xmlrpc.client.Transport):
            def __init__(self, timeout: int):
                super().__init__()
                self.timeout = timeout

            def make_connection(self, host):
                conn = super().make_connection(host)
                conn.timeout = self.timeout
                return conn

        transport = TimeoutTransport(timeout)
        self.proxy = xmlrpc.client.ServerProxy(endpoint, transport=transport, allow_none=True)
        self.session_id: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.role: Optional[int] = None

    # ------------- Gestión de sesión y auth -------------
    def login(self, username: str, password: str) -> bool:
        """
        Autentica usando robot.authenticate y almacena las credenciales.
        El servidor devuelve: {authenticated: bool, role: int}
        """
        try:
            # Usar robot.authenticate en lugar de login
            result = self.proxy.robot.authenticate(username, password)
            
            if isinstance(result, dict):
                is_authenticated = result.get("authenticated", False)
                
                if is_authenticated:
                    # Guardar credenciales para usarlas como "session"
                    # (El servidor requiere username/password en cada llamada, no session_id)
                    self.session_id = f"{username}:{password}"  # Formato temporal
                    self.username = username
                    self.password = password
                    self.role = result.get("role", 0)  # 0=OPERATOR, 1=ADMIN
                    return True
                else:
                    print(f"[ERROR] Autenticación fallida: Usuario o clave incorrectos")
                    return False
            else:
                print(f"[ERROR] Respuesta inesperada del servidor: {result}")
                return False
                
        except xmlrpc.client.Fault as e:
            print(f"[ERROR] Fault autenticación: {e}")
            return False
        except (socket.timeout, ConnectionRefusedError) as e:
            print(f"[ERROR] Conexión: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Error inesperado: {type(e).__name__}: {e}")
            return False

    def logout(self) -> None:
        """Limpia las credenciales almacenadas"""
        self.session_id = None
        self.username = None
        self.password = None
        self.role = None

    def _sid(self) -> str:
        """Retorna session_id (compatibilidad), pero el servidor usa username/password"""
        if not self.session_id:
            raise RuntimeError("No hay sesión activa. Inicie sesión primero.")
        return self.session_id
    
    def _credentials(self) -> tuple[str, str]:
        """Retorna las credenciales (username, password) para llamadas al servidor"""
        if not self.username or not self.password:
            raise RuntimeError("No hay sesión activa. Inicie sesión primero.")
        return (self.username, self.password)

    # ------------- Comandos principales (no opcionales) -------------
    def connect_robot(self) -> Dict[str, Any]:
        username, password = self._credentials()
        return self.proxy.robot.connect(username, password)

    def disconnect_robot(self) -> Dict[str, Any]:
        username, password = self._credentials()
        return self.proxy.robot.disconnect(username, password)

    def enable_remote(self) -> Dict[str, Any]:
        # Este método no parece existir en el servidor actual
        username, password = self._credentials()
        return {"success": False, "message": "Método enableRemote no disponible"}

    def disable_remote(self) -> Dict[str, Any]:
        username, password = self._credentials()
        return {"success": False, "message": "Método disableRemote no disponible"}

    def activate_motors(self) -> Dict[str, Any]:
        username, password = self._credentials()
        return self.proxy.robot.enableMotors(username, password)

    def deactivate_motors(self) -> Dict[str, Any]:
        username, password = self._credentials()
        return self.proxy.robot.disableMotors(username, password)

    def list_commands(self) -> List[Any]:
        # El servidor no tiene listCommands, usar listTasks en su lugar
        username, password = self._credentials()
        return self.proxy.robot.listTasks(username, password)

    def report_operator(self) -> Dict[str, Any]:
        # Usar getReport del servidor
        username, password = self._credentials()
        return self.proxy.robot.getReport(username, password)

    def report_admin(self) -> Dict[str, Any]:
        username, password = self._credentials()
        return self.proxy.robot.getAdminReport(username, password)

    def set_mode(self, mode: str, coord: str) -> Dict[str, Any]:
        # coord: "ABSOLUTE"|"RELATIVE"
        username, password = self._credentials()
        return self.proxy.robot.setCoordinateMode(username, password, coord)

    def home(self) -> Dict[str, Any]:
        # El servidor no parece tener método home
        username, password = self._credentials()
        return {"success": False, "message": "Método home no disponible"}

    def move(self, target: Vector3, speed: Optional[float] = None) -> Dict[str, Any]:
        username, password = self._credentials()
        if speed is None:
            return self.proxy.robot.moveDefaultSpeed(username, password, target.to_rpc())
        else:
            return self.proxy.robot.move(username, password, target.to_rpc(), float(speed))

    def set_end_effector(self, active: bool) -> Dict[str, Any]:
        username, password = self._credentials()
        return self.proxy.robot.setEffector(username, password, bool(active))

    # ------------- Aprendizaje manual a G-Code -------------
    def learning_start(self, name: str) -> Dict[str, Any]:
        username, password = self._credentials()
        return {"success": False, "message": "Método learning no disponible en este servidor"}

    def learning_add_step(self, target: Vector3, speed: float) -> Dict[str, Any]:
        username, password = self._credentials()
        return {"success": False, "message": "Método learning no disponible en este servidor"}

    def learning_save(self) -> Dict[str, Any]:
        username, password = self._credentials()
        return {"success": False, "message": "Método learning no disponible en este servidor"}

    # ------------- Programas (subida y ejecución) -------------
    def upload_program(self, path: str, owner_user_id: str = "") -> Dict[str, Any]:
        username, password = self._credentials()
        # Usar addTask en lugar de uploadProgram
        program = GCodeProgram.load_from_file(path, owner_user_id=owner_user_id)
        return self.proxy.robot.addTask(username, password, program.to_rpc())

    def run_program(self, program_id: str) -> Dict[str, Any]:
        username, password = self._credentials()
        return self.proxy.robot.executeTask(username, password, program_id)

    def list_programs(self) -> List[Any]:
        username, password = self._credentials()
        return self.proxy.robot.listTasks(username, password)