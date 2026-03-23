# CIMS Backend — Service Documentation

## Overview

The CIMS (Coaching Institute Management System) backend is a FastAPI application that provides a RESTful API for managing coaching institute operations. It supports both a web frontend and an Android mobile app with offline-first sync capability.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Clients                              │
│                                                             │
│   Android App (offline-first)    Web / Admin Browser        │
└────────────────┬────────────────────────┬───────────────────┘
                 │  HTTP/HTTPS            │  HTTP/HTTPS
                 ▼                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
│                                                             │
│  CORS Middleware → Router Dispatch → Dependency Injection   │
│                                                             │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌────────────────┐  │
│  │   Auth   │ │Teachers │ │ Students │ │   Fee Records  │  │
│  │  Router  │ │ Router  │ │  Router  │ │     Router     │  │
│  └──────────┘ └─────────┘ └──────────┘ └────────────────┘  │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐                      │
│  │ Batches  │ │Attendnc │ │   Sync   │                      │
│  │  Router  │ │  Router │ │  Router  │                      │
│  └──────────┘ └─────────┘ └──────────┘                      │
│                                                             │
│              SQLAlchemy ORM Layer                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Database (Render)                   │
│                                                             │
│  users  teachers  batches  students  fee_records            │
│  attendance  sync_logs  alembic_version                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Application Entry Points

| File | Purpose |
|---|---|
| `run.py` | Local dev server startup via `python run.py` |
| `app/main.py` | FastAPI app creation, middleware, router registration |
| `app/config.py` | All configuration loaded from environment variables |
| `app/database.py` | SQLAlchemy engine, session factory, `get_db` dependency |
| `app/models.py` | All SQLAlchemy ORM models |
| `app/auth.py` | Password hashing, JWT creation/decode, role guards |

---

## Services (Routers)

### 1. Auth Service — `/api/auth`

Handles user identity, session tokens, and access control.

**Endpoints:**

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/bootstrap-admin` | None | Create first admin (disabled once any user exists) |
| POST | `/login` | None | Returns JWT bearer token |
| POST | `/register` | Admin only | Create a new system user |
| GET | `/me` | Any user | Get current user profile |
| PUT | `/me` | Any user | Update own profile (role change blocked) |
| POST | `/change-password` | Any user | Change own password |
| GET | `/users` | Admin only | List all users |
| GET | `/users/{id}` | Admin only | Get user by ID |
| PUT | `/users/{id}` | Admin only | Update any user |
| DELETE | `/users/{id}` | Admin only | Soft delete user |
| GET | `/roles/permissions` | Any user | List role permission definitions |

**Auth Flow:**

```
Client                         Auth Service                  Database
  │                                 │                            │
  │── POST /login ─────────────────>│                            │
  │   {username, password}          │                            │
  │                                 │── query user by username ─>│
  │                                 │<─ user row ────────────────│
  │                                 │                            │
  │                                 │ verify SHA256+bcrypt hash  │
  │                                 │ update last_login_at       │
  │                                 │── commit ─────────────────>│
  │                                 │                            │
  │<─ {access_token, user} ─────────│                            │
  │   JWT signed with SECRET_KEY    │                            │
  │                                 │                            │
  │── GET /api/teachers/ ──────────>│                            │
  │   Authorization: Bearer <token> │                            │
  │                                 │ decode JWT → sub=username  │
  │                                 │── query user ─────────────>│
  │                                 │<─ user (role check) ───────│
  │<─ 200 data ─────────────────────│                            │
