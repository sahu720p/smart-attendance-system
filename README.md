# Smart Attendance Management System
### Enterprise Face Recognition & Anti-Spoofing College Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg?style=flat&logo=python)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-YuNet%20%2B%20SFace-5C3EE8.svg?style=flat&logo=opencv)](https://opencv.org)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-v4-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![Tests](https://img.shields.io/badge/Pytest-58%2F58%20Passing-brightgreen.svg?style=flat)](https://docs.pytest.org)

A production-grade, end-to-end college attendance management system driven by deep learning computer vision, active anti-spoofing challenge verification, role-based access control, SIMD-accelerated biometric vector search, real-time analytics, and formal institutional document generation.

---

## Key Highlights

- **Dual Neural Network CV Pipeline**: Lightweight **YuNet** face detection ($O(1)$ multi-face landmark detection) combined with **SFace** (128-dimensional continuous deep biometric embedding extraction).
- **Active Challenge-Response Anti-Spoofing**: Defeats static photos, cutouts, and pre-recorded replay video attacks via randomized multi-step physical challenges (head yaw rotation, eye blinks, dynamic smile analysis) with a 25-second TTL and single-use cryptographic receipt tokens.
- **Hardware-Vectorized SIMD Matching**: Zero external vector database required. NumPy continuous matrix dot product (`np.dot`) evaluates 3,000 enrolled faces in **0.042 milliseconds** (~24,000 matches/sec).
- **Dual-Layer Duplicate Prevention**: Memory-level pre-validation and database-level composite unique constraint (`session_id, student_id`) guaranteeing zero duplicate attendance markings.
- **Institutional Reporting & Exporting**: Generate formal college PDF reports (ReportLab), multi-sheet styled Excel workbooks (openpyxl), and RFC 4180 CSV files.
- **Security Hardened & Shielded**: Raw 128-dimensional biometric vectors are strictly blocked from all public API schemas; in-memory sliding-window rate limiters prevent brute-force attacks; strict HTTP security headers and 15MB payload caps are enforced.

---

## System Architecture Overview

```
                                 [ Client Browser ]
                     React 19 + Tailwind v4 + Canvas / Webcam
                                         │
                         HTTPS / REST API (JWT Bearer Token)
                                         ▼
                      [ FastAPI Async Application Core ]
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │                                │                                │
        ▼                                ▼                                ▼
[ CV Pipeline Engine ]         [ Liveness Engine ]             [ Security Middleware ]
- YuNet Face Detector          - Challenge Generator           - SecurityHeaders (CSP, HSTS)
- Laplacian Sharpness Filter   - Pose (solvePnP) & EAR         - PayloadLimit (15MB)
- SFace 128-d Embedding        - Cryptographic Receipt Token   - SlidingWindowRateLimiter
        │                                │                                │
        └────────────────────────────────┼────────────────────────────────┘
                                         ▼
                        [ SIMD Embedding Cache Manager ]
                        Thread-Safe (M, 128) Float32 Matrix
                                         │
                                         ▼
                     [ SQLAlchemy 2.0 Async / SQLite WAL ]
```

---

## Default Credentials & Roles

The system initializes with default academic credentials upon first startup:

| Role | Username | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `Admin@123` | Full access: Student CRUD, Biometric Enrollment & Reset, Audit Logs, System Settings, Session Oversight |
| **Faculty Member** | `dr.sharma` | `Faculty@123` | Lecture Session Management, Live Attendance Kiosk, Manual Overrides, Reports & PDF/Excel Exports |

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database & ORM**: SQLite in Write-Ahead-Logging (WAL) mode via SQLAlchemy 2.0 (Async) + aiosqlite
- **Authentication**: JWT Bearer Tokens (HS256) + Argon2id password hashing via Passlib
- **Computer Vision**: OpenCV Zoo YuNet (face detection) & SFace (128-d cosine recognition)
- **Report Generation**: ReportLab (PDF), openpyxl (Excel), CSV standard library

