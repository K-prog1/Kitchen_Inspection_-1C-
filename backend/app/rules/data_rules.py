"""Проверки данных: цены и артикулы."""
from .base import Hit, rule


@rule("DATA-01", "Цена модуля больше нуля", 0, "critical")
def price_not_zero(ctx, params):
    return [
        Hit(f"У модуля {m.label()} нулевая или отрицательная цена.", [m.index], {"price": m.price})
        for m in ctx.project.modules
        if m.price <= 0
    ]


@rule("DATA-02", "У модуля есть артикул", 0, "critical")
def code_not_empty(ctx, params):
    return [
        Hit(f"У модуля «{m.name}» нет артикула.", [m.index])
        for m in ctx.project.modules
        if not m.code
    ]
