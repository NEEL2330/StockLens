from fastapi import FastAPI
from app.api.routes import health

app = FastAPI(
    title="StockLens API",
    description="Full-stack Indian equities stock-market platform API",
    version="1.0.0",
)

app.include_router(health.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Welcome to StockLens API. Visit /docs for documentation."}
