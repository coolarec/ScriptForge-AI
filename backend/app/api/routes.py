from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.models import ConvertRequest, ConvertResponse
from app.pipeline.errors import ConversionError
from app.pipeline.service import convert_novel

router = APIRouter()

SAMPLE_PATH = Path(__file__).resolve().parents[3] / "samples" / "novel_3_chapters.txt"


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/sample")
def sample() -> dict[str, str]:
    if not SAMPLE_PATH.exists():
        raise HTTPException(status_code=404, detail="Sample novel is missing.")
    return {"text": SAMPLE_PATH.read_text(encoding="utf-8")}


@router.post("/convert", response_model=ConvertResponse)
def convert(request: ConvertRequest) -> ConvertResponse:
    try:
        return convert_novel(request)
    except ConversionError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": exc.code,
                "message": exc.message,
                "stage": exc.stage,
                "hints": exc.hints,
            },
        ) from exc
