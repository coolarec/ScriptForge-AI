# AI 小说转剧本工具设计规格

日期：2026-06-07

## 1. 背景与定位

七牛 XEngineer 第三批次题目三要求开发一款 AI 小说转剧本工具：能将 3 个章节以上的小说文本自动转换为结构化剧本（YAML 格式），并额外提供一篇定义剧本 YAML Schema 的文档，说明 Schema 的设计原因。

结合市场调研，项目不定位为通用 AI 编剧平台，而定位为“中文小说/IP 到短剧化分场剧本 YAML 初稿”的轻量工具。原因是短剧和网文改编场景更贴近中文创作者需求，也更能体现结构化改编、来源追踪和可编辑输出的差异化。

## 2. 评审规则转化

官网评审重点为作品完整度与创新性、开发过程与质量、演示与表达。设计中对应为：

- 作品完整度与创新性：提供可运行 Web 工具、mock/API 双模式、章节来源追踪、短剧钩子和 Schema 校验。
- 开发过程与质量：采用前后端分层架构，保持模块职责清晰；提交按小功能拆分，并在 README 中列明依赖和原创部分。
- 演示与表达：内置 3 章以上样例、稳定 YAML 输出、Schema 文档、demo 视频脚本和一键启动说明。

## 3. 技术选型

- 前端：Vue 3 + Vite + TypeScript。
- 后端：Python + FastAPI，使用 uv 管理 Python 版本和依赖。
- 数据结构：Pydantic 定义内部模型。
- YAML：后端生成 YAML 文本，并用 JSON Schema 校验解析后的 YAML 结构。
- AI 能力：provider 抽象，默认 mock provider 保证无 Key 可演示；可配置 OpenAI-compatible API provider。

## 4. 仓库结构

```text
frontend/
  Vue 页面、组件、API client、前端测试
backend/
  pyproject.toml
  uv.lock
  app/
    main.py
    api/
    pipeline/
    providers/
    schemas/
    services/
  tests/
docs/
  screenplay-yaml-schema.md
  demo-script.md
  pr-plan.md
  superpowers/specs/2026-06-07-ai-novel-to-screenplay-design.md
samples/
  novel_3_chapters.txt
  output_script.yaml
README.md
```

## 5. 用户流程

1. 用户打开 Web 页面。
2. 用户粘贴小说文本，或点击载入内置样例。
3. 系统检测章节数，少于 3 章时阻止转换并展示错误。
4. 用户选择 mock 模式或 API 模式，并可调整目标场次数量、对白密度、旁白保留策略。
5. 用户点击生成，页面展示章节解析、角色识别、剧情梳理、分场改编、YAML 生成、Schema 校验等阶段。
6. 页面展示 YAML 剧本、校验结果、角色摘要、场景数量和章节覆盖情况。
7. 用户复制或下载 YAML，并可查看 Schema 文档。

## 6. 后端流水线

后端提供 `POST /api/convert`，请求包含小说文本、provider 模式和转换配置。响应包含 YAML 文本、结构摘要、阶段日志、校验结果和错误信息。

流水线模块：

- `chapter_parser`：识别“第 X 章”“Chapter X”“### 标题”等章节格式，验证至少 3 章。
- `extractor`：抽取角色、地点、关键事件和每章摘要。
- `adapter`：将小说事件改编为短剧分场，生成冲突节奏、场景目的和结尾钩子。
- `yaml_builder`：将结构化数据组装为 YAML。
- `validator`：使用 JSON Schema 校验 YAML 结构，并返回可读错误。
- `providers`：提供 mock provider 和 OpenAI-compatible provider。

## 7. YAML Schema 核心结构

顶层字段：

- `schema_version`：Schema 版本。
- `project`：项目标题、来源类型、目标格式、语言。
- `source`：输入章节列表和章节摘要。
- `characters`：角色库，供对白 speaker 引用。
- `episodes`：短剧剧集和分场。
- `validation`：可选校验摘要，用于展示工具处理结果。

每个 scene 包含：

- `id`、`title`、`location`、`time_of_day`
- `source_chapters`：来源章节 ID 列表。
- `dramatic_purpose`：场景戏剧目的。
- `adaptation_note`：AI 改编说明。
- `elements`：动作、对白、旁白、转场等剧本元素。
- `hook`：短剧场景或剧集钩子。

设计原因：

- 来源追踪能证明工具理解了 3 章以上小说，而不是凭空生成。
- 角色独立建模能支持对白校验和后续编辑。
- `episodes/scenes/elements` 是短剧生产中自然的层级。
- `adaptation_note` 让 AI 改编过程可解释，增强创新性。
- JSON Schema 校验让 YAML 输出可自动验证，提升工程质量。

## 8. 错误处理

- 空文本或少于 3 章：返回 `CHAPTER_COUNT_TOO_LOW`。
- 章节识别置信度低：允许继续，但在阶段日志中提示。
- API provider 缺少 Key：返回 `PROVIDER_NOT_CONFIGURED`，前端提示切换 mock 模式。
- LLM 输出结构不合规：先尝试结构修复，再进行 Schema 校验。
- Schema 校验失败：返回字段路径、错误原因和修复建议。

## 9. 测试策略

后端测试：

- 章节解析覆盖中文章标题、Markdown 标题和混合文本。
- 少于 3 章时返回明确错误。
- mock provider 能稳定生成包含来源追踪的结构化剧本。
- YAML 输出可被解析并通过 JSON Schema。
- API 响应字段完整。

前端测试：

- 页面可加载。
- 内置样例可填充输入区。
- 转换后可展示 YAML、校验结果和摘要。
- 少于 3 章时显示错误。

集成验证：

- 使用 `samples/novel_3_chapters.txt` 生成 `samples/output_script.yaml`。
- README 中记录本地启动和验证命令。

## 10. 交付材料

- 公开 GitHub/Gitee 仓库。
- README：项目说明、安装启动、功能介绍、架构说明、依赖说明、mock/API 模式、测试方式、demo 链接位置。
- demo 视频：用声音讲解核心流程和设计亮点。
- `docs/screenplay-yaml-schema.md`：Schema 定义与设计原因。
- `docs/demo-script.md`：录屏讲解提纲。
- `docs/pr-plan.md`：PR 拆分与提交说明。

## 11. 提交节奏

建议拆分为以下提交或 PR：

1. 初始化仓库和设计规格。
2. 新增 YAML Schema 文档、示例输入和示例输出。
3. 新增后端 uv/FastAPI 项目与基础 API。
4. 新增转换流水线与 mock provider。
5. 新增 Schema 校验与后端测试。
6. 新增 Vue 前端页面与交互。
7. 完成前后端联调和前端验证。
8. 完善 README、demo 脚本和提交说明。

## 12. 非目标

- 不做账号系统、数据库、多人协作或复杂版本管理。
- 不做完整专业剧本编辑器。
- 不承诺 API 模式在无 Key 环境下可用，mock 模式必须始终可用。

