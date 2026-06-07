from fastapi import APIRouter, Depends, HTTPException

from app.pipeline.errors import ConversionError
from app.schemas.conversion import ConvertRequest, ConvertResponse
from app.services.conversion_service import ConversionService, get_conversion_service

router = APIRouter(prefix="/convert", tags=["conversion"])


@router.post("", response_model=ConvertResponse)
def convert(
    request: ConvertRequest,
    service: ConversionService = Depends(get_conversion_service),
) -> ConvertResponse:
    try:
        return service.convert(request)
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
