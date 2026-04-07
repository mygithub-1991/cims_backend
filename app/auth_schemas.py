from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Any
from datetime import datetime

# Import IST timezone utilities
from app.utils.timezone import datetime_to_timestamp


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str = "reception"  # admin, teacher, accountant, reception


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: int = Field(..., description="Account creation timestamp (Unix milliseconds, IST)")
    last_login_at: Optional[int] = Field(None, description="Last login timestamp (Unix milliseconds, IST)")

    @field_validator('created_at', 'last_login_at', mode='before')
    @classmethod
    def convert_datetime_to_timestamp(cls, v: Any) -> Optional[int]:
        """Convert datetime to timestamp for API response"""
        if v is None:
            return None
        if isinstance(v, datetime):
            return datetime_to_timestamp(v)
        return v

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class RolePermissions(BaseModel):
    role: str
    permissions: list[str]
