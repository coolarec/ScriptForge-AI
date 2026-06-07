from __future__ import annotations

import re
from collections import Counter

from app.providers.base import StoryProvider
from app.schemas.conversion import Chapter, Character, StoryAnalysis, StoryEvent

NAME_CONTEXT_PATTERN = re.compile(
    r"(?P<name>[\u4e00-\u9fff]{2,3})(?:在|回到|遇见|递来|说|问|提醒|把|约到|承认|要求|意识到|发现)"
)
COMMON_WORDS = {
    "她",
    "他",
    "我",
    "你",
    "我们",
    "他们",
    "少女",
    "少年",
    "男人",
    "女人",
    "第二天",
    "几秒后",
}
PLACE_WORDS = {"街口", "公司", "天台", "医院", "旧宅", "车站", "咖啡", "名单", "硬盘"}


class MockStoryProvider(StoryProvider):
    def analyze(self, chapters: list[Chapter]) -> StoryAnalysis:
        names = _guess_names(chapters)
        characters = [
            Character(
                id=f"char_{index + 1:02d}",
                name=name,
                role="protagonist" if index == 0 else "supporting",
                description=_describe_character(index),
                goals=[_goal_for(index)],
            )
            for index, name in enumerate(names)
        ]
        locations = _guess_locations(chapters)
        events = [
            StoryEvent(
                id=f"ev{index + 1:02d}",
                chapter_id=chapter.id,
                summary=chapter.summary,
                characters=[character.id for character in characters[: min(2, len(characters))]],
                location=locations[index % len(locations)],
            )
            for index, chapter in enumerate(chapters)
        ]
        return StoryAnalysis(
            title=_guess_title(chapters),
            chapters=chapters,
            characters=characters,
            events=events,
            locations=locations,
        )


def _guess_names(chapters: list[Chapter]) -> list[str]:
    text = "\n".join(chapter.content for chapter in chapters)
    contextual = [match.group("name") for match in NAME_CONTEXT_PATTERN.finditer(text)]
    two_char_names = []
    for name in contextual:
        two_char = name[-2:]
        if (
            two_char not in COMMON_WORDS
            and two_char not in PLACE_WORDS
            and not any(stop in two_char for stop in "的了这那么处")
        ):
            two_char_names.append(two_char)
    counts = Counter(two_char_names)
    names = [name for name, _ in counts.most_common(3)]
    defaults = ["林晚", "顾沉", "周岚"]
    merged = []
    for name in names + defaults:
        if name not in merged:
            merged.append(name)
    return merged[:3]


def _guess_locations(chapters: list[Chapter]) -> list[str]:
    text = "\n".join(chapter.content for chapter in chapters)
    known = ["咖啡馆", "公司", "雨夜街口", "医院", "天台", "旧宅", "车站"]
    locations = [place for _, place in sorted((text.find(place), place) for place in known if place in text)]
    return locations or ["城市街口", "临时会议室", "雨夜天台"]


def _guess_title(chapters: list[Chapter]) -> str:
    first_title = chapters[0].title
    clean = re.sub(r"^(第[零一二三四五六七八九十百千万\d]+章|Chapter\s+\d+)\s*", "", first_title).strip()
    return clean or "未命名改编项目"


def _describe_character(index: int) -> str:
    descriptions = [
        "故事主角，面临情感与命运的双重选择。",
        "关键对手或搭档，推动冲突升级。",
        "信息提供者，帮助揭开隐藏真相。",
    ]
    return descriptions[index % len(descriptions)]


def _goal_for(index: int) -> str:
    goals = ["找出真相并保护重要的人", "逼迫主角面对被回避的选择", "用自己的方式守住秘密"]
    return goals[index % len(goals)]
