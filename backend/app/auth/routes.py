"""
Authentication routes.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from app.config import get_settings
from app.auth.jwt import create_access_token, TokenData
from app.auth.middleware import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


class LoginRequest(BaseModel):
    """Login request body."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response with JWT token."""
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    region_id: str | None = None
    territory_id: str | None = None


class UserResponse(BaseModel):
    """Current user information."""
    username: str
    role: str
    region_id: str | None = None
    territory_id: str | None = None


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    Demo credentials:
    - territory_manager_1 / territory123
    - regional_manager_1 / regional123
    - demo_admin / admin123
    """
    
    user_config = settings.demo_users.get(request.username)
    
    if user_config is None or user_config["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    token = create_access_token(
        username=request.username,
        role=user_config["role"],
        region_id=user_config.get("region_id"),
        territory_id=user_config.get("territory_id"),
        db_user=user_config.get("db_user", "demo_admin")
    )
    
    return LoginResponse(
        access_token=token,
        username=request.username,
        role=user_config["role"],
        region_id=user_config.get("region_id"),
        territory_id=user_config.get("territory_id")
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: TokenData = Depends(get_current_user)):
    """Get current authenticated user information."""
    
    return UserResponse(
        username=user.username,
        role=user.role,
        region_id=user.region_id,
        territory_id=user.territory_id
    )

