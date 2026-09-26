from pathlib import Path
from typing import List
import os
import tempfile

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from satquery.agent.controller import AgentController


app = FastAPI(
    title="SatQuery AI API",
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Agent Controller
# ---------------------------------------------------------

controller = AgentController()


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "SatQuery AI",
        "agent": "ready"
    }


# ---------------------------------------------------------
# Analyze Satellite Imagery
# ---------------------------------------------------------

@app.post("/analyze")
async def analyze(
    query: str = Form(...),
    files: List[UploadFile] = File(...)
):
    temp_paths = []

    try:
        # -------------------------------------------------
        # Validate inputs
        # -------------------------------------------------

        if not query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty."
            )

        if not files:
            raise HTTPException(
                status_code=400,
                detail="At least one image is required."
            )

        # -------------------------------------------------
        # Save uploaded files temporarily
        # -------------------------------------------------

        for uploaded_file in files:

            if not uploaded_file.filename:
                continue

            suffix = Path(uploaded_file.filename).suffix

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temp_file:

                contents = await uploaded_file.read()
                temp_file.write(contents)
                temp_paths.append(Path(temp_file.name))

        if not temp_paths:
            raise HTTPException(
                status_code=400,
                detail="No valid files were uploaded."
            )

        # -------------------------------------------------
        # Load images using SatQuery geospatial pipeline
        # -------------------------------------------------

        images = controller.load_images(temp_paths)

        # -------------------------------------------------
        # Run actual AgentController
        # -------------------------------------------------

        result = controller.process(
            query=query,
            images=images
        )

        # -------------------------------------------------
        # Return dashboard-friendly JSON
        # -------------------------------------------------

        return {
            "status": result.status,
            "answer": result.answer,
            "confidence": result.confidence,
            "confidence_breakdown": result.confidence_breakdown,

            "task": result.task,
            "sub_capability": result.sub_capability,
            "intent": result.intent,

            "validation": result.validation,

            "tools_used": result.tools_used,

            "metrics": result.metrics,
            "visual_evidence": result.visual_evidence,

            "warnings": result.warnings,
            "errors": result.errors,

            "execution_summary": result.execution_summary,

            "inputs": [
                {
                    "filename": file.filename,
                    "content_type": file.content_type
                }
                for file in files
            ]
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

    finally:
        # -------------------------------------------------
        # Clean up temporary uploaded files
        # -------------------------------------------------

        for path in temp_paths:
            try:
                if path.exists():
                    os.remove(path)
            except Exception:
                pass
