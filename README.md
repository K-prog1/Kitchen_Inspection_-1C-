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
