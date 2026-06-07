from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    app_title: str = "AI 小说转剧本工具 API"
    app_version: str = "0.1.0"
    app_description: str = "Convert 3+ novel chapters into editable short-drama YAML."
    cors_origins: tuple[str, ...] = ("http://localhost:5173", "http://127.0.0.1:5173")
    sample_novel_path: Path = PROJECT_ROOT / "samples" / "novel_3_chapters.txt"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4.1-mini"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        llm_model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
    )
