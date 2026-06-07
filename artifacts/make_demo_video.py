from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path
from textwrap import wrap

sys.path.insert(0, "/tmp/qiniu_video_pkgs")

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "artifacts" / "demo-video-assets"
FRAME_DIR = ROOT / "artifacts" / "video-frames"
OUTPUT = ROOT / "artifacts" / "ScriptForge-AI-demo.mp4"

W, H = 1280, 720
FPS = 24

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


def screenshot_scene(path: str, caption: str) -> Image.Image:
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

    draw = ImageDraw.Draw(img)
    rounded_rect(draw, (112, 624, 1168, 690), (17, 24, 39, 226), None, 1, 18)
    draw.text((148, 641), caption, font=font(26, bold=True), fill="#ffffff")
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


def encode_video(scenes: list[tuple[Image.Image, float]]) -> None:
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
        str(OUTPUT),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None

    previous: Image.Image | None = None
    fade_frames = int(FPS * 0.35)
    for image, duration in scenes:
        frame_count = max(1, int(duration * FPS))
        if previous is not None:
            for i in range(fade_frames):
                alpha = (i + 1) / fade_frames
                mixed = Image.blend(previous, image, alpha)
                mixed.save(proc.stdin, format="PNG")
            frame_count -= fade_frames
        for _ in range(max(1, frame_count)):
            image.save(proc.stdin, format="PNG")
        previous = image

    proc.stdin.close()
    code = proc.wait()
    if code:
        raise SystemExit(code)


def main() -> None:
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    scenes = [
        (
            slide(
                "ScriptForge AI",
                "把中文小说快速改编成可编辑的短剧 YAML 初稿。",
                ["面向小说作者和 IP 改编场景", "从章节解析到剧本结构化输出", "内置 mock 演示，评审现场无需 API Key"],
            ),
            4.0,
        ),
        (
            slide(
                "为什么需要它？",
                "小说到剧本不是简单摘要，而是结构、场景和追看钩子的重组。",
                ["传统改编门槛高：章节、角色、事件、对白需要重新拆解", "通用聊天工具输出松散：难以稳定进入后续工作流", "YAML + Schema 让初稿可编辑、可校验、可二次加工"],
                "Product Value",
            ),
            6.0,
        ),
        (screenshot_scene("01-home.png", "现代化创作工作台：输入小说、调整参数、准备生成。"), 6.0),
        (screenshot_scene("02-sample-loaded.png", "载入 3 章样例后，系统自动识别章节数和覆盖范围。"), 6.0),
        (screenshot_scene("03-generated.png", "一键生成 YAML 剧本，并展示章节、角色、场次和 Schema 状态。"), 8.0),
        (screenshot_scene("04-yaml-detail.png", "YAML 中保留 source_chapters、adaptation_note 和 hook，方便继续打磨。"), 7.0),
        (architecture_slide(), 7.0),
        (
            slide(
                "Schema 设计重点",
                "让剧本初稿不是一段文本，而是能被工具链继续处理的数据。",
                ["source_chapters：每场戏可以追溯到原小说章节", "adaptation_note：记录改编取舍，便于作者复核", "validation：前端直接展示 Schema 校验结果"],
                "YAML Schema",
            ),
            6.0,
        ),
        (closing_slide(), 5.0),
    ]
    encode_video(scenes)
    print(OUTPUT)


if __name__ == "__main__":
    main()
