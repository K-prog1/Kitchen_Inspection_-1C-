"""Подсказки помощнику: что стоит сверить со спецификацией."""
from ..models import BOTTOM, TOP
from .base import Hit, rule


@rule("INFO-01", "Фасады верха и низа разного цвета", 3, "info")
def two_facade_colors(ctx, params):
    p = ctx.project
    has_top = any(not m.is_false_facade for m in p.modules_in(TOP))
    has_bottom = any(not m.is_false_facade for m in p.modules_in(BOTTOM))
    if has_top and has_bottom and p.facade_top_id and p.facade_bottom_id and p.facade_top_id != p.facade_bottom_id:
        return [
            Hit(
                f"Фасады верхних и нижних модулей разные (материалы {p.facade_top_id} и {p.facade_bottom_id}): "
                "в спецификации должен быть указан второй цвет.",
                [],
                {"facade_top": p.facade_top_id, "facade_bottom": p.facade_bottom_id},
            )
        ]
    return []


@rule("INFO-02", "В макете есть радиусные модули", 3, "info")
def radius_modules(ctx, params):
    radius = [m for m in ctx.project.modules if m.is_radius]
    if not radius:
        return []
    return [
        Hit(
            f"В макете радиусных модулей: {len(radius)}. Проверьте, что радиус указан в спецификации.",
            [m.index for m in radius],
            {"modules": [m.name for m in radius]},
        )
    ]
