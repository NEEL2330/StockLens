from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.watchlist import Watchlist
from app.schemas.watchlist import WatchlistCreate


class WatchlistService:
    """Business logic for user stock watchlist management."""

    def get_user_watchlist(self, db: Session, user_id: int) -> List[Watchlist]:
        """Retrieve all watchlist items for a specific user, ordered by newest first."""
        return db.execute(
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .order_by(Watchlist.created_at.desc())
        ).scalars().all()

    def add_to_watchlist(self, db: Session, user_id: int, watchlist_in: WatchlistCreate) -> Watchlist:
        """Add a stock symbol to the user's watchlist with duplicate prevention."""
        symbol = watchlist_in.symbol.strip().upper()

        # Check for duplicate symbol in this user's watchlist
        existing = db.execute(
            select(Watchlist).where(
                Watchlist.user_id == user_id,
                Watchlist.symbol == symbol,
            )
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock '{symbol}' is already in your watchlist",
            )

        # Create and persist new watchlist item
        watchlist_item = Watchlist(
            user_id=user_id,
            symbol=symbol,
        )
        db.add(watchlist_item)
        db.commit()
        db.refresh(watchlist_item)
        return watchlist_item

    def remove_from_watchlist(self, db: Session, user_id: int, watchlist_id: int) -> None:
        """Delete a watchlist item, ensuring ownership verification."""
        item = db.get(Watchlist, watchlist_id)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watchlist item not found",
            )

        # Enforce security: users can only delete their own items
        if item.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this watchlist item",
            )

        db.delete(item)
        db.commit()


watchlist_service = WatchlistService()
