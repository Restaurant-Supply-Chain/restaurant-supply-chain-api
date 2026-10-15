from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.api.v1.routers.auth import router as auth_router
from app.core.exceptions import (
    http_exception_handler,
    unexpected_exception_handler,
    validation_exception_handler,
)
from app.middleware.auth_rate_limit import AuthRateLimitMiddleware

app = FastAPI(
    title="Restaurant Supply Chain API",
    description="B2B API for restaurant supply chain management",
    version="0.1.0",
    # Use our JSON error handler instead of Starlette's debug traceback response.
    debug=False,
)

# Use the same problem format for HTTP errors and invalid input.
# This ensures a consistent error response format across the API.
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unexpected_exception_handler)
app.add_middleware(AuthRateLimitMiddleware)
app.include_router(auth_router)
