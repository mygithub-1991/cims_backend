# Timezone Handling Options

## Current Status: UTC ✅ (Recommended)

**What's happening now:**
- Database stores: `2026-04-06 18:01:31+00:00` (UTC)
- Backend uses: `datetime.utcnow()`
- Android sends/receives: Unix timestamps (always UTC-based)

**This is CORRECT and follows best practices!**

---

## Option 1: Keep UTC (Recommended) ✅

**Pros:**
- Industry standard
- No timezone conversion bugs
- Works globally if you expand
- Android timestamps are UTC-based anyway
- Easy to convert to any timezone for display

**Cons:**
- Need to convert to IST for display in UI

**Implementation:**
Already done! No changes needed.

**Display in IST:**
```python
# In reports or UI, convert to IST when displaying
from datetime import timezone, timedelta

ist = timezone(timedelta(hours=5, minutes=30))
ist_time = utc_time.astimezone(ist)
```

---

## Option 2: Store in IST (Not Recommended) ❌

**Pros:**
- Database shows times in your local timezone
- Easier for manual SQL queries

**Cons:**
- Non-standard approach
- Issues if you expand to other regions
- Android timestamps are UTC-based (conversion overhead)
- Confusing for developers
- DST issues if India ever implements it

**Implementation if you really want it:**

### 1. Update models.py
```python
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

# In models.py, change all defaults
created_at = Column(DateTime(timezone=True), nullable=False, 
                   default=lambda: datetime.now(IST))
updated_at = Column(DateTime(timezone=True), nullable=False, 
                   default=lambda: datetime.now(IST), 
                   onupdate=lambda: datetime.now(IST))
```

### 2. Update all routers
```python
# Replace all datetime.utcnow() with:
from datetime import timezone, timedelta
IST = timezone(timedelta(hours=5, minutes=30))

# Instead of datetime.utcnow()
datetime.now(IST)
```

### 3. Update timestamp conversion
```python
# In schemas.py
def timestamp_to_datetime(ts: Optional[int]) -> Optional[datetime]:
    """Convert Unix timestamp to IST datetime"""
    if ts is None:
        return None
    utc_dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    ist = timezone(timedelta(hours=5, minutes=30))
    return utc_dt.astimezone(ist)
```

---

## Option 3: Hybrid Approach (Recommended for Display) ✅

**Best of both worlds:**
- Store in UTC (database)
- Convert to IST for display (UI/Reports)

**Implementation:**

### Add timezone utility
```python
# app/utils/timezone.py
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

def utc_to_ist(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to IST"""
    return utc_dt.astimezone(IST)

def ist_to_utc(ist_dt: datetime) -> datetime:
    """Convert IST datetime to UTC"""
    return ist_dt.astimezone(timezone.utc)

def format_ist(dt: datetime) -> str:
    """Format datetime in IST for display"""
    ist_dt = utc_to_ist(dt)
    return ist_dt.strftime("%d-%m-%Y %I:%M %p IST")
```

### Use in reports/responses
```python
# When generating reports
from app.utils.timezone import format_ist

report_data = {
    "created_at_display": format_ist(record.created_at)
    # Database still stores UTC, just display in IST
}
```

---

## Android App Considerations

### Current (Correct):
```kotlin
// Android always works with UTC timestamps
val timestamp = System.currentTimeMillis()  // UTC-based
```

### If you store IST in database:
```kotlin
// Would need to convert - NOT RECOMMENDED
val istOffset = 5.5 * 60 * 60 * 1000  // 5:30 in milliseconds
val istTimestamp = System.currentTimeMillis() + istOffset.toLong()
// This is WRONG - causes issues
```

### For Display in Android:
```kotlin
// Convert timestamp to IST for display
val sdf = SimpleDateFormat("dd-MM-yyyy hh:mm a", Locale.getDefault())
sdf.timeZone = TimeZone.getTimeZone("Asia/Kolkata")
val istTime = sdf.format(Date(timestamp))
```

---

## Recommendation: Keep UTC ✅

**Keep the current implementation (UTC storage) because:**

1. ✅ Industry best practice
2. ✅ Android timestamps are UTC-based
3. ✅ No conversion errors
4. ✅ Works globally
5. ✅ Easy to display in any timezone

**For IST display:**
- Add helper functions to convert UTC → IST when displaying
- Keep database in UTC
- Android app shows times in IST using `SimpleDateFormat` with IST timezone

---

## Quick Fix for IST Display

If you just want to see times in IST when querying database:

```sql
-- Instead of:
SELECT created_at FROM users;

-- Use:
SELECT created_at AT TIME ZONE 'Asia/Kolkata' as created_at_ist 
FROM users;
```

This converts on-the-fly without changing storage!

---

## Summary

| Aspect | Current (UTC) | Alternative (IST) |
|--------|--------------|-------------------|
| Storage | UTC ✅ | IST ❌ |
| Android compatibility | Perfect ✅ | Needs conversion ❌ |
| Global expansion | Easy ✅ | Difficult ❌ |
| Best practice | Yes ✅ | No ❌ |
| Display conversion | Easy ✅ | Not needed |

**Verdict: Keep UTC storage, convert to IST for display only** ✅
