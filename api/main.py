from pathlib import Path
from typing import List
from datetime import date
import os
import tempfile
import base64
import io

import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from satquery.agent.controller import AgentController
from satquery.utils.live_imagery import fetch_roi_imagery, validate_bbox


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

        images = controller.load_images(temp_paths)

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
        for path in temp_paths:
            try:
                if path.exists():
                    os.remove(path)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# BI-TEMPORAL LIVE SATELLITE ACQUISITION
# ---------------------------------------------------------------------------

def _geotiff_bytes(img):
    import rasterio
    from rasterio.io import MemoryFile
    from rasterio.transform import Affine

    data = np.asarray(img.data)

    if data.ndim == 2:
        data = data[:, :, None]

    h, w, count = data.shape
    meta = img.metadata

    kwargs = {
        "driver": "GTiff",
        "height": int(h),
        "width": int(w),
        "count": int(count),
        "dtype": str(data.dtype),
        "transform": Affine(*list(meta.transform)[:6]),
    }

    if getattr(meta, "crs", None):
        kwargs["crs"] = meta.crs

    with MemoryFile() as mem:
        with mem.open(**kwargs) as dst:
            dst.write(np.moveaxis(data, -1, 0))
        return mem.read()


def _preview_data_url(img):
    from PIL import Image

    preview = getattr(img, "preview", None)

    if preview is None:
        data = np.asarray(img.data)

        if data.ndim == 2:
            data = data[:, :, None]

        rgb = (
            np.repeat(data, 3, axis=2)
            if data.shape[2] == 1
            else data[:, :, :3]
        )

        rgb = np.nan_to_num(rgb).astype(np.float32)

        lo = np.percentile(rgb, 2, axis=(0, 1), keepdims=True)
        hi = np.percentile(rgb, 98, axis=(0, 1), keepdims=True)

        rgb = np.clip(
            (rgb - lo) / np.maximum(hi - lo, 1e-6),
            0,
            1
        )

        preview = (rgb * 255).astype(np.uint8)

    pil_img = Image.fromarray(
        np.asarray(preview).astype(np.uint8)
    ).convert("RGB")

    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")

    return (
        "data:image/png;base64,"
        + base64.b64encode(buf.getvalue()).decode("ascii")
    )


@app.post("/fetch-imagery")
def fetch_imagery(
    west: float = Form(...),
    south: float = Form(...),
    east: float = Form(...),
    north: float = Form(...),
    t1: str = Form(...),
    t2: str = Form(...),
    include_sar: bool = Form(False),
):
    try:
        bbox = validate_bbox([
            float(west),
            float(south),
            float(east),
            float(north)
        ])

        start = date.fromisoformat(t1)
        end = date.fromisoformat(t2)

        if start >= end:
            raise ValueError("FROM date must be earlier than TO date.")

        fetched = fetch_roi_imagery(
            bbox,
            start,
            end,
            include_sar=False
        )

        images = []

        for img in fetched.images:
            raw = _geotiff_bytes(img)

            meta = img.metadata
            extra = getattr(meta, "extra", {}) or {}

            acquisition_date = str(
                extra.get("acquisition_datetime")
                or extra.get("datetime")
                or extra.get("date")
                or ""
            )[:10]

            role = None
            if acquisition_date:
                if acquisition_date <= t1:
                    role = "t1"
                elif acquisition_date >= t2:
                    role = "t2"

            images.append({
                "name": meta.name,
                "modality": meta.modality,
                "temporal_role": role,
                "mime": "image/tiff",
                "content_base64": base64.b64encode(raw).decode("ascii"),
                "preview_data_url": _preview_data_url(img),
                "metadata": {
                    "width": meta.width,
                    "height": meta.height,
                    "bands": meta.bands,
                    "crs": str(meta.crs) if meta.crs else None,
                    "bounds": (
                        list(meta.bounds)
                        if meta.bounds
                        else None
                    ),
                    "acquisition_date": acquisition_date,
                },
            })

        return {
            "success": True,
            "bbox": list(bbox),
            "requested": {
                "t1": t1,
                "t2": t2,
                "include_sar": False,
            },
            "images": images,
            "info": fetched.info,
            "warnings": list(fetched.warnings),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Live imagery acquisition failed: "
                f"{type(exc).__name__}: {exc}"
            )
        )


