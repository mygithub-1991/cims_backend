# Quick Start Guide

Get the CIMS backend running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- PostgreSQL 12+ installed
- Git installed

## Quick Setup

### 1. Install PostgreSQL & Create Database

**Windows:**
```bash
# Download from https://www.postgresql.org/download/windows/
# During installation, remember your postgres password

# After installation, open psql and run:
psql -U postgres

CREATE DATABASE cims_db;
CREATE USER cims_user WITH PASSWORD 'Cims@2024';
GRANT ALL PRIVILEGES ON DATABASE cims_db TO cims_user;
\q
```

**Linux/Mac:**
```bash
sudo -u postgres psql

CREATE DATABASE cims_db;
CREATE USER cims_user WITH PASSWORD 'Cims@2024';
GRANT ALL PRIVILEGES ON DATABASE cims_db TO cims_user;
\q
```

### 2. Setup Python Environment

```bash
# Navigate to backend directory
cd C:\android\cims_backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit .env (use notepad or any editor)
DATABASE_URL=postgresql://cims_user:Cims@2024@localhost:5432/cims_db
SECRET_KEY=change-this-to-a-random-secret-key
```

### 4. Run the Server

```bash
python run.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5. Test the API

Open browser and visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Test with cURL

```bash
# Create a teacher
curl -X POST "http://localhost:8000/api/teachers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Teacher",
    "subject": "Mathematics",
    "contact_number": "9876543210",
    "salary": 35000,
    "date_of_joining": 1711200000000
  }'

# Get all teachers
curl http://localhost:8000/api/teachers/

# Test sync endpoint
curl -X POST "http://localhost:8000/api/sync/pull" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test-device",
    "last_sync_timestamp": 0
  }'
```

## Troubleshooting

### PostgreSQL not running
```bash
# Windows
pg_ctl -D "C:\Program Files\PostgreSQL\14\data" start

# Linux
sudo systemctl start postgresql

# Mac
brew services start postgresql
```

### Port 8000 already in use
```bash
# Change port in .env
API_PORT=8001
```

### Import errors
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. Read [README.md](README.md) for detailed documentation
2. Read [ANDROID_INTEGRATION.md](ANDROID_INTEGRATION.md) for mobile app integration
3. Explore API at http://localhost:8000/docs
4. Start integrating with Android app

## Production Deployment

For production deployment, see README.md section on production configuration.

Key changes needed:
- Set strong SECRET_KEY
- Use production database
- Configure CORS properly
- Set API_RELOAD=False
- Use HTTPS
- Set up reverse proxy (nginx)
