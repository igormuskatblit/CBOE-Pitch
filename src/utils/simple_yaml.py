"""Minimal YAML reader/writer for controlled configs."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple


def _parse_value(value: str) -> object:
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def load_yaml(path: Path) -> Dict[str, object]:
    text = path.read_text(encoding="utf-8")
    result: Dict[str, object] = {}
    stack: list[Tuple[int, Dict[str, object]]] = [(0, result)]
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, value_part = line.strip().partition(":")
        value_part = value_part.strip()
        while stack and indent < stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        if value_part == "":
            new_map: Dict[str, object] = {}
            current[key] = new_map
            stack.append((indent + 2, new_map))
        else:
            current[key] = _parse_value(value_part)
    return result


def dump_yaml(data: Dict[str, object]) -> str:
    lines: list[str] = []

    def emit(mapping: Dict[str, object], indent: int) -> None:
        for key, value in mapping.items():
            prefix = " " * indent
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                emit(value, indent + 2)
            else:
                rendered = "true" if value is True else "false" if value is False else str(value)
                lines.append(f"{prefix}{key}: {rendered}")

    emit(data, 0)
    return "\n".join(lines) + "\n"


def save_yaml(path: Path, data: Dict[str, object]) -> None:
    path.write_text(dump_yaml(data), encoding="utf-8")
