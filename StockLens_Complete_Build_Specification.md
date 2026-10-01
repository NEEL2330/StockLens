# StockLens --- Complete Build Specification

## 1. Project Goal

StockLens is a full-stack stock-market platform focused on Indian
equities.

The application should allow a user to:

-   Register and log in securely.
-   Search Indian stocks.
-   View current/latest available market data from the selected
    market-data provider.
-   View historical prices.
-   View company information.
-   View financial statements and key financial metrics where the
    provider supports them.
-   View technical indicators/charts.
-   Create and manage a personal watchlist.
-   Track selected stocks.
-   View a personalized dashboard.
-   Authenticate using JWT.
-   Access only their own private resources.
-   Consume the backend through a REST API.

For the first version, use **FMP (Financial Modeling Prep)** as the
external market-data provider.

------------------------------------------------------------------------

# 2. Recommended Architecture

``` text
                    ┌──────────────────────┐
                    │      React Frontend  │
                    │       (Vite)         │
                    └──────────┬───────────┘
                               │
                               │ REST / JSON
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │                      │
                    │ Auth / Users         │
                    │ Stocks               │
                    │ Watchlists            │
                    │ Portfolio/Dashboard  │
                    └───────┬─────────┬────┘
                            │         │
                 SQLAlchemy │         │ HTTP
                            │         │
                            ▼         ▼
                    ┌────────────┐  ┌──────────────┐
                    │   MySQL    │  │     FMP      │
                    │ Application│  │ Market Data  │
                    │    Data    │  │     API      │
                    └────────────┘  └──────────────┘
```

------------------------------------------------------------------------

# 3. Technology Stack

## Backend

-   Python
-   FastAPI
-   SQLAlchemy 2.x
-   Pydantic
-   MySQL
-   PyMySQL
-   python-dotenv
-   JWT authentication
-   Passlib/bcrypt or an equivalent password-hashing library
-   httpx for calling FMP
-   Uvicorn

## Frontend

-   React
-   Vite
-   Axios
-   React Router
-   Tailwind CSS

## Database

-   MySQL

## External API

-   Financial Modeling Prep (FMP)

## Development / Deployment

-   Git + GitHub
-   Docker
-   Docker Compose
-   AWS can be added later

------------------------------------------------------------------------

# 4. Repository Structure

Use this structure:

``` text
StockLens/
│
├── backend/
│   ├── .env
│   ├── .gitignore
│   ├── requirements.txt
│   │
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── database.py
│       ├── config.py
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes/
│       │       ├── __init__.py
│       │       ├── health.py
│       │       ├── auth.py
│       │       ├── users.py
│       │       ├── stocks.py
│       │       ├── watchlists.py
│       │       └── dashboard.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   └── watchlist.py
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── user.py
│       │   ├── stock.py
│       │   └── watchlist.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── auth_service.py
│       │   ├── stock_service.py
│       │   └── watchlist_service.py
│       │
│       ├── dependencies/
│       │   ├── __init__.py
│       │   └── auth.py
│       │
│       └── clients/
│           ├── __init__.py
│           └── fmp_client.py
│
└── frontend/
    └── ...
```

------------------------------------------------------------------------

# 5. Environment Variables

Create:

``` text
backend/.env
```

Example:

``` env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/stock_platform

JWT_SECRET_KEY=your-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

FMP_API_KEY=your_fmp_api_key
FMP_BASE_URL=https://financialmodelingprep.com
```

If the MySQL password contains special URL characters, URL-encode them.

For example:

``` text
MyPass@123
```

becomes:

``` text
MyPass%40123
```

Never commit `.env` to GitHub.

------------------------------------------------------------------------

# 6. Database

## 6.1 Users table

Create:

``` text
users
```

Columns:

  Column          Type           Constraints
  --------------- -------------- -----------------------------
  id              INT            Primary Key, Auto Increment
  name            VARCHAR(100)   NOT NULL
  email           VARCHAR(255)   NOT NULL, UNIQUE
  password_hash   VARCHAR(255)   NOT NULL
  created_at      DATETIME       NOT NULL

The user password must never be stored directly.

Store only the password hash.

------------------------------------------------------------------------

# 7. Watchlist Database

Create:

``` text
watchlists
```

Columns:

  Column       Type          Constraints
  ------------ ------------- -----------------------------
  id           INT           Primary Key, Auto Increment
  user_id      INT           Foreign Key → users.id
  symbol       VARCHAR(20)   NOT NULL
  created_at   DATETIME      NOT NULL

Recommended constraint:

``` text
UNIQUE(user_id, symbol)
```

This prevents the same user from adding the same stock multiple times.

Example:

``` text
User 1 → RELIANCE
User 1 → TCS
User 1 → INFY

User 2 → RELIANCE
```

The same stock can exist in different users' watchlists.

------------------------------------------------------------------------

# 8. Authentication System

Use JWT access tokens.

## Registration

``` http
POST /api/auth/register
```

Request:

``` json
{
  "name": "Neel",
  "email": "neel@example.com",
  "password": "StrongPassword123"
}
```

Backend:

1.  Validate input.
2.  Check whether email already exists.
3.  Hash password.
4.  Create user.
5.  Save user.
6.  Return public user information.

Response:

``` json
{
  "id": 1,
  "name": "Neel",
  "email": "neel@example.com"
}
```

Status:

``` text
201 Created
```

------------------------------------------------------------------------

# 9. Login API

``` http
POST /api/auth/login
```

Request:

``` json
{
  "email": "neel@example.com",
  "password": "StrongPassword123"
}
```

Backend:

1.  Find user by email.
2.  Verify password hash.
3.  Create JWT.
4.  Return access token.

Response:

