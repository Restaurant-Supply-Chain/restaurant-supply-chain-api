from http import HTTPStatus

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException


async def http_exception_handler(request, exception: HTTPException):
    return JSONResponse(
        status_code=exception.status_code,
        media_type="application/problem+json",
        headers=exception.headers,
        content={
            "type": "about:blank",
            "title": HTTPStatus(exception.status_code).phrase,
            "status": exception.status_code,
            "detail": exception.detail,
            "instance": request.url.path,
        },
    )


async def validation_exception_handler(request, exception: RequestValidationError):
    errors = []
    # Return field errors without exposing submitted passwords or other input.
    for error in exception.errors():
        errors.append({
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
        })

    return JSONResponse(
        status_code=422,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": "Unprocessable Entity",
            "status": 422,
            "detail": "Check the submitted fields.",
            "instance": request.url.path,
            "errors": errors,
        },
    )
