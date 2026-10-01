from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate


class AuthService:
    """Authentication and user management business logic."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Securely hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a bcrypt hash."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    @staticmethod
    def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """Generate a signed JWT access token containing minimal payload (sub: user_id, exp)."""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }

        encoded_jwt = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return encoded_jwt

    def register_user(self, db: Session, user_in: UserCreate) -> User:
        """Validate, hash, and persist a new user in the database."""
        normalized_email = user_in.email.strip().lower()

        # Check for duplicate email
        existing_user = db.execute(
            select(User).where(User.email == normalized_email)
        ).scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Hash password securely
        password_hash = self.hash_password(user_in.password)

        # Create and persist new user
        new_user = User(
            name=user_in.name.strip(),
            email=normalized_email,
            password_hash=password_hash,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def authenticate_user(self, db: Session, login_data: LoginRequest) -> TokenResponse:
        """Authenticate user credentials and return a signed JWT token."""
        normalized_email = login_data.email.strip().lower()

        # 1. Find user by email
        user = db.execute(
            select(User).where(User.email == normalized_email)
        ).scalar_one_or_none()

        # 2. Verify existence and password hash
        if not user or not self.verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. Create JWT
        access_token = self.create_access_token(user.id)

        # 4. Return token response
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
        )


auth_service = AuthService()
