# OMR Web App — Step-by-Step Plan (React + Django + DRF + Postgres)

## 0) Tech + Repo Layout

**Stack**

* Frontend: **React** (Next.js 14, TypeScript), Bootstrap (or MUI) for quick UI.
* Backend: **Django 5 + Django REST Framework + SimpleJWT**, **OpenCV** for OMR, **Pillow**, **numpy**.
* DB: **PostgreSQL** (SQLite in dev).
* Reverse proxy: **nginx** (prod).
* Container: **Docker + docker-compose**.
* Tests: Django tests + Pytest for analytics.

**Repo tree**

```
omr-app/
  backend/
    manage.py
    omr_backend/            # Django project
      settings.py
      urls.py
    accounts/               # auth, roles
    core/                   # Batch, Student
    exams/                  # Exam, ExamSet, Score, CSV export
    scans/                  # Scan upload, storage, overlay
    analysis/               # analytics endpoints (DI, PBS, KR-20)
    omr/                    # OMR reader + calibration
      template.yaml         # ROI coordinates (editable)
      reader.py             # OMR pipeline
      overlay.py            # draw debug overlays
    media/                  # uploaded files (dev)
    requirements.txt
    Dockerfile
  frontend/
    next.config.js
    package.json
    src/
      lib/api.ts
      lib/auth.ts
      components/
      app/                  # Next.js App Router
        login/page.tsx
        batches/page.tsx
        batches/[id]/students/page.tsx
        batches/[id]/exams/page.tsx
        exams/[id]/keys/page.tsx
        exams/[id]/upload/page.tsx
        exams/[id]/review/page.tsx
        exams/[id]/results/page.tsx
        exams/[id]/analytics/page.tsx
    Dockerfile
  deploy/
    nginx.conf
  docker-compose.yml
  .env.example
  README.md
```

---

## 1) Bootstrap Backend (Django + DRF + JWT)

**Commands**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install "django>=5" djangorestframework djangorestframework-simplejwt psycopg[binary] pillow opencv-python-headless numpy pyyaml
django-admin startproject omr_backend .
python manage.py startapp accounts
python manage.py startapp core
python manage.py startapp exams
python manage.py startapp scans
python manage.py startapp analysis
python manage.py startapp omr
```

**`omr_backend/settings.py`**

* Add apps: `rest_framework`, `rest_framework_simplejwt`, `accounts`, `core`, `exams`, `scans`, `analysis`, `omr`.
* `REST_FRAMEWORK` JWT defaults (SimpleJWT).
* `MEDIA_ROOT = BASE_DIR / "media"`, `MEDIA_URL = "/media/"`.
* CORS (allow frontend origin in dev).

**`omr_backend/urls.py`**

* Include `api/` router, media serving in dev.

**Accounts (roles)**

* Use Django’s User; add `role = models.CharField(choices=[('admin','Admin'),('checker','Checker')])`.
* Create signup migration or a management command to seed an admin from env (`ADMIN_EMAIL`, `ADMIN_PASSWORD`).

**JWT endpoints**

* `/api/auth/token/` (obtain), `/api/auth/token/refresh/`.

**Success check**: `python manage.py runserver` returns OpenAPI root (add `drf-spectacular` optionally).

---

## 2) Data Models & Constraints

**core/models.py**

* `Batch(id, name, code unique, created_at auto)`
* `Student(id, batch FK, student_number, full_name, email?, created_at)`
* `UniqueConstraint('batch', 'student_number')`

**exams/models.py**

* `Exam(id, batch FK, title, num_items int, created_at)`
* `ExamSet(id, exam FK, set_code (char), answer_key JSON list[str])`
* `Score(id, exam FK, student FK, set_code, raw_score, percent float, breakdown_json JSON)`
  `UniqueConstraint('exam','student')`

**scans/models.py**

* `Scan(id, exam FK, student FK null, image FileField, extracted_student_number, extracted_set_code, answers_json JSON, confidence float, status choices('processed','needs_review','pending'), created_at)`
* Add path function for uploads (`scans/%Y/%m/%d/uuid.ext`).

**Migrate**

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 3) Serializers, ViewSets, Routers (DRF)

**Endpoints**

* `/api/batches` CRUD
* `/api/students` CRUD (filters: `batch`, `student_number`, `q`)
* `/api/exams` CRUD (filter by `batch`)
* `/api/exams/{id}/sets` CRUD (answer_key GET/PUT)
* `/api/scans`:

  * `POST` multipart: `exam`, `file` → process OMR (stub first) → create `Scan`
  * `GET` list by `exam`, `status`
* `/api/exams/{id}/scores/recompute` POST
* `/api/exams/{id}/results` GET (paged)
* `/api/exams/{id}/export.csv` GET
* `/api/exams/{id}/analytics/summary` GET
* `/api/exams/{id}/analytics/per-item` GET
* `/api/scans/{id}/overlay.png` GET (image)

**Permissions**

* `IsAuthenticated` globally.
* `IsAdminUser` for CRUD on master data.
* Role guard: `checker` allowed on upload/review/export.

**Success check**: Browsable API shows endpoints; JWT works.

---

## 4) Scoring Service

Create `exams/services/scoring.py`:

* `score_submission(answers, key) -> (raw, percent, breakdown)`
* On Scan save (signal or service), if `answers_json` + `set_code` + key exists → upsert `Score`.

Add `/api/exams/{id}/scores/recompute` to recompute all scores when keys change.

---

## 5) CSV Import/Export

* **Student import**: POST `/api/students/import` (CSV: `student_number,full_name,email?`, plus `batch_id` param). Reject duplicates within batch.
* **Results export**: `/api/exams/{id}/export.csv`:

  * Columns: `batch_code,exam_title,student_number,full_name,set_code,raw_score,percent,answer_1..N,correct_1..N`.

Use `StreamingHttpResponse` to stream CSV.

---

## 6) OMR Pipeline — Stub → Implementation

**Goal**: parse your specific answer sheet: set code (A/B), examinee ID digits grid, 100 items (A–E). Ship a documented **stub** first, then fill with OpenCV.

**`omr/template.yaml`**

* Store canonical A4 canvas size and ROIs for:

  * page corners / fiducials
  * set code bubbles (A/B)
  * examinee ID grid (10 columns × digits 0–9)
  * answers blocks: items 1–100 × choices A–E (x,y,w,h per bubble)
* Allow global `offset_x/offset_y/scale` to tune per scanner.

**`omr/reader.py` (stub → code)**

```python
from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class ParsedScan:
    student_number: Optional[str]
    set_code: Optional[str]
    answers: List[Optional[str]]
    confidence: float
    issues: List[str]

