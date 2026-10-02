"""Services package for StockLens business logic."""
from app.services.auth_service import AuthService, auth_service
from app.services.watchlist_service import WatchlistService, watchlist_service

__all__ = ["AuthService", "auth_service", "WatchlistService", "watchlist_service"]