``` json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

Status:

``` text
200 OK
```

------------------------------------------------------------------------

# 10. JWT Payload

Keep the token payload minimal.

Example:

``` json
{
  "sub": "1",
  "exp": 1790000000
}
```

Where:

``` text
sub = user ID
exp = expiration timestamp
```

Do not put passwords or sensitive information inside the JWT.

------------------------------------------------------------------------

# 11. Current User Dependency

Create:

``` text
app/dependencies/auth.py
```

The dependency should:

1.  Read the Authorization header.
2.  Extract the Bearer token.
3.  Verify the JWT signature.
4.  Validate expiration.
5.  Extract the user ID.
6.  Query the database.
7.  Return the current user.
8.  Raise 401 if authentication fails.

Routes should use:

``` python
current_user: User = Depends(get_current_user)
```

This avoids repeating JWT verification logic in every protected
endpoint.

------------------------------------------------------------------------

# 12. User APIs

## Get Current User

``` http
GET /api/users/me
```

Authentication:

``` text
Required
```

Response:

``` json
{
  "id": 1,
  "name": "Neel",
  "email": "neel@example.com"
}
```

Status:

``` text
200 OK
```

------------------------------------------------------------------------

## Get User by ID

``` http
GET /api/users/{user_id}
```

Authentication:

``` text
Required
```

Response:

``` json
{
  "id": 1,
  "name": "Neel",
  "email": "neel@example.com"
}
```

For the first version, preferably restrict this endpoint so users cannot
arbitrarily inspect other users unless there is a genuine requirement.

------------------------------------------------------------------------

# 13. Stock API Design

Stock data should come from FMP.

The FastAPI backend should act as the application-facing API.

The frontend should NOT call FMP directly.

Correct:

``` text
React
  ↓
FastAPI
  ↓
FMP
```

Avoid:

``` text
React
  ↓
FMP
```

This keeps the FMP API key on the backend.

------------------------------------------------------------------------

# 14. Stock Search API

``` http
GET /api/stocks/search?query=reliance
```

Purpose:

Search for stocks/companies.

Example response:

``` json
{
  "results": [
    {
      "symbol": "RELIANCE",
      "name": "Reliance Industries Limited",
      "exchange": "NSE"
    }
  ]
}
```

The exact fields returned should be mapped from the FMP response rather
than exposing FMP's raw response directly.

------------------------------------------------------------------------

# 15. Stock Quote API

``` http
GET /api/stocks/{symbol}/quote
```

Example:

``` http
GET /api/stocks/RELIANCE/quote
```

Return the latest available quote information supported by FMP.

Example application response:

``` json
{
  "symbol": "RELIANCE",
  "price": 1400.50,
  "change": 12.40,
  "change_percent": 0.89,
  "volume": 1234567
}
```

Important:

The application should describe this as the provider's latest available
data, not necessarily a tick-by-tick real-time price.

------------------------------------------------------------------------

# 16. Historical Stock Data API

``` http
GET /api/stocks/{symbol}/history
```

Query parameters:

``` text
from
to
```

Example:

``` http
GET /api/stocks/RELIANCE/history?from=2026-01-01&to=2026-09-30
```

Return:

``` json
{
  "symbol": "RELIANCE",
  "prices": [
    {
      "date": "2026-09-29",
      "open": 1380,
      "high": 1410,
      "low": 1370,
      "close": 1400,
      "volume": 1234567
    }
  ]
}
```

This data will power the frontend price chart.

------------------------------------------------------------------------

# 17. Company Profile API

``` http
GET /api/stocks/{symbol}/profile
```

Example:

``` http
GET /api/stocks/TCS/profile
```

Return supported company information such as:

``` json
{
  "symbol": "TCS",
  "name": "Tata Consultancy Services",
  "industry": "...",
  "sector": "...",
  "description": "...",
  "website": "...",
  "market_cap": 0
}
```

Only include fields actually supported and available from the provider.

------------------------------------------------------------------------

# 18. Financial Metrics API

``` http
GET /api/stocks/{symbol}/metrics
```

Use the FMP endpoints that provide supported financial metrics.

Potential fields:

``` text
market capitalization
PE ratio
EPS
ROE
ROA
debt/equity
profit margin
dividend yield
```

Do not invent missing data.

If FMP does not provide a metric for a particular Indian
company/security, return `null` or omit it according to the response
schema.

------------------------------------------------------------------------

# 19. Financial Statements API

Provide:

``` http
GET /api/stocks/{symbol}/income-statement
```

``` http
GET /api/stocks/{symbol}/balance-sheet
```

``` http
GET /api/stocks/{symbol}/cash-flow
```

Support a period parameter if required:

``` text
annual
quarter
```

Example:

``` http
GET /api/stocks/RELIANCE/income-statement?period=annual
```

The backend should normalize the provider response into a stable
StockLens response.

------------------------------------------------------------------------

# 20. Technical Indicators

For the first version, implement a limited set instead of trying to
build every indicator.

Recommended:

``` text
SMA
EMA
RSI
MACD
```

APIs:

``` http
GET /api/stocks/{symbol}/indicators/sma
GET /api/stocks/{symbol}/indicators/ema
GET /api/stocks/{symbol}/indicators/rsi
GET /api/stocks/{symbol}/indicators/macd
```

Use query parameters for:

``` text
period
timeframe
from
to
```

Example:

``` http
GET /api/stocks/RELIANCE/indicators/rsi?period=14
```

------------------------------------------------------------------------

# 21. Watchlist APIs

All watchlist endpoints must require authentication.

## Add stock

``` http
POST /api/watchlists
```

Request:

``` json
{
  "symbol": "RELIANCE"
}
```

Backend:

1.  Get authenticated user.
2.  Validate symbol.
3.  Check whether it already exists in that user's watchlist.
4.  Insert it.
5.  Return the watchlist item.

Response:

``` json
{
  "id": 10,
  "symbol": "RELIANCE"
}
```

Status:

``` text
201 Created
```

------------------------------------------------------------------------

# 22. Get Watchlist

``` http
GET /api/watchlists
```

Authentication:

``` text
Required
```

Response:

``` json
[
  {
    "id": 10,
    "symbol": "RELIANCE"
  },
  {
    "id": 11,
    "symbol": "TCS"
  }
]
```

The query must filter by the authenticated user's ID.

Never return another user's watchlist.

------------------------------------------------------------------------

# 23. Delete Watchlist Item

``` http
DELETE /api/watchlists/{watchlist_id}
```

Authentication:

``` text
Required
```

Backend must verify that the item belongs to the current user.

If it does not belong to the user, do not allow deletion.

Recommended response:

``` text
204 No Content
```

------------------------------------------------------------------------

# 24. Dashboard API

Create one endpoint that provides the data required by the user's
dashboard.

``` http
GET /api/dashboard
```

Authentication:

``` text
Required
```

Possible response:

``` json
{
  "watchlist": [
    {
      "symbol": "RELIANCE",
      "price": 1400,
      "change_percent": 0.89
    },
    {
      "symbol": "TCS",
      "price": 3500,
      "change_percent": -0.25
    }
  ]
}
```

The dashboard endpoint can internally:

1.  Get current user.
2.  Get user's watchlist.
3.  Fetch market information.
4.  Aggregate the response.

Keep this endpoint focused on dashboard data rather than creating
another source of truth.

------------------------------------------------------------------------

# 25. Health Check

Create:

``` http
GET /api/health
```

Response:

``` json
{
  "status": "ok"
}
```

Use this to verify that the backend is running.

------------------------------------------------------------------------

# 26. Complete API List

## Public

``` text
GET  /api/health

