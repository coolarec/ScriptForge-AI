# AI 小说转剧本工具

面向七牛 XEngineer 第三批次题目三的 AI 辅助剧本创作工具。系统可将 3 个章节以上的中文小说文本转换为结构化短剧剧本 YAML，并提供 YAML Schema 文档、Schema 校验、来源章节追踪和 mock/API 双生成模式。

## 核心功能

- 3 章以上小说文本输入与章节检测。
- 中文短剧/网剧分场剧本生成。
- YAML 输出、复制和下载。
- YAML Schema 自动校验。
- 每个场景保留 `source_chapters` 和 `adaptation_note`。
- mock provider 默认可演示，无需 API Key。
- OpenAI-compatible API provider 可通过环境变量启用。

## 技术架构

```text
frontend/  Vue 3 + Vite + TypeScript
backend/   Python + uv + FastAPI
docs/      Schema 文档、demo 脚本、PR 计划
samples/   3 章小说样例和 YAML 输出样例
```

后端转换流水线：

```text
chapter_parser -> provider -> adapter -> yaml_builder -> validator
```

## 本地启动

后端：

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

如果 PyPI 网络不稳定，可使用镜像：

```bash
uv sync --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

前端：

```bash
cd frontend
pnpm install
pnpm dev
```

打开 `http://localhost:5173`，点击“载入样例”，再点击“生成 YAML 剧本”。

## API 模式

默认使用 mock provider。若要接入真实大模型，在启动后端前设置：

```bash
export LLM_API_KEY="..."
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL="gpt-4.1-mini"
```

前端选择“API 生成”后会调用后端 LLM provider。未配置 Key 时，系统会提示切回 mock 模式。

## 测试

后端：

```bash
cd backend
uv run pytest
```

前端：

```bash
cd frontend
pnpm build
```

## 示例文件

- 输入样例：`samples/novel_3_chapters.txt`
- 输出样例：`samples/output_script.yaml`
- Schema 文档：`docs/screenplay-yaml-schema.md`
- Demo 脚本：`docs/demo-script.md`
- PR 计划：`docs/pr-plan.md`
- 提交清单：`docs/submission-checklist.md`

## Demo 视频

录制脚本见 `docs/demo-script.md`。视频上传到 bilibili、网盘或其他可访问平台后，将链接追加到本节，并在报名表中填写同一个链接。

## 依赖与原创说明

使用的主要第三方依赖：

- 前端：Vue、Vite、TypeScript。
- 后端：FastAPI、Pydantic、PyYAML、jsonschema、httpx、pytest。

原创功能部分：

- 小说章节解析与 3 章限制校验。
- 短剧化改编流水线。
- mock provider 的故事分析与角色/地点抽取。
- YAML 剧本结构生成。
- JSON Schema 校验与前端校验结果展示。
- Vue 转换工作台交互。

## 评审关注点

- 作品完整度：前后端可运行，内置样例可完整演示。
- 创新性：来源章节追踪、改编说明、短剧钩子和 YAML Schema 校验。
- 开发质量：模块分层、类型模型、测试覆盖、commit 拆分。
- 演示表达：按 `docs/demo-script.md` 录制视频即可覆盖核心功能。

## 提交前检查

见 `docs/submission-checklist.md`。当前本地仓库尚未配置 GitHub/Gitee 远程地址，提交报名材料前需要先推送到公开仓库。
