# CIMS Backend API

FastAPI backend for Coaching Institute Management System with PostgreSQL database and mobile sync support.

## Features

- **RESTful API** for all CIMS modules (Teachers, Batches, Students, Fee Records, Attendance)
- **PostgreSQL Database** with SQLAlchemy ORM
- **Data Synchronization** - Bi-directional sync with mobile app
- **Soft Delete** support for all entities
- **Device Tracking** for multi-device scenarios
- **API Documentation** - Auto-generated Swagger/OpenAPI docs

## Project Structure

```text
cims_backend/
|-- app/                      # FastAPI application code
|-- alembic/                  # Database migrations
|-- docs/                     # Project documentation
|   |-- QUICK_START.md
|   |-- deployment/
|   |   `-- RENDER_DEPLOYMENT.md
|   |-- mobile/
|   |   `-- ANDROID_INTEGRATION.md
|   `-- archive/
|       `-- PHASE2_IMPLEMENTATION_SUMMARY.md
|-- scripts/
|   `-- database/
|       `-- setup_database.sql
|-- .github/workflows/        # CI workflow
|-- render.yaml               # Render blueprint
|-- requirements.txt
`-- run.py
```

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Robust relational database
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## Setup Instructions

### 1. Install PostgreSQL

Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)

### 2. Create Database

```sql
CREATE DATABASE cims_db;
CREATE USER cims_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cims_db TO cims_user;
```

### 3. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows PowerShell: .\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment

Copy `.env.example` to `.env` and update:

```env
DATABASE_URL=postgresql://cims_user:your_password@localhost:5432/cims_db
SECRET_KEY=your-secret-key-here
```

### 6. Apply Database Migrations

```bash
alembic upgrade head
```

### 7. Run Server

```bash
python run.py
```

Server will start at `http://localhost:8000`

### 8. Bootstrap First Admin (One-Time)

`/api/auth/register` is admin-protected. For a brand new database, create the first admin once:

```bash
curl -X POST "http://localhost:8000/api/auth/bootstrap-admin" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin",
    "full_name": "System Admin",
    "role": "admin"
  }'
```

After the first user exists, this endpoint is disabled and returns 403 by design.

## API Endpoints

### Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Teachers API
- `GET /api/teachers/` - List all teachers
- `GET /api/teachers/{id}` - Get teacher by ID
- `POST /api/teachers/` - Create teacher
- `PUT /api/teachers/{id}` - Update teacher
- `DELETE /api/teachers/{id}` - Delete teacher (soft)
- `POST /api/teachers/{id}/restore` - Restore deleted teacher

### Batches API
- `GET /api/batches/` - List all batches
- `GET /api/batches/{id}` - Get batch by ID
- `POST /api/batches/` - Create batch
- `PUT /api/batches/{id}` - Update batch
- `DELETE /api/batches/{id}` - Delete batch (soft)
- `POST /api/batches/{id}/restore` - Restore deleted batch

### Students API
- `GET /api/students/` - List all students
- `GET /api/students/{id}` - Get student by ID
- `GET /api/students/roll/{roll_number}` - Get by roll number
- `POST /api/students/` - Create student
- `PUT /api/students/{id}` - Update student
- `DELETE /api/students/{id}` - Delete student (soft)
- `POST /api/students/{id}/restore` - Restore deleted student

### Fee Records API
- `GET /api/fee-records/` - List all fee records
- `GET /api/fee-records/{id}` - Get fee record by ID
- `GET /api/fee-records/receipt/{receipt_id}` - Get by receipt ID
- `POST /api/fee-records/` - Create fee record

### Attendance API
- `GET /api/attendance/` - List attendance records
- `GET /api/attendance/{id}` - Get attendance by ID
- `POST /api/attendance/` - Create attendance record
- `POST /api/attendance/bulk` - Create bulk attendance

### Sync API
- `POST /api/sync/pull` - Pull changes from server
- `POST /api/sync/push/teachers` - Push teachers to server
- `POST /api/sync/push/batches` - Push batches to server
- `POST /api/sync/push/students` - Push students to server
- `POST /api/sync/push/fee-records` - Push fee records to server
- `POST /api/sync/push/attendance` - Push attendance to server
- `GET /api/sync/status` - Get sync status for device

### Auth API
- `POST /api/auth/bootstrap-admin` - Create first admin user (one-time, only when no users exist)
- `POST /api/auth/login` - Login and get bearer token
- `POST /api/auth/register` - Create user (admin only)
- `GET /api/auth/me` - Get current user

