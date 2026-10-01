# StockLens

StockLens is a full-stack stock-market platform focused on Indian equities.

## Architecture
- **Backend**: FastAPI, SQLAlchemy 2.x, MySQL, Pydantic, Uvicorn
- **Frontend**: React (Vite), Tailwind CSS
- **Market Data**: Financial Modeling Prep (FMP)

## Getting Started

### Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # On Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```