POST /api/auth/register
POST /api/auth/login

GET  /api/stocks/search
GET  /api/stocks/{symbol}/quote
GET  /api/stocks/{symbol}/history
GET  /api/stocks/{symbol}/profile
GET  /api/stocks/{symbol}/metrics
GET  /api/stocks/{symbol}/income-statement
GET  /api/stocks/{symbol}/balance-sheet
GET  /api/stocks/{symbol}/cash-flow
GET  /api/stocks/{symbol}/indicators/sma
GET  /api/stocks/{symbol}/indicators/ema
GET  /api/stocks/{symbol}/indicators/rsi
GET  /api/stocks/{symbol}/indicators/macd
```

## Protected

``` text
GET    /api/users/me

GET    /api/users/{user_id}

GET    /api/watchlists
POST   /api/watchlists
DELETE /api/watchlists/{watchlist_id}

GET    /api/dashboard
```

------------------------------------------------------------------------

# 27. HTTP Status Codes

Use consistent status codes.

``` text
200 OK
```

Successful request where a resource is returned.

Examples:

``` text
GET /users/me
GET /stocks/RELIANCE/quote
POST /auth/login
```

``` text
201 Created
```

A new resource was created.

Examples:

``` text
POST /auth/register
POST /watchlists
```

``` text
204 No Content
```

Successful operation with no response body.

Example:

``` text
DELETE /watchlists/10
```

``` text
400 Bad Request
```

Malformed or invalid request.

``` text
401 Unauthorized
```

Missing/invalid authentication.

``` text
403 Forbidden
```

Authenticated user does not have permission.

``` text
404 Not Found
```

Requested resource does not exist.

``` text
409 Conflict
```

Useful for conflicts such as attempting to register an already-existing
email or duplicate watchlist item.

``` text
422 Unprocessable Entity
```

FastAPI commonly uses this for request validation failures.

------------------------------------------------------------------------

# 28. Pydantic Schemas

Do not use SQLAlchemy models directly as your request/response contract.

Create separate schemas.

Example:

``` python
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
```

``` python
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
```

The important separation is:

``` text
SQLAlchemy Model
       ↓
Database representation

Pydantic Schema
       ↓
API request/response representation
```

------------------------------------------------------------------------

# 29. SQLAlchemy Models

Use SQLAlchemy 2.x style.

Example:

``` python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
```

The ORM converts Python operations into SQL.

For example:

``` python
db.get(User, user_id)
```

causes SQLAlchemy to generate and execute SQL against MySQL.

------------------------------------------------------------------------

# 30. Service Layer

Do not put all business logic inside route functions.

Example:

``` text
Route
  ↓
Service
  ↓
Database / FMP client
```

Example:

``` python
@router.get("/stocks/{symbol}/quote")
def get_quote(symbol: str):
    return stock_service.get_quote(symbol)
```

The service handles:

-   Calling FMP
-   Validating/normalizing provider data
-   Business rules
-   Error handling

------------------------------------------------------------------------

# 31. FMP Client

Create:

``` text
app/clients/fmp_client.py
```

This file is responsible for external FMP communication.

Example conceptual structure:

``` python
class FMPClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search_stocks(...):
        ...

    async def get_quote(...):
        ...

    async def get_historical_data(...):
        ...

    async def get_profile(...):
        ...
```

Do not scatter raw FMP HTTP calls across route files.

Correct:

``` text
Route
 ↓
Service
 ↓
FMP Client
 ↓
FMP
```

------------------------------------------------------------------------

# 32. Async HTTP

Use `httpx.AsyncClient` for external FMP requests if the
endpoint/service is asynchronous.

Example architecture:

``` text
FastAPI async route
       ↓
async service
       ↓
async FMP client
       ↓
FMP API
```

Do not use async merely for CPU-heavy work.

The primary benefit here is handling I/O without blocking the event
loop.

------------------------------------------------------------------------

# 33. Error Handling for FMP

Do not expose raw FMP errors directly to the frontend.

For example, if FMP is unavailable:

``` text
FMP
 ↓
timeout / 5xx
 ↓
StockLens backend
 ↓
