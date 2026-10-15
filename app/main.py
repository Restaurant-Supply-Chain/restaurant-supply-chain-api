
from fastapi import FastAPI

from app.modules.purchase_orders.router import (
    router as purchase_orders_router,
)

app = FastAPI(
    title="Restaurant Supply Chain API",
    description="B2B API for restaurant supply chain management",
    version="0.1.0",
)

app.include_router(purchase_orders_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "rsc-api"}
