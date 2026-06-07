from __future__ import annotations

import math
import subprocess
import sys
import wave
from pathlib import Path
from textwrap import wrap

sys.path.insert(0, "/tmp/qiniu_video_pkgs")

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "artifacts" / "demo-video-assets"
FRAME_DIR = ROOT / "artifacts" / "video-frames"
OUTPUT = ROOT / "artifacts" / "ScriptForge-AI-demo-narrated.mp4"
VIDEO_ONLY = ROOT / "artifacts" / "ScriptForge-AI-demo-narrated-video-only.mp4"
NARRATION_DIR = ROOT / "artifacts" / "narration"

W, H = 1280, 720
FPS = 24
VOICE = "Sandy (中文（中国大陆）)"
SAY_RATE = "178"

FONT_REGULAR = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_MONO = "/System/Library/Fonts/Menlo.ttc"


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono else FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(path, size=size)


def rounded_rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill, outline=None, width=1, radius=18):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def base_background() -> Image.Image:
    img = Image.new("RGB", (W, H), "#eef3f8")
    draw = ImageDraw.Draw(img)
    for x in range(0, W, 28):
        draw.line((x, 0, x, H), fill="#dfe7f0", width=1)
    for y in range(0, H, 28):
        draw.line((0, y, W, y), fill="#dfe7f0", width=1)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 0, W, H), fill=(255, 255, 255, 80))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], fnt, fill, max_chars: int, line_gap: int = 10):
    x, y = xy
    for line in wrap(text, width=max_chars):
        draw.text((x, y), line, font=fnt, fill=fill)
        bbox = draw.textbbox((x, y), line, font=fnt)
        y += bbox[3] - bbox[1] + line_gap
    return y


def wrap_cjk(text: str, max_chars: int) -> list[str]:
    lines: list[str] = []
    remaining = text
    while remaining:
        lines.append(remaining[:max_chars])
        remaining = remaining[max_chars:]
    return lines


def split_subtitles(text: str, max_chars: int = 30) -> list[str]:
    chunks: list[str] = []
    current = ""
    for char in text:
        current += char
        if char in "。！？；，：":
            chunks.append(current.strip())
            current = ""
    if current.strip():
        chunks.append(current.strip())

    merged: list[str] = []
    buffer = ""
    for chunk in chunks:
        if not buffer:
            buffer = chunk
        elif len(buffer) + len(chunk) <= max_chars:
            buffer += chunk
        else:
            merged.append(buffer)
            buffer = chunk
    if buffer:
        merged.append(buffer)
    return merged


def subtitle_for(scene: dict, elapsed: float, duration: float) -> str:
    chunks = scene["subtitle_chunks"]
    if not chunks:
        return ""
    weights = [max(1, len(chunk)) for chunk in chunks]
    total = sum(weights)
    cursor = 0.0
    for chunk, weight in zip(chunks, weights):
        span = duration * weight / total
        if elapsed <= cursor + span:
            return chunk
        cursor += span
    return chunks[-1]


def draw_subtitle(image: Image.Image, text: str) -> Image.Image:
    if not text:
        return image
    img = image.convert("RGBA")
    draw = ImageDraw.Draw(img)
    lines = wrap_cjk(text, 30)[:2]
    subtitle_font = font(28, bold=True)
    line_height = 39
    box_h = 34 + line_height * len(lines)
    box = (96, H - box_h - 28, W - 96, H - 28)
    rounded_rect(draw, box, (17, 24, 39, 232), None, 1, 20)
    y = box[1] + 17
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=subtitle_font)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=subtitle_font, fill="#ffffff")
        y += line_height
    return img.convert("RGB")


def slide(title: str, subtitle: str, bullets: list[str], kicker: str = "ScriptForge AI") -> Image.Image:
    img = base_background().convert("RGBA")
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    rounded_rect(draw, (74, 70, 1206, 650), (255, 255, 255, 232), "#d7e0ea", 2, 24)
    rounded_rect(draw, (104, 104, 164, 164), "#2563eb", None, 1, 14)
    draw.text((184, 106), kicker, font=font(24, bold=True), fill="#2563eb")
    draw.text((184, 140), title, font=font(52, bold=True), fill="#111827")
    draw.text((184, 210), subtitle, font=font(25), fill="#43546a")

    y = 306
    for item in bullets:
        rounded_rect(draw, (184, y - 8, 1090, y + 52), "#f8fafc", "#d7e0ea", 1, 16)
        rounded_rect(draw, (204, y + 8, 224, y + 28), "#0f766e", None, 1, 10)
        draw_wrapped(draw, item, (242, y), font(25, bold=True), "#172033", 42, 8)
        y += 78

    img = Image.alpha_composite(img, card)
    return img.convert("RGB")


