"""
JWT token encoding and decoding.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import get_settings

settings = get_settings()


class TokenData(BaseModel):
    """JWT token payload data."""
    username: str
    role: str
    region_id: Optional[str] = None
    territory_id: Optional[str] = None
    db_user: str
    exp: datetime


def create_access_token(
    username: str,
    role: str,
    region_id: Optional[str] = None,
    territory_id: Optional[str] = None,
    db_user: str = "demo_admin"
) -> str:
    """Create a JWT access token."""
    expires = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    
    payload = {
        "sub": username,
        "role": role,
        "region_id": region_id,
        "territory_id": territory_id,
        "db_user": db_user,
        "exp": expires
    }
    
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        
        return TokenData(
            username=payload.get("sub"),
            role=payload.get("role"),
            region_id=payload.get("region_id"),
            territory_id=payload.get("territory_id"),
            db_user=payload.get("db_user", "demo_admin"),
            exp=datetime.fromtimestamp(payload.get("exp"))
        )
    except JWTError:
        return None

