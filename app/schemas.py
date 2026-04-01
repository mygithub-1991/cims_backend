from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# School Schemas
class SchoolBase(BaseModel):
    school_name: str
    address: str
    pincode: str


class SchoolCreate(SchoolBase):
    device_id: Optional[str] = None


class SchoolUpdate(BaseModel):
    school_name: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[int] = None
    updated_at: Optional[int] = None


class SchoolResponse(SchoolBase):
    id: int
    is_deleted: bool
    deleted_at: Optional[int]
    created_at: int
    updated_at: int
    last_synced_at: Optional[int]

    class Config:
        from_attributes = True


# Teacher Schemas
class TeacherBase(BaseModel):
    name: str
    subject: str
    contact_number: str
    salary: float
    date_of_joining: int


class TeacherCreate(TeacherBase):
    device_id: Optional[str] = None


class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    contact_number: Optional[str] = None
    salary: Optional[float] = None
    date_of_joining: Optional[int] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[int] = None
    updated_at: Optional[int] = None


class TeacherResponse(TeacherBase):
    id: int
    is_deleted: bool
    deleted_at: Optional[int]
    created_at: int
    updated_at: int
    last_synced_at: Optional[int]

    class Config:
        from_attributes = True


# Batch Schemas
class BatchBase(BaseModel):
    name: str
    time: str
    teacher_id: int


class BatchCreate(BatchBase):
    device_id: Optional[str] = None


class BatchUpdate(BaseModel):
    name: Optional[str] = None
    time: Optional[str] = None
    teacher_id: Optional[int] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[int] = None
    updated_at: Optional[int] = None


class BatchResponse(BatchBase):
    id: int
    is_deleted: bool
    deleted_at: Optional[int]
    created_at: int
    updated_at: int
    last_synced_at: Optional[int]

    class Config:
        from_attributes = True


# Student Schemas
class StudentBase(BaseModel):
    roll_number: str
    name: str
    contact_number: str
    total_fees: float
    paid_fees: float = 0.0
    batch_id: int
    payment_mode: str
    installment_type: Optional[str] = None
    referred_by: Optional[str] = None
    board: Optional[str] = None
    school_id: Optional[int] = None


class StudentCreate(StudentBase):
    device_id: Optional[str] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    contact_number: Optional[str] = None
    total_fees: Optional[float] = None
    paid_fees: Optional[float] = None
    batch_id: Optional[int] = None
    payment_mode: Optional[str] = None
    installment_type: Optional[str] = None
    referred_by: Optional[str] = None
    board: Optional[str] = None
    school_id: Optional[int] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[int] = None
    updated_at: Optional[int] = None


class StudentResponse(StudentBase):
    id: int
    is_deleted: bool
    deleted_at: Optional[int]
    created_at: int
    updated_at: int
    last_synced_at: Optional[int]

    class Config:
        from_attributes = True


# FeeRecord Schemas
class FeeRecordBase(BaseModel):
    student_id: int
    amount_paid: float
    payment_method: str
    date: int
    receipt_id: str
    remarks: Optional[str] = None


class FeeRecordCreate(FeeRecordBase):
    device_id: Optional[str] = None


class FeeRecordResponse(FeeRecordBase):
    id: int
    is_deleted: bool
    deleted_at: Optional[int]
    created_at: int
    last_synced_at: Optional[int]

    class Config:
        from_attributes = True


# Attendance Schemas
class AttendanceBase(BaseModel):
    student_id: int
    date: int
    is_present: bool


class AttendanceCreate(AttendanceBase):
    device_id: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    id: int
    is_deleted: bool
    deleted_at: Optional[int]
    created_at: int
    last_synced_at: Optional[int]

    class Config:
        from_attributes = True


# Sync Schemas
class SyncRequest(BaseModel):
    device_id: str
    last_sync_timestamp: int  # Client's last sync time


class SyncData(BaseModel):
    schools: List[SchoolResponse] = []
    teachers: List[TeacherResponse] = []
    batches: List[BatchResponse] = []
    students: List[StudentResponse] = []
    fee_records: List[FeeRecordResponse] = []
    attendance: List[AttendanceResponse] = []
    expenses: List[ExpenseResponse] = []


class SyncResponse(BaseModel):
    success: bool
    message: str
    server_timestamp: int
    data: SyncData


# Bulk operations for sync
class BulkSchoolCreate(BaseModel):
    schools: List[SchoolCreate]


class BulkTeacherCreate(BaseModel):
    teachers: List[TeacherCreate]


class BulkBatchCreate(BaseModel):
    batches: List[BatchCreate]


class BulkStudentCreate(BaseModel):
    students: List[StudentCreate]


class BulkFeeRecordCreate(BaseModel):
    fee_records: List[FeeRecordCreate]


class BulkAttendanceCreate(BaseModel):
    attendance: List[AttendanceCreate]


# Expense Schemas
class ExpenseBase(BaseModel):
    category: str
    description: str
    amount: float
    expense_date: int
    payment_method: str
    vendor_name: Optional[str] = None
    receipt_number: Optional[str] = None
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    device_id: Optional[str] = None


class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    expense_date: Optional[int] = None
    payment_method: Optional[str] = None
    vendor_name: Optional[str] = None
    receipt_number: Optional[str] = None
    notes: Optional[str] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[int] = None
    updated_at: Optional[int] = None


class ExpenseResponse(ExpenseBase):
    id: int
    is_deleted: bool
    deleted_at: Optional[int]
    created_at: int
    updated_at: int
    last_synced_at: Optional[int]

    class Config:
        from_attributes = True


class BulkExpenseCreate(BaseModel):
    expenses: List[ExpenseCreate]