def architecture_slide() -> Image.Image:
    img = slide(
        "清晰的工程流水线",
        "前端工作台只负责编辑体验，后端 pipeline 保证转换质量和可测性。",
        [
            "chapter_parser：识别 3 章以上输入并给出明确错误提示",
            "provider：mock 可演示，API 可接入 OpenAI-compatible 模型",
            "adapter → yaml_builder → validator：生成可编辑 YAML 并执行 Schema 校验",
        ],
        "Architecture",
    )
    draw = ImageDraw.Draw(img)
    steps = ["parse", "provider", "adapt", "yaml", "validate"]
    x = 170
    y = 555
    for index, step in enumerate(steps):
        rounded_rect(draw, (x, y, x + 150, y + 54), "#111827" if index == 0 else "#ffffff", "#aebfd0", 2, 12)
        draw.text((x + 28, y + 14), step, font=font(21, bold=True, mono=index != 0), fill="#ffffff" if index == 0 else "#172033")
        if index < len(steps) - 1:
            draw.line((x + 160, y + 27, x + 205, y + 27), fill="#2563eb", width=4)
            draw.polygon([(x + 205, y + 27), (x + 193, y + 19), (x + 193, y + 35)], fill="#2563eb")
        x += 210
    return img


def screenshot_scene(path: str) -> Image.Image:
    shot = Image.open(ASSET_DIR / path).convert("RGB")
    shot.thumbnail((W - 96, H - 96), Image.Resampling.LANCZOS)
    img = base_background().convert("RGBA")
    shadow = Image.new("RGBA", (shot.width + 18, shot.height + 18), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    rounded_rect(sd, (9, 9, shot.width + 9, shot.height + 9), (15, 23, 42, 46), None, 1, 18)
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    x = (W - shot.width) // 2
    y = 42
    img.alpha_composite(shadow, (x - 9, y - 9))
    mask = Image.new("L", shot.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, shot.width, shot.height), radius=14, fill=255)
    img.paste(shot, (x, y), mask)

    return img.convert("RGB")


def closing_slide() -> Image.Image:
    return slide(
        "交付结果",
        "一个可运行、可演示、可继续迭代的 AI 小说转剧本工具。",
        [
            "题目要求：3 章以上小说自动转换为结构化剧本 YAML",
            "产品亮点：来源章节追踪、改编说明、短剧钩子、Schema 校验",
            "工程质量：Vue + FastAPI + uv + 测试 + 文档 + GitHub 仓库",
        ],
        "Ready for Demo",
    )


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / float(audio.getframerate())


def make_narration(scenes: list[dict]) -> list[float]:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    NARRATION_DIR.mkdir(parents=True, exist_ok=True)
    durations: list[float] = []
    concat_lines: list[str] = []

    for index, scene in enumerate(scenes, start=1):
        text = scene["narration"]
        aiff = NARRATION_DIR / f"{index:02d}.aiff"
        wav = NARRATION_DIR / f"{index:02d}.wav"
        padded = NARRATION_DIR / f"{index:02d}-padded.wav"

        subprocess.run(["say", "-v", VOICE, "-r", SAY_RATE, "-o", str(aiff), text], check=True)
        subprocess.run(["afconvert", str(aiff), str(wav), "-f", "WAVE", "-d", "LEI16"], check=True)

        duration = max(scene.get("min_duration", 0), wav_duration(wav) + 0.55)
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(wav),
                "-af",
                "apad",
                "-t",
                f"{duration:.3f}",
                str(padded),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        durations.append(duration)
        concat_lines.append(f"file '{padded}'")

    concat_file = NARRATION_DIR / "concat.txt"
    concat_file.write_text("\n".join(concat_lines), encoding="utf-8")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(NARRATION_DIR / "narration.wav"),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return durations


def encode_video(scenes: list[dict], durations: list[float]) -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "image2pipe",
        "-vcodec",
        "png",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(VIDEO_ONLY),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None

    previous: Image.Image | None = None
    fade_frames = int(FPS * 0.35)
    for scene, duration in zip(scenes, durations):
        image = scene["image"]
        frame_count = max(1, int(duration * FPS))
        if previous is not None:
            for i in range(fade_frames):
                alpha = (i + 1) / fade_frames
                mixed = Image.blend(previous, image, alpha)
                subtitle = subtitle_for(scene, i / FPS, duration)
                draw_subtitle(mixed, subtitle).save(proc.stdin, format="PNG")
            frame_count -= fade_frames
        for frame_index in range(max(1, frame_count)):
            elapsed = (frame_index + fade_frames) / FPS
            subtitle = subtitle_for(scene, elapsed, duration)
            draw_subtitle(image, subtitle).save(proc.stdin, format="PNG")
        previous = image

    proc.stdin.close()
    code = proc.wait()
    if code:
        raise SystemExit(code)

    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(VIDEO_ONLY),
            "-i",
            str(NARRATION_DIR / "narration.wav"),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(OUTPUT),
        ],
        check=True,
    )


