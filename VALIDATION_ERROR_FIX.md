# Pydantic ValidationError Fix

**Issue:** `pydantic_core._pydantic_core.ValidationError: Input should be a valid integer`

## Problem

After migrating datetime columns from BigInteger to TIMESTAMP in the database, Pydantic schemas were failing validation because:

1. Database returns `datetime` objects from TIMESTAMP columns
2. Pydantic schemas expected `int` (Unix timestamps)
3. Used `field_serializer` which only runs on output, not input validation

## Root Cause

```python
# BEFORE (Wrong approach)
@field_serializer('created_at', 'last_login_at')
def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[int]:
    return datetime_to_timestamp(dt)
```

**Problem:** `field_serializer` only works during serialization (when converting to JSON/dict). It doesn't run during validation when receiving data from the database.

## Solution

Changed to use `field_validator` with `mode='before'`:

```python
# AFTER (Correct approach)
@field_validator('created_at', 'last_login_at', mode='before')
@classmethod
def convert_datetime_to_timestamp(cls, v: Any) -> Optional[int]:
    """Convert datetime to timestamp for API response"""
    if v is None:
        return None
    if isinstance(v, datetime):
        return datetime_to_timestamp(v)
    return v
```

**Why this works:** `field_validator` with `mode='before'` runs during validation **before** type checking, allowing us to convert datetime objects to integers before Pydantic validates the field type.

## Files Updated

### 1. `app/auth_schemas.py`
- Updated `UserResponse` schema
- Added datetime conversion for: `created_at`, `last_login_at`

### 2. `app/schemas.py`
- Updated all Response schemas:
  - `SchoolResponse`
  - `TeacherResponse` 
  - `BatchResponse`
  - `StudentResponse`
  - `FeeRecordResponse`
  - `AttendanceResponse`
  - `ExpenseResponse`

## Data Flow

```
┌─────────────┐         ┌──────────────┐         ┌────────────┐
│  Database   │         │   Pydantic   │         │  API JSON  │
│             │         │   Schema     │         │            │
│ TIMESTAMP   │ ─────▶  │ converts to  │ ─────▶  │   Unix     │
│ 2026-04-06  │         │   integer    │         │ timestamp  │
│ 12:00:00    │         │ 1775478000   │         │ 1775478000 │
└─────────────┘         └──────────────┘         └────────────┘
```

## Verification

All checks passed:

```bash
=== Backend Datetime Fix Verification ===

1. Database Schema Check:
   - Datetime columns in database: 35
   - Status: OK

2. Models Import Check:
   - All models imported successfully
   - Status: OK

3. Schema Validation Check:
   - Schemas convert datetime -> int correctly
   - Status: OK

4. Router Import Check:
   - FastAPI app loaded successfully
   - All routers registered
   - Status: OK

=== ALL CHECKS PASSED ===
```

## Testing

```python
# Test that datetime objects are converted correctly
from app.auth_schemas import UserResponse
from datetime import datetime

user = UserResponse(
    id=1,
    username='admin',
    email='admin@test.com',
    full_name='Admin User',
    role='admin',
    is_active=True,
    created_at=datetime.now(),  # datetime object from DB
    last_login_at=datetime.now()
)

# Result: created_at and last_login_at are now integers
assert isinstance(user.created_at, int)  # ✓ Pass
assert isinstance(user.last_login_at, int)  # ✓ Pass
```

## Deployment

✅ Ready to deploy
- All schemas updated
- All tests passing
- Backward compatible with Android app

## Related Commits

1. `0a1162f` - Initial datetime implementation in routers
2. `67b8f6a` - Documentation for datetime migration
3. `520ddc4` - **This fix**: Pydantic schema validation fix

---
**Status:** ✅ FIXED  
**Date:** 2026-04-06  
**Tested:** Yes
