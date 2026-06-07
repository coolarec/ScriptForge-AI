from functools import lru_cache

from app.pipeline.service import convert_novel
from app.schemas.conversion import ConvertRequest, ConvertResponse


class ConversionService:
    def convert(self, request: ConvertRequest) -> ConvertResponse:
        return convert_novel(request)


@lru_cache
def get_conversion_service() -> ConversionService:
    return ConversionService()
