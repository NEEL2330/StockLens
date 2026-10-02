from typing import Any, Dict, List, Optional
import httpx
from fastapi import HTTPException, status

from app.config import settings


class FMPClient:
    """Dedicated asynchronous HTTP client for Financial Modeling Prep (FMP) API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 10.0,
    ):
        self.base_url = (base_url or settings.FMP_BASE_URL).rstrip("/")
        self.api_key = api_key if api_key is not None else settings.FMP_API_KEY
        self.timeout = timeout

    def _normalize_indian_symbol(self, symbol: str) -> str:
        """Helper to ensure Indian equities have proper exchange suffix if needed.
        
        If symbol already has .NS or .BO suffix, preserve it; otherwise return as-is.
        """
        clean_symbol = symbol.strip().upper()
        return clean_symbol

    async def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute async HTTP GET request to FMP with standardized timeout and error handling."""
        if not self.api_key:
            # Handle case where user has not provided FMP API key yet
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="FMP_API_KEY is not configured in .env",
            )

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        query_params = {"apikey": self.api_key}
        if params:
            query_params.update(params)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=query_params)

                if response.status_code == 401 or response.status_code == 403:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Market data provider authentication failed. Please verify FMP_API_KEY.",
                    )
                elif response.status_code == 429:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Market data provider rate limit reached. Please try again later.",
                    )
                elif response.status_code >= 500:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Market data provider is temporarily unavailable.",
                    )

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Market data provider request timed out.",
            )
        except httpx.NetworkError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Market data provider is unreachable.",
            )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Market data provider returned HTTP {exc.response.status_code}.",
            )

    async def search(self, query: str, limit: int = 10, exchange: Optional[str] = "NSE") -> List[Dict[str, Any]]:
        """Search for stock symbols matching query."""
        params: Dict[str, Any] = {"query": query, "limit": limit}
        if exchange:
            params["exchange"] = exchange
        data = await self._request("/api/v3/search", params=params)
        return data if isinstance(data, list) else []

    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest real-time/delayed quote for a symbol."""
        clean_symbol = self._normalize_indian_symbol(symbol)
        data = await self._request(f"/api/v3/quote/{clean_symbol}")
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        # Also try with .NS suffix for Indian NSE if not found
        if not clean_symbol.endswith(".NS") and not clean_symbol.endswith(".BO"):
            alt_data = await self._request(f"/api/v3/quote/{clean_symbol}.NS")
            if isinstance(alt_data, list) and len(alt_data) > 0:
                return alt_data[0]
        return None

    async def get_historical_prices(
        self,
        symbol: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get historical daily stock prices."""
        clean_symbol = self._normalize_indian_symbol(symbol)
        params: Dict[str, Any] = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        data = await self._request(f"/api/v3/historical-price-full/{clean_symbol}", params=params)
        if isinstance(data, dict) and "historical" in data:
            return data
        if not clean_symbol.endswith(".NS") and not clean_symbol.endswith(".BO"):
            alt_data = await self._request(f"/api/v3/historical-price-full/{clean_symbol}.NS", params=params)
            if isinstance(alt_data, dict) and "historical" in alt_data:
                return alt_data
        return data if isinstance(data, dict) else {"symbol": clean_symbol, "historical": []}

    async def get_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company profile and overview information."""
        clean_symbol = self._normalize_indian_symbol(symbol)
        data = await self._request(f"/api/v3/profile/{clean_symbol}")
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        if not clean_symbol.endswith(".NS") and not clean_symbol.endswith(".BO"):
            alt_data = await self._request(f"/api/v3/profile/{clean_symbol}.NS")
            if isinstance(alt_data, list) and len(alt_data) > 0:
                return alt_data[0]
        return None

    async def get_key_metrics(self, symbol: str, limit: int = 1) -> Optional[Dict[str, Any]]:
        """Get key financial metrics / valuation ratios."""
        clean_symbol = self._normalize_indian_symbol(symbol)
        data = await self._request(f"/api/v3/key-metrics-ttm/{clean_symbol}", params={"limit": limit})
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        if not clean_symbol.endswith(".NS") and not clean_symbol.endswith(".BO"):
            alt_data = await self._request(f"/api/v3/key-metrics-ttm/{clean_symbol}.NS", params={"limit": limit})
            if isinstance(alt_data, list) and len(alt_data) > 0:
                return alt_data[0]
        return None

    async def get_income_statement(self, symbol: str, period: str = "annual", limit: int = 5) -> List[Dict[str, Any]]:
        """Get historical income statement."""
        clean_symbol = self._normalize_indian_symbol(symbol)
        data = await self._request(f"/api/v3/income-statement/{clean_symbol}", params={"period": period, "limit": limit})
        if isinstance(data, list) and len(data) > 0:
            return data
        if not clean_symbol.endswith(".NS") and not clean_symbol.endswith(".BO"):
            alt_data = await self._request(f"/api/v3/income-statement/{clean_symbol}.NS", params={"period": period, "limit": limit})
            if isinstance(alt_data, list):
                return alt_data
        return data if isinstance(data, list) else []

    async def get_balance_sheet(self, symbol: str, period: str = "annual", limit: int = 5) -> List[Dict[str, Any]]:
        """Get historical balance sheet statement."""
        clean_symbol = self._normalize_indian_symbol(symbol)
        data = await self._request(f"/api/v3/balance-sheet-statement/{clean_symbol}", params={"period": period, "limit": limit})
        if isinstance(data, list) and len(data) > 0:
            return data
        if not clean_symbol.endswith(".NS") and not clean_symbol.endswith(".BO"):
            alt_data = await self._request(f"/api/v3/balance-sheet-statement/{clean_symbol}.NS", params={"period": period, "limit": limit})
            if isinstance(alt_data, list):
                return alt_data
        return data if isinstance(data, list) else []

    async def get_cash_flow(self, symbol: str, period: str = "annual", limit: int = 5) -> List[Dict[str, Any]]:
        """Get historical cash flow statement."""
        clean_symbol = self._normalize_indian_symbol(symbol)
        data = await self._request(f"/api/v3/cash-flow-statement/{clean_symbol}", params={"period": period, "limit": limit})
        if isinstance(data, list) and len(data) > 0:
            return data
        if not clean_symbol.endswith(".NS") and not clean_symbol.endswith(".BO"):
            alt_data = await self._request(f"/api/v3/cash-flow-statement/{clean_symbol}.NS", params={"period": period, "limit": limit})
            if isinstance(alt_data, list):
                return alt_data
        return data if isinstance(data, list) else []

    async def get_technical_indicator(
        self,
        symbol: str,
        indicator_type: str = "rsi",
        period: int = 14,
    ) -> List[Dict[str, Any]]:
        """Get technical indicator series (RSI, SMA, EMA, MACD)."""
        clean_symbol = self._normalize_indian_symbol(symbol)
        endpoint = f"/api/v3/technical_indicator/daily/{clean_symbol}"
        params = {"type": indicator_type.lower(), "period": period}
        data = await self._request(endpoint, params=params)
        if isinstance(data, list):
            return data
        if not clean_symbol.endswith(".NS") and not clean_symbol.endswith(".BO"):
            alt_data = await self._request(f"/api/v3/technical_indicator/daily/{clean_symbol}.NS", params=params)
            if isinstance(alt_data, list):
                return alt_data
        return []


fmp_client = FMPClient()
