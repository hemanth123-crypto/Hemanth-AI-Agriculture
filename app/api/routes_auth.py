"""
app/api/routes_auth.py
Authentication API routes for login, user registration (sign-up), and session verification.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel, Field

from app.auth.database import authenticate_user, create_user, get_user_by_email
from app.auth.security import create_access_token, decode_access_token
from app.utils.logging import get_logger

logger = get_logger("routes_auth")

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Account password")


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2, description="Full name of user")
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password with minimum 6 characters")
    role: Optional[str] = Field("specialist", description="User role (specialist, agronomist, officer)")


class UserResponse(BaseModel):
    email: str
    name: str
    role: str


class AuthSuccessResponse(BaseModel):
    success: bool = True
    token: str
    user: UserResponse
    message: Optional[str] = None


@router.post("/login", response_model=AuthSuccessResponse)
async def login(payload: LoginRequest):
    """Authenticate user credentials and return signed JWT session token."""
    email = payload.email.strip()
    password = payload.password

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are both required."
        )

    user = authenticate_user(email, password)
    if not user:
        logger.warning(f"Failed login attempt for email: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Verify your credentials or create an account."
        )

    token = create_access_token({
        "sub": user["email"],
        "name": user["name"],
        "role": user["role"]
    })

    logger.info(f"Successful login for user: {user['email']}")
    return AuthSuccessResponse(
        success=True,
        token=token,
        user=UserResponse(
            email=user["email"],
            name=user["name"],
            role=user["role"]
        ),
        message="Login successful."
    )


@router.post("/signup", response_model=AuthSuccessResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest):
    """Register a new user account, hash credentials, and return access token."""
    name = payload.name.strip()
    email = payload.email.strip()
    password = payload.password
    role = payload.role.strip() if payload.role else "specialist"

    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Full name is required.")
    if not email or "@" not in email or "." not in email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A valid email address is required.")
    if len(password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 6 characters.")
    if role.lower() == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access must be assigned by a system administrator.")

    try:
        user = create_user(email=email, password=password, name=name, role=role)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error during user registration: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error during account registration.")

    token = create_access_token({
        "sub": user["email"],
        "name": user["name"],
        "role": user["role"]
    })

    logger.info(f"New user registered: {user['email']}")
    return AuthSuccessResponse(
        success=True,
        token=token,
        user=UserResponse(
            email=user["email"],
            name=user["name"],
            role=user["role"]
        ),
        message="Account registered successfully."
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Validate bearer token and return currently authenticated user info."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing or invalid.")

    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired authentication token.")

    email = payload.get("sub")
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return UserResponse(
        email=user["email"],
        name=user["name"],
        role=user["role"]
    )