```

**Roles and permissions:**

| Role | Capabilities |
|---|---|
| `admin` | Full access — manage users, teachers, students, batches, fees, attendance, settings |
| `teacher` | View students, manage attendance, view batches and reports |
| `accountant` | View students, manage fees, view reports |
| `reception` | Manage students, view batches and teachers |

**Password security:**
- Passwords are pre-hashed with SHA-256 before bcrypt to avoid the bcrypt 72-byte limit.
- Verification checks the normalized path first, then falls back to legacy direct bcrypt for older hashes.

---

### 2. Teachers Service — `/api/teachers`

Manages teacher records.

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| GET | `/` | List all teachers (supports pagination) |
| GET | `/{id}` | Get teacher by ID |
| POST | `/` | Create teacher |
| PUT | `/{id}` | Update teacher |
| DELETE | `/{id}` | Soft delete (sets `is_deleted=true`) |
| POST | `/{id}/restore` | Restore soft-deleted teacher |

**Data model:** `name`, `subject`, `contact_number`, `salary`, `date_of_joining`, soft-delete fields, device tracking fields.

---

### 3. Batches Service — `/api/batches`

Manages class batches. Each batch is linked to a teacher.

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| GET | `/` | List batches |
| GET | `/{id}` | Get batch |
| POST | `/` | Create batch (requires valid `teacher_id`) |
| PUT | `/{id}` | Update batch |
| DELETE | `/{id}` | Soft delete |
| POST | `/{id}/restore` | Restore |

**Data model:** `name`, `time`, `teacher_id` (FK), soft-delete fields, device tracking fields.

---

### 4. Students Service — `/api/students`

Manages student enrollment and fee tracking.

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| GET | `/` | List students (filter by `batch_id`, pagination) |
| GET | `/{id}` | Get student by internal ID |
| GET | `/roll/{roll_number}` | Get student by roll number |
| POST | `/` | Create student |
| PUT | `/{id}` | Update student |
| DELETE | `/{id}` | Soft delete |
| POST | `/{id}/restore` | Restore |

**Data model:** `roll_number` (unique), `name`, `contact_number`, `total_fees`, `paid_fees`, `batch_id` (FK), `payment_mode`, `installment_type`, `referred_by`, soft-delete and device tracking fields.

---

### 5. Fee Records Service — `/api/fee-records`

Records individual fee payment transactions per student.

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| GET | `/` | List fee records (filter by `student_id`) |
| GET | `/{id}` | Get record by ID |
| GET | `/receipt/{receipt_id}` | Get record by receipt ID |
| POST | `/` | Create fee record |

**Data model:** `student_id` (FK), `amount_paid`, `payment_method`, `date`, `receipt_id` (unique), `remarks`, device tracking fields.

---

### 6. Attendance Service — `/api/attendance`

Records daily per-student attendance.

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| GET | `/` | List records (filter by `student_id`, `date`) |
| GET | `/{id}` | Get by ID |
| POST | `/` | Create single attendance record |
| POST | `/bulk` | Create multiple attendance records in one request |

**Data model:** `student_id` (FK), `date` (epoch ms), `is_present`, soft-delete and device tracking fields.

---

### 7. Sync Service — `/api/sync`

Provides bi-directional sync between the Postgres server and the Android Room database.

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| POST | `/pull` | Pull all records changed since `last_sync_timestamp` |
| POST | `/push/teachers` | Push teacher changes from device |
| POST | `/push/batches` | Push batch changes from device |
| POST | `/push/students` | Push student changes from device |
| POST | `/push/fee-records` | Push fee records from device |
| POST | `/push/attendance` | Push attendance from device |
| GET | `/status` | Get last sync status for a device |

**Sync flow:**

```
Android App                        Sync Service               Database
     │                                   │                        │
     │ 1) App comes online               │                        │
     │                                   │                        │
     │── POST /api/sync/push/students ──>│                        │
     │   {students: [...], device_id}    │                        │
     │                                   │ upsert each student    │
     │                                   │── commit ─────────────>│
     │<─ {created, updated, errors} ─────│                        │
     │                                   │                        │
     │── POST /api/sync/pull ───────────>│                        │
     │   {device_id, last_sync: 1710000} │                        │
     │                                   │ query all tables       │
     │                                   │ WHERE updated_at >     │
     │                                   │ last_sync_timestamp    │
     │                                   │── fetch ──────────────>│
     │                                   │<─ changed rows ────────│
     │<─ {data: {teachers,batches,...},   │                        │
     │    server_timestamp} ─────────────│                        │
     │                                   │                        │
     │ 2) App saves server_timestamp     │                        │
     │    locally for next sync          │                        │
