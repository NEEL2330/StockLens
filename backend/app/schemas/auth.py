from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema for user login credentials."""
    email: EmailStr = Field(..., description="Registered user email")
    password: str = Field(..., min_length=1, description="Account password")


class TokenResponse(BaseModel):
    """Schema for JWT authentication response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
