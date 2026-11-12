"""Движок: прогоняет все включённые правила и собирает результат проверки."""
from __future__ import annotations

from dataclasses import dataclass, field

from .layout import Layout, analyze_layout
from .models import Project
from .rules import LEVELS, REGISTRY, Context

RULES_VERSION = "0.1.0"
SCHEMA_VERSION = "1"


@dataclass
class Finding:
    rule: str
    level: str
    step: int
    title: str
    message: str
    modules: list = field(default_factory=list)
    details: dict = field(default_factory=dict)


@dataclass
class CheckResult:
    project: Project
    layout: Layout
    findings: list

    @property
    def summary(self) -> dict:
        return {level: sum(1 for f in self.findings if f.level == level) for level in LEVELS}

    def to_dict(self) -> dict:
        p = self.project
        return {
            "schema_version": SCHEMA_VERSION,
            "rules_version": RULES_VERSION,
            "project": {
                "name": p.name,
                "project_id": p.project_id,
                "format_version": p.format_version,
                "room_mm": {"width": p.room.width, "depth": p.room.depth, "height": p.room.height},
                "module_count": len(p.modules),
                "panel_count": len(p.panels),
                "total_price": p.total_price,
                "notes": list(p.notes),
            },
            "layout": {
                "shape": self.layout.shape,
                "shape_label": self.layout.shape_label,
                "bottom_corner_count": self.layout.bottom_corner_count,
                "top_corner_count": self.layout.top_corner_count,
                "runs": [
                    {"group": r.group, "rotation": r.rotation, "modules": r.indices, "start_cm": r.start, "end_cm": r.end}
                    for r in self.layout.runs
                ],
                "modules": [
                    {
                        "index": m.index,
                        "code": m.code,
                        "name": m.name,
                        "group": m.group,
                        "kind": m.kind,
                        "width_mm": m.width,
                        "height_mm": m.height,
                        "depth_mm": m.depth,
                        "rotation": m.rotation,
                        "footprint_cm": list(m.footprint()) if m.footprint() else None,
                        "has_sink": m.has_sink,
                        "has_hob": m.has_hob,
                        "price": m.price,
                    }
                    for m in p.modules
                ],
            },
            "findings": [
                {
                    "rule": f.rule,
                    "level": f.level,
                    "step": f.step,
                    "title": f.title,
                    "message": f.message,
                    "modules": f.modules,
                    "details": f.details,
                }
                for f in self.findings
            ],
            "summary": self.summary,
        }


def list_rules(config: dict = None) -> list:
    """Описание правил с учётом настроек (для экрана «правила» и для документации)."""
    overrides = (config or {}).get("rules", {})
    result = []
    for code, (meta, _fn) in REGISTRY.items():
        ov = overrides.get(code, {})
        result.append(
            {
                "code": code,
                "title": meta.title,
                "step": meta.step,
                "level": ov.get("level", meta.level),
                "enabled": ov.get("enabled", True),
                "params": {**meta.params, **ov.get("params", {})},
            }
        )
    return result


def run_checks(project: Project, config: dict = None) -> CheckResult:
    overrides = (config or {}).get("rules", {})
    layout = analyze_layout(project)
    ctx = Context(project=project, layout=layout)
    findings = []
    for code, (meta, fn) in REGISTRY.items():
        ov = overrides.get(code, {})
        if ov.get("enabled", True) is False:
            continue
        level = ov.get("level", meta.level)
        if level not in LEVELS:
            raise ValueError(f"Правило {code}: неизвестный уровень {level!r} в настройках")
        params = {**meta.params, **ov.get("params", {})}
        for hit in fn(ctx, params):
            findings.append(
                Finding(code, level, meta.step, meta.title, hit.message, list(hit.modules), dict(hit.details))
            )
    findings.sort(key=lambda f: LEVELS.index(f.level))  # критичное сверху, порядок правил сохраняется
    return CheckResult(project=project, layout=layout, findings=findings)
