from __future__ import annotations

import json

import httpx

from app.core.config import get_settings
from app.pipeline.errors import ConversionError
from app.providers.base import StoryProvider
from app.schemas.conversion import Chapter, Character, StoryAnalysis, StoryEvent


class LLMStoryProvider(StoryProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_base_url
        self.model = settings.llm_model

    def analyze(self, chapters: list[Chapter]) -> StoryAnalysis:
        if not self.api_key:
            raise ConversionError(
                "PROVIDER_NOT_CONFIGURED",
                "API 模式需要配置 LLM_API_KEY。",
                stage="provider",
                hints=["切换到 mock 模式，或在后端环境中设置 LLM_API_KEY。"],
            )

        prompt = self._build_prompt(chapters)
        try:
            response = httpx.post(
                f"{self.base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "你是小说改编短剧的故事分析助手，只输出 JSON。"},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                },
                timeout=60,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            data = json.loads(content)
            return self._from_json(chapters, data)
        except ConversionError:
            raise
        except Exception as exc:
            raise ConversionError(
                "PROVIDER_FAILED",
                "LLM 分析失败，请检查网络、模型配置或切换 mock 模式。",
                stage="provider",
                hints=[str(exc)],
            ) from exc

    def _build_prompt(self, chapters: list[Chapter]) -> str:
        payload = [{"id": chapter.id, "title": chapter.title, "content": chapter.content[:1800]} for chapter in chapters]
        return (
            "请分析以下小说章节，输出 JSON："
            '{"title": string, "characters": [{"id": string, "name": string, "role": string, "description": string, "goals": [string]}], '
            '"locations": [string], "events": [{"id": string, "chapter_id": string, "summary": string, "characters": [string], "location": string}]}\n'
            f"{json.dumps(payload, ensure_ascii=False)}"
        )

    def _from_json(self, chapters: list[Chapter], data: dict) -> StoryAnalysis:
        return StoryAnalysis(
            title=data.get("title") or "未命名改编项目",
            chapters=chapters,
            characters=[Character(**item) for item in data.get("characters", [])],
            locations=data.get("locations") or ["未指定地点"],
            events=[StoryEvent(**item) for item in data.get("events", [])],
        )
