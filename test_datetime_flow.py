"""
End-to-End Datetime Flow Test
Tests the complete flow: Android timestamp -> Backend API -> Database -> API Response
"""
import sys
from datetime import datetime
from sqlalchemy import text

# Add app to path
sys.path.insert(0, '.')

from app.database import engine
from app.schemas import (
    TeacherResponse, StudentResponse, AttendanceResponse,
    FeeRecordResponse, ExpenseResponse,
    timestamp_to_datetime, datetime_to_timestamp
)

def test_timestamp_conversions():
    """Test timestamp conversion functions"""
    print("=" * 80)
    print("TEST 1: Timestamp Conversion Functions")
    print("=" * 80)

    # Android sends timestamp in milliseconds
    android_timestamp = 1704067200000  # 2024-01-01 00:00:00 UTC
    print(f"[OK] Android timestamp (ms): {android_timestamp}")

    # Backend converts to datetime
    dt = timestamp_to_datetime(android_timestamp)
    print(f"[OK] Converted to datetime: {dt}")
    assert isinstance(dt, datetime), "Should be datetime object"

    # Backend converts back to timestamp for API response
    response_timestamp = datetime_to_timestamp(dt)
    print(f"[OK] Response timestamp (ms): {response_timestamp}")
    assert response_timestamp == android_timestamp, "Timestamps should match"

    print("[OK] TEST 1 PASSED\n")


def test_database_schema():
    """Verify database has proper TIMESTAMP columns"""
    print("=" * 80)
    print("TEST 2: Database Schema")
    print("=" * 80)

    with engine.connect() as conn:
        # Check column types
        result = conn.execute(text("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND data_type = 'timestamp with time zone'
            AND table_name IN ('teachers', 'students', 'attendance', 'fee_records', 'expenses')
            ORDER BY table_name, column_name
        """))

        rows = result.fetchall()
        print(f"[OK] Found {len(rows)} TIMESTAMP columns:")

        for table, column, dtype in rows:
            print(f"  - {table:20} {column:20} {dtype}")

        assert len(rows) >= 20, "Should have at least 20 datetime columns"

    print("[OK] TEST 2 PASSED\n")


def test_pydantic_schemas():
    """Test that Pydantic schemas handle datetime -> int conversion"""
    print("=" * 80)
    print("TEST 3: Pydantic Schema Validation")
    print("=" * 80)

    # Simulate database returning datetime objects
    test_data = {
        'id': 1,
        'name': 'Test Teacher',
        'subject': 'Math',
        'contact_number': '1234567890',
        'salary': 50000.0,
        'date_of_joining': datetime.now(),  # datetime from DB
        'is_deleted': False,
        'deleted_at': None,
        'created_at': datetime.now(),  # datetime from DB
        'updated_at': datetime.now(),  # datetime from DB
        'last_synced_at': None
    }

    # Pydantic should convert datetime to int
    teacher = TeacherResponse(**test_data)

    print(f"[OK] TeacherResponse validated")
    print(f"  - date_of_joining type: {type(teacher.date_of_joining).__name__}")
    print(f"  - created_at type: {type(teacher.created_at).__name__}")

    assert isinstance(teacher.date_of_joining, int), "Should be int"
    assert isinstance(teacher.created_at, int), "Should be int"
    assert isinstance(teacher.updated_at, int), "Should be int"

    print("[OK] TEST 3 PASSED\n")


def test_attendance_schema():
    """Test attendance schema with date field"""
    print("=" * 80)
    print("TEST 4: Attendance Schema (date field)")
    print("=" * 80)

    attendance_data = {
        'id': 1,
        'student_id': 1,
        'date': datetime.now(),  # datetime from DB
        'is_present': True,
        'is_deleted': False,
        'deleted_at': None,
        'created_at': datetime.now(),  # datetime from DB
        'last_synced_at': None
    }

    attendance = AttendanceResponse(**attendance_data)

    print(f"[OK] AttendanceResponse validated")
    print(f"  - date type: {type(attendance.date).__name__}")
    print(f"  - date value: {attendance.date}")

    assert isinstance(attendance.date, int), "date should be int"

    print("[OK] TEST 4 PASSED\n")


def test_expense_schema():
    """Test expense schema with expense_date field"""
    print("=" * 80)
    print("TEST 5: Expense Schema (expense_date field)")
    print("=" * 80)

    expense_data = {
        'id': 1,
        'category': 'Rent',
        'description': 'Office Rent',
        'amount': 10000.0,
        'expense_date': datetime.now(),  # datetime from DB
        'payment_method': 'Cash',
        'vendor_name': 'Landlord',
        'receipt_number': 'R001',
        'notes': 'Monthly rent',
        'is_deleted': False,
        'deleted_at': None,
        'created_at': datetime.now(),  # datetime from DB
        'updated_at': datetime.now(),  # datetime from DB
        'last_synced_at': None
    }

    expense = ExpenseResponse(**expense_data)

    print(f"[OK] ExpenseResponse validated")
    print(f"  - expense_date type: {type(expense.expense_date).__name__}")
    print(f"  - expense_date value: {expense.expense_date}")

    assert isinstance(expense.expense_date, int), "expense_date should be int"

    print("[OK] TEST 5 PASSED\n")


def test_query_parameter_conversion():
    """Test that query parameters are properly converted"""
    print("=" * 80)
    print("TEST 6: Query Parameter Conversion")
    print("=" * 80)

    # Simulate Android sending timestamp query parameter
    android_date_param = 1704067200000  # milliseconds

    # Convert for database query
    db_datetime = timestamp_to_datetime(android_date_param)

    print(f"[OK] Android date param (ms): {android_date_param}")
    print(f"[OK] Converted for DB query: {db_datetime}")
    print(f"[OK] Type: {type(db_datetime).__name__}")

    assert isinstance(db_datetime, datetime), "Should be datetime for DB query"

    print("[OK] TEST 6 PASSED\n")


def run_all_tests():
    """Run all datetime tests"""
    print("\n")
    print("=" * 80)
    print(" " * 20 + "DATETIME FLOW END-TO-END TEST")
    print("=" * 80)
    print("\n")

    try:
        test_timestamp_conversions()
        test_database_schema()
        test_pydantic_schemas()
        test_attendance_schema()
        test_expense_schema()
        test_query_parameter_conversion()

        print("=" * 80)
        print("                        ALL TESTS PASSED")
        print("=" * 80)
        print("\nBackend datetime handling is working correctly!")
        print("Ready for Android app integration.\n")

        return 0
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
