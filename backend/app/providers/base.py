from abc import ABC, abstractmethod

from app.schemas.conversion import Chapter, StoryAnalysis


class StoryProvider(ABC):
    @abstractmethod
    def analyze(self, chapters: list[Chapter]) -> StoryAnalysis:
        """Return story analysis for screenplay adaptation."""
