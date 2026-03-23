# Render Deployment Guide

This document describes the recommended production deployment flow for this FastAPI backend on Render.

## Target Architecture

- Render Web Service for the FastAPI app
- Render Postgres for the production database
- Alembic migrations run before each deploy
- Runtime app process starts only after migrations succeed

## Recommended Render Setup

Use:

- A `Web Service` for the application
- A managed `Postgres` instance for the database
- A paid web service plan if you want to use Render's `Pre-Deploy Command`
- A linked GitHub repository for automatic deploys

Reason:

- Render's pre-deploy step is the right place for `alembic upgrade head`
- That keeps schema changes out of application startup
- GitHub Actions provides the deployment gate before Render starts a deploy

## Production-Grade Automation Model

The recommended automation chain for this repo is:

1. Push code to GitHub.
2. GitHub Actions runs CI.
3. Render waits for CI checks to pass.
4. Render builds the service.
5. Render runs `python -m alembic upgrade head` in pre-deploy.
6. Render starts the new instance and health-checks `/health`.
7. Traffic switches only if the new instance is healthy.

This repo now includes the files needed for that flow:

- [../../render.yaml](../../render.yaml)
- [../../.github/workflows/ci.yml](../../.github/workflows/ci.yml)

## Before You Deploy

Make sure the repo already contains:

- [../../alembic.ini](../../alembic.ini)
- [../../alembic/env.py](../../alembic/env.py)
- [../../alembic/versions/20260323_000001_initial_schema.py](../../alembic/versions/20260323_000001_initial_schema.py)

Also make sure you have removed any `Base.metadata.create_all(...)` startup logic, which has already been done in [../../app/main.py](../../app/main.py).

## GitHub To Render Automation Setup

### 1. Push This Repository To GitHub

Your Render service should be linked to the same repository that contains:

- [../../render.yaml](../../render.yaml)
- [../../.github/workflows/ci.yml](../../.github/workflows/ci.yml)

### 2. Create The Service From The Blueprint

In Render:

1. Open `New +`.
2. Choose `Blueprint`.
3. Select your GitHub repository.
4. Review the resources defined in [../../render.yaml](../../render.yaml).
5. Fill in any prompted values such as `ALLOWED_ORIGINS`.
6. Create the resources.

The blueprint is configured with:

- `autoDeployTrigger: checksPass`
- `preDeployCommand: python -m alembic upgrade head`
- `healthCheckPath: /health`

That means Render will deploy only after GitHub Actions reports success.

### 3. Keep Auto-Deploy On Checks Pass

This is the production-grade setting for Render when your source of truth is GitHub.

Reason:

- broken commits do not deploy
- schema validation runs in CI before Render starts a deployment
- Render still applies migrations right before startup, which keeps database state aligned with the deployed code

## Option 1: Deploy From The Render Dashboard

Create a new `Web Service` and use these values:

- Runtime: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Pre-Deploy Command: `python -m alembic upgrade head`
- Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`

Why this start command:

- It uses Render's assigned `$PORT`
- It avoids depending on local-only startup habits
- It starts the exact ASGI app object used in development

If you are using the blueprint in [../../render.yaml](../../render.yaml), you do not need to enter these values manually after the initial setup.

## If Pre-Deploy Is Not Available

Render's pre-deploy command is the cleanest option for production, but it is not available on every plan.

If you do not have pre-deploy available, use this fallback:

1. Put the service in maintenance mode or otherwise stop traffic.
2. Run migrations manually against the production database:

```bash
python -m alembic upgrade head
```

3. Trigger the application deploy.
4. Verify `/health` before restoring traffic.

Do not move migrations back into application startup just to work around plan limitations.

## Environment Variables

Set these in Render:

- `DATABASE_URL`: set from your Render Postgres connection string
- `SECRET_KEY`: generate a strong random secret
- `ALGORITHM`: `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
- `API_RELOAD`: `False`
- `ALLOWED_ORIGINS`: your frontend origins, comma-separated

Example:

```env
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_RELOAD=False
ALLOWED_ORIGINS=https://your-frontend.example.com,https://admin.your-frontend.example.com
```

Notes:

- Do not use `localhost` in `DATABASE_URL` on Render
- Do not leave `SECRET_KEY` at the default value
- Keep `API_RELOAD=False` in production

## Render Postgres Connection

If you create the database in Render, use the Render Postgres connection string for `DATABASE_URL`.

Prefer the internal Render connection string when both app and database are on Render, because it stays on Render's network path.

## First Production Deploy

For a brand new database:

