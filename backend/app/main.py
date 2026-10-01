from fastapi import FastAPI, Response
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


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

