<<<<<<< Updated upstream
# KITCHEN_INSPECTION_1C

> Automated quality control for kitchen orders in the procurement department

---

## About the Product

**Kitchen_Inspection_1C** is a commercial web platform that replaces paper checklists and technical cards used by the procurement department of a furniture company. The system cross-checks the contract, room measurements, specification, visual mockup, and the 1C ERP order against each other, detects discrepancies before production, and blocks erroneous orders from moving forward.

---

## The Problem

The procurement department manually verified every kitchen order across five documents. A single overlooked manager error led to incorrect material procurement, rework, and dissatisfied clients.

**Typical errors the system catches automatically:**

- An extra corner cabinet added to the order that does not exist on the mockup
- A hood ordered at 500 mm while the mockup shows a 450 mm cabinet above the stove
- A countertop cut placed next to the stove
- The second facade color for mezzanines not specified in the specification
- Measurement mismatch with the mockup: 2345 mm on measurements vs 2370 mm on the mockup
- Incorrect countertop depth for the sink
- Missing countertop radius specification
- Hood misaligned relative to the stove

---

## The Solution

The system processes every order through four mandatory verification stages:

### Step 1. Document Verification
Checks presence and correctness of:
- Contract
- Room measurements
- Specification
- Color mockup
- Black-and-white mockup with client full name, signing date, and client signature

### Step 2. Measurements vs Mockup Comparison
- Overall room dimensions
- Distances between walls
- Placement of windows and doors
- Presence of protrusions and niches
- Appliance installation dimensions

### Step 3. Specification vs Mockup Comparison
- Body color
- Facade material and color, upper and lower separately
- Countertop color
- Countertop radius or cut

### Step 4. 1C Order vs Mockup Comparison
- Body color in 1C against the mockup
- Facade colors in 1C against the mockup, each color verified separately
- Countertop color in 1C against the mockup
- Module quantities and types in 1C against the mockup

---

## Key Features

- Blocking checklist: the order cannot proceed to production without passing all checks
- Automatic comparison of 1C order data with the mockup
- Detection and logging of common manager errors
- Verification statuses and action history
- Discrepancy report with comments
- Unified validation rules database

---

## Business Value

- Reduced material procurement errors
- Fewer returns and rework
- Faster order approval process
- Transparent and controlled verification workflow
- Independence from individual employee experience

---

## Tech Stack

- **Frontend:** React, TypeScript
- **Backend:** FastAPI, Python
- **Database:** PostgreSQL
- **Integration:** 1C ERP

---

## Team

The project was developed by a two-person team as a commercial engagement. Full lifecycle: procurement department requirements analysis, system design, frontend and backend development, 1C integration, testing, and deployment.

---

*Kitchen order quality control system. Errors never reach production.*
=======
# Проверка кухонь: ядро бэкенда (версия 0.1.0)

Принимает файл проекта из конструктора (`.dbs`, внутри JSON), разбирает его, определяет форму кухни
и прогоняет проверки. Результат: список замечаний трёх уровней (критично, предупреждение, подсказка).

Это первый этап: проверки, которые можно сделать по одному файлу конструктора. Сверки со спецификацией
и заказом из 1С появятся, когда будут данные из 1С и справочник материалов.

## Быстрый старт

Ядро работает на стандартной библиотеке Python 3.10+, ничего ставить не нужно.

```bash
cd backend
python -m app.cli tests/fixtures/project_l_shape_19modules.dbs          # отчёт текстом
python -m app.cli tests/fixtures/project_l_shape_19modules.dbs --json   # то же в JSON
python -m unittest discover -s tests -v                                  # тесты
```

