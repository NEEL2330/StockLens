import bcrypt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
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


auth_service = AuthService()