## Sync Strategy

### How Sync Works

1. **Last Sync Timestamp** - Client tracks last successful sync time
2. **Pull Changes** - Client requests all data modified since last sync
3. **Push Changes** - Client sends all local changes to server
4. **Conflict Resolution** - Server timestamp wins (last write wins)

### Sync Flow

```
Mobile App                                Server
    |                                        |
    |-- POST /api/sync/pull --------------->|
    |   (last_sync_timestamp)               |
    |<-- Returns changed data ---------------|
    |                                        |
    |-- POST /api/sync/push/students ------>|
    |   (local changes)                     |
    |<-- Returns created/updated count ------|
```

### Device Tracking

Each record has:
- `device_id` - Which device created/modified
- `last_synced_at` - When it was last synced

This helps in:
- Multi-device scenarios
- Conflict detection
- Audit trails

## Database Schema

### Tables
- `teachers` - Teacher information
- `batches` - Batch/class information
- `students` - Student enrollment data
- `fee_records` - Fee payment transactions
- `attendance` - Daily attendance records
- `sync_logs` - Sync operation logs

All tables include:
- `is_deleted` - Soft delete flag
- `deleted_at` - Deletion timestamp
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `device_id` - Device identifier
- `last_synced_at` - Last sync timestamp

## Testing

### Manual API Testing

Use the Swagger UI at `http://localhost:8000/docs` to test endpoints interactively.

### Example: Create Teacher

```bash
curl -X POST "http://localhost:8000/api/teachers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "subject": "Mathematics",
    "contact_number": "9876543210",
    "salary": 35000,
    "date_of_joining": 1711200000000,
    "device_id": "device_123"
  }'
```

### Example: Pull Sync

```bash
curl -X POST "http://localhost:8000/api/sync/pull" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "device_123",
    "last_sync_timestamp": 0
  }'
```

## Development

### Database Migrations

Apply the current schema to a local database:

```bash
alembic upgrade head
```

If you modify models, generate and review a new migration:

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

The application no longer creates tables at startup. Schema changes should go through Alembic revisions only.

### Running in Development

```bash
python run.py
```

Server auto-reloads on code changes.

## Production Deployment

Render-specific deployment instructions are in [docs/deployment/RENDER_DEPLOYMENT.md](docs/deployment/RENDER_DEPLOYMENT.md).

1. Set `API_RELOAD=False` in `.env`
2. Use production database credentials
3. Set strong `SECRET_KEY`
4. Configure CORS origins
5. Run `alembic upgrade head` as a separate deployment step before starting the app
6. Use a runtime DB user without schema-change permissions
7. Use process manager (PM2, systemd)
8. Set up reverse proxy (nginx)
9. Enable HTTPS

### Ideal Production Migration Flow

1. Create a reviewed migration in CI or during release prep with `alembic revision --autogenerate -m "..."`.
2. Test that migration against a staging database populated with representative data.
3. If the database schema already exists from the old `create_all()` startup behavior, validate that it matches the initial Alembic revision and run `alembic stamp 20260323_000001` once to baseline it without re-creating tables.
4. Back up production before the release.
5. Run `alembic upgrade head` during deployment, before new app instances receive traffic.
6. Start the new application version only after the migration succeeds.
7. Keep downgrade scripts for emergency rollback, but prefer roll-forward fixes for complex production changes.

For production, do not rely on `Base.metadata.create_all()` because it bypasses migration history, review, and controlled rollout.

### Existing Database Baseline

If a database already has these tables because an older app version created them automatically, do not run the initial migration directly against it.

Recommended sequence:

```bash
# Verify the live schema matches the initial revision first.
alembic stamp 20260323_000001

# Future releases then use normal upgrades.
alembic upgrade head
```

Use `stamp` only after you confirm the existing schema matches the migration. `stamp` records migration history; it does not modify tables.

### Render

For deployment on Render, use the dedicated guide in [docs/deployment/RENDER_DEPLOYMENT.md](docs/deployment/RENDER_DEPLOYMENT.md).

## Troubleshooting

### Database Connection Error
- Check PostgreSQL is running
- Verify DATABASE_URL in `.env`
- Test connection: `psql -U cims_user -d cims_db`

### Port Already in Use
- Change `API_PORT` in `.env`
- Kill existing process on port 8000

### Import Errors
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

## Support

For issues or questions, refer to the FastAPI documentation:
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