controlled application error
```

Return an appropriate API error such as:

``` json
{
  "detail": "Market data provider is temporarily unavailable"
}
```

------------------------------------------------------------------------

# 34. Frontend Pages

Build these pages.

## Public

``` text
/login
/register
```

## Main application

``` text
/dashboard
/stocks
/stocks/:symbol
/watchlist
/profile
```

------------------------------------------------------------------------

# 35. Dashboard UI

Dashboard should show:

-   User name
-   Watchlist summary
-   Latest available price
-   Daily change
-   Daily percentage change
-   Quick links to stock details

------------------------------------------------------------------------

# 36. Stock Search UI

Provide:

``` text
Search box
    ↓
GET /api/stocks/search?query=...
    ↓
Search results
```

When a stock is selected:

``` text
/stocks/RELIANCE
```

------------------------------------------------------------------------

# 37. Stock Detail Page

Show:

``` text
Company name
Symbol
Exchange
Latest price
Change
Change %
Historical price chart
Company profile
Key metrics
Financial statements
Technical indicators
Add/remove watchlist button
```

------------------------------------------------------------------------

# 38. Watchlist Page

Show:

``` text
Symbol
Latest price
Change
Change %
Remove button
```

Use:

``` text
GET /api/watchlists
```

Then obtain market data for the displayed symbols.

------------------------------------------------------------------------

# 39. Frontend Authentication Flow

Registration:

``` text
Register form
 ↓
POST /api/auth/register
 ↓
Success
 ↓
Redirect to login
```

Login:

``` text
Login form
 ↓
POST /api/auth/login
 ↓
Receive JWT
 ↓
Store token
 ↓
Use token for protected API calls
```

Protected request:

``` http
Authorization: Bearer <JWT>
```

For a simple first version, token storage can use browser storage, but
for a production-grade application consider an HttpOnly secure cookie
strategy.

------------------------------------------------------------------------

# 40. Backend Request Flow

For a protected watchlist request:

``` text
React
  ↓
GET /api/watchlists
Authorization: Bearer JWT
  ↓
FastAPI
  ↓
get_current_user dependency
  ↓
verify JWT
  ↓
load User
  ↓
watchlist route
  ↓
watchlist service
  ↓
SQLAlchemy
  ↓
MySQL
  ↓
Pydantic response schema
  ↓
JSON
  ↓
React
```

------------------------------------------------------------------------

# 41. Stock Request Flow

For stock details:

``` text
React
  ↓
GET /api/stocks/RELIANCE/quote
  ↓
FastAPI
  ↓
Stock route
  ↓
Stock service
  ↓
FMP client
  ↓
FMP
  ↓
normalize response
  ↓
Pydantic schema
  ↓
React
```

------------------------------------------------------------------------

# 42. Security Requirements

Implement:

-   Password hashing
-   JWT authentication
-   JWT expiration
-   Environment variables for secrets
-   No FMP API key in frontend
-   No plaintext passwords in database
-   Authorization checks for user-owned resources
-   Input validation through Pydantic
-   Parameterized SQL through SQLAlchemy
-   CORS restricted to frontend origin in production

Never commit:

``` text
.env
database passwords
JWT secrets
FMP API keys
```

------------------------------------------------------------------------

# 43. CORS

During development, allow the Vite frontend origin.

Example:

``` text
http://localhost:5173
```

Configure FastAPI CORS middleware.

In production, replace development wildcard settings with the actual
frontend domain.

------------------------------------------------------------------------

# 44. Development Order

Build the project in this exact order.

## Phase 1 --- Backend foundation

1.  Create Git repository.
2.  Create Python virtual environment.
3.  Install FastAPI.
4.  Create project structure.
5.  Create `main.py`.
6.  Add health endpoint.
7.  Run Uvicorn.
8.  Verify `/docs`.

------------------------------------------------------------------------

## Phase 2 --- Database

1.  Create MySQL database.
2.  Configure `.env`.
3.  Create SQLAlchemy engine.
4.  Create `Base`.
5.  Create database session dependency.
6.  Create `User` model.
7.  Create `Watchlist` model.
8.  Create tables.

For now, schema migration tooling can be added later.

------------------------------------------------------------------------

## Phase 3 --- User APIs

Implement:

``` text
POST /api/auth/register
POST /api/auth/login
GET  /api/users/me
```

Test everything through Swagger UI.

------------------------------------------------------------------------

## Phase 4 --- JWT

Implement:

``` text
JWT creation
JWT verification
get_current_user dependency
```

Protect:

``` text
/users/me
/watchlists
/dashboard
```

------------------------------------------------------------------------

## Phase 5 --- FMP Integration

Create:

``` text
FMPClient
```

Implement:

``` text
stock search
quote
historical data
profile
metrics
financial statements
```

Test FMP independently before connecting it to the frontend.

------------------------------------------------------------------------

## Phase 6 --- Stock APIs

Implement all StockLens stock endpoints.

Normalize FMP responses.

Do not expose provider-specific structures unnecessarily.

------------------------------------------------------------------------

## Phase 7 --- Watchlist

Implement:

``` text
POST /watchlists
GET /watchlists
DELETE /watchlists/{id}
```

Ensure every query is scoped to the authenticated user.

------------------------------------------------------------------------

## Phase 8 --- Dashboard

Implement:

``` text
GET /dashboard
```

Combine:

``` text
user
+
watchlist
+
market data
```

------------------------------------------------------------------------

## Phase 9 --- React Frontend

Build:

``` text
Login
Register
Dashboard
Stock Search
Stock Details
Watchlist
Profile
```

------------------------------------------------------------------------

## Phase 10 --- Integration

Connect:

``` text
React
 ↓
FastAPI
 ↓
MySQL + FMP
```

Test complete user journeys.

------------------------------------------------------------------------

# 45. Core User Journey

The final application should support:

``` text
User opens StockLens
        ↓
Register
        ↓
Login
        ↓
Receive JWT
        ↓
Dashboard
        ↓
