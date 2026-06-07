from __future__ import annotations

import yaml

from app.pipeline.adapter import adapt_to_script
from app.pipeline.chapter_parser import parse_chapters
from app.pipeline.provider_factory import get_provider
from app.pipeline.validator import validate_yaml
from app.pipeline.yaml_builder import build_yaml
from app.schemas.conversion import ConvertRequest, ConvertResponse, ConvertSummary, StageLog


def convert_novel(request: ConvertRequest) -> ConvertResponse:
    stages: list[StageLog] = []

    chapters, parser_log = parse_chapters(request.text)
    stages.append(parser_log)

    provider = get_provider(request.provider)
    analysis = provider.analyze(chapters)
    stages.append(
        StageLog(
            stage="extractor",
            status="success",
            message=f"抽取 {len(analysis.characters)} 个角色、{len(analysis.locations)} 个地点、{len(analysis.events)} 个事件。",
        )
    )

    project = adapt_to_script(analysis, request.config)
    stages.append(
        StageLog(
            stage="adapter",
            status="success",
            message=f"改编为 {sum(len(episode.scenes) for episode in project.episodes)} 个短剧分场。",
        )
    )

    yaml_text = build_yaml(project)
    stages.append(StageLog(stage="yaml_builder", status="success", message="YAML 剧本已生成。"))

    validation = validate_yaml(yaml_text)
    stages.append(
        StageLog(
            stage="validator",
            status="success" if validation.valid else "error",
            message="Schema 校验通过。" if validation.valid else "Schema 校验未通过。",
        )
    )

    parsed = yaml.safe_load(yaml_text)
    source_chapters = {chapter["id"] for chapter in parsed["source"]["chapters"]}
    covered_chapters = sorted(
        {
            chapter_id
            for episode in parsed["episodes"]
            for scene in episode["scenes"]
            for chapter_id in scene["source_chapters"]
            if chapter_id in source_chapters
        }
    )
    return ConvertResponse(
        yaml=yaml_text,
        summary=ConvertSummary(
            chapter_count=len(chapters),
            character_count=len(project.characters),
            scene_count=sum(len(episode.scenes) for episode in project.episodes),
            covered_chapters=covered_chapters,
        ),
        validation=validation,
        stages=stages,
    )
