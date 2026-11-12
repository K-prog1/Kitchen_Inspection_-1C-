"""Адаптер формата конструктора (.dbs, внутри JSON). Другие источники (1С) получат свои адаптеры."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional

from .models import BOTTOM, OTHER, TOP, Module, Project, Room, WallPanel

SUPPORTED_FORMAT_VERSIONS = (4,)


class ParseError(ValueError):
    """Файл не удалось разобрать. Сообщение предназначено для пользователя."""


def _rotation_deg(obj: dict) -> Optional[int]:
    """Поворот вокруг вертикальной оси в градусах: 0/90/180/270 или None, если не кратен 90."""
    rot = obj.get("rotation") or {}
    rad = rot.get("_y", 0) or 0
    deg = math.degrees(rad)
    snapped = round(deg / 90.0) * 90
    if abs(deg - snapped) > 1.0:
        return None
    return int(snapped) % 360


def _as_int(value) -> Optional[int]:
    """Целое число из int или из строки с числом ('4'); иначе None."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value.strip())
    return None


def parse_dbs(data: bytes) -> Project:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ParseError(f"Файл не похож на проект конструктора: не удалось прочитать текст ({exc}).") from exc
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ParseError(f"Файл не похож на проект конструктора: это не JSON (строка {exc.lineno}).") from exc
    return parse_dbs_dict(raw)


def parse_dbs_file(path) -> Project:
    return parse_dbs(Path(path).read_bytes())


def parse_dbs_dict(raw) -> Project:
    if not isinstance(raw, dict):
        raise ParseError("Файл не похож на проект конструктора: ожидался объект JSON.")
    for key in ("room", "objects", "project_settings"):
        if key not in raw:
            raise ParseError(f"В файле нет раздела «{key}»: это не проект конструктора или формат изменился.")

    notes = []
    version = _as_int(raw.get("version"))
    if version not in SUPPORTED_FORMAT_VERSIONS:
        notes.append(f"Версия формата файла: {raw.get('version')!r}. Проверялась только версия 4, результат может быть неточным.")

    room_raw = raw["room"]
    try:
        room = Room(width=int(room_raw["width"]), depth=int(room_raw["depth"]), height=int(room_raw["height"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ParseError("В разделе «room» нет ширины, глубины или высоты комнаты.") from exc

    settings = raw["project_settings"] or {}
    selected = settings.get("selected_materials") or {}
    top_sel = selected.get("top") or {}
    bottom_sel = selected.get("bottom") or {}

    project = Project(
        name=str(settings.get("name") or ""),
        project_id=_as_int(settings.get("project_id")),
        format_version=version,
        room=room,
        facade_top_id=_as_int(top_sel.get("facades")),
        facade_bottom_id=_as_int(bottom_sel.get("facades")),
        corpus_id=_as_int(bottom_sel.get("corpus")),
        tabletop_id=_as_int(selected.get("tabletop")),
        notes=notes,
    )

    for idx, obj in enumerate(raw["objects"]):
        obj_type = obj.get("type")
        if obj_type == "Cabinet":
            cabinet = obj.get("cabinet")
            if not isinstance(cabinet, dict):
                raise ParseError(f"У объекта №{idx} нет данных модуля («cabinet»).")
            group = obj.get("cabinet_group") or obj.get("group")
            if group not in (BOTTOM, TOP):
                notes.append(f"Модуль №{idx} «{obj.get('name')}»: неизвестная группа {group!r}, в проверках расположения не участвует.")
                group = OTHER
            pos = obj.get("position") or {}
            project.modules.append(
                Module(
                    index=idx,
                    code=str(obj.get("code") or "").strip(),
                    name=str(obj.get("name") or ""),
                    group=group,
                    kind=str(cabinet.get("type") or obj.get("cabinet_type") or ""),
                    width=int(cabinet.get("width") or 0),
                    height=int(cabinet.get("height") or 0),
                    depth=int(cabinet.get("depth") or 0),
                    x=float(pos.get("x") or 0),
                    y=float(pos.get("y") or 0),
                    z=float(pos.get("z") or 0),
                    rotation=_rotation_deg(obj),
                    price=float(obj.get("price") or 0),
                    has_sink=bool((obj.get("sink") or {}).get("active")),
                    has_hob=bool((obj.get("hob") or {}).get("active")),
                )
            )
        elif obj_type == "Wall_panel":
            mat = obj.get("material") or {}
            project.panels.append(
                WallPanel(
                    index=idx,
                    width=int(obj.get("width") or 0),
                    height=int(obj.get("height") or 0),
                    material_id=_as_int(mat.get("id")),
                    material_name=mat.get("name"),
                )
            )
    return project
