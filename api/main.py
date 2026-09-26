from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from satquery.agent.controller import AgentController

class AnalyzeRequest(BaseModel):
    query: str
    
app = FastAPI(
    title="SatQuery AI API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


controller = AgentController()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "SatQuery AI",
        "agent": "ready"
    }

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    return {
        "status": "received",
        "query": request.query
    }
