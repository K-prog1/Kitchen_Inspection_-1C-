"""Настройки правил: переопределяют уровень, включение и допуски. Логика правил остаётся в коде."""
from __future__ import annotations

import json
from pathlib import Path


def load_config(path=None) -> dict:
    """Читает JSON вида {"rules": {"LAYOUT-02": {"enabled": false, "level": "info", "params": {...}}}}.
    Без пути возвращает пустые настройки (действуют значения по умолчанию из кода)."""
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))
