"""Проверка из командной строки: python -m app.cli проект.dbs [--json] [--config rules.json]"""
from __future__ import annotations

import argparse
import json
import sys

from .config import load_config
from .engine import run_checks
from .parsers import ParseError, parse_dbs_file
from .rules import LEVEL_LABELS


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Проверка проекта кухни из конструктора")
    parser.add_argument("file", help="файл проекта .dbs")
    parser.add_argument("--json", action="store_true", help="вывести результат в JSON")
    parser.add_argument("--config", help="файл настроек правил (JSON)")
    args = parser.parse_args(argv)

    try:
        project = parse_dbs_file(args.file)
    except (ParseError, OSError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 2
    result = run_checks(project, load_config(args.config))

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        p = result.project
        print(f"Проект: {p.name} (комната {p.room.width}×{p.room.depth}×{p.room.height} мм)")
        print(f"Форма кухни: {result.layout.shape_label}")
        print(f"Модулей: {len(p.modules)}, панелей: {len(p.panels)}, сумма: {p.total_price:.0f} ₽")
        for note in p.notes:
            print(f"Примечание: {note}")
        print()
        if not result.findings:
            print("Замечаний нет.")
        for f in result.findings:
            print(f"[{LEVEL_LABELS[f.level]}] {f.rule} — {f.message}")
        s = result.summary
        print(f"\nИтого: критично {s['critical']}, предупреждений {s['warning']}, подсказок {s['info']}")
    return 1 if result.summary["critical"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
