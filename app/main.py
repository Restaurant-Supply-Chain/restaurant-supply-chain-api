from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.api.v1.routers.auth import router as auth_router
from app.core.config import settings
from app.core.exceptions import http_exception_handler, validation_exception_handler

app = FastAPI(
    title="Restaurant Supply Chain API",
    description="B2B API for restaurant supply chain management",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Use the same problem format for HTTP errors and invalid input.
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.include_router(auth_router)