# ---------------------------------------------------------------------------
# BI-TEMPORAL ANALYSIS
# Receives T1 and T2 separately and sends them together to AgentController.
# ---------------------------------------------------------------------------

def _json_safe(value):
    """Convert numpy values/arrays into JSON-safe values."""
    if isinstance(value, np.ndarray):
        if value.ndim >= 2 and value.dtype.kind not in "OUS":
            return _array_png_data_url(value)

        if value.ndim >= 2 and value.dtype.kind in "OUS":
            vals, counts = np.unique(
                value.astype(str),
                return_counts=True
            )
            return {
                "shape": list(value.shape),
                "counts": {
                    str(k): int(v)
                    for k, v in zip(vals, counts)
                }
            }

        return value.tolist()

    if isinstance(value, np.generic):
        return value.item()

    if isinstance(value, dict):
        return {
            str(k): _json_safe(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]

    return value


def _array_png_data_url(value):
    from PIL import Image

    arr = np.asarray(value)

    if arr.ndim == 2:
        arr = np.nan_to_num(arr.astype(np.float32))

        lo, hi = np.percentile(arr, [2, 98])

        arr = np.clip(
            (arr - lo) / max(float(hi - lo), 1e-6),
            0,
            1
        )

        arr = (arr * 255).astype(np.uint8)

        image = Image.fromarray(arr, mode="L").convert("RGB")

    else:
        arr = np.asarray(arr)

        if arr.shape[-1] == 1:
            arr = np.repeat(arr, 3, axis=-1)
        elif arr.shape[-1] > 3:
            arr = arr[..., :3]

        arr = np.nan_to_num(arr.astype(np.float32))

        lo = np.percentile(
            arr, 2, axis=(0, 1), keepdims=True
        )
        hi = np.percentile(
            arr, 98, axis=(0, 1), keepdims=True
        )

        arr = np.clip(
            (arr - lo) / np.maximum(hi - lo, 1e-6),
            0,
            1
        )

        arr = (arr * 255).astype(np.uint8)

        image = Image.fromarray(arr, mode="RGB")

    buf = io.BytesIO()
    image.save(buf, format="PNG")

    return (
        "data:image/png;base64,"
        + base64.b64encode(buf.getvalue()).decode("ascii")
    )


@app.post("/analyze-bitemporal")
async def analyze_bitemporal(
    query: str = Form(...),
    t1: UploadFile = File(...),
    t2: UploadFile = File(...),
):
    temp_paths = []

    try:
        if not query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty."
            )

        for upload in (t1, t2):
            suffix = Path(upload.filename or ".tif").suffix

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temp_file:
                temp_file.write(await upload.read())
                temp_paths.append(Path(temp_file.name))

        # IMPORTANT:
        # Preserve the acquisition order supplied by the frontend:
        # t1 = FROM / earlier observation
        # t2 = TO / later observation
        images = controller.load_images(temp_paths)

        result = controller.process(
            query=query.strip(),
            images=images
        )

        return {
            "success": True,
            "status": result.status,
            "answer": result.answer,
            "confidence": float(result.confidence),
            "confidence_breakdown": _json_safe(
                result.confidence_breakdown
            ),
            "task": result.task,
            "sub_capability": result.sub_capability,
            "intent": _json_safe(result.intent),
            "validation": _json_safe(result.validation),
            "tools_used": list(result.tools_used),
            "metrics": _json_safe(result.metrics),
            "visual_evidence": _json_safe(
                result.visual_evidence
            ),
            "warnings": list(result.warnings),
            "errors": list(result.errors),
            "execution_summary": _json_safe(
                result.execution_summary or {}
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Bi-temporal analysis failed: "
                f"{type(exc).__name__}: {exc}"
            )
        )

    finally:
        for path in temp_paths:
            try:
                if path.exists():
                    path.unlink()
            except Exception:
                pass
