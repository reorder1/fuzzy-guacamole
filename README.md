# OMR Assessment Platform

A full-stack web platform for scanning OMR answer sheets, managing exams and students, computing psychometric analytics, and exporting results.

## Features

- **Exam & Student Management**: Create batches, register students (CSV import API), set up exams and answer keys for multiple sets.
- **OMR Processing**: Upload scans, auto-extract answers/student IDs using an OpenCV pipeline, and flag ambiguous scans for manual review with overlays.
- **Scoring & Results**: Automatic scoring, manual corrections, CSV export, and on-demand recompute.
- **Analytics Dashboard**: Difficulty, discrimination index (27%), point-biserial correlation, and KR-20 reliability.
- **Role-based Access**: Admin (full control) and checker (upload/review/export) via JWT auth.
- **Dockerized Deployment**: Postgres, Django backend, Next.js frontend, and nginx reverse proxy.

## Requirements

- Docker & Docker Compose (recommended)
- Or: Python 3.11, Node.js 20, PostgreSQL 15 (for manual setup)

## Quick Start (Docker Compose)

```bash
git clone <repo>
cd omr-app
cp .env.example .env
docker-compose up --build
```

Services:

- Backend API: http://localhost/api/
- Frontend: http://localhost/
- Media (scan overlays): http://localhost/media/

## Manual Development Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_admin  # optional admin seed from env
python manage.py runserver 0.0.0.0:8000
```

Environment variables:

- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`
- `DATABASE_URL` (defaults to SQLite if unset)
- `ALLOWED_HOSTS`
- `ADMIN_EMAIL` / `ADMIN_PASSWORD`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE` to the backend API root (e.g., `http://localhost:8000/api`).

## Running Tests

```bash
cd backend
python manage.py test
```

Tests cover scoring logic, analytics calculations, and the OMR extraction stub pipeline.

## API Highlights

- JWT Auth: `POST /api/auth/token/`, `POST /api/auth/token/refresh/`, `GET /api/auth/me/`
- Core CRUD: `/api/batches/`, `/api/students/`, `/api/exams/`, `/api/exam-sets/`
- Scan ingestion: `POST /api/scans/` (multipart image), `POST /api/scans/{id}/review/` (manual corrections)
- Results: `/api/scores/?exam=<id>`, `/api/exams/{id}/export/`
- Analytics: `GET /api/analysis/exams/{id}/`

## Acceptance Workflow

1. Create a batch and register students.
2. Create an exam, configure answer keys per set.
3. Upload OMR scans to auto-score.
4. Review flagged scans with overlays and manual corrections.
5. Inspect analytics dashboard and export CSV results.

## Deployment Notes

- Set `DJANGO_DEBUG=0`, provide a strong `DJANGO_SECRET_KEY`, and restrict `ALLOWED_HOSTS`.
- Configure persistent storage for `/backend/media` for uploaded scans/overlays.
- Terminate TLS at nginx and adjust CORS origins for production domains.
