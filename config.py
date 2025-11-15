#!/usr/bin/env python3
import os

# Endpoint del servidor XML-RPC (puede ajustarse por variable de entorno)
# Opciones comunes:
#   - Servidor local: "http://localhost:8080/RPC2"
#   - Servidor remoto: "http://10.68.4.101:8080/RPC2"    "http://192.168.1.125:8080/RPC2"
RPC_ENDPOINT = os.getenv("ROBOT_RPC_ENDPOINT", "http://localhost:8080/RPC2")

# Timeout de socket (segundos)
RPC_TIMEOUT = int(os.getenv("ROBOT_RPC_TIMEOUT", "30"))