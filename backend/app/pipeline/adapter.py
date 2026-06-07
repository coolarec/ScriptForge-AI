from __future__ import annotations

from app.schemas.conversion import ConvertConfig, Episode, Scene, ScriptElement, ScriptProject, StoryAnalysis


def adapt_to_script(analysis: StoryAnalysis, config: ConvertConfig) -> ScriptProject:
    scene_count = max(config.target_scene_count, len(analysis.chapters))
    scenes = [_build_scene(index, analysis, config) for index in range(scene_count)]
    episode = Episode(
        id="ep01",
        title=f"{analysis.title}：第一集",
        logline="主角在连续冲突中发现真相的第一块拼图，并被迫做出选择。",
        scenes=scenes,
    )
    return ScriptProject(
        project={
            "title": analysis.title,
            "source_type": "novel",
            "target_format": "short_drama",
            "language": "zh-CN",
        },
        source={
            "chapters": [
                {"id": chapter.id, "title": chapter.title, "summary": chapter.summary}
                for chapter in analysis.chapters
            ]
        },
        characters=analysis.characters,
        episodes=[episode],
        validation={},
    )


def _build_scene(index: int, analysis: StoryAnalysis, config: ConvertConfig) -> Scene:
    event = analysis.events[index % len(analysis.events)]
    chapter = next(chapter for chapter in analysis.chapters if chapter.id == event.chapter_id)
    protagonist = analysis.characters[0] if analysis.characters else None
    counterpart = analysis.characters[1] if len(analysis.characters) > 1 else protagonist
    scene_number = index + 1
    elements = [
        ScriptElement(
            type="action",
            text=f"{event.location}，{chapter.title}的核心事件被压缩成可视化冲突。{event.summary}",
        )
    ]
    if config.preserve_narration:
        elements.append(
            ScriptElement(type="narration", text="旁白用一句话交代人物无法说出口的隐秘动机。")
        )
    if protagonist:
        elements.append(
            ScriptElement(
                type="dialogue",
                speaker=protagonist.id,
                text=_dialogue_for(scene_number, "lead"),
            )
        )
    if counterpart and counterpart != protagonist:
        elements.append(
            ScriptElement(
                type="dialogue",
                speaker=counterpart.id,
                text=_dialogue_for(scene_number, "counter"),
            )
        )
    if config.dialogue_density == "high" and protagonist:
        elements.append(
            ScriptElement(
                type="dialogue",
                speaker=protagonist.id,
                text="如果今天不说清楚，我们就再也没有机会了。",
            )
        )
    elements.append(ScriptElement(type="transition", text="切至下一场，冲突继续升级。"))

    return Scene(
        id=f"sc{scene_number:02d}",
        title=f"第 {scene_number} 场：{_purpose_for(scene_number)}",
        location=event.location,
        time_of_day="night" if scene_number % 2 else "day",
        source_chapters=[event.chapter_id],
        dramatic_purpose=_purpose_for(scene_number),
        adaptation_note=f"将 {chapter.title} 的叙述压缩为短剧分场，保留事件核心并强化场景钩子。",
        elements=elements,
        hook=_hook_for(scene_number),
    )


def _purpose_for(scene_number: int) -> str:
    purposes = ["建立人物目标", "引爆外部冲突", "暴露隐藏秘密", "制造关系反转", "逼近真相", "留下追看钩子"]
    return purposes[(scene_number - 1) % len(purposes)]


def _hook_for(scene_number: int) -> str:
    hooks = [
        "门外传来一句熟悉的声音。",
        "手机屏幕亮起，出现一张被删除的照片。",
        "主角突然意识到，对方早就知道真相。",
        "灯光熄灭，桌上的证据不见了。",
        "一个新名字出现在旧名单上。",
        "镜头停在主角震惊的眼神上。",
    ]
    return hooks[(scene_number - 1) % len(hooks)]


def _dialogue_for(scene_number: int, role: str) -> str:
    if role == "lead":
        lines = [
            "我不是来解释的，我是来要一个答案。",
            "你以为我什么都不知道吗？",
            "这件事从一开始就不是巧合。",
        ]
    else:
        lines = [
            "答案比你想的更危险。",
            "你现在回头，还来得及。",
            "真正瞒着你的人不是我。",
        ]
    return lines[(scene_number - 1) % len(lines)]
