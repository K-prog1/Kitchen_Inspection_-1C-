"""Тесты ядра на реальных проектах из конструктора и на искусственных поломках."""
import copy
import json
import unittest
from pathlib import Path

from app.config import load_config
from app.engine import list_rules, run_checks
from app.parsers import ParseError, parse_dbs, parse_dbs_dict, parse_dbs_file

FIXTURES = Path(__file__).parent / "fixtures"
L_SHAPE = FIXTURES / "project_l_shape_19modules.dbs"
SIX = FIXTURES / "project_straight_corner_6modules.dbs"


def load_raw(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rules_found(raw, config=None):
    result = run_checks(parse_dbs_dict(raw), config)
    return {f.rule for f in result.findings}, result


def find_object(raw, predicate):
    for obj in raw["objects"]:
        if obj.get("type") == "Cabinet" and predicate(obj):
            return obj
    raise AssertionError("объект для теста не найден")


class RealProjects(unittest.TestCase):
    def test_l_shape_project_is_parsed_completely(self):
        project = parse_dbs_file(L_SHAPE)
        self.assertEqual(len(project.modules), 19)
        self.assertEqual(len(project.modules_in("bottom")), 9)
        self.assertEqual(len(project.modules_in("top")), 10)
        self.assertEqual(len(project.panels), 2)
        self.assertEqual(project.total_price, 177970)  # совпадает со стоимостью в конструкторе
        self.assertEqual(project.format_version, 4)
        self.assertEqual(project.notes, [])

    def test_l_shape_project_layout_and_findings(self):
        found, result = rules_found(load_raw(L_SHAPE))
        self.assertEqual(result.layout.shape, "L")
        self.assertEqual(result.layout.bottom_corner_count, 1)
        self.assertEqual(result.summary["critical"], 0)
        self.assertEqual(result.summary["warning"], 0)
        self.assertEqual(found, {"INFO-01", "INFO-02"})  # два цвета фасадов, есть радиусные модули

    def test_six_modules_project_is_clean(self):
        found, result = rules_found(load_raw(SIX))
        self.assertEqual(result.layout.shape, "L")
        self.assertEqual(len(result.project.modules), 6)
        self.assertEqual(found, set())  # верхних модулей нет: подсказка про цвета не нужна

    def test_result_is_json_serializable(self):
        _, result = rules_found(load_raw(L_SHAPE))
        data = json.loads(json.dumps(result.to_dict(), ensure_ascii=False))
        self.assertEqual(data["schema_version"], "1")
        self.assertEqual(len(data["layout"]["modules"]), 19)
        self.assertEqual(data["summary"], {"critical": 0, "warning": 0, "info": 2})


class BrokenProjects(unittest.TestCase):
    def setUp(self):
        self.raw = load_raw(L_SHAPE)

    def test_zero_price(self):
        find_object(self.raw, lambda o: True)["price"] = 0
        found, result = rules_found(self.raw)
        self.assertIn("DATA-01", found)
        self.assertGreaterEqual(result.summary["critical"], 1)

    def test_empty_code(self):
        find_object(self.raw, lambda o: True)["code"] = "  "
        found, _ = rules_found(self.raw)
        self.assertIn("DATA-02", found)

    def test_removed_corner_module(self):
        corner = find_object(self.raw, lambda o: o["cabinet_group"] == "bottom" and o["cabinet"]["type"] == "corner_straight")
        self.raw["objects"].remove(corner)
        found, _ = rules_found(self.raw)
        self.assertIn("LAYOUT-04", found)

    def test_extra_corner_module(self):
        module = find_object(self.raw, lambda o: o["cabinet_group"] == "bottom" and o["cabinet"]["type"] == "common")
        module["cabinet"]["type"] = "corner"
        found, _ = rules_found(self.raw)
        self.assertIn("LAYOUT-05", found)

    def test_shifted_module_gives_gap_and_overlap(self):
        # модуль «под технику» (x=130) сдвигаем на 10 см: слева зазор, справа наложение
        module = find_object(self.raw, lambda o: o["position"]["x"] == 130 and o["cabinet_group"] == "bottom")
        module["position"]["x"] = 140
        found, _ = rules_found(self.raw)
        self.assertIn("LAYOUT-02", found)
        self.assertIn("LAYOUT-03", found)

    def test_module_outside_room(self):
        module = find_object(self.raw, lambda o: o["position"]["x"] == 190 and o["cabinet_group"] == "bottom")
        module["position"]["x"] = 400
        found, _ = rules_found(self.raw)
        self.assertIn("LAYOUT-01", found)

    def test_small_rounding_gap_is_tolerated(self):
        # зазор 5 мм из-за округления координат не должен срабатывать (допуск 10 мм)
        found, _ = rules_found(self.raw)
        self.assertNotIn("LAYOUT-02", found)

    def test_oblique_rotation_is_skipped_not_crashing(self):
        module = find_object(self.raw, lambda o: o["cabinet_group"] == "bottom" and o["cabinet"]["type"] == "common")
        module["rotation"]["_y"] = 0.5  # ~29°, не кратно 90
        result = run_checks(parse_dbs_dict(self.raw))
        self.assertIsNotNone(result)


class Config(unittest.TestCase):
    def test_rule_can_be_disabled_and_level_changed(self):
        raw = load_raw(L_SHAPE)
        find_object(raw, lambda o: True)["price"] = 0
        config = {"rules": {"DATA-01": {"level": "warning"}, "INFO-02": {"enabled": False}}}
        found, result = rules_found(raw, config)
        self.assertNotIn("INFO-02", found)
        data01 = [f for f in result.findings if f.rule == "DATA-01"][0]
        self.assertEqual(data01.level, "warning")

    def test_tolerance_from_config(self):
        raw = load_raw(L_SHAPE)
        module = find_object(raw, lambda o: o["position"]["x"] == 130 and o["cabinet_group"] == "bottom")
        module["position"]["x"] = 131  # зазор 10 мм слева, наложение 10 мм справа
        found_default, _ = rules_found(raw)
        found_strict, _ = rules_found(raw, {"rules": {"LAYOUT-02": {"params": {"gap_tolerance_mm": 1}}}})
        self.assertNotIn("LAYOUT-02", found_default)
        self.assertIn("LAYOUT-02", found_strict)

    def test_unknown_level_in_config_is_rejected(self):
        with self.assertRaises(ValueError):
            run_checks(parse_dbs_file(L_SHAPE), {"rules": {"DATA-01": {"level": "fatal"}}})

    def test_rules_listing(self):
        codes = [r["code"] for r in list_rules()]
        self.assertEqual(
            codes,
            ["DATA-01", "DATA-02", "LAYOUT-01", "LAYOUT-02", "LAYOUT-03", "LAYOUT-04", "LAYOUT-05", "INFO-01", "INFO-02"],
        )

    def test_load_config_without_path(self):
        self.assertEqual(load_config(None), {})


class ParsingErrors(unittest.TestCase):
    def test_not_json(self):
        with self.assertRaises(ParseError):
            parse_dbs(b"hello")

    def test_binary_garbage(self):
        with self.assertRaises(ParseError):
            parse_dbs(bytes([0xFF, 0xFE, 0x00, 0x81]))

    def test_json_without_objects(self):
        with self.assertRaises(ParseError):
            parse_dbs(b'{"room": {"width": 1, "depth": 1, "height": 1}, "project_settings": {}}')

    def test_json_list(self):
        with self.assertRaises(ParseError):
            parse_dbs(b"[1, 2, 3]")

    def test_unknown_format_version_adds_note(self):
        raw = load_raw(L_SHAPE)
        raw["version"] = "9"
        self.assertTrue(parse_dbs_dict(raw).notes)

    def test_cabinet_without_data(self):
        raw = load_raw(L_SHAPE)
        raw["objects"][0].pop("cabinet")
        with self.assertRaises(ParseError):
            parse_dbs_dict(raw)


if __name__ == "__main__":
    unittest.main()
