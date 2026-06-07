from typing import Literal

from pydantic import BaseModel, Field


ProviderMode = Literal["mock", "api"]
DialogueDensity = Literal["low", "medium", "high"]
ElementType = Literal["action", "dialogue", "narration", "transition"]


class ConvertConfig(BaseModel):
    target_scene_count: int = Field(default=6, ge=3, le=12)
    dialogue_density: DialogueDensity = "medium"
    preserve_narration: bool = True


class ConvertRequest(BaseModel):
    text: str = Field(min_length=1)
    provider: ProviderMode = "mock"
    config: ConvertConfig = Field(default_factory=ConvertConfig)


class Chapter(BaseModel):
    id: str
    title: str
    content: str
    summary: str = ""


class Character(BaseModel):
    id: str
    name: str
    role: str
    description: str
    goals: list[str] = Field(default_factory=list)


class StoryEvent(BaseModel):
    id: str
    chapter_id: str
    summary: str
    characters: list[str] = Field(default_factory=list)
    location: str = "未指定地点"


class StoryAnalysis(BaseModel):
    title: str
    chapters: list[Chapter]
    characters: list[Character]
    events: list[StoryEvent]
    locations: list[str]


class ScriptElement(BaseModel):
    type: ElementType
    text: str
    speaker: str | None = None


class Scene(BaseModel):
    id: str
    title: str
    location: str
    time_of_day: str
    source_chapters: list[str]
    dramatic_purpose: str
    adaptation_note: str
    elements: list[ScriptElement]
    hook: str


class Episode(BaseModel):
    id: str
    title: str
    logline: str
    scenes: list[Scene]


class ScriptProject(BaseModel):
    schema_version: str = "1.0"
    project: dict[str, str]
    source: dict[str, list[dict[str, str]]]
    characters: list[Character]
    episodes: list[Episode]
    validation: dict[str, object]


class StageLog(BaseModel):
    stage: str
    status: Literal["success", "warning", "error"]
    message: str


class ValidationIssue(BaseModel):
    path: str
    message: str


class ValidationResult(BaseModel):
    valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)


class ConvertSummary(BaseModel):
    chapter_count: int
    character_count: int
    scene_count: int
    covered_chapters: list[str]


class ConvertResponse(BaseModel):
    yaml: str
    summary: ConvertSummary
    validation: ValidationResult
    stages: list[StageLog]