HTTP API (нужны зависимости):

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# документация и пробный запуск: http://127.0.0.1:8000/docs
pytest        # или python -m unittest discover -s tests (тесты API запустятся автоматически)
```

| Запрос | Что делает |
|---|---|
| `POST /v1/check` | Принимает файл `.dbs`, возвращает результат проверки |
| `GET /v1/rules` | Список правил с уровнями и допусками |
| `GET /v1/health` | Проверка, что сервис жив |
| `GET /` | Страница сайта (`site/index.html`) |

Ошибка в файле возвращается как `422` с понятным текстом. Настройки правил можно переопределить файлом JSON
(переменная окружения `KITCHEN_RULES_CONFIG`, пример: `backend/config/rules.example.json`).

## Сайт (одна страница)

Файл `site/index.html` открывается двойным щелчком, сервер не нужен. Страница сама разбирает файл `.dbs`,
считает те же правила, рисует план-вид и проверяет набор документов сделки по именам файлов. Данные
остаются в браузере. Интернет нужен только для шрифта (без него подставится системный).

В файле всё в одном месте: стили, затем разметка, затем скрипт. В скрипте по порядку: разбор файла (`parse`),
ряды и форма кухни (`layout`), правила (`RULES`), рисование плана (`plan`), вывод результата (`show`),
документы и замер (`docF`, `renderDocs`, `renderMeas`).

Важно: правила записаны дважды, в Python (`backend/app/rules/`) и в JavaScript (`RULES` в `site/index.html`).
При изменении правила или допуска правьте оба места. Когда фронтенд перейдёт на API бэкенда, JavaScript-копию уберут.

## Запуск из VS Code (кнопками)

Откройте в VS Code корневую папку `kitchen-checker` (не `backend`). Настройки лежат в `.vscode/`.

1. Первый раз: Terminal → Run Task → «Установка (один раз)». Создаётся окружение `backend/.venv`
   и ставятся зависимости. Затем Ctrl+Shift+P → «Developer: Reload Window».
2. Запуск: Ctrl+Shift+B запускает сервер и открывает две страницы: сайт (http://127.0.0.1:8000/) и техническую
   документацию API (http://127.0.0.1:8000/docs). Либо панель Run and Debug (значок треугольника с жуком) →
   «API: запустить сервер» → зелёный треугольник или F5. Документация: http://127.0.0.1:8000/docs
3. Проверка файла: Run and Debug → «Проверить пример (19 модулей)» или «Проверить свой файл .dbs».
4. Тесты: Run and Debug → «Тесты», либо Terminal → Run Task → «Запустить тесты».
5. Сайт: Terminal → Run Task → «Открыть сайт в браузере (Windows)», либо двойной щелчок по `site/index.html`.

Настройки рассчитаны на Windows (путь `.venv\Scripts\python.exe`). На macOS и Linux замените в `.vscode`
`Scripts/python.exe` на `bin/python`, а задачу про сайт на `open` или `xdg-open`.

## Структура

```
backend/app/models.py      модель проекта (модули, комната, панели)
backend/app/parsers.py     адаптер формата конструктора (.dbs); для 1С будет свой адаптер
backend/app/layout.py      ряды модулей и форма кухни (прямая, Г, П, двухрядная)
backend/app/rules/         правила: data_rules, layout_rules, info_rules
backend/app/engine.py      прогон правил, формат результата
backend/app/config.py      настройки правил (уровень, включено, допуски)
backend/app/cli.py         проверка из командной строки
backend/app/main.py        HTTP-слой (FastAPI)
backend/tests/             тесты и два реальных проекта в fixtures/
docs/                      примеры результата для фронтенда
.vscode/                   настройки запуска в VS Code
site/index.html            страница для браузера (проверка, план, документы, замер)
```

## Правила

| Код | Что проверяет | Уровень |
|---|---|---|
| DATA-01 | Цена модуля больше нуля | критично |
| DATA-02 | У модуля есть артикул | критично |
| LAYOUT-01 | Модули в пределах комнаты (допуск 10 мм) | критично |
| LAYOUT-02 | Нет зазоров между модулями в ряду (допуск 10 мм) | предупреждение |
| LAYOUT-03 | Модули не накладываются друг на друга (допуск 10 мм) | критично |
| LAYOUT-04 | Есть угловой нижний модуль там, где кухня поворачивает | критично |
| LAYOUT-05 | Нет лишних угловых нижних модулей | предупреждение |
| INFO-01 | Фасады верха и низа разного цвета: нужен «цвет 2» в спецификации | подсказка |
| INFO-02 | Есть радиусные модули: радиус должен быть в спецификации | подсказка |

Допуск 10 мм выбран по реальным файлам: координаты в файле округлены до 0,5 см, из-за этого между
соседними модулями бывает «зазор» 5 мм, который ошибкой не является.

## Как добавить правило

1. В файле из `backend/app/rules/` написать функцию с декоратором `@rule(код, название, шаг, уровень, допуски)`.
2. Функция получает `ctx` (проект и расположение) и `params` (допуски) и возвращает список `Hit(сообщение, модули, детали)`.
3. Написать тест: один проект, где ошибка есть, и один, где её нет (образец в `tests/test_core.py`).

Код правила не менять при смене допуска или уровня: это делается в файле настроек.

## Формат результата

Смотри `docs/example_result_clean.json` (проверка без замечаний) и `docs/example_result_with_findings.json`
(три критичных, одно предупреждение, две подсказки). В них есть список модулей с прямоугольниками
на плане (`footprint_cm`), по которым фронтенд может нарисовать план-вид. Контракт версионируется
полем `schema_version`.

## Что известно и что нет

- Проверено на двух проектах формата версии 4. Для других версий в результат добавляется примечание.
- Координаты в файле в сантиметрах (центр модуля), размеры в миллиметрах.
- Контур угловых и радиусных модулей берётся прямоугольником «ширина × глубина», точная форма в файле не хранится.
- Флаг `oven.active` (духовка) в файле ненадёжен: на проекте, где духовка стоит, он `false`. В правилах не используется.
- Окна, двери и выступы в двух проверенных файлах отсутствуют. Как они хранятся, неизвестно.
- Слой FastAPI (`main.py`, `test_api.py`) написан, но в среде разработки не запускался из-за отсутствия сети.
  Первым делом запустите тесты после `pip install -r requirements.txt`.

## Следующие шаги

1. Больше проектов: с окном и дверью, с плитой и вытяжкой, с духовкой и без неё, с радиусом на столешнице.
2. Справочник материалов (номер → название), чтобы сравнивать цвета со спецификацией.
3. Формат JSON сделки из 1С и адаптер для него; правила шагов 3 и 4 чек-листа.
4. Хранение проверок и ошибок в PostgreSQL, итоги за месяц по типам ошибок и менеджерам.
5. Фронтенд: загрузка файла и экран результата (на примерах из `docs/`).
>>>>>>> Stashed changes