Search "RELIANCE"
        ↓
Open RELIANCE
        ↓
View quote
        ↓
View historical chart
        ↓
View company information
        ↓
View metrics
        ↓
Add RELIANCE to watchlist
        ↓
Open watchlist
        ↓
See RELIANCE
        ↓
Remove RELIANCE
```

------------------------------------------------------------------------

# 46. API Testing Checklist

Before building the frontend, test every backend API through
Swagger/Postman.

## Authentication

``` text
[ ] Register new user
[ ] Duplicate email rejected
[ ] Login with correct password
[ ] Login with incorrect password rejected
[ ] JWT returned
[ ] Invalid JWT rejected
[ ] Expired JWT rejected
```

## Users

``` text
[ ] GET /users/me works with valid JWT
[ ] GET /users/me fails without JWT
```

## Stocks

``` text
[ ] Search works
[ ] Quote works
[ ] Historical data works
[ ] Profile works
[ ] Metrics work
[ ] Financial statements work
[ ] Invalid symbol handled
[ ] FMP errors handled
```

## Watchlist

``` text
[ ] Add stock
[ ] Duplicate stock prevented
[ ] Get user's watchlist
[ ] Delete stock
[ ] Cannot delete another user's item
```

------------------------------------------------------------------------

# 47. Final Backend API Contract

The backend should expose these main resources:

``` text
/auth
/users
/stocks
/watchlists
/dashboard
/health
```

Complete contract:

``` text
POST   /api/auth/register
POST   /api/auth/login

GET    /api/users/me
GET    /api/users/{user_id}

GET    /api/stocks/search
GET    /api/stocks/{symbol}/quote
GET    /api/stocks/{symbol}/history
GET    /api/stocks/{symbol}/profile
GET    /api/stocks/{symbol}/metrics
GET    /api/stocks/{symbol}/income-statement
GET    /api/stocks/{symbol}/balance-sheet
GET    /api/stocks/{symbol}/cash-flow

GET    /api/stocks/{symbol}/indicators/sma
GET    /api/stocks/{symbol}/indicators/ema
GET    /api/stocks/{symbol}/indicators/rsi
GET    /api/stocks/{symbol}/indicators/macd

GET    /api/watchlists
POST   /api/watchlists
DELETE /api/watchlists/{watchlist_id}

GET    /api/dashboard

GET    /api/health
```

------------------------------------------------------------------------

# 48. What NOT to Build Initially

Do not overcomplicate version 1.

Skip initially:

-   Real-time WebSockets
-   Stock trading
-   Broker integration
-   Payments
-   Notifications
-   Social features
-   AI stock recommendations
-   Complex portfolio accounting
-   Microservices
-   Kubernetes
-   Redis
-   Kafka
-   Celery
-   Advanced caching
-   Admin panel

Build the core product first.

------------------------------------------------------------------------

# 49. Version 1 Definition of Done

StockLens V1 is complete when:

``` text
[ ] User can register
[ ] User can login
[ ] JWT authentication works
[ ] Protected routes work
[ ] MySQL stores users
[ ] MySQL stores watchlists
[ ] FMP integration works
[ ] Stock search works
[ ] Stock quote works
[ ] Historical chart data works
[ ] Company profile works
[ ] Key metrics work
[ ] Financial statements work
[ ] Technical indicators work
[ ] User can add stocks to watchlist
[ ] User can remove stocks
[ ] User can only access their own watchlist
[ ] Dashboard works
[ ] React frontend is connected
[ ] API errors are handled
[ ] Secrets are stored in environment variables
[ ] Project runs locally from a clean setup
```

------------------------------------------------------------------------

# 50. Recommended Interview Talking Point

The project architecture should be explainable as:

> "StockLens is a full-stack stock-market application where React
> communicates with a FastAPI backend through REST APIs. FastAPI handles
> authentication, authorization, business logic, and communication with
> MySQL through SQLAlchemy. For market data, the backend integrates with
> Financial Modeling Prep through a dedicated client layer. JWT is used
> for stateless authentication, and FastAPI dependency injection is used
> to provide the database session and current authenticated user to
> protected routes. Pydantic schemas keep the API contract separate from
> the database models."

This is the architecture to build before adding deployment or advanced
features.

# 51. Detailed Phase-Wise Project Implementation Plan

This section is the practical build order for StockLens. Complete and
test one phase before moving to the next.

------------------------------------------------------------------------

## Phase 0 --- Project Setup and Git

### Goal

Create a clean repository and development environment.

### Tasks

``` text
[ ] Create GitHub repository: StockLens
[ ] Create backend and frontend folders
[ ] Create Python virtual environment
[ ] Add .gitignore
[ ] Add README.md
[ ] Make first Git commit
```

### Backend setup

``` bash
cd backend
python -m venv .venv
```

Activate it on Windows:

``` powershell
.venv\Scripts\Activate.ps1
```

Install initial dependencies:

``` bash
pip install fastapi uvicorn
```

### Deliverable

The repository should run a basic FastAPI application.

------------------------------------------------------------------------

# Phase 1 --- FastAPI Backend Skeleton

### Goal

Get the backend running with a clean structure.

### Create

``` text
backend/
└── app/
    ├── __init__.py
    ├── main.py
    └── api/
        ├── __init__.py
        └── routes/
            ├── __init__.py
            └── health.py
```

### Implement

``` text
GET /api/health
```

Response:

``` json
{
  "status": "ok"
}
```

### Test

Open:

``` text
http://127.0.0.1:8000/docs
```

### Deliverable

Swagger UI works and `/api/health` returns 200.

------------------------------------------------------------------------

# Phase 2 --- Configuration and Environment Variables

### Goal

Centralize configuration and keep secrets outside the source code.

### Install

``` bash
pip install python-dotenv
```

### Create

``` text
backend/
├── .env
└── app/
    └── config.py
