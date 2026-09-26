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
async def analyze(
    query: str = Form(...),
    files: List[UploadFile] = File(...)
):
    temp_paths = []

    try:
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

        # Save uploaded files temporarily
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

                temp_paths.append(
                    Path(temp_file.name)
                )

        if not temp_paths:
            raise HTTPException(
                status_code=400,
                detail="No valid files were uploaded."
            )

        # Load images through the real SatQuery pipeline
        images = controller.load_images(temp_paths)

        # Run the real AgentController
        result = controller.process(
            query=query,
            images=images
        )

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
        # Clean up temporary uploaded files
        for path in temp_paths:
            try:
                if path.exists():
                    os.remove(path)
            except Exception:
                pass