"""Тесты HTTP-слоя. Пропускаются, если FastAPI не установлен (pip install -r requirements.txt)."""
import unittest
from pathlib import Path

try:
    from fastapi.testclient import TestClient

    from app.main import app

    HAVE_FASTAPI = True
except ImportError:  # pragma: no cover
    HAVE_FASTAPI = False

FIXTURE = Path(__file__).parent / "fixtures" / "project_l_shape_19modules.dbs"


@unittest.skipUnless(HAVE_FASTAPI, "FastAPI не установлен")
class Api(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_serves_site(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Проверка кухонь", response.text)

    def test_health(self):
        self.assertEqual(self.client.get("/v1/health").json()["status"], "ok")

    def test_rules(self):
        codes = [r["code"] for r in self.client.get("/v1/rules").json()]
        self.assertIn("LAYOUT-02", codes)

    def test_check_real_project(self):
        with FIXTURE.open("rb") as fh:
            response = self.client.post("/v1/check", files={"file": ("project.dbs", fh)})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["layout"]["shape"], "L")
        self.assertEqual(body["summary"]["critical"], 0)

    def test_check_garbage_returns_422(self):
        response = self.client.post("/v1/check", files={"file": ("x.dbs", b"not json")})
        self.assertEqual(response.status_code, 422)
