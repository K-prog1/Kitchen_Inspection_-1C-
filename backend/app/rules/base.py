"""Каркас правил: каждое правило регистрируется декоратором и возвращает список находок (Hit)."""
from __future__ import annotations

from dataclasses import dataclass, field

LEVELS = ("critical", "warning", "info")  # критично, предупреждение, подсказка
LEVEL_LABELS = {"critical": "Критично", "warning": "Предупреждение", "info": "Подсказка"}


@dataclass
class Hit:
    message: str
    modules: list = field(default_factory=list)  # индексы модулей, к которым относится находка
    details: dict = field(default_factory=dict)


@dataclass(frozen=True)
class RuleMeta:
    code: str
    title: str
    step: int  # шаг чек-листа закупа (1-4); 0 = проверка самого макета
    level: str
    params: dict


@dataclass
class Context:
    project: object
    layout: object

    def module(self, index: int):
        for m in self.project.modules:
            if m.index == index:
                return m
        raise KeyError(index)


REGISTRY: dict = {}  # code -> (RuleMeta, функция)


def rule(code: str, title: str, step: int, level: str, params: dict = None):
    if level not in LEVELS:
        raise ValueError(f"Неизвестный уровень {level!r} у правила {code}")

    def decorator(fn):
        if code in REGISTRY:
            raise ValueError(f"Правило {code} уже зарегистрировано")
        REGISTRY[code] = (RuleMeta(code, title, step, level, dict(params or {})), fn)
        return fn

    return decorator
