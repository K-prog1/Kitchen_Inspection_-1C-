"""Геометрия кухни: ряды модулей и форма кухни (прямая, Г, П, двухрядная)."""
from __future__ import annotations

from dataclasses import dataclass, field

from .models import BOTTOM, TOP, Project

SHAPE_LABELS = {
    "none": "Нет нижних модулей",
    "unknown": "Не определена",
    "straight": "Прямая",
    "L": "Г-образная",
    "U": "П-образная",
    "parallel": "Двухрядная (параллельная)",
    "other": "Сложная форма",
}
# Сколько нижних угловых модулей ожидается для формы (None: не проверяем)
EXPECTED_BOTTOM_CORNERS = {"straight": 0, "parallel": 0, "L": 1, "U": 2}


@dataclass
class Run:
    """Ряд модулей одной группы с одним поворотом."""

    group: str
    rotation: int
    indices: list  # индексы модулей по порядку вдоль ряда
    start: float  # см вдоль оси ряда
    end: float


@dataclass
class Layout:
    shape: str = "none"
    runs: list = field(default_factory=list)
    bottom_corner_count: int = 0
    top_corner_count: int = 0

    @property
    def shape_label(self) -> str:
        return SHAPE_LABELS[self.shape]

    @property
    def expected_bottom_corners(self):
        return EXPECTED_BOTTOM_CORNERS.get(self.shape)


def _detect_shape(project: Project) -> str:
    bottom = [m for m in project.modules_in(BOTTOM) if not m.is_false_facade]
    if not bottom:
        return "none"
    rotations = sorted({m.rotation for m in bottom if not m.is_corner and m.rotation is not None})
    if not rotations:
        return "unknown"
    if len(rotations) == 1:
        return "straight"
    if len(rotations) == 2:
        diff = (rotations[1] - rotations[0]) % 180
        return "L" if diff == 90 else "parallel"
    if len(rotations) == 3:
        return "U"
    return "other"


def analyze_layout(project: Project) -> Layout:
    layout = Layout(shape=_detect_shape(project))
    layout.bottom_corner_count = sum(1 for m in project.modules_in(BOTTOM) if m.is_corner)
    layout.top_corner_count = sum(1 for m in project.modules_in(TOP) if m.is_corner)

    for group in (BOTTOM, TOP):
        by_rotation = {}
        for m in project.modules_in(group):
            if m.is_false_facade or m.rotation is None:
                continue
            by_rotation.setdefault(m.rotation, []).append(m)
        for rotation in sorted(by_rotation):
            members = sorted(by_rotation[rotation], key=lambda m: sum(m.along_range()) / 2)
            ranges = [m.along_range() for m in members]
            layout.runs.append(
                Run(
                    group=group,
                    rotation=rotation,
                    indices=[m.index for m in members],
                    start=min(r[0] for r in ranges),
                    end=max(r[1] for r in ranges),
                )
            )
    return layout