def read_omr(image_path: str) -> ParsedScan:
    """
    1) Load image/PDF (first page) → grayscale
    2) Deskew/perspective warp to canonical canvas (four-point transform)
    3) For each ROI in template.yaml, compute fill ratio in circle masks
    4) Extract set_code, student_number, answers[]; compute confidence
    5) Return ParsedScan with issues (e.g., 'ambiguous_q_17')
    """
    raise NotImplementedError
```

**Implementation outline**

* Use `pdf2image` if PDF.
* Preprocess: grayscale, Gaussian blur, adaptive threshold or Otsu.
* Detect page contour (largest), `cv2.getPerspectiveTransform` to warp.
* For each ROI bubble:

  * Build circular mask; compute ink density; pick argmax.
  * If two close values within `epsilon`, tag **ambiguous**.
* Student number: per digit column, read chosen row 0–9.
* Confidence: avg margin between top and runner-up fill ratios.
* Status rule: if missing set code OR >5 ambiguous → `needs_review`, else `processed`.

**Wire into `/api/scans` POST**

* Save file → call `read_omr()` → create `Scan` with extracted fields, `status`.
* If `student_number` matches a student in the exam’s batch, attach FK.
* If `set_code` key exists → score now.
* Else wait for manual review.

---

## 7) Overlay for Review

**`omr/overlay.py`**

* Draw page contour + each ROI box; highlight selected bubbles; print detected set code and student number.
* Save PNG under `media/overlays/<scan_id>.png`.

**Endpoint** `/api/scans/{id}/overlay.png` returns the file (permission-checked).

---

## 8) Analytics (Difficulty, DI, PBS, KR-20)

**`analysis/services.py`**

* **Difficulty p**: proportion correct per item.
* **DI (27%)**: sort students by total score; top = ceil(0.27*N), bottom = ceil(0.27*N); `DI = (correct_top/n_top) - (correct_bottom/n_bottom)`. If N < 20, fall back to 33%.
* **Point-Biserial**: correlation of per-item correct (0/1) vs total score **excluding that item**.
* **KR-20**: `k/(k-1) * [1 - (Σ(pq))/σ^2_total]` where `k=num_items`, `p=item difficulty`, `q=1-p`.

**Endpoints**

* `/api/exams/{id}/analytics/summary`: mean, median, SD, KR-20, count.
* `/api/exams/{id}/analytics/per-item`: for 1..N: p, DI, PBS + A–E frequency.

Add unit tests with small fixtures verifying known values.

---

## 9) Review & Overrides

**`scans` endpoints**

* `GET /api/scans?exam={id}&status=needs_review`
* `PATCH /api/scans/{id}` body: `{ student_id?, set_code?, answers_json? }` → on save, re-score that student; possibly trigger analytics recompute (or recompute on demand).

---

## 10) Frontend (Next.js + TS)

**Commands**

```bash
cd ../frontend
npx create-next-app@latest . --ts --eslint --src-dir --app
npm i axios @tanstack/react-query bootstrap
```

**`src/lib/api.ts`**

* Axios instance with baseURL from env, JWT attach via interceptor, 401 refresh.

**`src/lib/auth.ts`**

* Helpers to store/refresh tokens, role checks.

**Pages (App Router)**

* `/login`: form → `/api/auth/token/`.
* `/batches`: list + create/edit modal.
* `/batches/[id]/students`: table (search, import CSV).
* `/batches/[id]/exams`: list + create.
* `/exams/[id]/keys`: grid editor 1..N × A–E; tabs per set; import/export key string or CSV.
* `/exams/[id]/upload`: drag-drop (react-dropzone) → POST `/api/scans`.
* `/exams/[id]/review`: table of `needs_review`; detail drawer: show image + `/overlay.png`, fields for student, set, answers, save.
* `/exams/[id]/results`: data grid (student, set, raw, %), export CSV button.
* `/exams/[id]/analytics`: summary cards + per-item table (p, DI, PBS) and mini bar chart (client-side).

**Navigation & Role guards**

* If role=checker → hide master data CRUD UI.

**Success check**: Can log in, create batch→students→exam→keys, upload a scan (stubbed), see it in review/results.

---

## 11) Docker & Compose

**`backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y poppler-utils gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn","omr_backend.wsgi:application","--bind","0.0.0.0:8000","--workers","3"]
```

**`frontend/Dockerfile`**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/.next/static /usr/share/nginx/html/_next/static
# Optional: use next export if fully static; otherwise reverse proxy to next server instead of nginx static.
COPY ./deploy/nginx.conf /etc/nginx/nginx.conf
```

