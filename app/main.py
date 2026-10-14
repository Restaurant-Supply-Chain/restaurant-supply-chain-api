from fastapi import FastAPI
from app.modules.products.router import router as product_catalog_router

app = FastAPI(title="Restaurant Supply Chain API")

app.include_router(product_catalog_router)