```

### Add

``` env
DATABASE_URL=...
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FMP_API_KEY=...
FMP_BASE_URL=...
```

### Tasks

``` text
[ ] Load environment variables
[ ] Verify variables exist
[ ] Add .env to .gitignore
[ ] Never hardcode API keys
```

### Deliverable

The application can read configuration from `.env`.

------------------------------------------------------------------------

# Phase 3 --- MySQL + SQLAlchemy

### Goal

Connect FastAPI to MySQL.

### Install

``` bash
pip install sqlalchemy pymysql
```

### Create

``` text
app/
└── database.py
```

Implement:

``` text
DATABASE_URL
        ↓
SQLAlchemy Engine
        ↓
SessionLocal
        ↓
Base
        ↓
get_db()
```

### Test

Create a simple database connection test.

### Deliverable

FastAPI can create a SQLAlchemy database session.

------------------------------------------------------------------------

# Phase 4 --- User Model and Database Tables

### Goal

Create the first real application model.

### Create

``` text
app/models/user.py
```

Implement:

``` text
users
├── id
├── name
├── email
├── password_hash
└── created_at
```

### Also create

``` text
app/schemas/user.py
```

Schemas:

``` text
UserCreate
UserResponse
UserUpdate
```

### Deliverable

The User model and schemas work correctly.

------------------------------------------------------------------------

# Phase 5 --- User Registration

### Goal

Allow a new user to create an account.

### Endpoint

``` http
POST /api/auth/register
```

### Flow

``` text
Request
  ↓
Validate Pydantic schema
  ↓
Check email
  ↓
Hash password
  ↓
Create User
  ↓
Save to MySQL
  ↓
Return UserResponse
```

### Install password hashing dependencies

Use a maintained password-hashing library appropriate for the
implementation.

### Test

``` text
[ ] Valid registration
[ ] Duplicate email
[ ] Missing fields
[ ] Invalid email
[ ] Password validation
```

### Deliverable

A user can register and their password is stored only as a hash.

------------------------------------------------------------------------

# Phase 6 --- JWT Login

### Goal

Implement authentication.

### Endpoint

``` http
POST /api/auth/login
```

### Flow

``` text
email + password
       ↓
find user
       ↓
verify password hash
       ↓
create JWT
       ↓
return access token
```

### Response

``` json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

### Deliverable

A valid user can log in and receive a JWT.

------------------------------------------------------------------------

# Phase 7 --- Current User Dependency

### Goal

Build reusable authentication using FastAPI Dependency Injection.

### Create

``` text
app/dependencies/auth.py
```

Implement:

``` text
oauth2_scheme
      ↓
get_current_user()
      ↓
decode JWT
      ↓
extract user ID
      ↓
load User
```

Protected routes use:

``` python
current_user: User = Depends(get_current_user)
```

### Test

``` text
[ ] Valid JWT
[ ] Missing JWT
[ ] Invalid JWT
[ ] Expired JWT
[ ] Deleted/nonexistent user
```

### Deliverable

Any protected endpoint can reuse the same authentication dependency.

------------------------------------------------------------------------

# Phase 8 --- User APIs

### Goal

Complete the user functionality.

### Endpoints

``` http
GET /api/users/me
GET /api/users/{user_id}
```

### Important

`/users/me` should use:

``` python
current_user: User = Depends(get_current_user)
```

### Deliverable

Authenticated users can retrieve their own profile.

------------------------------------------------------------------------

# Phase 9 --- Watchlist Database Model

### Goal

Create the user's stock watchlist.

### Create

``` text
app/models/watchlist.py
app/schemas/watchlist.py
```

Database:

``` text
watchlists
├── id
├── user_id
├── symbol
└── created_at
```

Add:

``` text
FOREIGN KEY user_id → users.id
UNIQUE(user_id, symbol)
```

### Deliverable

Database supports user-specific watchlists.

------------------------------------------------------------------------

# Phase 10 --- Watchlist APIs

### Goal

Implement complete watchlist CRUD required by V1.

### APIs

``` http
GET    /api/watchlists
POST   /api/watchlists
DELETE /api/watchlists/{watchlist_id}
```

### POST flow

``` text
JWT
 ↓
current_user
 ↓
validate symbol
 ↓
check duplicate
 ↓
create watchlist row
 ↓
return 201
```

### GET flow

``` text
JWT
 ↓
current_user.id
 ↓
SELECT watchlists WHERE user_id = current_user.id
 ↓
return user's watchlist
```

### Security test

User A must never see or delete User B's watchlist item.

### Deliverable

Watchlist functionality works independently of market-data integration.

------------------------------------------------------------------------

# Phase 11 --- FMP Client

### Goal

Create a dedicated external API client.

### Install

``` bash
pip install httpx
```

### Create

``` text
app/clients/fmp_client.py
```

Responsibilities:

``` text
[ ] Build FMP requests
[ ] Add API key
[ ] Send HTTP requests
[ ] Handle timeouts
[ ] Handle provider errors
[ ] Return normalized/raw provider data to service layer
```

Do not call FMP directly from route files.

Architecture:

``` text
Route
  ↓
Service
  ↓
FMPClient
  ↓
FMP
```

### Deliverable

The backend can successfully communicate with FMP.

------------------------------------------------------------------------

# Phase 12 --- Stock Search

### Goal

Allow users to search stocks.

### API

``` http
GET /api/stocks/search?query=reliance
```

### Flow

``` text
React / Swagger
      ↓
FastAPI route
      ↓
stock_service
      ↓
FMPClient
      ↓
FMP
      ↓
normalize result
      ↓
StockSearchResponse
```

### Deliverable

Stock search returns StockLens-formatted results.

------------------------------------------------------------------------

# Phase 13 --- Stock Quote

### Goal

Display the latest available market quote.

### API

``` http
GET /api/stocks/{symbol}/quote
```

