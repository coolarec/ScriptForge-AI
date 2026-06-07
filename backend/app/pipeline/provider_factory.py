from app.providers.base import StoryProvider
from app.providers.llm_provider import LLMStoryProvider
from app.providers.mock_provider import MockStoryProvider
from app.schemas.conversion import ProviderMode


def get_provider(mode: ProviderMode) -> StoryProvider:
    if mode == "api":
        return LLMStoryProvider()
    return MockStoryProvider()
