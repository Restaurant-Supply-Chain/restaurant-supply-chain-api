from http import HTTPStatus

from pydantic import BaseModel


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str
    errors: list[dict[str, str]] | None = None


def problem_responses(*status_codes):
    # Document the real error media type instead of FastAPI's default JSON error.
    responses = {}
    for code in status_codes:
        responses[code] = {
            "description": HTTPStatus(code).phrase,
            "content": {
                "application/problem+json": {"schema": ProblemDetails.model_json_schema()},
            },
        }
        if code == 429:
            responses[code]["headers"] = {
                "Retry-After": {
                    "description": "Seconds to wait before retrying.",
                    "schema": {"type": "integer"},
                },
            }
    return responses