### Response

Normalize the provider response into fields such as:

``` text
symbol
price
change
change_percent
volume
```

### Important

Label the data accurately as the provider's latest available data where
it is not truly real-time.

### Deliverable

Stock detail pages can retrieve quote data.

------------------------------------------------------------------------

# Phase 14 --- Historical Price Data

### Goal

Provide data for stock charts.

### API

``` http
GET /api/stocks/{symbol}/history?from=YYYY-MM-DD&to=YYYY-MM-DD
```

### Flow

``` text
Frontend
  ↓
History API
  ↓
Stock Service
  ↓
FMP Client
  ↓
FMP historical endpoint
  ↓
normalize
  ↓
JSON
```

### Deliverable

The backend returns chart-ready historical data.

------------------------------------------------------------------------

# Phase 15 --- Company Profile

### Goal

Display basic company information.

### API

``` http
GET /api/stocks/{symbol}/profile
```

### Data

Use supported FMP fields such as:

``` text
name
symbol
exchange
sector
industry
description
website
market cap
```

### Deliverable

Stock detail page can display company information.

------------------------------------------------------------------------

# Phase 16 --- Financial Metrics

### Goal

Add fundamental metrics.

### API

``` http
GET /api/stocks/{symbol}/metrics
```

### Metrics

Where supported:

``` text
PE
EPS
ROE
ROA
Debt/Equity
Profit Margin
Dividend Yield
Market Cap
```

### Important

Do not fabricate unavailable values.

### Deliverable

The stock detail page displays a fundamentals section.

------------------------------------------------------------------------

# Phase 17 --- Financial Statements

### Goal

Add company financial statements.

### APIs

``` http
GET /api/stocks/{symbol}/income-statement
GET /api/stocks/{symbol}/balance-sheet
GET /api/stocks/{symbol}/cash-flow
```

Support:

``` text
annual
quarter
```

where the provider supports the requested period.

### Deliverable

Users can inspect historical financial statements.

------------------------------------------------------------------------

# Phase 18 --- Technical Indicators

### Goal

Add basic technical-analysis data.

Implement first:

``` text
SMA
EMA
RSI
MACD
```

### APIs

``` http
GET /api/stocks/{symbol}/indicators/sma
GET /api/stocks/{symbol}/indicators/ema
GET /api/stocks/{symbol}/indicators/rsi
GET /api/stocks/{symbol}/indicators/macd
```

### Deliverable

Backend provides technical-indicator data for charting.

------------------------------------------------------------------------

# Phase 19 --- Dashboard API

### Goal

Create a personalized dashboard response.

### API

``` http
GET /api/dashboard
```

### Flow

``` text
JWT
 ↓
Current User
 ↓
Get user's watchlist
 ↓
Get market data for watchlist
 ↓
Aggregate
 ↓
Dashboard response
```

### Response can contain

``` text
user
watchlist
latest prices
daily changes
```

### Deliverable

One API can provide the main dashboard data.

------------------------------------------------------------------------

# Phase 20 --- React Frontend Setup

### Goal

Create the frontend after the backend API contract is stable.

### Create

``` bash
npm create vite@latest frontend
```

Choose:

``` text
React
```

### Install

``` bash
npm install axios react-router-dom
```

Add Tailwind according to the current Tailwind setup.

### Create pages

``` text
Login
Register
Dashboard
Stocks
Stock Details
Watchlist
Profile
```

### Deliverable

React application runs locally.

------------------------------------------------------------------------

# Phase 21 --- Frontend Authentication

### Goal

Connect React authentication to FastAPI.

### Build

``` text
Login form
Register form
Auth state
Protected routes
API client
```

### Login flow

``` text
Login form
 ↓
POST /api/auth/login
 ↓
receive JWT
 ↓
store authentication state
 ↓
redirect /dashboard
```

### Protected requests

``` http
Authorization: Bearer <JWT>
```

### Deliverable

A user can log in through the UI and access protected pages.

------------------------------------------------------------------------

# Phase 22 --- Stock Search UI

### Goal

Connect the stock search screen to the backend.

### Flow

``` text
Search input
 ↓
GET /api/stocks/search
 ↓
Results
 ↓
Click stock
 ↓
/stocks/:symbol
```

### Deliverable

User can search and open a stock.

------------------------------------------------------------------------

# Phase 23 --- Stock Detail UI

### Goal

Build the complete stock detail experience.

Display:

``` text
Company name
Symbol
Latest price
Change
Change %
Historical chart
Company profile
Financial metrics
Financial statements
Technical indicators
Watchlist button
```

### APIs used

``` text
quote
history
profile
metrics
financial statements
indicators
```

### Deliverable

A complete stock research page.

------------------------------------------------------------------------

# Phase 24 --- Watchlist UI

### Goal

Connect watchlist APIs to the frontend.

### Flow

``` text
Stock detail
 ↓
Add to Watchlist
 ↓
POST /api/watchlists
 ↓
Watchlist page
 ↓
GET /api/watchlists
```

Removal:

``` text
Remove
 ↓
DELETE /api/watchlists/{id}
```

### Deliverable

Users can manage their watchlist from the UI.

------------------------------------------------------------------------

# Phase 25 --- Dashboard UI

### Goal

Create the application's main page.

Display:

``` text
Welcome message
Watchlist
Latest prices
Daily changes
Quick stock links
```

Use:

``` http
GET /api/dashboard
```

### Deliverable

Authenticated users have a useful personalized home screen.

------------------------------------------------------------------------

# Phase 26 --- Error Handling and Validation

### Goal

Make the application production-like.

Handle:

``` text
400
401
403
404
409
422
500
502/503 for provider failures where appropriate
```

### Backend

Create consistent error responses.

Example:

``` json
{
  "detail": "Stock data provider is temporarily unavailable"
}
```

### Frontend

Show useful messages instead of raw exceptions.