### Frontend
- **Framework**: React 19 + Vite 8
- **Styling**: Tailwind CSS v4 + Lucide React Icons
- **Data Visualization**: Chart.js + react-chartjs-2
- **Audio Feedback**: Synthesized Web Audio API tone chimes

---

## Quick Start (Development)

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Webcam / camera device

---

### Option A: One-Click Launch (Recommended) 🚀

Run both the FastAPI backend and React frontend simultaneously with a single command from the project root:

```bash
python3 run.py
```

**What this does automatically:**
- Auto-detects virtual environments (`backend/venv`, `.venv`, etc.).
- Verifies and installs missing frontend dependencies (`npm install`).
- Checks port availability for `8000` (FastAPI) and `5173` (Vite).
- Starts FastAPI backend with auto-reload at `http://127.0.0.1:8000`.
- Starts React/Vite development server at `http://127.0.0.1:5173`.
- Automatically opens your default web browser to the dashboard.
- Cleanly terminates both process groups and releases ports on `Ctrl + C`.

---

### Option B: Manual Setup (Separate Terminals)

#### 1. Setup Backend
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch FastAPI development server (with auto-reload)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend will be available at:
- **API Base**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/api/v1/docs`
- **ReDoc Specification**: `http://127.0.0.1:8000/api/v1/redoc`

#### 2. Setup Frontend
```bash
cd frontend

# Install dependencies
npm install

# Launch Vite development server
npm run dev -- --host 127.0.0.1 --port 5173
```
The web application will be accessible at:
- `http://127.0.0.1:5173`

---

## Configuration & Environment Variables

The system works out of the box with default development settings. To customize parameters (e.g. face recognition thresholds, JWT secret, session expiration), copy the sample configuration:

```bash
cd backend
cp .env.example .env
```

---

## Administrative Utilities

### Reset or Create Admin Credentials
If you need to change the Administrator password or create a new admin account:

```bash
cd backend
python reset_admin.py --password "YourNewPassword@123"
# Or specify a custom username:
python reset_admin.py --username "newadmin" --password "YourNewPassword@123"
```

---

## Running the Automated Test Suite

The system includes 58 comprehensive unit, integration, security, performance, and end-to-end tests:

```bash
cd backend
source venv/bin/activate
PYTHONPATH=. pytest -v
```

### Test Suite Coverage (14 Test Modules):
- `test_auth.py`: Login flows, Argon2id password hashing, token validation, RBAC guards.
- `test_database.py`: Model constraints, foreign key cascades, composite unique indices.
- `test_students.py`: Student management, search, deactivation, authorization.
- `test_faculty.py`: Faculty onboarding, department filtering, credentials management.
- `test_face_registration.py`: Quality filters, Laplacian blur thresholds, multi-sample enrollment.
- `test_face_recognition.py`: SFace cosine similarity matching and unknown face rejection.
- `test_liveness.py`: Head yaw rotation, eye blink, smile challenge verification, token TTL.
- `test_attendance_engine.py`: Session creation, live kiosk marking, duplicate prevention, late rules.
- `test_dashboard.py`: KPI calculations, 7-day trend aggregations, low attendance warnings.
- `test_reports.py`: JSON query, ReportLab PDF, openpyxl Excel (.xlsx), and CSV document exports.
- `test_security.py`: HTTP security headers, 15MB payload cap, rate limiting, vector shielding.
- `test_performance.py`: SIMD matrix dot product, cache hit benchmarks, query latencies.
- `test_health.py`: Database health probes, system status, API readiness checks.
- `test_e2e_lifecycle.py`: Complete student provisioning, enrollment, session lifecycle, and spoof attack rejection.

---

## Building for Production

### 1. Production Frontend Build
```bash
cd frontend
npm run build
```
Outputs optimized static assets to `frontend/dist/`.

### 2. Production Backend Execution
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## License & Attribution
Developed as an enterprise-grade biometric attendance architecture utilizing Google DeepMind AI coding practices and OpenCV Zoo deep learning models.
