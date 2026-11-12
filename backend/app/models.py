"""Нормализованная модель проекта: всё, что нужно правилам, независимо от формата источника."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

BOTTOM = "bottom"
TOP = "top"
OTHER = "other"
GROUP_LABELS = {BOTTOM: "нижние", TOP: "верхние", OTHER: "прочие"}

CORNER_KINDS = ("corner", "corner_straight")


@dataclass
class Module:
    """Один модуль кухни. Размеры в мм, координаты центра в см (как в файле конструктора)."""

    index: int
    code: str
    name: str
    group: str  # bottom | top | other
    kind: str  # cabinet.type из файла: common, corner_straight, end_radius_facade, ...
    width: int
    height: int
    depth: int
    x: float
    y: float
    z: float
    rotation: Optional[int]  # 0 / 90 / 180 / 270; None, если угол не кратен 90
    price: float
    has_sink: bool = False
    has_hob: bool = False

    @property
    def is_corner(self) -> bool:
        return self.kind in CORNER_KINDS

    @property
    def is_false_facade(self) -> bool:
        return self.kind.startswith("false_facade")

    @property
    def is_radius(self) -> bool:
        return "radius" in self.kind

    def footprint(self) -> Optional[tuple]:
        """Прямоугольник на плане (x0, z0, x1, z1) в см или None, если модуль повёрнут не на 90°."""
        if self.rotation is None:
            return None
        half_w = self.width / 20.0
        half_d = self.depth / 20.0
        if self.rotation in (0, 180):
            hx, hz = half_w, half_d
        else:
            hx, hz = half_d, half_w
        return (self.x - hx, self.z - hz, self.x + hx, self.z + hz)

    def along_range(self) -> Optional[tuple]:
        """Занимаемый отрезок вдоль ряда (см): по x для поворота 0/180, по z для 90/270."""
        if self.rotation is None:
            return None
        half_w = self.width / 20.0
        center = self.x if self.rotation in (0, 180) else self.z
        return (center - half_w, center + half_w)

    def label(self) -> str:
        return f"«{self.name}» ({self.code})"


@dataclass
class WallPanel:
    index: int
    width: int
    height: int
    material_id: Optional[int]
    material_name: Optional[str]


@dataclass
class Room:
    width: int  # мм
    depth: int
    height: int


@dataclass
class Project:
    name: str
    project_id: Optional[int]
    format_version: Optional[int]
    room: Room
    modules: list = field(default_factory=list)
    panels: list = field(default_factory=list)
    facade_top_id: Optional[int] = None
    facade_bottom_id: Optional[int] = None
    corpus_id: Optional[int] = None
    tabletop_id: Optional[int] = None
    notes: list = field(default_factory=list)  # замечания разбора (например, неизвестная версия формата)

    @property
    def total_price(self) -> float:
        return sum(m.price for m in self.modules)

    def modules_in(self, group: str) -> list:
        return [m for m in self.modules if m.group == group]
