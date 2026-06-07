from __future__ import annotations

import re

from app.pipeline.errors import ConversionError
from app.schemas.conversion import Chapter, StageLog

CHAPTER_PATTERN = re.compile(
    r"(?m)^(?P<title>\s*(?:第[零一二三四五六七八九十百千万\d]+章[^\n]*|Chapter\s+\d+[^\n]*|#{1,3}\s+[^\n]+))$",
    re.IGNORECASE,
)


def parse_chapters(text: str) -> tuple[list[Chapter], StageLog]:
    normalized = text.strip()
    if not normalized:
        raise ConversionError(
            "EMPTY_TEXT",
            "请输入小说文本。",
            stage="chapter_parser",
            hints=["粘贴至少 3 个章节，或载入内置样例。"],
        )

    matches = list(CHAPTER_PATTERN.finditer(normalized))
    chapters = _split_by_headings(normalized, matches) if matches else _split_by_blocks(normalized)

    if len(chapters) < 3:
        raise ConversionError(
            "CHAPTER_COUNT_TOO_LOW",
            f"当前只识别到 {len(chapters)} 个章节，至少需要 3 个章节。",
            stage="chapter_parser",
            hints=["使用“第一章/第二章/第三章”或 Markdown 标题分隔章节。"],
        )

    log_status = "success" if matches else "warning"
    message = (
        f"识别到 {len(chapters)} 个章节。"
        if matches
        else f"未发现标准章节标题，已按文本块辅助切分为 {len(chapters)} 个章节。"
    )
    return chapters, StageLog(stage="chapter_parser", status=log_status, message=message)


def _split_by_headings(text: str, matches: list[re.Match[str]]) -> list[Chapter]:
    chapters: list[Chapter] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        title = match.group("title").strip().lstrip("#").strip()
        content = text[start:end].strip()
        chapters.append(
            Chapter(
                id=f"ch{index + 1:02d}",
                title=title or f"第 {index + 1} 章",
                content=content,
                summary=_summarize(content),
            )
        )
    return chapters


def _split_by_blocks(text: str) -> list[Chapter]:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    return [
        Chapter(
            id=f"ch{index + 1:02d}",
            title=f"自动切分章节 {index + 1}",
            content=block,
            summary=_summarize(block),
        )
        for index, block in enumerate(blocks)
    ]


def _summarize(content: str, limit: int = 72) -> str:
    compact = re.sub(r"\s+", " ", content).strip()
    if len(compact) <= limit:
        return compact
    return f"{compact[:limit]}..."
