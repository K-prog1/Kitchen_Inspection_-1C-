"""Импорт модулей регистрирует правила в REGISTRY (порядок = порядок вывода)."""
from . import data_rules, layout_rules, info_rules  # noqa: F401
from .base import LEVELS, LEVEL_LABELS, REGISTRY, Context, Hit, RuleMeta  # noqa: F401