### Deliverable

Expected failures are handled cleanly.

------------------------------------------------------------------------

# Phase 27 --- CORS and Security Hardening

### Goal

Secure communication between frontend and backend.

Implement:

``` text
[ ] CORS
[ ] Strong JWT secret
[ ] Password hashing
[ ] Environment variables
[ ] Input validation
[ ] Ownership checks
[ ] No API keys in frontend
[ ] No secrets in Git
```

### Deliverable

Security basics are complete.

------------------------------------------------------------------------

# Phase 28 --- API Documentation

### Goal

Make the backend easy to understand and demonstrate.

Improve:

``` text
endpoint summaries
response models
request models
tags
status codes
```

Organize Swagger into:

``` text
Auth
Users
Stocks
Watchlists
Dashboard
Health
```

### Deliverable

`/docs` clearly documents the entire API.

------------------------------------------------------------------------

# Phase 29 --- Integration Testing

### Goal

Test the complete backend before deployment.

Test:

``` text
Register
 ↓
Login
 ↓
JWT
 ↓
Search stock
 ↓
Get stock
 ↓
Add watchlist
 ↓
Get watchlist
 ↓
Dashboard
 ↓
Delete watchlist
```

Also test failure cases:

``` text
Wrong password
No token
Invalid token
Expired token
Duplicate email
Duplicate watchlist
Invalid stock
Unauthorized ownership access
FMP failure
```

### Deliverable

The complete backend workflow works reliably.

------------------------------------------------------------------------

# Phase 30 --- Dockerization

### Goal

Make StockLens reproducible and portable.

Create:

``` text
backend/Dockerfile
frontend/Dockerfile
docker-compose.yml
```

Possible local architecture:

``` text
docker-compose
│
├── frontend
├── backend
└── mysql
```

Environment:

``` text
Frontend
   ↓
Backend
   ↓
MySQL

Backend
   ↓
FMP
```

### Deliverable

The project can be started with Docker Compose.

------------------------------------------------------------------------

# Phase 31 --- Production Preparation

### Goal

Prepare for cloud deployment.

Before AWS deployment:

``` text
[ ] Production environment variables
[ ] Production CORS
[ ] Secure JWT secret
[ ] Database credentials
[ ] Health check
[ ] Docker images
[ ] Logging
[ ] Error handling
[ ] API documentation
```

### Deliverable

The application is ready for cloud deployment.

------------------------------------------------------------------------

# Phase 32 --- AWS Deployment (After V1)

Do this only after the application works locally.

A simple first deployment can be:

``` text
React
  ↓
Static hosting / frontend server

FastAPI
  ↓
Docker container
  ↓
AWS compute

MySQL
  ↓
Managed database
```

The exact AWS architecture can be chosen later based on cost and
learning goals.

Do not introduce ECS/EKS/Kubernetes just for the sake of complexity.

------------------------------------------------------------------------

# Phase 33 --- CI/CD (After Deployment)

Once manual deployment works, automate it.

Possible flow:

``` text
Developer
   ↓
git push
   ↓
GitHub
   ↓
GitHub Actions
   ↓
Run tests
   ↓
Build Docker image
   ↓
Push image to registry
   ↓
Deploy backend
```

Use OIDC for AWS authentication rather than storing long-lived AWS
access keys in GitHub when the deployment architecture supports it.

------------------------------------------------------------------------

# Phase 34 --- Optional V2 Features

Only after V1 is stable, consider:

``` text
[ ] Caching
[ ] Redis
[ ] More technical indicators
[ ] Advanced portfolio tracking
[ ] Price alerts
[ ] More detailed analytics
[ ] Historical comparison
[ ] Sector comparison
[ ] Market overview
[ ] AI-assisted stock research
[ ] WebSockets / live updates
```

Do not add these before the core application is complete.

------------------------------------------------------------------------

# 52. Phase Completion Rule

Use this rule throughout the project:

> **Do not move to the next phase until the current phase is running and
> tested.**

For each phase:

``` text
Implement
   ↓
Run
   ↓
Test
   ↓
Fix
   ↓
Commit
   ↓
Move to next phase
```

Recommended Git workflow:

``` bash
git add .
git commit -m "feat: complete phase X"
```

This gives the project a clean development history and makes it easier
to revert mistakes.

------------------------------------------------------------------------

# 53. Final Build Sequence

The complete order is:

``` text
Phase 0   Git + project setup
   ↓
Phase 1   FastAPI skeleton
   ↓
Phase 2   Configuration
   ↓
Phase 3   MySQL + SQLAlchemy
   ↓
Phase 4   User model
   ↓
Phase 5   Registration
   ↓
Phase 6   JWT login
   ↓
Phase 7   Auth dependency
   ↓
Phase 8   User APIs
   ↓
Phase 9   Watchlist model
   ↓
Phase 10  Watchlist APIs
   ↓
Phase 11  FMP client
   ↓
Phase 12  Stock search
   ↓
Phase 13  Stock quote
   ↓
Phase 14  Historical data
   ↓
Phase 15  Company profile
   ↓
Phase 16  Financial metrics
   ↓
Phase 17  Financial statements
   ↓
Phase 18  Technical indicators
   ↓
Phase 19  Dashboard API
   ↓
Phase 20  React setup
   ↓
Phase 21  Frontend authentication
   ↓
Phase 22  Search UI
   ↓
Phase 23  Stock detail UI
   ↓
Phase 24  Watchlist UI
   ↓
Phase 25  Dashboard UI
   ↓
Phase 26  Error handling
   ↓
Phase 27  Security
   ↓
Phase 28  API documentation
   ↓
Phase 29  Integration testing
   ↓
Phase 30  Docker
   ↓
Phase 31  Production preparation
   ↓
Phase 32  AWS deployment
   ↓
Phase 33  CI/CD
   ↓
Phase 34  Optional V2
```
