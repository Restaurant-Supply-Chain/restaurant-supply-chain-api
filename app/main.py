from fastapi import FastAPI

from app.routers.supplier import router as supplier_router

app = FastAPI(
    title="Restaurant Supply Chain API",
    description="B2B API for restaurant supply chain management",
    version="0.1.0",
)

app.include_router(supplier_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "rsc-api"}