```

**Conflict resolution:** Last write wins based on `updated_at` timestamp. The server timestamp is authoritative.

---

## Database Schema

```
users
  id, username*, email*, hashed_password, full_name
  role (ENUM: admin/teacher/accountant/reception)
  is_active, is_deleted, deleted_at
  created_at, updated_at, last_login_at

teachers
  id, name, subject, contact_number, salary, date_of_joining
  is_deleted, deleted_at, created_at, updated_at
  device_id, last_synced_at

batches
  id, name, time, teacher_id (FK→teachers)
  is_deleted, deleted_at, created_at, updated_at
  device_id, last_synced_at

students
  id, roll_number*, name, contact_number
  total_fees, paid_fees, batch_id (FK→batches)
  payment_mode, installment_type, referred_by
  is_deleted, deleted_at, created_at, updated_at
  device_id, last_synced_at

fee_records
  id, student_id (FK→students), amount_paid
  payment_method, date, receipt_id*, remarks
  is_deleted, deleted_at, created_at
  device_id, last_synced_at

attendance
  id, student_id (FK→students), date, is_present
  is_deleted, deleted_at, created_at
  device_id, last_synced_at

sync_logs
  id, device_id, entity_type, entity_id
  operation, synced_at, status, error_message

* = unique index
```

---

## Request Lifecycle

```
HTTP Request
     │
     ▼
CORS Middleware
  (validates Origin header against ALLOWED_ORIGINS)
     │
     ▼
FastAPI Router matching
  (path + method)
     │
     ▼
Dependency injection
  ├── get_db()       → opens SQLAlchemy session
  └── get_current_user() (if protected endpoint)
       ├── extract Bearer token from Authorization header
       ├── decode JWT (verify signature + expiry)
       ├── query User from DB
       └── check is_active
             │
             ▼
         require_role() (if role-restricted)
           └── compare user.role to allowed roles list
     │
     ▼
Route handler executes
  └── DB queries via SQLAlchemy ORM
     │
     ▼
Pydantic response model serialization
     │
     ▼
HTTP Response (JSON)
```

---

## Environment Configuration

All settings are loaded from `.env` via `app/config.py`.

| Variable | Purpose | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT signing key | long random string |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL | `30` |
| `API_HOST` | Bind host | `0.0.0.0` |
| `API_PORT` | Bind port (falls back to `PORT` env for Render) | `8000` |
| `API_RELOAD` | Auto reload in dev | `True` (dev) / `False` (prod) |
| `ALLOWED_ORIGINS` | CORS whitelist, comma-separated | `https://myapp.com` |

---

## Deployment Flow

```
Developer
    │
    │ git push origin main
    ▼
GitHub
    │
    │ triggers GitHub Actions CI (.github/workflows/ci.yml)
    ▼
CI pipeline
    ├── pip install -r requirements.txt
    ├── pip check (dependency graph validation)
    ├── python -m compileall app (syntax check)
    ├── alembic upgrade head --sql (offline migration dry-run)
    └── python -c "from app.main import app" (import smoke test)
    │
    │ all checks pass
    ▼
Render (autoDeployTrigger: checksPass)
    │
    ├── Build: pip install -r requirements.txt
    ├── Pre-deploy: python -m alembic upgrade head  ← runs migrations
    ├── Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    └── Health check: GET /health → {"status": "healthy"}
    │
    │ health check passes
    ▼
Live traffic served
```

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Soft delete on all entities | Enables sync recovery and audit trail without permanent data loss |
| Epoch milliseconds for all timestamps | Consistent with Android Room / mobile clients that use `System.currentTimeMillis()` |
| SHA-256 pre-hash before bcrypt | Avoids bcrypt's 72-byte input limit for long passwords |
| Migration-first schema (no `create_all` at startup) | Prevents accidental schema drift in production |
| Internal Render DB URL for app | Stays within Render's private network; no internet exposure needed |
| `device_id` + `last_synced_at` on all entities | Tracks origin device for audit and enables per-device conflict analysis |
