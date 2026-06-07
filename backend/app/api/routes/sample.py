from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings, get_settings

router = APIRouter(prefix="/sample", tags=["sample"])


@router.get("")
def sample(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    if not settings.sample_novel_path.exists():
        raise HTTPException(status_code=404, detail="Sample novel is missing.")
    return {"text": settings.sample_novel_path.read_text(encoding="utf-8")}
