"""HTTP-слой: тонкая обёртка над ядром. Запуск: uvicorn app.main:app --reload (из папки backend)."""
import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from .config import load_config
from .engine import RULES_VERSION, list_rules, run_checks
from .parsers import ParseError, parse_dbs

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
SITE_FILE = Path(__file__).resolve().parents[2] / "site" / "index.html"  # kitchen-checker/site/index.html
CONFIG = load_config(os.environ.get("KITCHEN_RULES_CONFIG"))

app = FastAPI(title="Проверка кухонь", version=RULES_VERSION)

# Адреса фронтенда на время разработки; в проде задаётся переменной окружения (через запятую)
origins = os.environ.get("KITCHEN_CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])


@app.get("/", include_in_schema=False)
def index():
    """Корневой адрес: страница сайта. Техническая документация API остаётся на /docs."""
    if SITE_FILE.exists():
        return FileResponse(SITE_FILE, media_type="text/html; charset=utf-8")
    return HTMLResponse('<p>Файл site/index.html не найден. Документация API: <a href="/docs">/docs</a></p>')


@app.get("/v1/health")
def health():
    return {"status": "ok", "rules_version": RULES_VERSION}


@app.get("/v1/rules")
def rules():
    return list_rules(CONFIG)


@app.post("/v1/check")
async def check(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Файл слишком большой.")
    try:
        project = parse_dbs(data)
    except ParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return run_checks(project, CONFIG).to_dict()
