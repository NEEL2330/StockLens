from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class WatchlistBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20, description="Stock ticker symbol (e.g., RELIANCE, TCS)")

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        return v.strip().upper()


class WatchlistCreate(WatchlistBase):
    """Schema for adding a stock symbol to a user's watchlist."""
    pass


class WatchlistResponse(BaseModel):
    """Schema for watchlist entry output."""
    id: int
    user_id: int
    symbol: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
