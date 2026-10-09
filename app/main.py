@"
from fastapi import FastAPI

app = FastAPI(
    title="Restaurant Supply Chain API",
    description="B2B API for restaurant supply chain management",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "rsc-api"}
"@ | Out-File -Encoding utf8 app\main.py