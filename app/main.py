from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, schools, teachers, batches, students, fee_records, attendance, sync

app = FastAPI(
    title="CIMS Backend API",
    description="Coaching Institute Management System - Backend API",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(schools.router, prefix="/api/schools", tags=["Schools"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["Teachers"])
app.include_router(batches.router, prefix="/api/batches", tags=["Batches"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(fee_records.router, prefix="/api/fee-records", tags=["Fee Records"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(sync.router, prefix="/api/sync", tags=["Sync"])


@app.get("/")
def read_root():
    return {
        "message": "CIMS Backend API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
