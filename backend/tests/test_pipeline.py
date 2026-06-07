import pytest

from app.models import ConvertRequest
from app.pipeline.chapter_parser import parse_chapters
from app.pipeline.errors import ConversionError
from app.pipeline.service import convert_novel


SAMPLE_TEXT = """第一章 雨夜重逢
林晚在雨夜街口遇见顾沉。他递来一把旧伞，却说这不是巧合。

第二章 消失的名单
林晚回到公司，在抽屉里发现一份被撕掉一角的名单。周岚提醒她，名单上的人都在三年前离开过同一个项目。

第三章 天台告白
顾沉把林晚约到天台，承认自己一直在调查那场事故。灯光忽然熄灭，证据从桌上消失。
"""


def test_parse_three_chapters() -> None:
    chapters, log = parse_chapters(SAMPLE_TEXT)

    assert len(chapters) == 3
    assert chapters[0].id == "ch01"
    assert log.status == "success"


def test_reject_less_than_three_chapters() -> None:
    with pytest.raises(ConversionError) as exc:
        parse_chapters("第一章 开端\n只有一章。")

    assert exc.value.code == "CHAPTER_COUNT_TOO_LOW"


def test_convert_mock_provider_generates_valid_yaml() -> None:
    response = convert_novel(ConvertRequest(text=SAMPLE_TEXT))

    assert response.validation.valid
    assert response.summary.chapter_count == 3
    assert response.summary.scene_count >= 3
    assert "source_chapters" in response.yaml
    assert any(stage.stage == "validator" for stage in response.stages)
