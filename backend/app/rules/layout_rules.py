"""Проверки расположения модулей по координатам из конструктора."""
from ..models import BOTTOM, GROUP_LABELS
from .base import Hit, rule


@rule("LAYOUT-01", "Модули в пределах комнаты", 0, "critical", {"tolerance_mm": 10})
def inside_room(ctx, params):
    room = ctx.project.room
    width_cm, depth_cm = room.width / 10.0, room.depth / 10.0
    tol = params["tolerance_mm"] / 10.0
    hits = []
    for m in ctx.project.modules:
        fp = m.footprint()
        if fp is None:
            continue
        x0, z0, x1, z1 = fp
        overflow = max(-x0, -z0, x1 - width_cm, z1 - depth_cm)
        if overflow > tol:
            mm = round(overflow * 10)
            hits.append(Hit(f"Модуль {m.label()} выходит за пределы комнаты на {mm} мм.", [m.index], {"overflow_mm": mm}))
    return hits


@rule("LAYOUT-02", "Нет зазоров между модулями в ряду", 0, "warning", {"gap_tolerance_mm": 10})
def gaps_in_runs(ctx, params):
    tol = params["gap_tolerance_mm"]
    hits = []
    for run in ctx.layout.runs:
        modules = [ctx.module(i) for i in run.indices]
        for prev, nxt in zip(modules, modules[1:]):
            gap_mm = (nxt.along_range()[0] - prev.along_range()[1]) * 10
            if gap_mm > tol:
                hits.append(
                    Hit(
                        f"Зазор {round(gap_mm)} мм между модулями {prev.label()} и {nxt.label()} "
                        f"({GROUP_LABELS[run.group]} модули).",
                        [prev.index, nxt.index],
                        {"gap_mm": round(gap_mm), "group": run.group},
                    )
                )
    return hits


@rule("LAYOUT-03", "Модули не накладываются друг на друга", 0, "critical", {"overlap_tolerance_mm": 10})
def overlaps(ctx, params):
    tol = params["overlap_tolerance_mm"] / 10.0
    hits = []
    for group in ({m.group for m in ctx.project.modules}):
        members = [m for m in ctx.project.modules_in(group) if not m.is_false_facade and m.footprint()]
        for pos, a in enumerate(members):
            for b in members[pos + 1 :]:
                ax0, az0, ax1, az1 = a.footprint()
                bx0, bz0, bx1, bz1 = b.footprint()
                over_x = min(ax1, bx1) - max(ax0, bx0)
                over_z = min(az1, bz1) - max(az0, bz0)
                if over_x > tol and over_z > tol:
                    hits.append(
                        Hit(
                            f"Модули {a.label()} и {b.label()} накладываются друг на друга "
                            f"({round(over_x * 10)} × {round(over_z * 10)} мм).",
                            [a.index, b.index],
                            {"overlap_x_mm": round(over_x * 10), "overlap_z_mm": round(over_z * 10)},
                        )
                    )
    return hits


@rule("LAYOUT-04", "Есть угловой модуль там, где кухня поворачивает", 0, "critical")
def corner_missing(ctx, params):
    layout = ctx.layout
    expected = layout.expected_bottom_corners
    if expected is not None and layout.bottom_corner_count < expected:
        return [
            Hit(
                f"Форма кухни: {layout.shape_label.lower()}. Нижних угловых модулей должно быть "
                f"не меньше {expected}, найдено {layout.bottom_corner_count}.",
                [],
                {"shape": layout.shape, "expected": expected, "found": layout.bottom_corner_count},
            )
        ]
    return []


@rule("LAYOUT-05", "Нет лишних угловых модулей", 0, "warning")
def corner_extra(ctx, params):
    layout = ctx.layout
    expected = layout.expected_bottom_corners
    if expected is not None and layout.bottom_corner_count > expected:
        indices = [m.index for m in ctx.project.modules_in(BOTTOM) if m.is_corner]
        return [
            Hit(
                f"Форма кухни: {layout.shape_label.lower()}. Нижних угловых модулей ожидается {expected}, "
                f"найдено {layout.bottom_corner_count}.",
                indices,
                {"shape": layout.shape, "expected": expected, "found": layout.bottom_corner_count},
            )
        ]
    return []
