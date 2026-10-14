
from fastapi import FastAPI

from app.core.config import settings
from app.modules.products.router import router as products_router

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

app.include_router(products_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}