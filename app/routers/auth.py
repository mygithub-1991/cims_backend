from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import User, UserRole
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    require_role
)
from app.auth_schemas import (
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserUpdate,
    UserResponse,
    ChangePasswordRequest,
    RolePermissions
)

router = APIRouter()


@router.post("/bootstrap-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def bootstrap_admin(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create the first admin user if no active users exist yet."""
    existing_active_user = db.query(User).filter(User.is_deleted == False).first()
    if existing_active_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bootstrap is disabled because users already exist.",
        )

    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=UserRole.ADMIN
        # created_at and updated_at use defaults from model
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # Update last login time
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Create access token
    user_role = user.role if isinstance(user.role, UserRole) else UserRole(user.role)
    access_token = create_access_token(data={"sub": user.username, "role": user_role.value})

    return LoginResponse(
        access_token=access_token,
        user=UserResponse.from_orm(user)
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Register a new user (Admin only)"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Validate role
    try:
        UserRole(user_data.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}",
        )

    # Create user
    requested_role = UserRole(user_data.role)

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=requested_role
        # created_at and updated_at use defaults from model
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    update_data = user_update.model_dump(exclude_unset=True)

    # Users cannot change their own role
    if "role" in update_data:
        del update_data["role"]

    update_data["updated_at"] = datetime.utcnow()

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Password changed successfully"}


@router.get("/users", response_model=list[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Get all users (Admin only)"""
    users = db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Get user by ID (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Update user (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)

    if "role" in update_data and update_data["role"] is not None:
        try:
            update_data["role"] = UserRole(update_data["role"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}",
            )

    update_data["updated_at"] = datetime.utcnow()

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Soft delete user (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "User deleted successfully"}


@router.get("/roles/permissions", response_model=list[RolePermissions])
async def get_role_permissions(current_user: User = Depends(get_current_user)):
    """Get role-based permissions"""
    permissions = [
        RolePermissions(
            role="admin",
            permissions=[
                "manage_users",
                "manage_teachers",
                "manage_students",
                "manage_batches",
                "manage_fees",
                "manage_attendance",
                "view_reports",
                "manage_settings"
            ]
        ),
        RolePermissions(
            role="teacher",
            permissions=[
                "view_students",
                "manage_attendance",
                "view_batches",
                "view_reports"
            ]
        ),
        RolePermissions(
            role="accountant",
            permissions=[
                "view_students",
                "manage_fees",
                "view_reports"
            ]
        ),
        RolePermissions(
            role="reception",
            permissions=[
                "manage_students",
                "view_batches",
                "view_teachers"
            ]
        )
    ]
    return permissions