def main() -> None:
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    scenes = [
        {
            "image": slide(
                "ScriptForge AI",
                "把中文小说快速改编成可编辑的短剧 YAML 初稿。",
                ["面向小说作者和 IP 改编场景", "从章节解析到剧本结构化输出", "内置 mock 演示，评审现场无需 API Key"],
            ),
            "narration": "大家好，我来介绍一下 ScriptForge AI。它是一个 AI 小说转剧本工具，目标很直接：把三章以上的小说文本，快速整理成一份能继续编辑、能校验格式、也方便二次打磨的短剧剧本 YAML 初稿。",
            "min_duration": 10.0,
        },
        {
            "image": slide(
                "为什么需要它？",
                "小说到剧本不是简单摘要，而是结构、场景和追看钩子的重组。",
                ["传统改编门槛高：章节、角色、事件、对白需要重新拆解", "通用聊天工具输出松散：难以稳定进入后续工作流", "YAML + Schema 让初稿可编辑、可校验、可二次加工"],
                "Product Value",
            ),
            "narration": "为什么要做这个工具？因为小说改剧本不只是总结剧情。作者要重新拆章节、整理角色关系，把叙述改成能拍的场景，还要补上短剧需要的追看钩子。通用聊天工具经常输出一整段文字，看起来能用，但后续很难编辑和校验。所以这里用 YAML 加 Schema，把初稿变成结构化数据。",
            "min_duration": 13.0,
        },
        {
            "image": screenshot_scene("01-home.png"),
            "narration": "先看界面。这个页面不是落地页，而是一个创作工作台。左边放小说原文和改编参数，右边放生成结果。用户可以选择 mock 演示，也可以切到 API 生成；还可以设置场次数量、对白密度，以及要不要保留旁白。",
            "min_duration": 11.0,
        },
        {
            "image": screenshot_scene("02-sample-loaded.png"),
            "narration": "我点击载入样例。系统会把三章小说放进编辑器，并立刻识别章节数量。这里可以看到已经识别到三章，字数和覆盖范围也同步更新。这个反馈对作者很有用，因为他在生成之前就知道输入是否符合要求。",
            "min_duration": 12.0,
        },
        {
            "image": screenshot_scene("03-generated.png"),
            "narration": "现在点生成。后端会先解析章节，再抽取角色、地点和事件，然后改编成短剧分场，最后生成 YAML 并做 Schema 校验。生成完成以后，右侧会显示章节数、角色数、场次数，以及 Schema 是否通过。下面的阶段日志也能看到每一步做了什么。",
            "min_duration": 14.0,
        },
        {
            "image": screenshot_scene("04-yaml-detail.png"),
            "narration": "重点看这份 YAML。它不是一段随便生成的文本，而是按剧本结构组织好的数据。每个场景都有 source_chapters，可以追溯到原小说章节；adaptation_note 会说明这一场为什么这样改；hook 则帮助作者保留短剧的追看点。",
            "min_duration": 14.0,
        },
        {
            "image": slide(
                "错误处理与演示稳定性",
                "评审现场可以不依赖外部模型，也能完整跑通核心流程。",
                ["少于 3 章时返回明确错误和修复建议", "mock provider 保证无 API Key 环境也能演示", "API provider 支持接入 OpenAI-compatible 服务"],
                "Reliability",
            ),
            "narration": "我也做了演示稳定性的兜底。评审现场如果没有 API Key，mock provider 也能完整跑通流程。以后要接真实模型，就切到 OpenAI compatible 的 API provider。输入不足三章时，后端会返回明确错误，前端也会告诉用户怎么修。",
            "min_duration": 13.0,
        },
        {
            "image": architecture_slide(),
            "narration": "工程上没有把逻辑堆在一个大文件里。后端是 FastAPI 分层：路由处理 HTTP，service 作为用例入口，pipeline 负责核心转换。流水线从章节解析开始，经过 provider 分析，再做剧本改编、YAML 构建和 Schema 校验。这样的结构更好维护，也更容易测试。",
            "min_duration": 13.0,
        },
        {
            "image": slide(
                "Schema 设计重点",
                "让剧本初稿不是一段文本，而是能被工具链继续处理的数据。",
                ["source_chapters：每场戏可以追溯到原小说章节", "adaptation_note：记录改编取舍，便于作者复核", "validation：前端直接展示 Schema 校验结果"],
                "YAML Schema",
            ),
            "narration": "Schema 的设计也不是为了形式感。它把剧本拆成项目、来源章节、角色、集、场和剧本元素。这样作者能追踪来源，工具能继续编辑，系统也能检查字段是否完整。换句话说，它让 AI 输出从一段文字，变成可以进入工作流的数据。",
            "min_duration": 13.0,
        },
        {
            "image": closing_slide(),
            "narration": "最后总结一下。ScriptForge AI 满足题目要求，可以把三章以上小说转换为结构化 YAML 剧本。它有 Vue 前端、FastAPI 后端、uv 依赖管理、Schema 文档、测试和 GitHub 提交记录。比较重要的亮点，是来源追踪、改编说明、短剧钩子，以及自动 Schema 校验。",
            "min_duration": 12.0,
        },
    ]
    for scene in scenes:
        scene["subtitle_chunks"] = split_subtitles(scene["narration"])
    durations = make_narration(scenes)
    encode_video(scenes, durations)
    print(OUTPUT)


if __name__ == "__main__":
    main()