1. Create the Render Postgres instance.
2. Set `DATABASE_URL` on the web service.
3. Deploy the web service.
4. Let the pre-deploy command run `python -m alembic upgrade head`.
5. Confirm the app becomes healthy at `/health`.

## Initialize First Admin User

`POST /api/auth/register` is admin-protected. After a brand new deployment, create the first admin once with:

```bash
curl -X POST "https://<your-render-service>.onrender.com/api/auth/bootstrap-admin" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin",
    "full_name": "System Admin",
    "role": "admin"
  }'
```

Then login to obtain a bearer token:

```bash
curl -X POST "https://<your-render-service>.onrender.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'
```

After the first user exists, `/api/auth/bootstrap-admin` is disabled and returns 403 by design.

## Existing Database Created By Older App Versions

If your production database already has tables because a previous app version used automatic table creation, do not run the initial migration blindly.

Use this flow:

1. Compare the live schema to [../../alembic/versions/20260323_000001_initial_schema.py](../../alembic/versions/20260323_000001_initial_schema.py).
2. If it matches, baseline the database once with:

```bash
python -m alembic stamp 20260323_000001
```

3. After that, all future deploys should use:

```bash
python -m alembic upgrade head
```

Important:

- `stamp` writes migration history only
- `stamp` does not create or alter tables

## Recommended Production Deployment Flow

For each release:

1. Generate a migration locally:

```bash
python -m alembic revision --autogenerate -m "describe change"
```

2. Review the migration file manually.
3. Apply it to staging and verify the app still boots.
4. Back up production.
5. Push the release.
6. Let GitHub Actions pass.
7. Let Render run the pre-deploy migration.
8. Let Render start the new app instance only after migration succeeds.
9. Verify `/health` and a few core endpoints.

## What The CI Pipeline Validates

The GitHub Actions workflow in [../../.github/workflows/ci.yml](../../.github/workflows/ci.yml) currently checks:

- dependency installation
- dependency consistency via `pip check`
- Python module compilation
- Alembic migration rendering in offline mode
- FastAPI application import

That is a pragmatic production baseline for this repository even though it does not yet include application tests.

As you add tests later, extend the same workflow instead of creating a separate gate.

## Minimal Operational Checklist

After each deploy, verify:

- `GET /health` returns `200`
- Swagger loads at `/docs`
- The app can read from the database
- Render logs show successful startup

## Health Check

Set Render's health check path to:

```text
/health
```

This app already exposes that endpoint in [../../app/main.py](../../app/main.py).

## Logging And Failure Behavior

If the build fails:

- Render does not deploy the new version

If the pre-deploy migration fails:

- Render does not start the new version
- The previous successful deployment keeps serving traffic

If the app fails health checks:

- Render will not cut traffic over to the failed instance

That is the correct behavior for schema-first deploy safety.

## Optional: render.yaml Blueprint Example

This repo already includes a production-ready starting point in [../../render.yaml](../../render.yaml):

```yaml
services:
  - type: web
    name: cims-backend
    runtime: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    preDeployCommand: python -m alembic upgrade head
    startCommand: python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: cims-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ALGORITHM
        value: HS256
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: "30"
      - key: API_RELOAD
        value: "False"
      - key: ALLOWED_ORIGINS
        sync: false

databases:
  - name: cims-db
    plan: basic-256mb
    databaseName: cims_db
    user: cims_user
```

Notes about this blueprint:

- `DATABASE_URL` is sourced from the Render Postgres instance
- `SECRET_KEY` is generated once by Render
- `ALLOWED_ORIGINS` is marked `sync: false` so you can enter the real value in the dashboard during creation

## Security Notes For Production

- Restrict `ALLOWED_ORIGINS` to real frontend domains only
- Keep migration privileges out of the long-running application account if you later split deploy and runtime identities
- Rotate secrets if they were ever committed or exposed
- Use Render-managed TLS or a custom domain with HTTPS enabled

## Common Mistakes

- Using `python run.py` without making sure the service binds to Render's assigned port
- Forgetting to run migrations before startup
- Pointing `DATABASE_URL` at `localhost`
- Leaving `API_RELOAD=True` in production
- Using the old auto-created schema without baselining Alembic

## Recommended First Render Deployment For This Repo

Use this exact setup first:

- Build Command: `pip install -r requirements.txt`
- Pre-Deploy Command: `python -m alembic upgrade head`
- Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`

If you want, the next step can be adding a real `render.yaml` to the repo so Render can provision the web service and database from source control instead of dashboard clicks.