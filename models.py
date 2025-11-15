#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Vector3:
    x: float
    y: float
    z: float

    def to_rpc(self) -> dict:
        return {"x": float(self.x), "y": float(self.y), "z": float(self.z)}


@dataclass
class GCodeCommand:
    code: str
    args: Dict[str, float] = field(default_factory=dict)
    comment: str = ""

    def to_rpc(self) -> dict:
        return {
            "code": self.code,
            "args": {str(k): float(v) for k, v in self.args.items()},
            "comment": self.comment,
        }

    @staticmethod
    def from_line(line: str) -> "GCodeCommand":
        """
        Parseo simple de una línea de G-Code.
        Soporta ejemplos tipo:
          - G0 X0 Y0 Z0
          - G1 X10.5 Y-3.1 Z0.0 F500
          - M3 ; comentario
        No valida sintaxis completa de G-Code (lo mínimo para armar args).
        """
        raw = line.strip()
        if not raw:
            return None  # línea vacía
        # Remover comentarios ; o ( )
        comment = ""
        if ";" in raw:
            raw, comment = raw.split(";", 1)
            comment = comment.strip()
        raw = raw.strip()
        if not raw:
            return None

        parts = raw.split()
        code = parts[0].upper()
        args: Dict[str, float] = {}
        for token in parts[1:]:
            token = token.strip()
            if not token:
                continue
            # Formato típico: X10.5, Y-2, F500
            key = token[0].upper()
            val = token[1:]
            try:
                args[key] = float(val)
            except ValueError:
                # Si no es número (p.ej. S1000 para spindle), intentamos float;
                # si falla, lo ignoramos (o podrías guardarlo aparte).
                continue
        return GCodeCommand(code=code, args=args, comment=comment)


@dataclass
class GCodeProgram:
    id: str = ""
    ownerUserId: str = ""
    name: str = ""
    commands: List[GCodeCommand] = field(default_factory=list)

    def to_rpc(self) -> dict:
        return {
            "id": self.id,
            "ownerUserId": self.ownerUserId,
            "name": self.name,
            "commands": [c.to_rpc() for c in self.commands],
        }

    @staticmethod
    def load_from_file(path: str, owner_user_id: str = "") -> "GCodeProgram":
        import os

        name = os.path.basename(path)
        commands: List[GCodeCommand] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                cmd = GCodeCommand.from_line(line)
                if cmd is not None:
                    commands.append(cmd)
        return GCodeProgram(id="", ownerUserId=owner_user_id, name=name, commands=commands)