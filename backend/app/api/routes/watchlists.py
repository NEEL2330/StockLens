from typing import List

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.watchlist import WatchlistCreate, WatchlistResponse
from app.services.watchlist_service import watchlist_service

router = APIRouter()


@router.get(
    "",
    response_model=List[WatchlistResponse],
    status_code=status.HTTP_200_OK,
    summary="Get user watchlist",
    description="Retrieve all stock symbols saved in the authenticated user's watchlist.",
)
def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return watchlist_service.get_user_watchlist(db, current_user.id)


@router.post(
    "",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add stock to watchlist",
    description="Add a new stock ticker symbol to the authenticated user's watchlist.",
)
def add_to_watchlist(
    watchlist_in: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return watchlist_service.add_to_watchlist(db, current_user.id, watchlist_in)


@router.delete(
    "/{watchlist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove stock from watchlist",
    description="Delete a stock item from the authenticated user's watchlist.",
)
def remove_from_watchlist(
    watchlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    watchlist_service.remove_from_watchlist(db, current_user.id, watchlist_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
