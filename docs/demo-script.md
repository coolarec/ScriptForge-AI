# Demo 视频脚本

建议时长：3 到 5 分钟。

## 1. 开场

说明题目：AI 小说转剧本工具，将 3 个章节以上小说自动转换为结构化剧本 YAML，并提供 Schema 文档。

强调定位：不是通用聊天式写作工具，而是面向中文小说/IP 到短剧分场剧本初稿的转换工具。

## 2. 展示启动

展示两个终端：

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
cd frontend
pnpm dev
```

打开 `http://localhost:5173`。

## 3. 核心流程

1. 点击“载入样例”。
2. 展示左侧识别到 3 章。
3. 保持 mock 模式，点击“生成 YAML 剧本”。
4. 展示右侧章节数、角色数、场次数和 Schema 通过状态。
5. 展示阶段日志：章节解析、角色识别、分场改编、YAML 生成、Schema 校验。
6. 滚动 YAML，重点讲 `source_chapters`、`adaptation_note`、`hook`。
7. 点击下载 YAML。

## 4. 错误处理

删掉输入，只保留一章，再点击生成，展示少于 3 章的错误提示。

## 5. 架构说明

展示 README 中的流水线：

```text
chapter_parser -> provider -> adapter -> yaml_builder -> validator
```

说明 mock provider 保证评审环境可演示，API provider 可接入真实 OpenAI-compatible 模型。

## 6. Schema 文档

打开 `docs/screenplay-yaml-schema.md`，说明为什么 Schema 包含章节、角色、集、场、剧本元素、来源追踪和改编说明。

## 7. 收尾

总结三点：

- 满足题目要求：3 章以上小说到 YAML 剧本。
- 工程完整：Vue 前端、FastAPI 后端、uv 管理、测试和文档。
- 创新点明确：来源追踪、改编说明、短剧钩子、Schema 校验。
