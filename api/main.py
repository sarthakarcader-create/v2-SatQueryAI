from fastapi import FastAPI

app = FastAPI(
    title="SatQuery AI API",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "SatQuery AI"
    }
