#!/usr/bin/env python3
"""
CLI adaptado del cliente C++ proporcionado.
Provee login con robot.authenticate, menús por rol (admin/operator), y el loop de comandos.
"""
import sys
import shlex
import os
import argparse
from typing import Optional, Tuple, List

try:
    from client_api import RobotRpcClient
except ImportError:
    from .client_api import RobotRpcClient


# Estado global de aprendizaje
learning_mode_active = False
learning_task_id: str = ""
learning_task_name: str = ""
learned_gcode_commands: List[str] = []


def generate_gcode(x: float, y: float, z: float, speed: float = 0.0) -> str:
    return f"G1 X{ x:.3f } Y{ y:.3f } Z{ z:.3f } E{ speed:.1f }"


class CLI:
    def __init__(self, client: RobotRpcClient):
        self.client = client
        self.current_user_info: Optional[Tuple[str, str, int]] = None  # (username, password, role)

    def start(self) -> None:
        print("=== Cliente de Control del Robot ===")
        host = getattr(self.client.proxy, '_ServerProxy__host', 'RPC server')
        print(f"Intentando conectar con el servidor en {host}...")
        # allow prefilled credentials via env or args
        user_from_env = os.environ.get("ROBOT_USER")
        pass_from_env = os.environ.get("ROBOT_PASS")
        if user_from_env and pass_from_env:
            self.current_user_info = (user_from_env, pass_from_env, 1)
        if self.login():
            self.main_loop()
        print("Saliendo del cliente...")

    def login(self) -> bool:
        # If credentials are already set (from env), use them
        if self.current_user_info:
            # re-authenticate to obtain actual role from server
            username, password, _ = self.current_user_info
            try:
                result = self.client.proxy.robot.authenticate(username, password)
                if isinstance(result, dict) and result.get("authenticated", False):
                    role_int = int(result.get("role", 1))
                    self.current_user_info = (username, password, role_int)
                    return True
                else:
                    print("Credenciales de entorno inválidas o rechazadas por el servidor.")
                    self.current_user_info = None
            except Exception as e:
                print(f"[CLI] Error de conexión o RPC: {e}")
                return False

        try:
            username = input("Usuario: ").strip()
        except EOFError:
            print("\nNo hay entrada interactiva (EOF). Usa las variables de entorno ROBOT_USER y ROBOT_PASS o ejecuta en modo no interactivo.")
            return False
        try:
            password = input("Clave: ").strip()
        except EOFError:
            print("\nNo hay entrada interactiva (EOF) al solicitar la clave. Abortando login.")
            return False
        try:
            result = self.client.proxy.robot.authenticate(username, password)
            if isinstance(result, dict):
                is_authenticated = result.get("authenticated", False)
                if is_authenticated:
                    role_int = int(result.get("role", 1))
                    role_str = "Administrador" if role_int == 0 else "Operador"
                    print(f"¡Inicio de sesión exitoso! Bienvenido, {username} ({role_str}).")
                    self.current_user_info = (username, password, role_int)
                    return True
                else:
                    print("Error: Usuario o clave incorrectos.")
                    self.current_user_info = None
                    return False
            else:
                print(f"Error: Respuesta inesperada del servidor: {result}")
                return False
        except Exception as e:
            print(f"[CLI] Error de conexión o RPC: {e}")
            return False

    def main_loop(self) -> None:
        while True:
            if self.current_user_info and self.current_user_info[2] == 0:
                self.display_menu_admin()
            else:
                self.display_menu_operator()

            try:
                command = input("> ")
            except EOFError:
                break
            if not command:
                continue
            if command.strip() == "salir":
                break
            self.process_command(command)

    def display_menu_admin(self) -> None:
        print("\n+-----------------------------------------------------------------------------------------+")
        print("|                      PANEL DE CONTROL DEL ROBOT                                         |")
        print("+-----------------------------------------------------------------------------------------+")
        print("| Comandos de Conexión:                                                                   |")
        print("|   conectar                      - Conecta con el robot.                                 |")
        print("|   desconectar                   - Desconecta el robot.                                  |")
        print("+-----------------------------------------------------------------------------------------+")
        print("| Comandos de Usuario:                                                                    |")
        print("|   user_add <user> <pass> <role> - Añade un usuario (role: 0=ADMIN, 1=OPERATOR)          |")
        print("+-----------------------------------------------------------------------------------------+")
        print("| Comandos de Control:                                                                    |")
        print("|   motores_on                    - Activa los motores.                                   |")
        print("|   motores_off                   - Desactiva los motores.                                |")
        print("|   mover <x> <y> <z> [vel]       - Mueve el efector a una posición. 'vel' es opcional.   |")
        print("|   efector_on                    - Activa el efector final.                              |")
        print("|   efector_off                   - Desactiva el efector final.                           |")
        print("|   modo_absoluto                 - Fija el modo de coordenadas a absoluto.               |")
        print("|   modo_relativo                 - Fija el modo de coordenadas a relativo.               |")
        print("+-----------------------------------------------------------------------------------------+")
        print("| Comandos de Tareas:                                                                     |")
        print("|   lista_tareas                  - Muestra las tareas predefinidas.                      |")
        print("|   ejecutar_tarea <id_tarea>     - Ejecuta una tarea por su ID.                          |")
        print("|   aprender_inicio <id> <nombre> - Inicia el modo de aprendizaje de trayectoria.         |")
        print("|   aprender_fin                  - Finaliza el aprendizaje y guarda la tarea.            |")
        print("+-----------------------------------------------------------------------------------------+")
        print("| Comandos de Información y Salida:                                                       |")
        print("|   estado                        - Muestra el estado actual del robot.                   |")
        print("|   reporte                       - Muestra un reporte de actividad.                      |")
        print("|   report_admin [filtro] [val]   - Muestra reporte admin con filtros usuario, resultado. |")
        print("|   report_log   [filtro] [val]   - Muestra reporte log con filtros usuario, nivel.       |")
        print("|   ayuda                         - Muestra esta ayuda.                                   |")
        print("|   salir                         - Cierra la consola.                                    |")
        print("+-----------------------------------------------------------------------------------------+")

    def display_menu_operator(self) -> None:
        print("\n+--------------------------------------------------------------------------------+")
        print("|                      PANEL DE CONTROL DEL ROBOT                                |")
        print("+--------------------------------------------------------------------------------+")
        print("| Comandos de Control:                                                           |")
        print("|   motores_on                - Activa los motores.                              |")
        print("|   motores_off               - Desactiva los motores.                           |")
        print("|   mover <x> <y> <z> [vel]   - Mueve el efector. 'vel' es opcional.             |")
        print("|   efector_on                - Activa el efector final.                         |")
        print("|   efector_off               - Desactiva el efector final.                      |")
        print("|   modo_absoluto             - Fija el modo de coordenadas a absoluto.          |")
        print("|   modo_relativo             - Fija el modo de coordenadas a relativo.          |")
        print("+--------------------------------------------------------------------------------+")
        print("| Comandos de Tareas:                                                            |")
        print("|   lista_tareas              - Muestra las tareas predefinidas.                 |")
        print("|   ejecutar_tarea <id_tarea> - Ejecuta una tarea por su ID.                     |")
        print("|   aprender_inicio <id> <nombre> - Inicia el modo de aprendizaje.               |")
        print("|   aprender_fin              - Finaliza y guarda la tarea aprendida.            |")
        print("+--------------------------------------------------------------------------------+")
        print("| Comandos de Información y Salida:                                              |")
        print("|   estado                    - Muestra el estado actual del robot.              |")
        print("|   reporte                   - Muestra un reporte de actividad.                 |")
        print("|   ayuda                     - Muestra esta ayuda.                              |")
        print("|   salir                     - Cierra la consola.                               |")
        print("+--------------------------------------------------------------------------------+")

    def process_command(self, full_command: str) -> None:
        global learning_mode_active, learning_task_id, learning_task_name, learned_gcode_commands
        parts = shlex.split(full_command)
        if not parts:
            return
        command = parts[0]

        if not self.current_user_info:
            print("[CLI] Error crítico: No hay un usuario autenticado. Saliendo.")
            return

        username, password, role = self.current_user_info
        is_admin = (role == 0)

        try:
            if command == "conectar":
                if not is_admin:
                    print("[CLI] Error: Permiso denegado. Solo los administradores pueden conectar.")
                    return
                self.client.proxy.robot.connect(username, password)
                print("[CLI] Comando 'conectar' enviado.")

            elif command == "desconectar":
                if not is_admin:
                    print("[CLI] Error: Permiso denegado. Solo los administradores pueden desconectar.")
                    return
                self.client.proxy.robot.disconnect(username, password)
                print("[CLI] Comando 'desconectar' enviado.")

            elif command == "motores_on":
                self.client.proxy.robot.enableMotors(username, password)
                print("Los Motores fueron Activados")

            elif command == "motores_off":
                self.client.proxy.robot.disableMotors(username, password)
                if learning_mode_active:
                    learned_gcode_commands.append("M18")
                    print("[APRENDIZAJE] Comando 'M18' grabado.")
                print("Los Motores fueron Desactivados")

            elif command == "efector_on":
                self.client.proxy.robot.setEffector(username, password, True)
                if learning_mode_active:
                    learned_gcode_commands.append("M3")
                    print("[APRENDIZAJE] Comando 'M3' grabado.")
                print("El Efector fue Activado")

            elif command == "efector_off":
                self.client.proxy.robot.setEffector(username, password, False)
                if learning_mode_active:
                    learned_gcode_commands.append("M5")
                    print("[APRENDIZAJE] Comando 'M5' grabado.")
                print("El Efector fue Desactivado")

            elif command == "mover":
                if len(parts) < 4:
                    print("[CLI] Error: Sintaxis incorrecta. Uso: mover <x> <y> <z> [velocidad]")
                    return
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                if len(parts) >= 5:
                    speed = float(parts[4])
                    gcode = generate_gcode(x, y, z, speed)
                    self.client.proxy.robot.move(username, password, x, y, z, speed)
                    print("Movimiento enviado al robot")
                else:
                    gcode = generate_gcode(x, y, z)
                    self.client.proxy.robot.moveDefaultSpeed(username, password, x, y, z)
                    print("Movimiento enviado al robot")

                if learning_mode_active:
                    learned_gcode_commands.append(gcode)
                    print(f"[APRENDIZAJE] Comando '{gcode}' grabado.")

            elif command == "modo_absoluto":
                self.client.proxy.robot.setCoordinateMode(username, password, True)
                if learning_mode_active:
                    learned_gcode_commands.append("G90")
                    print("[APRENDIZAJE] Comando 'G90' grabado.")
                print("Modo de coordenadas fijado a ABSOLUTO (G90)")

            elif command == "modo_relativo":
                self.client.proxy.robot.setCoordinateMode(username, password, False)
                if learning_mode_active:
                    learned_gcode_commands.append("G91")
                    print("[APRENDIZAJE] Comando 'G91' grabado.")
                print("Modo de coordenadas fijado a RELATIVO (G91)")

            elif command == "user_add":
                if not is_admin:
                    print("[CLI] Error: Permiso denegado. Solo los administradores pueden añadir usuarios.")
                    return
                if len(parts) < 4:
                    print("[CLI] Error: Sintaxis incorrecta. Uso: user_add <user> <pass> <role>")
                    return
                new_user = parts[1]
                new_pass = parts[2]
                role_int = int(parts[3])
                if role_int not in (0, 1):
                    print("[CLI] Error: Rol inválido. Use 0 para ADMIN o 1 para OPERATOR.")
                    return
                self.client.proxy.robot.user_add(username, password, new_user, new_pass, role_int)
                print(f"El usuario '{new_user}' fue creado")

            elif command == "estado":
                status = self.client.proxy.robot.getStatus(username, password)
                print("[CLI] Estado del robot:")
                print(status)

            elif command == "reporte" or command == "reporte_operator":
                report = self.client.proxy.robot.getReport(username, password)
                print("[CLI] Reporte:")
                print(report)

            elif command == "report_admin":
                user_filter = parts[1] if len(parts) >= 2 else None
                result_filter = parts[2] if len(parts) >= 3 else None
                report = self.client.proxy.robot.getAdminReport(username, password, user_filter, result_filter)
                print("[CLI] Reporte Admin:")
                print(report)

            elif command == "report_log":
                user_filter = parts[1] if len(parts) >= 2 else None
                level_filter = parts[2] if len(parts) >= 3 else None
                report = self.client.proxy.robot.getLogReport(username, password, user_filter, level_filter)
                print("[CLI] Reporte Log:")
                print(report)

            elif command == "lista_tareas":
                tasks = self.client.proxy.robot.listTasks(username, password)
                print("[CLI] Tareas disponibles:")
                print(tasks)

            elif command == "ejecutar_tarea":
                if len(parts) < 2:
                    print("[CLI] Uso: ejecutar_tarea <id_tarea>")
                    return
                task_id = parts[1]
                self.client.proxy.robot.executeTask(username, password, task_id)
                print(f"La tarea '{task_id}' fue ejecutada")

            elif command == "aprender_inicio":
                if len(parts) < 3:
                    print("[CLI] Uso: aprender_inicio <id> <nombre>")
                    return
                learning_task_id = parts[1]
                learning_task_name = parts[2]
                learning_mode_active = True
                learned_gcode_commands = []
                print(f"[APRENDIZAJE] Iniciado modo aprendizaje para tarea '{learning_task_name}' (id={learning_task_id}).")

            elif command == "aprender_fin":
                if not learning_mode_active:
                    print("[APRENDIZAJE] No hay un aprendizaje en curso.")
                    return
                learning_mode_active = False
                try:
                    self.client.proxy.robot.addTask(username, password, learning_task_id, learning_task_name, learned_gcode_commands)
                    print(f"La tarea '{learning_task_name}' fue guardada con {len(learned_gcode_commands)} comandos.")
                except Exception as e:
                    print(f"[APRENDIZAJE] Error al guardar la tarea: {e}")

            elif command == "ayuda" or command == "help":
                    help = self.client.proxy.robot.help(username, password)
                    print("[CLI] Ayuda mostrada para administrador.")
                    print(help)

            else:
                print(f"[CLI] Comando desconocido: {command}. Escriba 'ayuda' para ver los comandos disponibles.")

        except Exception as e:
            print(f"[CLI] Error al ejecutar comando '{command}': {e}")


def main() -> int:
    client = RobotRpcClient()
    cli = CLI(client)
    cli.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())