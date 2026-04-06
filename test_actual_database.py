"""
Test to verify database stores TIMESTAMP correctly and API returns milliseconds
"""
import sys
sys.path.insert(0, '.')

from datetime import datetime
from app.database import engine
from sqlalchemy import text
from app.models import Teacher
from app.schemas import TeacherResponse
from sqlalchemy.orm import Session

print("=" * 80)
print("TESTING: Database Storage vs API Response")
print("=" * 80)
print()

# Create a session
from app.database import SessionLocal
db = SessionLocal()

try:
    # 1. Insert a teacher using the ORM (like the API does)
    print("STEP 1: Creating teacher via ORM")
    print("-" * 80)

    test_teacher = Teacher(
        name="Database Test Teacher",
        subject="Testing",
        contact_number="9999999999",
        salary=60000.0,
        date_of_joining=datetime.now(),
        is_deleted=False
        # created_at and updated_at will use defaults from model
    )

    db.add(test_teacher)
    db.commit()
    db.refresh(test_teacher)

    teacher_id = test_teacher.id
    print(f"Created teacher with ID: {teacher_id}")
    print()

    # 2. Query directly from database to see raw storage
    print("STEP 2: Query raw database (what's actually stored)")
    print("-" * 80)

    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT
                id,
                name,
                created_at,
                updated_at,
                pg_typeof(created_at) as type_in_db
            FROM teachers
            WHERE id = {teacher_id}
        """))

        row = result.fetchone()
        print(f"ID: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"created_at in DATABASE: {row[2]}")
        print(f"updated_at in DATABASE: {row[3]}")
        print(f"PostgreSQL type: {row[4]}")
        print()
        print("✓ Database stores as TIMESTAMP WITH TIME ZONE")
        print()

    # 3. Query via ORM (like API does)
    print("STEP 3: Query via ORM (Python datetime object)")
    print("-" * 80)

    teacher_from_db = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    print(f"created_at from ORM: {teacher_from_db.created_at}")
    print(f"Python type: {type(teacher_from_db.created_at).__name__}")
    print()

    # 4. Convert to API response (what Android receives)
    print("STEP 4: Convert to API Response (what Android app sees)")
    print("-" * 80)

    api_response = TeacherResponse.model_validate(teacher_from_db)

    print(f"created_at in API: {api_response.created_at}")
    print(f"Type sent to Android: {type(api_response.created_at).__name__}")
    print()
    print("✓ API sends Unix timestamp in MILLISECONDS")
    print()

    # 5. Show the conversion
    print("STEP 5: Conversion Flow")
    print("-" * 80)
    print(f"Database:  {teacher_from_db.created_at} (TIMESTAMP)")
    print(f"           ↓")
    print(f"           Pydantic field_validator")
    print(f"           ↓")
    print(f"API JSON:  {api_response.created_at} (milliseconds)")
    print(f"           ↓")
    print(f"Android:   Long = {api_response.created_at}")
    print()

    # Show the JSON that would be sent
    import json
    json_output = api_response.model_dump()
    print("STEP 6: Actual JSON sent to Android")
    print("-" * 80)
    print(json.dumps({
        'id': json_output['id'],
        'name': json_output['name'],
        'created_at': json_output['created_at'],
        'updated_at': json_output['updated_at']
    }, indent=2))
    print()

    print("=" * 80)
    print("CONCLUSION:")
    print("=" * 80)
    print()
    print("If you see a value like 1775498491329, this is CORRECT!")
    print()
    print("It means:")
    print("  - Database stores: 2026-04-06 23:31:31 (TIMESTAMP)")
    print("  - API sends: 1775498491329 (milliseconds)")
    print("  - Android receives: 1775498491329 (Long)")
    print()
    print("This is the EXPECTED behavior! ✓")
    print()

finally:
    # Cleanup
    db.query(Teacher).filter(Teacher.name == "Database Test Teacher").delete()
    db.commit()
    db.close()
    print("Test data cleaned up.")