> If you need SSR, run Next server instead:
>
> * Build stage → `RUN npm run build`
> * Final stage → `CMD ["npm","run","start"]` and proxy via nginx or expose 3000.

**`deploy/nginx.conf` (reverse proxy both apps)**

```nginx
events {}
http {
  server {
    listen 80;
    client_max_body_size 20m;

    # Frontend (Next on :3000)
    location / {
      proxy_pass http://frontend:3000;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Backend API (Django on :8000)
    location /api/ {
      proxy_pass http://backend:8000/api/;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Media files (overlays)
    location /media/ {
      proxy_pass http://backend:8000/media/;
    }
  }
}
```

**`docker-compose.yml`**

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: omr
      POSTGRES_USER: omr
      POSTGRES_PASSWORD: omr
    volumes: [dbdata:/var/lib/postgresql/data]
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgres://omr:omr@db:5432/omr
      DJANGO_SECRET_KEY: change-me
      DJANGO_DEBUG: "1"
      ALLOWED_HOSTS: "*"
    volumes: ["./backend:/app"]
    depends_on: [db]
  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_BASE: http://localhost/api
    volumes: ["./frontend:/app"]
  nginx:
    image: nginx:1.27
    volumes:
      - ./deploy/nginx.conf:/etc/nginx/nginx.conf
    ports: ["80:80"]
    depends_on: [frontend, backend]
volumes:
  dbdata:
```

**Run**

```bash
docker-compose up --build
```

---

## 12) Environment & Secrets

**`.env.example` (root)**

```
# Backend
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=1
DATABASE_URL=postgres://omr:omr@db:5432/omr
ALLOWED_HOSTS=*

# Frontend
NEXT_PUBLIC_API_BASE=http://localhost/api

# Admin seed
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=ChangeMe123!
```

---

## 13) Seed & Fixtures

* Management command `accounts/management/commands/seed_admin.py` to create admin from env.
* Demo data script: create 1 batch, 5 students, 1 exam (100 items), 1 set (A) with dummy key.

---

## 14) Tests

* **Analytics**: assert difficulty, DI, PBS, KR-20 against known small fixtures.
* **Scoring**: answers vs key.
* **OMR**: synthetic images—draw filled circles at ROIs, ensure detection.
* **API**: auth guards (checker vs admin), CSV export schema.

---

## 15) UX Polish (fast wins)

* Answer-key grid: keyboard navigation ←↑→↓, number keys to jump to item, A–E hotkeys.
* Bulk set copy: “Copy Set A → B”.
* Review page: show “Issues” chips (e.g., `ambiguous_q_17`).
* Results: quick search by student_number/name; “Recompute All” button (calls endpoint).

---

## 16) Production Notes

* Turn `DEBUG=0`, set `ALLOWED_HOSTS`, generate strong `SECRET_KEY`.
* Serve media from persistent storage (volume or S3).
* Add HTTPS termination on nginx.
* Configure CORS properly (only your domain).

---

## 17) Acceptance Checklist (what to demo)

1. Create Batch → Import Students (CSV) → Create Exam + Set A key.
2. Upload a scan → OMR populates student number, set code, answers → auto-score.
3. Flagged scan appears in Review with overlay; fix fields → score updates.
4. View Analytics (difficulty/DI/PBS/KR-20).
5. Export CSV → columns exactly as specified.
